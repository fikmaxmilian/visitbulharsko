from pathlib import Path
import json, shutil, re
from PIL import Image

root = Path(__file__).resolve().parents[1]
data_path = root / 'src/data/site-data.json'
backup_dir = root / 'data/backups/hermes_publish_bulharsko_dovolena_20260731'
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(data_path, backup_dir / 'site-data_before.json')

src = Path(r'C:\Users\lukas\AppData\Local\hermes\cache\images\openai_codex_gpt-image-2-medium_20260731_112652_5fc1a99f.png')
out_dir = root / 'public/uploads/2026/07'
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / 'bulharsko-dovolena-kam-jet-kdy-vyrazit.webp'
img = Image.open(src).convert('RGB')
w, h = img.size
ratio = 16 / 9
if w / h > ratio:
    nw = int(h * ratio)
    left = (w - nw) // 2
    img = img.crop((left, 0, left + nw, h))
else:
    nh = int(w / ratio)
    top = (h - nh) // 2
    img = img.crop((0, top, w, top + nh))
img = img.resize((1280, 720), Image.Resampling.LANCZOS)
q_used = None
for q in [82, 76, 70, 64, 58, 52, 46, 40, 34]:
    img.save(out, 'WEBP', quality=q, method=6)
    if out.stat().st_size <= 300 * 1024:
        q_used = q
        break
if q_used is None:
    q_used = q

