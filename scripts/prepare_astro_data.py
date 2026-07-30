import json
import re
import shutil
from pathlib import Path
from html import unescape

ROOT=Path(__file__).resolve().parents[1]
content_dir=ROOT/'data'/'content'
export=json.loads((content_dir/'wp_export.json').read_text(encoding='utf-8'))
media_map=json.loads((content_dir/'media_map.json').read_text(encoding='utf-8')) if (content_dir/'media_map.json').exists() else {}
SITE='https://visitbulharsko.cz'

def repl_urls(html):
    html=html or ''
    html=unescape(html)
    for remote,local in sorted(media_map.items(), key=lambda x: -len(x[0])):
        html=html.replace(remote, local)
        html=html.replace(remote.replace('https://','http://'), local)
    html=html.replace(SITE, '')
    html=re.sub(r'\s(srcset|sizes)="[^"]*"','',html)
    html=re.sub(r'<script[\s\S]*?</script>','',html,flags=re.I)
    html=re.sub(r'<style[\s\S]*?</style>','',html,flags=re.I)
    # strip common WP classes but keep semantic content
    html=re.sub(r' class="[^"]*(wp-block|align|size-|attachment-|schema|yoast)[^"]*"','',html)
    return html.strip()

def local_img(url):
    if not url: return None
    url=unescape(url)
    return media_map.get(url) or media_map.get(url.replace('http://','https://')) or url.replace(SITE,'')

def clean_text(s):
    s=unescape(s or '')
    s=re.sub(r'\*\*(.*?)\*\*', r'\1', s)
    s=s.replace('Magazin není magazín a jiné vtipná slova', 'Magazin není magazín a jiná vtipná slova')
    return s.strip()

FALLBACKS={
    'nejoblibenejsi-destinace':'/uploads/2025/01/nessebar.jpeg',
    'historie-bulharska':'/uploads/2025/01/Rila_Monastery-scaled.jpg',
    'kultura-a-tradice':'/uploads/2025/01/sonyx97140_A_serene_scene_of_a_Bulgarian_folk_ensemble_with_a_54b36ab0-0a0e-400f-902f-808ce413f332_3.png',
    'tipy-na-vylety':'/uploads/2025/03/plovdiv-pohled-scaled.webp',
    'cestovni-pruvodce':'/uploads/2025/01/AdobeStock_163952053-scaled.jpeg',
    'prakticke-tipy':'/uploads/2025/03/smejici-se-lide-scaled.webp',
    'zpravy-bulharsko':'/uploads/2023/07/header-image-2-1.jpg',
}
def exists_local(path):
    return bool(path and path.startswith('/uploads/') and (ROOT/'public'/path.lstrip('/')).exists())

def fallback_for(cats):
    for c in cats or []:
        f=FALLBACKS.get(c.get('slug'))
        if exists_local(f): return f
    return '/uploads/2023/07/header-image-2-1.jpg'

def safe_image_path(img, slug):
    if not exists_local(img):
        return img
    name=Path(img).name
    if len(name) < 95 and all(ord(ch) < 128 for ch in name):
        return img
    src=ROOT/'public'/img.lstrip('/')
    ext=src.suffix.lower() or '.jpg'
    dest_rel=f'/uploads/hermes/{slug}{ext}'
    dest=ROOT/'public'/dest_rel.lstrip('/')
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists() or dest.stat().st_size != src.stat().st_size:
        shutil.copy2(src, dest)
    return dest_rel

def item(x):
    y={k:x.get(k) for k in ['id','type','slug','path','title','excerpt','date','modified','categories','seo']}
    y['title']=clean_text(y.get('title'))
    y['excerpt']=clean_text(y.get('excerpt'))
    y['content']=repl_urls(x.get('content',''))
    img=local_img(x.get('featured_image'))
    if not exists_local(img):
        img=fallback_for(y.get('categories'))
    y['featured_image']=safe_image_path(img, y.get('slug') or str(y.get('id')))
    y['featured_alt']=x.get('featured_alt') or x.get('title') or ''
    y['reading_minutes']=max(1, round(len((x.get('text') or '').split())/220))
    return y
posts=[item(p) for p in export['posts']]
pages=[item(p) for p in export['pages']]
# Sort newest first like current news feed
posts.sort(key=lambda p:p.get('date') or '', reverse=True)
# ensure important travel evergreen featured manually based on slugs if needed
categories=export['categories']
out={'posts':posts,'pages':pages,'categories':categories,'generatedFrom':SITE}
(ROOT/'src'/'data').mkdir(parents=True,exist_ok=True)
(ROOT/'src'/'data'/'site-data.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'posts':len(posts),'pages':len(pages),'categories':len(categories),'out':str(ROOT/'src'/'data'/'site-data.json')},ensure_ascii=False,indent=2))
