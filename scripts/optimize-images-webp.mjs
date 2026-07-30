// @ts-nocheck
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const root = process.cwd();
const publicDir = path.join(root, 'public');
const uploadsDir = path.join(publicDir, 'uploads');
const outDir = path.join(root, 'data', 'output');
const backupDir = path.join(root, 'data', 'backups', `original-images-before-webp-${new Date().toISOString().replace(/[:.]/g, '-')}`);
const maxBytes = 300 * 1024;
const imageExt = new Set(['.png', '.jpg', '.jpeg', '.gif', '.webp']);
const sourceExt = new Set(['.json', '.astro', '.ts', '.js', '.mjs', '.css', '.md']);

function walk(dir) {
  if (!fs.existsSync(dir)) return [];
  const out = [];
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name);
    const st = fs.statSync(p);
    if (st.isDirectory()) out.push(...walk(p));
    else out.push(p);
  }
  return out;
}
function posixRel(p, base) { return path.relative(base, p).split(path.sep).join('/'); }
function ensureDir(p) { fs.mkdirSync(p, { recursive: true }); }
function backupAndRemoveOriginal(file) {
  const rel = posixRel(file, publicDir);
  const dst = path.join(backupDir, rel);
  ensureDir(path.dirname(dst));
  fs.copyFileSync(file, dst);
  fs.rmSync(file);
}
async function writeWebpUnderLimit(src, dst) {
  const meta = await sharp(src, { animated: false, pages: 1 }).metadata();
  const origW = meta.width || 0;
  const origH = meta.height || 0;
  for (const maxDim of [1800, 1600, 1400, 1200, 1000, 900, 800, 700, 600, 500]) {
    const scale = Math.min(1, maxDim / Math.max(origW || maxDim, origH || maxDim));
    const width = Math.max(1, Math.round((origW || maxDim) * scale));
    for (const quality of [84, 80, 76, 72, 68, 64, 60, 56, 52, 48, 44, 40, 36, 32, 28, 24, 20]) {
      ensureDir(path.dirname(dst));
      await sharp(src, { animated: false, pages: 1 })
        .rotate()
        .resize({ width, withoutEnlargement: true })
        .webp({ quality, effort: 6 })
        .toFile(dst);
      const size = fs.statSync(dst).size;
      if (size <= maxBytes) return { ok: true, size, quality, width };
    }
  }
  return { ok: false, size: fs.existsSync(dst) ? fs.statSync(dst).size : 0 };
}

const allProjectFiles = walk(root).filter(p => {
  if (p.includes(`${path.sep}node_modules${path.sep}`) || p.includes(`${path.sep}dist${path.sep}`) || p.includes(`${path.sep}data${path.sep}backups${path.sep}`)) return false;
  return sourceExt.has(path.extname(p).toLowerCase());
});
const fileTexts = new Map(allProjectFiles.map(p => [p, fs.readFileSync(p, 'utf8')]));
const refs = new Set();
const re = /\/?uploads\/[^\s"'<>),]+\.(?:png|jpe?g|gif|webp)/gi;
for (const txt of fileTexts.values()) {
  for (const m of txt.matchAll(re)) refs.add(m[0]);
}
const allImages = walk(uploadsDir).filter(p => imageExt.has(path.extname(p).toLowerCase()));
const usedImages = new Set();
for (const ref of refs) {
  const p = path.join(publicDir, ref.replace(/^\//, '').split('/').join(path.sep));
  if (fs.existsSync(p)) usedImages.add(p);
}
const toProcess = Array.from(new Set([
  ...allImages.filter(p => fs.statSync(p).size > maxBytes),
  ...Array.from(usedImages).filter(p => path.extname(p).toLowerCase() !== '.webp'),
]));

const replacements = new Map();
const converted = [];
const failed = [];
for (const src of toProcess) {
  if (!fs.existsSync(src)) continue;
  const oldRel = posixRel(src, publicDir);
  const ext = path.extname(src).toLowerCase();
  const dst = ext === '.webp' ? src + '.tmp.webp' : src.slice(0, -ext.length) + '.webp';
  try {
    const before = fs.statSync(src).size;
    const res = await writeWebpUnderLimit(src, dst);
    if (!res.ok) {
      failed.push({ path: oldRel, oldKb: Math.round(before / 102.4) / 10, resultKb: Math.round(res.size / 102.4) / 10 });
      if (fs.existsSync(dst) && dst !== src) fs.rmSync(dst);
      continue;
    }
    const finalDst = ext === '.webp' ? src : dst;
    if (ext === '.webp') {
      const bak = path.join(backupDir, oldRel);
      ensureDir(path.dirname(bak));
      fs.copyFileSync(src, bak);
      fs.renameSync(dst, src);
    } else {
      backupAndRemoveOriginal(src);
    }
    const newRel = posixRel(finalDst, publicDir);
    replacements.set('/' + oldRel, '/' + newRel);
    replacements.set(oldRel, newRel);
    converted.push({ old: oldRel, new: newRel, oldKb: Math.round(before / 102.4) / 10, newKb: Math.round(fs.statSync(finalDst).size / 102.4) / 10, quality: res.quality, width: res.width });
  } catch (err) {
    failed.push({ path: oldRel, error: String(err?.message || err) });
  }
}

const changedFiles = [];
const replacementEntries = Array.from(replacements.entries()).sort((a, b) => b[0].length - a[0].length);
for (const [fp, oldTxt] of fileTexts) {
  let txt = oldTxt;
  for (const [from, to] of replacementEntries) txt = txt.split(from).join(to);
  if (txt !== oldTxt) {
    fs.writeFileSync(fp, txt, 'utf8');
    changedFiles.push(posixRel(fp, root));
  }
}
const remainingOversized = walk(uploadsDir)
  .filter(p => imageExt.has(path.extname(p).toLowerCase()))
  .map(p => ({ path: posixRel(p, publicDir), size: fs.statSync(p).size }))
  .filter(x => x.size > maxBytes)
  .sort((a, b) => b.size - a.size)
  .map(x => ({ path: x.path, kb: Math.round(x.size / 102.4) / 10 }));

ensureDir(outDir);
const report = { maxKb: 300, convertedCount: converted.length, failed, changedFiles, backupDir: posixRel(backupDir, root), remainingOversized, topConverted: converted.sort((a,b)=>b.oldKb-a.oldKb).slice(0, 80) };
fs.writeFileSync(path.join(outDir, 'image_webp_optimization_20260729.json'), JSON.stringify(report, null, 2), 'utf8');
console.log(JSON.stringify({ converted: converted.length, failed: failed.length, changedFiles, backupDir: report.backupDir, remainingOversized: remainingOversized.slice(0, 20) }, null, 2));