slug = 'bulharsko-dovolena-kam-jet-kdy-vyrazit'
title = 'Bulharsko dovolená: kam jet, kdy vyrazit a co čekat u moře'
excerpt = 'Praktický průvodce pro dovolenou v Bulharsku: nejlepší období, letoviska u moře, doprava, ceny, počasí, all inclusive i tipy pro rodiny s dětmi.'
cat = {'id': 53, 'name': 'Cestovní průvodce', 'slug': 'cestovni-pruvodce', 'link': 'https://visitbulharsko.cz/category/cestovni-pruvodce/'}
content = '''<p><strong>Bulharsko dovolená</strong> dává největší smysl, když chcete moře, rozumné ceny, krátký let a jednoduchou organizaci bez exotických komplikací. Není to destinace, která se tváří jako luxusní katalogový sen. Je praktičtější: dlouhé pláže, teplé moře, hotely pro rodiny, levnější restaurace než ve velké části Středomoří a dost možností vybrat si mezi rušným letoviskem a klidnějším pobytem.</p>
<p>Nejčastější otázka nezní jen „jestli jet do Bulharska“, ale <strong>kam přesně</strong>. Slunečné pobřeží, Nesebar, Primorsko, Sozopol, Zlaté písky nebo Albena jsou rozdílné světy. Někde najdete noční život a velké hotely, jinde menší město, promenádu, historické centrum nebo pohodlnější zázemí pro děti.</p>
<p>Tento průvodce je psaný prakticky: kdy jet, jakou oblast zvolit, co čekat od cen, počasí, hotelů, pláží i dopravy. Bez růžové mlhy. Tu ostatně v létě u Černého moře většinou stejně obstará klimatizace v hotelovém pokoji.</p>
<h2>Kdy jet do Bulharska k moři</h2>
<p>Hlavní sezóna u Černého moře trvá přibližně od konce června do začátku září. Nejstabilnější koupací období bývá v červenci a srpnu, kdy je moře nejteplejší, fungují všechny služby a letoviska jedou naplno. To je výhoda pro rodiny a pro každého, kdo nechce řešit, jestli bude otevřená restaurace na rohu.</p>
<p>Červen a září jsou příjemnější pro cestovatele, kteří chtějí klidnější atmosféru, nižší ceny a méně lidí. Počasí může být proměnlivější než v hlavní sezoně, ale na procházky, výlety a kombinaci moře s poznáváním bývá ideální. Pokud řešíte hlavně koupání s malými dětmi, držel bych se spíš přelomu června/července až srpna.</p>
<ul>
<li><strong>Červen:</strong> lepší ceny, méně lidí, voda se ještě dohřívá.</li>
<li><strong>Červenec:</strong> stabilní léto, teplé moře, vyšší obsazenost.</li>
<li><strong>Srpen:</strong> nejteplejší moře, plná sezóna, nejrušnější letoviska.</li>
<li><strong>Září:</strong> klidnější pobřeží, příjemné výlety, větší riziko změny počasí.</li>
</ul>
<p>Detailněji se počasí věnujeme v článku <a href="/pocasi-v-bulharsku-kdy-vyrazit-a-co-ocekavat/">Počasí v Bulharsku: kdy vyrazit a co očekávat</a>.</p>
<h2>Kam jet: rychlý výběr podle typu dovolené</h2>
<p>Výběr letoviska je důležitější než výběr státu. Bulharsko umí být hlučné, klidné, rodinné, historické i trochu chaotické — záleží, kam se trefíte. Pokud chcete jednoduché pravidlo: velká letoviska vybírejte kvůli službám, menší města kvůli atmosféře.</p>
<h3>Slunečné pobřeží: hodně služeb a nejvíc ruchu</h3>
<p><a href="/slunecne-pobrezi-klenot-cerneho-more/">Slunečné pobřeží</a> je nejznámější volba pro ty, kdo chtějí širokou pláž, velký výběr hotelů, bary, restaurace, atrakce a minimum plánování. Je vhodné pro první cestu do Bulharska, pokud vám nevadí rušnější prostředí. Pro rodiny je výhoda množství hotelů s bazény a all inclusive, pro klidné páry může být hlavní promenáda v sezoně trochu moc.</p>
<h3>Nesebar: historie vedle koupání</h3>
<p>Nesebar je dobrá volba, pokud nechcete jen ležet na pláži. Staré město na poloostrově má atmosféru, úzké uličky, restaurace a výhledy na moře. Prakticky se dá spojit se Slunečným pobřežím: bydlet můžete v hotelové části a večer vyrazit do historického centra.</p>
<h3>Primorsko a Sozopol: příjemnější městská atmosféra</h3>
<p>Primorsko a Sozopol často sednou lidem, kteří chtějí moře, ale nechtějí každý večer bojovat s katalogovým lunaparkem. Primorsko má dobrý poměr ceny a pláží, Sozopol působí romantičtěji a městštěji. Obě lokality se hodí pro kombinaci koupání, procházek a výletů.</p>
<h3>Zlaté písky a Albena: severní pobřeží</h3>
<p>Zlaté písky jsou rušnější klasika u Varny, Albena je organizovanější a rodinnější. Severní pobřeží se hodí, pokud letíte do Varny nebo chcete kombinovat pobyt u moře s výlety v okolí. Albena bývá dobrá pro rodiny, které chtějí čistší, přehlednější resortní prostředí.</p>
<h2>All inclusive, apartmán nebo menší hotel?</h2>
<p>Bulharsko je silné v hotelových dovolených s polopenzí nebo all inclusive. Pro rodiny s dětmi je all inclusive pohodlné: nemusíte řešit každé jídlo, pití a svačinu. U levnějších hotelů je ale dobré číst recenze opatrně. Rozdíl mezi čtyřmi hvězdami v katalogu a čtyřmi hvězdami v realitě může být — diplomaticky řečeno — kreativní.</p>
<p>Apartmán dává smysl, pokud chcete víc prostoru, vlastní režim a možnost nakupovat v místních obchodech. Hodí se pro delší pobyt nebo pro lidi, kteří nechtějí být vázaní na hotelový jídelní režim. Menší hotely a penziony zase vyhovují těm, kdo chtějí klidnější dovolenou a víc kontaktu s místním prostředím.</p>
<ul>
<li><strong>All inclusive:</strong> nejpohodlnější pro rodiny a krátký pobyt.</li>
<li><strong>Apartmán:</strong> lepší prostor a volnost, více vlastní organizace.</li>
<li><strong>Menší hotel:</strong> klidnější atmosféra, často bez velkých resortních služeb.</li>
</ul>
<h2>Ceny v Bulharsku: pořád levnější, ale ne zadarmo</h2>
<p>Bulharsko bývá cenově příjemnější než Chorvatsko, Itálie nebo Řecko, hlavně u ubytování, jídla mimo hlavní turistické pasti a běžných služeb. Neznamená to ale, že všechno stojí pár korun. V top sezoně a v nejrušnějších místech umí ceny vyskočit, zvlášť přímo na promenádách.</p>
<p>Největší úsporu obvykle uděláte výběrem termínu a lokality. Červen, začátek července nebo září mohou vyjít výrazně lépe než hlavní srpnové týdny. U balíčků od cestovek sledujte nejen cenu zájezdu, ale i odletové letiště, transfer, stravu, recenze hotelu a vzdálenost od pláže.</p>
<h2>Doprava: letecky nejjednodušší, autem spíš pro trpělivé</h2>
<p>Pro běžnou dovolenou je nejjednodušší letět do Burgasu nebo Varny. Burgas se hodí pro jižní a střední část pobřeží, Varna pro sever. Transfer z letiště řeší cestovka, hotel nebo lokální doprava. Pokud cestujete individuálně, předem si ověřte příjezd v nočních hodinách a možnosti dopravy z letiště.</p>
<p>Cesta autem do Bulharska je možná, ale je dlouhá. Dává smysl hlavně tehdy, pokud plánujete delší pobyt, chcete vzít víc věcí nebo spojit cestu s více zastávkami. Pro týdenní dovolenou u moře je letadlo ve většině případů praktičtější. Auto je trochu romantika, dokud nejste třetí hodinu v koloně a nezačnete přehodnocovat životní rozhodnutí.</p>
<h2>Co čekat od pláží a moře</h2>
<p>Bulharské pobřeží má dlouhé písčité pláže, pozvolný vstup do vody a teplé moře v hlavní sezoně. To je důvod, proč sem míří tolik rodin. Na známých plážích počítejte s placenými zónami se slunečníky a lehátky i s volnými úseky. Pravidla se mohou lišit podle pláže a sezóny.</p>
<p>U dětí je výhoda písek a mělké vstupy, nevýhoda může být vítr, vlny a občasné proudy. Sledujte vlajky na pláži a nepodceňujte zákazy koupání. U Černého moře se počasí umí změnit rychleji, než naznačuje ranní výhled z balkonu.</p>
<h2>Pro koho je Bulharsko dobrá volba</h2>
<p>Bulharsko bych doporučil hlavně lidem, kteří chtějí dostupnou letní dovolenou, písečné pláže, krátký let a méně formální atmosféru než v dražších středomořských destinacích. Skvěle sedí rodinám, cestovatelům s rozumným rozpočtem a lidem, kteří chtějí moře bez složité logistiky.</p>
<p>Naopak pokud čekáte špičkový servis v každém detailu, sterilní luxus a dokonalou organizaci všude kolem, vybírejte hotel opravdu pečlivě. Bulharsko umí být skvělé, ale je fér počítat s tím, že některé věci budou prostě balkánštější. Což je někdy kouzlo, jindy test charakteru.</p>
<h2>Praktický checklist před rezervací</h2>
<ul>
<li>Vyberte letiště podle oblasti: Burgas pro jižní část pobřeží, Varna pro sever.</li>
<li>U hotelu zkontrolujte aktuální recenze, ne jen hvězdičky.</li>
<li>Ověřte vzdálenost k pláži pěšky, ne pouze „od moře“ v popisu.</li>
<li>U all inclusive sledujte recenze jídla a čistoty.</li>
<li>U apartmánu si ověřte klimatizaci, Wi-Fi a reálné předání klíčů.</li>
<li>Na výlety plánujte ráno nebo podvečer, hlavně v červenci a srpnu.</li>
<li>Počítejte s hotovostí na menší platby, i když karty jsou běžné.</li>
</ul>
<h2>FAQ: Bulharsko dovolená</h2>
<h3>Je Bulharsko vhodné pro rodiny s dětmi?</h3>
<p>Ano, hlavně díky písečným plážím, pozvolnému vstupu do moře a široké nabídce hotelů. Pro rodiny jsou praktické lokality s kratším transferem, dobrým zázemím a klidnější částí pláže.</p>
<h3>Kdy je v Bulharsku nejteplejší moře?</h3>
<p>Nejteplejší bývá v červenci a srpnu. V červnu může být voda ještě chladnější, v září často příjemná, ale počasí může být méně stabilní.</p>
<h3>Je lepší Slunečné pobřeží, nebo Primorsko?</h3>
<p>Slunečné pobřeží je větší, rušnější a má víc hotelových služeb. Primorsko působí komorněji a může sednout lidem, kteří chtějí příjemnější městskou atmosféru a dobrý poměr ceny a pláží.</p>
<h3>Vyplatí se all inclusive v Bulharsku?</h3>
<p>Pro rodiny a krátký pobyt často ano. U levnějších hotelů ale pečlivě čtěte recenze, protože kvalita jídla a služeb se může výrazně lišit.</p>
<h3>Dá se do Bulharska jet autem?</h3>
<p>Dá, ale cesta je dlouhá a hodí se spíš pro delší pobyt nebo cestování s více zastávkami. Pro běžnou týdenní dovolenou je letecký zájezd obvykle jednodušší.</p>
<p><em>Tip na závěr: pokud jedete do Bulharska poprvé, nezačínejte jen podle nejnižší ceny. Vyberte si nejdřív styl dovolené — klid, rodina, zábava, výlety — a až potom hledejte konkrétní hotel nebo apartmán.</em></p>'''
words = len(re.sub(r'<[^>]+>', ' ', content).split())
post = {
    'id': 3503,
    'type': 'post',
    'slug': slug,
    'path': f'/{slug}/',
    'title': title,
    'excerpt': excerpt,
    'date': '2026-07-31T00:00:00',
    'modified': '2026-07-31T00:00:00',
    'categories': [cat],
    'seo': {
        'title': 'Bulharsko dovolená: kam jet, kdy vyrazit a co čekat',
        'description': 'Praktický průvodce pro dovolenou v Bulharsku: letoviska, počasí, ceny, doprava, all inclusive a tipy pro rodiny s dětmi.'
    },
    'content': content,
    'featured_image': '/uploads/2026/07/bulharsko-dovolena-kam-jet-kdy-vyrazit.webp',
    'featured_alt': 'Bulharsko dovolená u Černého moře – pláž, mapa a cestovní plánování',
    'reading_minutes': max(1, round(words / 220))
}
data = json.loads(data_path.read_text(encoding='utf-8'))
data['posts'] = [p for p in data['posts'] if p.get('slug') != slug and p.get('id') != 3503]
data['posts'].insert(0, post)
data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
report = {
    'ok': True,
    'slug': slug,
    'path': post['path'],
    'title': title,
    'words': words,
    'reading_minutes': post['reading_minutes'],
    'image': str(out),
    'image_size_kb': round(out.stat().st_size / 1024, 1),
    'image_quality': q_used,
    'backup': str(backup_dir / 'site-data_before.json')
}
(root / 'data/output/publish_bulharsko_dovolena_article_result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
