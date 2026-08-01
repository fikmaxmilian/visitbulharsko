# Publikování rychlých zpráv z Bulharska

## Cíl

Rychlé zprávy na Visit Bulharsko nejsou automatický překlad cizích médií. RSS zdroje používáme jen jako podklad pro vlastní českou aktualitu.

Jde o obsah typu „právě se děje“, takže nemá smysl uměle vyrábět FAQ ani povinné obrázky.

Publikujeme pouze zprávy s jasným dopadem na české čtenáře:

- turistické lokality,
- pobřeží a letoviska,
- počasí a bezpečnost,
- letiště, lety a doprava,
- hranice, Schengen, víza a pravidla cestování,
- praktické změny pro návštěvníky Bulharska.

Nepublikujeme běžný politický šum, sport, burzu, obecné zahraniční zprávy ani články bez vazby na cestování.

## Workflow

1. `scripts/fetch_rss_news.py` stáhne titulky a krátké podklady z ověřených RSS zdrojů.
2. Skript vyfiltruje jen zprávy s cestovatelským dopadem.
3. Každá položka obsahuje prompt pro AI přepis vlastními slovy.
4. AI z podkladu vytvoří vlastní krátkou českou aktualitu.
5. Publikace probíhá automaticky 3× denně.
6. Po úspěšném buildu jde změna na GitHub.

## Povinné náležitosti rychlé zprávy

Rychlá zpráva není připravená k publikaci, pokud nemá:

- SEO titulek do cca 60 znaků,
- meta description do cca 155 znaků,
- čistý URL slug,
- H1/titulek,
- krátký excerpt pro homepage/kategorie,
- vlastní text cca 180–350 slov,
- jasný praktický dopad pro cestovatele,
- zdrojovou citaci a odkaz na původní zdroj.

## Co rychlá zpráva naopak nemá vyžadovat

- FAQ,
- povinný obrázek,
- dlouhý SEO článek 500–800 slov,
- umělé rozepisování kvůli délce.

Pokud se z tématu později ukáže evergreen potenciál, může se z něj samostatně udělat větší SEO článek. Rychlá zpráva má ale zůstat rychlá zpráva.

## Pravidla přepisu

- Nekopírovat formulace zdroje.
- Nepřekládat větu po větě.
- Nepřebírat celé odstavce.
- Nevyrábět clickbait.
- Pokud zpráva nemá praktický dopad pro cestovatele, označit jako `skip`.
- Zdroj vždy uvést jako podklad, ne jako převzatý text.

## Doporučená struktura rychlé zprávy

```html
<p>Krátký úvod s hlavní informací a dopadem na českého čtenáře.</p>

<h2>Co se stalo</h2>
<p>Vlastní shrnutí situace.</p>

<h2>Co to znamená pro cestovatele</h2>
<p>Praktické doporučení nebo vysvětlení dopadu.</p>

<p class="source-credit">Zdroj: <a href="..." rel="nofollow noopener" target="_blank">Název zdroje</a></p>
```
