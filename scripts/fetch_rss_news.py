import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, UTC
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT / 'data' / 'feed_sources.json'
OUT = ROOT / 'src' / 'data' / 'feed-news.json'
RAW_OUT = ROOT / 'data' / 'live-news-raw.json'

TRAVEL_KEYWORDS = {
    # lokality a turistická místa
    'sofia': 3, 'varna': 4, 'burgas': 4, 'nesebar': 5, 'nessebar': 5, 'sunny beach': 5,
    'slanchev bryag': 5, 'sozopol': 5, 'primorsko': 5, 'kiten': 5, 'pomorie': 5,
    'golden sands': 5, 'zlatni pyasatsi': 5, 'albena': 5, 'balchik': 5, 'bansko': 5,
    'borovets': 5, 'pamporovo': 5, 'plovdiv': 3, 'rila': 3, 'black sea': 5,
    'coast': 4, 'beach': 5, 'resort': 5, 'seaside': 5,

    # cestování, doprava, hranice
    'airport': 6, 'flight': 6, 'flights': 6, 'airline': 6, 'ryanair': 6, 'wizz air': 6,
    'border': 5, 'schengen': 5, 'passport': 5, 'visa': 5, 'customs': 5, 'traffic': 4,
    'road': 4, 'highway': 4, 'motorway': 4, 'train': 4, 'railway': 4, 'bus': 4,
    'ferry': 4, 'port': 4, 'tourist': 6, 'tourists': 6, 'tourism': 6, 'travel': 6,
    'holiday': 5, 'vacation': 5,

    # dopad na cestování / bezpečnost / počasí
    'weather': 5, 'storm': 5, 'snow': 4, 'heatwave': 5, 'rain': 4, 'flood': 6,
    'fire': 5, 'wildfire': 6, 'earthquake': 6, 'warning': 5, 'alert': 5,
    'strike': 5, 'protest': 3, 'accident': 4, 'closure': 5, 'delay': 5, 'delays': 5,
    'cancelled': 5, 'cancelled flights': 7, 'water shortage': 6, 'power outage': 5,
}

EXCLUDE_KEYWORDS = {
    'parliament', 'coalition', 'election', 'minister said', 'party leader', 'cabinet',
    'football', 'basketball', 'tennis', 'stock exchange', 'shares', 'cryptocurrency',
}

IMPORTANT_OVERRIDE = {'schengen', 'airport', 'flight', 'flights', 'tourism', 'tourist', 'weather', 'border', 'black sea'}

BULGARIA_CONTEXT = {
    'bulgaria', 'bulgarian', 'sofia', 'varna', 'burgas', 'nesebar', 'nessebar', 'sunny beach',
    'slanchev bryag', 'sozopol', 'primorsko', 'kiten', 'pomorie', 'golden sands',
    'zlatni pyasatsi', 'albena', 'balchik', 'bansko', 'borovets', 'pamporovo', 'plovdiv',
    'rila', 'black sea'
}

GENERIC_FALSE_POSITIVES = {'port', 'fire', 'rain', 'bus', 'road'}


def local_name(tag):
    return tag.rsplit('}', 1)[-1].lower()


def child_text(el, names):
    names = {n.lower() for n in names}
    for child in list(el):
        if local_name(child.tag) in names:
            return unescape(''.join(child.itertext()).strip())
    return ''


def first_link(el):
    # RSS/RDF: <link>url</link>; Atom: <link href="..." />
    direct = child_text(el, {'link'})
    if direct:
        return direct
    for child in list(el):
        if local_name(child.tag) == 'link' and child.attrib.get('href'):
            return child.attrib['href']
    return ''


def strip_html(s):
    s = re.sub(r'<[^>]+>', ' ', s or '')
    s = re.sub(r'\s+', ' ', s)
    s = unescape(s).strip()
    s = re.sub(r'The post .*? appeared first on .*?\s*\.?$', '', s, flags=re.I).strip()
    return clean_markup(s)


