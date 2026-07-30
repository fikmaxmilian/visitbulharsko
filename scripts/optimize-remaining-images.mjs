// @ts-nocheck
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const root = process.cwd();
const publicDir = path.join(root, 'public');
const backupDir = path.join(root, 'data', 'backups', `remaining-oversized-images-${new Date().toISOString().replace(/[:.]/g, '-')}`);
const outDir = path.join(root, 'data', 'output');
const maxBytes = 300 * 1024;
const imageExt = new Set(['.png', '.jpg', '.jpeg', '.gif', '.webp']);
const sourceExt = new Set(['.json', '.astro', '.ts', '.js', '.mjs', '.css', '.md']);
function walk(dir){ if(!fs.existsSync(dir)) return []; return fs.readdirSync(dir).flatMap(n=>{const p=path.join(dir,n); const s=fs.statSync(p); return s.isDirectory()?walk(p):[p];}); }
function rel(p,b=publicDir){ return path.relative(b,p).split(path.sep).join('/'); }
function ensure(p){ fs.mkdirSync(p,{recursive:true}); }
async function writeUnder(src,dst){
  const m=await sharp(src,{animated:false,pages:1}).metadata();
  const ow=m.width||1000, oh=m.height||1000;
  for (const maxDim of [1400,1200,1000,900,800,700,600,500,420]) {
    const scale=Math.min(1,maxDim/Math.max(ow,oh));
    const width=Math.max(1,Math.round(ow*scale));
    for (const q of [80,72,64,56,48,40,32,26,20,16]) {
      ensure(path.dirname(dst));
      await sharp(src,{animated:false,pages:1}).rotate().resize({width,withoutEnlargement:true}).webp({quality:q,effort:6}).toFile(dst);
      if (fs.statSync(dst).size<=maxBytes) return {quality:q,width,kb:Math.round(fs.statSync(dst).size/102.4)/10};
    }
  }
  return null;
}
const oversized=walk(path.join(publicDir,'uploads')).filter(p=>imageExt.has(path.extname(p).toLowerCase()) && fs.statSync(p).size>maxBytes);
const replacements=[]; const done=[]; const failed=[];
for (const src of oversized) {
  const oldRel=rel(src);
  const ext=path.extname(src);
  const base=src.slice(0,-ext.length);
  const dst=base.replace(/-optimized$/,'')+'-optimized.webp';
  try {
    const res=await writeUnder(src,dst);
    if (!res) { failed.push({path:oldRel, reason:'cannot_get_under_300kb'}); continue; }
    const newRel=rel(dst);
    replacements.push(['/'+oldRel,'/'+newRel],[oldRel,newRel]);
    const bak=path.join(backupDir,oldRel); ensure(path.dirname(bak)); fs.copyFileSync(src,bak);
    try { fs.chmodSync(src,0o666); fs.rmSync(src,{force:true}); } catch(e) { failed.push({path:oldRel, reason:'optimized_but_could_not_remove_original', error:String(e.message||e)}); }
    done.push({old:oldRel,new:newRel,oldKb:Math.round(fs.statSync(bak).size/102.4)/10,newKb:res.kb,quality:res.quality,width:res.width});
  } catch(e) { failed.push({path:oldRel,error:String(e.message||e)}); }
}
const files=walk(root).filter(p=>!p.includes(`${path.sep}node_modules${path.sep}`)&&!p.includes(`${path.sep}dist${path.sep}`)&&!p.includes(`${path.sep}data${path.sep}backups${path.sep}`)&&sourceExt.has(path.extname(p).toLowerCase()));
const changed=[];
for (const fp of files) {
  let txt=fs.readFileSync(fp,'utf8'), old=txt;
  for (const [a,b] of replacements.sort((x,y)=>y[0].length-x[0].length)) txt=txt.split(a).join(b);
  if (txt!==old) { fs.writeFileSync(fp,txt,'utf8'); changed.push(rel(fp,root)); }
}
const rem=walk(path.join(publicDir,'uploads')).filter(p=>imageExt.has(path.extname(p).toLowerCase()) && fs.statSync(p).size>maxBytes).map(p=>({path:rel(p),kb:Math.round(fs.statSync(p).size/102.4)/10})).sort((a,b)=>b.kb-a.kb);
const report={done,failed,changed,backupDir:rel(backupDir,root),remainingOversized:rem};
fs.writeFileSync(path.join(outDir,'image_webp_remaining_optimization_20260729.json'),JSON.stringify(report,null,2),'utf8');
console.log(JSON.stringify({done:done.length,failed:failed.length,changed,remaining:rem},null,2));
