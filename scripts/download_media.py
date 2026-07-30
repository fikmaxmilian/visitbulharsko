import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPORT=json.loads((ROOT/'data'/'content'/'wp_export.json').read_text(encoding='utf-8'))
PUBLIC=ROOT/'public'/'uploads'
PUBLIC.mkdir(parents=True,exist_ok=True)
urls=[]
for m in EXPORT['media']:
    if m.get('source_url'): urls.append(m['source_url'])
for item in EXPORT['posts']+EXPORT['pages']:
    if item.get('featured_image'): urls.append(item['featured_image'])
    urls += re.findall(r'https://visitbulharsko\.cz/wp-content/uploads/[^\s"\')<>]+', item.get('content',''))
urls=sorted(set(u.replace('\\/','/') for u in urls))
map_={}
errors=[]
for i,u in enumerate(urls,1):
    parsed=urllib.parse.urlparse(u)
    # keep wp-content path under public/uploads by basename; avoid huge tree but preserve unique dirs partially
    parts=[p for p in parsed.path.split('/') if p]
    try:
        idx=parts.index('uploads')
        rel=Path(*parts[idx+1:])
    except ValueError:
        rel=Path(Path(parsed.path).name)
    if not rel.name:
        continue
    dest=PUBLIC/rel
    dest.parent.mkdir(parents=True,exist_ok=True)
    local='/uploads/' + '/'.join(rel.parts)
    map_[u]=local
    if dest.exists() and dest.stat().st_size>0:
        continue
    try:
        parsed_u=urllib.parse.urlsplit(u)
        safe_path=urllib.parse.quote(urllib.parse.unquote(parsed_u.path), safe='/')
        safe_url=urllib.parse.urlunsplit((parsed_u.scheme, parsed_u.netloc, safe_path, parsed_u.query, parsed_u.fragment))
        req=urllib.request.Request(safe_url, headers={'User-Agent':'Hermes VisitBulharsko media mirror'})
        with urllib.request.urlopen(req, timeout=12) as r:
            data=r.read()
        dest.write_bytes(data)
        print(f'[{i}/{len(urls)}] OK {local} {len(data)}')
    except Exception as e:
        errors.append({'url':u,'error':str(e)})
        print(f'[{i}/{len(urls)}] ERR {u}: {e}')
(ROOT/'data'/'content'/'media_map.json').write_text(json.dumps(map_,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'data'/'content'/'media_errors.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'urls':len(urls),'downloaded_or_existing':len(map_)-len(errors),'errors':len(errors)},ensure_ascii=False,indent=2))