def clean_markup(s):
    s = unescape(s or '')
    s = re.sub(r'\*\*(.*?)\*\*', r'\1', s)
    s = re.sub(r'__(.*?)__', r'\1', s)
    # Zpravodajský layout působí seriózněji bez emoji v titulcích z RSS.
    s = re.sub(r'[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]+', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def parse_date(s):
    if not s:
        return ''
    try:
        return parsedate_to_datetime(s).isoformat()
    except Exception:
        return s


def keyword_present(blob, keyword):
    pattern = r'(?<![a-z0-9])' + re.escape(keyword.lower()) + r'(?![a-z0-9])'
    return re.search(pattern, blob) is not None


def has_bulgaria_context(blob):
    return any(keyword_present(blob, kw) for kw in BULGARIA_CONTEXT)


def relevance_score(title, excerpt):
    blob = f'{title} {excerpt}'.lower()
    if not has_bulgaria_context(blob):
        return 0, [], ['missing-bulgaria-context']

    score = 0
    matched = []
    for kw, weight in TRAVEL_KEYWORDS.items():
        if keyword_present(blob, kw):
            # Samotná obecná slova typu „road/fire/rain/port“ nestačí; bereme je jen jako slabý doplněk.
            if kw in GENERIC_FALSE_POSITIVES:
                weight = min(weight, 1)
            score += weight
            matched.append(kw)

    excluded = [kw for kw in EXCLUDE_KEYWORDS if keyword_present(blob, kw)]
    if excluded and not any(keyword_present(blob, kw) for kw in IMPORTANT_OVERRIDE):
        score -= 5
    return score, matched, excluded


def editorial_angle(matches):
    m = set(matches)
    if {'airport', 'flight', 'flights', 'airline', 'ryanair', 'wizz air'} & m:
        return 'doprava / lety'
    if {'weather', 'storm', 'snow', 'heatwave', 'rain', 'flood', 'fire', 'wildfire', 'earthquake'} & m:
        return 'počasí / bezpečnost'
    if {'border', 'schengen', 'passport', 'visa', 'customs'} & m:
        return 'hranice / pravidla cestování'
    if {'beach', 'resort', 'seaside', 'black sea', 'coast', 'tourist', 'tourism', 'travel'} & m:
        return 'turismus / pobřeží'
    return 'praktická aktualita'


def rewrite_prompt(item):
    return (
        'Vytvoř z podkladu vlastní českou rychlou zprávu pro Visit Bulharsko. '
        'Nekopíruj formulace ze zdroje a nepřekládej větu po větě. Piš vlastními slovy, věcně a stručně. '
        'Zaměř se jen na dopad pro české cestovatele, turistické lokality, dopravu, počasí, bezpečnost, pobřeží nebo pravidla cestování. '
        'Pokud zpráva nemá jasný cestovatelský dopad, označ ji jako NEPUBLIKOVAT. FAQ ani obrázek nevytvářej — jde o rychlou aktuální zprávu.\n\n'
        'Povinný výstup ve struktuře JSON:\n'
        '{\n'
        '  "decision": "publish|skip",\n'
        '  "slug": "kratky-url-slug",\n'
        '  "seoTitle": "max 60 znaků",\n'
        '  "metaDescription": "max 155 znaků",\n'
        '  "h1": "český titulek",\n'
        '  "excerpt": "1–2 věty pro homepage",\n'
        '  "articleHtml": "rychlá zpráva 180–350 slov: úvod + Co se stalo + Co to znamená pro cestovatele",\n'
        '  "sourceCredit": "Zdroj: název média",\n'
        '  "sourceUrl": "původní URL"\n'
        '}\n\n'
        'Obsahová pravidla: žádné FAQ, žádný povinný obrázek, žádná výplň. Musí být jasné, proč je zpráva relevantní pro cestování.\n\n'
        f'Zdroj: {item["source"]}\n'
        f'Původní titulek: {item["originalTitle"]}\n'
        f'Podklad: {item["originalExcerpt"]}\n'
        f'Odkaz: {item["link"]}'
    )

def empty_fast_news_draft(item):
    return {
        'decision': 'draft',
        'slug': '',
        'seoTitle': '',
        'metaDescription': '',
        'h1': '',
        'excerpt': '',
        'articleHtml': '',
        'sourceCredit': f'Zdroj: {item.get("source", "")}',
        'sourceUrl': item.get('link', ''),
    }

def fetch_source(src):
    req = urllib.request.Request(src['url'], headers={'User-Agent': 'Hermes VisitBulharsko RSS importer'})
    with urllib.request.urlopen(req, timeout=25) as r:
        raw = r.read(700_000)
    root = ET.fromstring(raw)
    entries = [el for el in root.iter() if local_name(el.tag) in {'item', 'entry'}]
    items = []
    for item in entries[:20]:
        title = clean_markup(child_text(item, {'title'}))
        link = first_link(item)
        description = strip_html(child_text(item, {'description', 'summary', 'content', 'encoded'}))
        pub = parse_date(child_text(item, {'pubDate', 'published', 'updated', 'date'}))
        guid = child_text(item, {'guid', 'id'}) or link or title
        score, matched, excluded = relevance_score(title, description)
        if score < 8:
            continue
        record = {
            'source': src.get('name', ''),
            'sourceUrl': src.get('url', ''),
            'category': src.get('category', 'zpravy-bulharsko'),
            'language': src.get('language', ''),
            'status': 'draft',
            'copyPolicy': 'own-words-summary-only',
            'title': title,
            'excerpt': description[:220],
            'originalTitle': title,
            'originalExcerpt': description[:600],
            'link': link,
            'published': pub,
            'guid': guid,
            'relevanceScore': score,
            'relevanceKeywords': matched[:12],
            'excludedSignals': excluded[:8],
            'editorialAngle': editorial_angle(matched),
        }
        record['fastNewsDraft'] = empty_fast_news_draft(record)
        record['rewritePrompt'] = rewrite_prompt(record)
        items.append(record)
    return items


def main():
    sources = [s for s in json.loads(SOURCES_FILE.read_text(encoding='utf-8')) if s.get('enabled', True)]
    all_items = []
    errors = []
    seen = set()
    for src in sources:
        try:
            for item in fetch_source(src):
                key = item['guid'] or item['link'] or item['title']
                if key in seen:
                    continue
                seen.add(key)
                all_items.append(item)
        except Exception as e:
            errors.append({'source': src.get('name'), 'url': src.get('url'), 'error': f'{type(e).__name__}: {e}'})
    all_items.sort(key=lambda x: (x.get('published') or '', x.get('relevanceScore') or 0), reverse=True)
    data = {
        'generatedAt': datetime.now(UTC).isoformat(),
        'mode': 'fast-news-drafts',
        'policy': 'External RSS is used only as source material. Publish short Czech own-words fast news with clear travel impact. No FAQ or mandatory image for fast updates.',
        'items': all_items[:24],
        'errors': errors,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    RAW_OUT.write_text(json.dumps({'generatedAt': data['generatedAt'], 'items': all_items, 'errors': errors}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'items': len(all_items[:24]), 'rawItems': len(all_items), 'errors': len(errors), 'out': str(OUT)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
