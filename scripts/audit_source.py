import json
import re
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

SITE = 'https://visitbulharsko.cz'
OUT = Path(__file__).resolve().parents[1] / 'data' / 'source'
OUT.mkdir(parents=True, exist_ok=True)

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.assets=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag=='a' and d.get('href'):
            self.links.append(d['href'])
        for k in ['src','href','data-src']:
            if d.get(k):
                v=d[k]
                if any(x in v for x in ['/wp-content/','.css','.js','.webp','.jpg','.png','.svg']):
                    self.assets.append(v)

def fetch(url, timeout=25):
    req=urllib.request.Request(url, headers={'User-Agent':'Hermes VisitBulharsko migration audit'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.headers, r.read().decode('utf-8','replace')

def try_fetch(url):
    try:
        status, headers, body = fetch(url)
        return {'ok': True, 'status': status, 'headers': dict(headers), 'body': body}
    except Exception as e:
        return {'ok': False, 'error': str(e)}

def clean_text(html):
    html=re.sub(r'<script[\s\S]*?</script>',' ',html,flags=re.I)
    html=re.sub(r'<style[\s\S]*?</style>',' ',html,flags=re.I)
    return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',html)).strip()

report={'site': SITE, 'endpoints': {}, 'urls': [], 'assets': [], 'nav_candidates': []}
for path in ['/', '/sitemap.xml', '/post-sitemap.xml', '/page-sitemap.xml', '/category-sitemap.xml', '/wp-json/', '/wp-json/wp/v2/types']:
    u=SITE+path
    got=try_fetch(u)
    report['endpoints'][path]={k:v for k,v in got.items() if k!='body'}
    if got.get('body'):
        (OUT / (path.strip('/').replace('/','_') or 'homepage')).with_suffix('.html').write_text(got['body'], encoding='utf-8')

# sitemap urls
sitemap_text=''
for p in ['/sitemap.xml','/post-sitemap.xml','/page-sitemap.xml']:
    fp=(OUT / (p.strip('/').replace('/','_'))).with_suffix('.html')
    if fp.exists(): sitemap_text += '\n' + fp.read_text(encoding='utf-8', errors='replace')
urls=sorted(set(re.findall(r'<loc>(https?://[^<]+)</loc>', sitemap_text)))
# fallback homepage links
home=(OUT/'homepage.html').read_text(encoding='utf-8',errors='replace') if (OUT/'homepage.html').exists() else ''
p=LinkParser(); p.feed(home)
for href in p.links:
    absu=urllib.parse.urljoin(SITE+'/',href).split('#')[0]
    if absu.startswith(SITE): urls.append(absu)
for asset in p.assets:
    report['assets'].append(urllib.parse.urljoin(SITE+'/',asset))
report['urls']=sorted(set(u.rstrip('/')+'/' for u in urls if u.startswith(SITE)))
report['assets']=sorted(set(report['assets']))
# WP REST published posts/pages basic
for typ in ['pages','posts','categories']:
    all_items=[]
    for page in range(1,8):
        url=f'{SITE}/wp-json/wp/v2/{typ}?per_page=100&page={page}&_fields=id,slug,link,title,date,modified,excerpt,categories,featured_media'
        got=try_fetch(url)
        if not got['ok']:
            break
        try:
            data=json.loads(got['body'])
        except Exception:
            break
        if not data: break
        all_items.extend(data)
    report[f'wp_{typ}']=all_items

# homepage summary
text=clean_text(home)
report['homepage_text_sample']=text[:2500]
report['counts']={k: len(v) for k,v in report.items() if isinstance(v,list)}
(OUT/'audit_source.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'urls.txt').write_text('\n'.join(report['urls']),encoding='utf-8')
print(json.dumps({'counts':report['counts'], 'endpoints':report['endpoints'], 'urls_file':str(OUT/'urls.txt')}, ensure_ascii=False, indent=2))
