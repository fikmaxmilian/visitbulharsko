import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'src' / 'data' / 'site-data.json'
OUT = ROOT / 'src' / 'data' / 'property-feed.json'


def clean(s):
    s = re.sub(r'<[^>]+>', ' ', s or '')
    s = unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def main():
    data = json.loads(DATA.read_text(encoding='utf-8'))
    page = next((p for p in data.get('pages', []) if p.get('slug') == 'nemovitosti-bulharsko'), None)
    if not page:
        OUT.write_text(json.dumps({'items': []}, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({'items': 0, 'warning': 'page not found'}, ensure_ascii=False))
        return

    html = page.get('content', '')
    # Elementor export opakuje pro každou nemovitost: image, price text, title, detail URL.
    imgs = re.findall(r'src="([^"]+/uploads/[^"]+?)"', html)
    if not imgs:
        imgs = re.findall(r'(/uploads/[^"\s<>]+)', html)

    links = []
    seen_links = set()
    for href in re.findall(r'href="(https?://www\.mojenemovitostumore\.cz/nemovitosti/detail/[^"]+)"', html):
        href = unescape(href)
        if href not in seen_links:
            seen_links.add(href)
            links.append(href)

    text = clean(html)
    # Matches common exported pattern: "80 700 EUR 2+kk ... Prohlédnout nemovitost".
    matches = re.findall(r'((?:\d{2,3}\s?\d{3}|\d{1,3}\s?\d{3}\s?\d{3})\s*EUR)\s+(.+?)(?=\s+Prohlédnout nemovitost|\s+Více nemovitostí|\s+\d{1,2}\.\s*\d{1,2}\.\s*\d{4})', text)

    items = []
    for i, (price, title) in enumerate(matches):
        title = clean(title)
        # Odstranit datum, pokud se do titulku přilepí.
        title = re.sub(r'\s+\d{1,2}\.\s*\d{1,2}\.\s*\d{4}.*$', '', title).strip()
        if not title or len(title) < 8:
            continue
        img = imgs[i] if i < len(imgs) else '/uploads/2025/01/apartmany-levne.png'
        if img.startswith('https://visitbulharsko.cz'):
            img = img.replace('https://visitbulharsko.cz', '')
        href = links[i] if i < len(links) else 'https://www.mojenemovitostumore.cz/nemovitosti?aff=l4todz91fb'
        items.append({
            'title': title,
            'price': re.sub(r'\s+', ' ', price).strip(),
            'img': img,
            'href': href,
            # Lokální WordPress export neříká aktuální dostupnost. Bez živého ověření
            # nesmí homepage zobrazovat konkrétní položku jako dostupnou.
            'available': False,
        })
        if len(items) >= 9:
            break

    OUT.write_text(json.dumps({'source': '/nemovitosti-bulharsko/', 'items': items}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'items': len(items), 'out': str(OUT)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
