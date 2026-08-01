# Visit Bulharsko Astro migrace – stav lokálního klonu

Datum kontroly: 2026-07-20

## Umístění projektu

- Projekt: `C:\Users\lukas\Desktop\Hermes\visitbulharsko-astro`
- Static build výstup: `C:\Users\lukas\Desktop\Hermes\visitbulharsko-astro\dist`
- Lokální preview: `http://127.0.0.1:4322/`

## Stav buildu

- `npm run build` prošel čistě.
- `astro check`: 0 errors, 0 warnings, 0 hints.
- Vygenerováno: 135 statických stránek.

## Zachované hlavní URL

Ověřené lokálně jako HTTP 200:

- `/`
- `/vtipna-slova-v-bulharstine/`
- `/bulharsky-jazyk/`
- `/bulharsko-primorsko/`
- `/plovdiv-nejstarsi-mesto-evropy/`
- `/nemovitosti-bulharsko/`
- `/category/zpravy-bulharsko/`
- `/sitemap.xml`
- `/robots.txt`

Dále jsou generované i ostatní post/page/category URL z veřejně dostupného WP exportu.

## Co bylo doladěno po kritické kontrole

- Zhutněný header a top spacing.
- Search ikona dostala jasnější kruhový hitbox.
- Zmenšené mezery mezi hero, aktuálními zprávami a reklamním/newsletter pásem.
- Reklamní/newsletter pás je kompaktnější.
- Hero/overlay karty jsou nově řešené jako full-image background s gradientem, ne jako obrázek + těžký prázdný tmavý blok.
- Hero karta má krátký perex, aby plocha nepůsobila prázdně.
- Newsletter formuláře jsou odolnější na mobilu (`grid` fallback, pak `flex`).
- Footer copy odstranil interní/dev texty typu „Astro verze“.
- Feed texty se čistí od markdownu `**...**` a věty `The post ... appeared first on Visit Bulharsko`.
- Dlouhé/nebezpečné názvy obrázků se kopírují do krátkých aliasů v `/uploads/hermes/...`.
- Vizuálně podezřelý obrázek pro „Kouzlo tradiční bulharské hudby“ byl ověřen jako použitelný asset; šedý dojem vznikal kvůli overlay/CSS, ne kvůli souboru.

## RSS/feed napojení

Přidané soubory:

- `data/feed_sources.json`
- `scripts/fetch_rss_news.py`
- `src/data/feed-news.json`

Výchozí zdroj:

- `https://visitbulharsko.cz/category/zpravy-bulharsko/feed/`

Chování:

- Build-time skript stáhne RSS položky.
- Homepage sekce „Aktuální zprávy“ bere feed položky, pokud existují.
- Pokud feed není dostupný, web může dál používat statická data z původního exportu.
- Feed import čistí HTML, markdown a WP patičkové texty.

Spuštění před buildem:

```bash
python scripts/fetch_rss_news.py
npm run build
```

## ADS stav

Reklamní plochy jsou připravené jako placeholdery:

- top reklamní banner na apartmány,
- široký ADS banner ve střední části,
- sidebar/box ADS u některých layoutů,
- footer ADS prostor.

Před produkcí rozhodnout:

1. nechat placeholdery jako prodané reklamní pozice,
2. nahradit reálnými bannery,
3. napojit AdSense/custom HTML,
4. nebo dočasně skrýt prázdné ADS bloky, aby nepůsobily jako nedodělky.

## Co zůstává na později

- Plnohodnotné vyhledávání.
- Napojení newsletter formulářů na reálný odběr.
- Finální ADS/affiliate implementace.
- Mobilní hamburger menu, pokud bude potřeba místo wrap navigace.
- Redirect mapa z původních WP/emoji/azbuka URL na čistší slugs, pokud se budou URL měnit.
- Produkční deploy na Cloudflare Pages / Netlify / Vercel / statický hosting.
- Případné přidání dalších externích bulharských RSS zdrojů do `data/feed_sources.json`.

## Finální technická kontrola

Lokálně ověřeno:

- důležité URL vrací 200,
- homepage neobsahuje `**`, `appeared first`, `Astro verze`, `WordPressu`,
- homepage obsahuje RSS sekci,
- browser DOM kontrola nenašla žádný dokončeně načtený broken image (`naturalWidth === 0` u `complete === true`).

## Verdikt

Lokální Astro klon je použitelný jako stabilní statický základ pro Visit Bulharsko. Není to pixel-perfect kopie původního WP theme, ale vizuálně drží magazínovou identitu, zachovává hlavní URL, obsah, kategorie, média, sitemap/robots a má základní RSS import pro čerstvé zprávy.
