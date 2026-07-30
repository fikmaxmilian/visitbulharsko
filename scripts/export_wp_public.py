import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

SITE='https://visitbulharsko.cz'
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'content'
OUT.mkdir(parents=True,exist_ok=True)

TAG_RE=re.compile(r'<[^>]+>')
def fetch_json(url, timeout=30):
    req=urllib.request.Request(url, headers={'User-Agent':'Hermes VisitBulharsko content export'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8','replace')), dict(r.headers)

def clean(s):
    return re.sub(r'\s+',' ',TAG_RE.sub(' ',s or '')).strip()

def get_all(typ, params=''):
    items=[]
    total_pages=1
    page=1
    while page<=total_pages:
        sep='&' if params else ''
        url=f'{SITE}/wp-json/wp/v2/{typ}?per_page=100&page={page}{sep}{params}'
        try:
            data, headers = fetch_json(url)
        except Exception as e:
            print('ERR', typ, page, e)
            break
        total_pages=int(headers.get('X-WP-TotalPages') or total_pages)
        if not data: break
        items.extend(data)
        page+=1
        time.sleep(0.15)
    return items

categories=get_all('categories', '_fields=id,count,description,link,name,slug,parent')
media=get_all('media', '_fields=id,source_url,alt_text,caption,media_details')
media_by_id={m['id']:m for m in media}
posts=get_all('posts', '_fields=id,slug,link,title,content,excerpt,date,modified,categories,featured_media,yoast_head_json')
pages=get_all('pages', '_fields=id,slug,link,title,content,excerpt,date,modified,featured_media,yoast_head_json')
cat_by_id={c['id']:c for c in categories}

def norm(item, typ):
    title=clean(item.get('title',{}).get('rendered',''))
    content=item.get('content',{}).get('rendered','') or ''
    excerpt=clean(item.get('excerpt',{}).get('rendered',''))
    path=urllib.parse.urlparse(item.get('link','')).path or '/'
    fm=media_by_id.get(item.get('featured_media'))
    cats=[cat_by_id.get(cid) for cid in item.get('categories',[]) if cat_by_id.get(cid)]
    yoast=item.get('yoast_head_json') or {}
    return {
        'id': item['id'], 'type': typ, 'slug': item.get('slug'), 'url': item.get('link'), 'path': path,
        'title': title, 'excerpt': excerpt, 'content': content, 'text': clean(content),
        'date': item.get('date'), 'modified': item.get('modified'),
        'categories': [{'id':c['id'],'name':c['name'],'slug':c['slug'],'link':c['link']} for c in cats],
        'featured_image': fm.get('source_url') if fm else (yoast.get('og_image',[{}])[0].get('url') if yoast.get('og_image') else None),
        'featured_alt': (fm or {}).get('alt_text','') if fm else '',
        'seo': {'title': yoast.get('title') or title, 'description': yoast.get('description') or excerpt}
    }

bundle={'site':SITE,'categories':categories,'posts':[norm(p,'post') for p in posts],'pages':[norm(p,'page') for p in pages], 'media':media}
(OUT/'wp_export.json').write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding='utf-8')
# summary md
lines=['# VisitBulharsko export','',f'- posts: {len(posts)}',f'- pages: {len(pages)}',f'- categories: {len(categories)}',f'- media: {len(media)}','','## Pages']
for p in bundle['pages']:
    lines.append(f"- {p['path']} — {p['title']}")
lines.append('\n## Categories')
for c in categories:
    lines.append(f"- /category/{c['slug']}/ — {c['name']} ({c['count']})")
lines.append('\n## Posts')
for p in bundle['posts']:
    cats=', '.join(c['name'] for c in p['categories'])
    lines.append(f"- {p['path']} — {p['title']} [{cats}]")
(OUT/'export_report.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'posts':len(posts),'pages':len(pages),'categories':len(categories),'media':len(media),'export':str(OUT/'wp_export.json')},ensure_ascii=False,indent=2))
