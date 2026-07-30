import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'src' / 'data' / 'property-feed.json'
FEED_LAST = ROOT / 'data' / 'property-feed-last.xml'

FEED_URL = 'https://s1.system.softreal.cz/mojenemovitostumore/softreal/publicExportFacebook/index/1002/'
AFFILIATE_CODE = 'l4todz91fb'
MAX_ITEMS = 36
MIN_PRICE_EUR = 35_000
MAX_PRICE_EUR = 180_000

FOREIGN_RE = re.compile(r'\b(alb[aá]nie|albania|durres|durr[eë]s|vlora|sarand|egypt|hurghada|čern[aá]\s*hora|montenegro|chorvatsko|croatia|řecko|greece)\b', re.I)
HOUSE_RE = re.compile(r'\b(vila|villa|house)\b', re.I)
PROPERTY_RE = re.compile(r'\b(\d\+kk|apartm[aá]n|byt|studio|apartment|garsonka)\b', re.I)

BG_LOCATIONS = [
    'Sluneční pobřeží', 'Sveti Vlas', 'Sozopol', 'Nesebar', 'Nessebar', 'Ravda', 'Pomorie',
    'Burgas', 'Varna', 'Kavarna', 'Balčik', 'Balchik', 'Carevo', 'Tsarevo', 'Černomorec',
    'Chernomorets', 'Primorsko', 'Lozenec', 'Aheloy', 'Byala', 'Obzor', 'Elenite', 'Pamporovo',
    'Bansko', 'Kosharitsa', 'Sunny Beach'
]
BG_RE = re.compile('|'.join(re.escape(x) for x in BG_LOCATIONS), re.I)


def local_name(tag):
    return tag.split('}', 1)[-1].lower()


def node_text(node):
    if node is None:
        return ''
    return ''.join(node.itertext()).strip()


def first_text(item, names):
    names = {n.lower() for n in names}
    for child in item.iter():
        if child is item:
            continue
        if local_name(child.tag) in names:
            value = node_text(child)
            if value:
                return value
    return ''


def clean(s):
    s = re.sub(r'<[^>]+>', ' ', s or '')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def parse_price(value):
    s = str(value or '').replace('\xa0', ' ')
    m = re.search(r'(\d[\d\s.,]*)', s)
    if not m:
        return None
    raw = m.group(1).replace(' ', '').replace(',', '.')
    try:
        return float(raw)
    except ValueError:
        return None


def fmt_price(price):
    return f"{round(price):,}".replace(',', ' ') + ' EUR'


def append_affiliate(url):
    if not url:
        return url
    parsed = urlparse(url.strip())
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query['aff'] = AFFILIATE_CODE
    return urlunparse(parsed._replace(query=urlencode(query)))


def extract_location(title):
    for loc in sorted(BG_LOCATIONS, key=len, reverse=True):
        if re.search(re.escape(loc), title, re.I):
            return loc
    parts = [p.strip() for p in title.split(',') if p.strip()]
    return parts[-1] if len(parts) > 1 and len(parts[-1]) < 28 else ''


def looks_like_bulgaria(title, description):
    text = f'{title} {description}'
    if FOREIGN_RE.search(text):
        return False
    # Některé exportní descriptiony jsou obecné, proto bulharskou lokaci vyžadujeme
    # přímo v titulku nabídky.
    return bool(BG_RE.search(title) or re.search(r'Bulharsk|Bulgaria', title, re.I))


def find_items(root):
    items = [el for el in root.iter() if local_name(el.tag) in {'item', 'entry', 'product', 'listing'}]
    return items


def main():
    req = urllib.request.Request(FEED_URL, headers={'User-Agent': 'VisitBulharsko feed sync/1.0', 'Accept': 'application/xml,text/xml,*/*'})
    with urllib.request.urlopen(req, timeout=90) as response:
        xml = response.read()

    FEED_LAST.parent.mkdir(parents=True, exist_ok=True)
    FEED_LAST.write_bytes(xml)

    root = ET.fromstring(xml)
    records = []
    seen = set()

    for item in find_items(root):
        title = clean(first_text(item, ['title', 'g:title', 'name']))
        description = clean(first_text(item, ['description', 'g:description']))
        href = first_text(item, ['link', 'g:link', 'url'])
        image = first_text(item, ['image_link', 'g:image_link', 'image', 'photo'])
        raw_price = first_text(item, ['price', 'g:price', 'cena'])
        raw_id = first_text(item, ['id', 'g:id'])
        price = parse_price(raw_price)

        if not title or not href or not price:
            continue
        if href in seen:
            continue
        if not (MIN_PRICE_EUR <= price <= MAX_PRICE_EUR):
            continue
        if HOUSE_RE.search(f'{title} {description}'):
            continue
        if not PROPERTY_RE.search(f'{title} {description}'):
            continue
        if not looks_like_bulgaria(title, description):
            continue

        seen.add(href)
        records.append({
            'id': raw_id or f'feed-{len(records) + 1}',
            'title': title,
            'price': fmt_price(price),
            'priceNum': round(price),
            'img': image,
            'href': append_affiliate(href),
            'location': extract_location(title),
            'available': True,
        })
        if len(records) >= MAX_ITEMS:
            break

    OUT.write_text(json.dumps({
        'source': FEED_URL,
        'fetchedAt': datetime.now(timezone.utc).isoformat(),
        'items': records,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'items': len(records), 'out': str(OUT), 'source': FEED_URL}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
