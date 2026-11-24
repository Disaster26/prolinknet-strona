# ProlinkNET - generator strony (python -I buduj.py)
# Buduje dwie wersje z tych samych treści:
#   ../paczka/prolinknet.pl/  - wersja docelowa na nazwa.pl (indeksowana, formularz PHP)
#   ../docs/                  - wersja testowa na GitHub Pages /prolinknet-strona/ (noindex, bez PHP)
import os, re, json, shutil, datetime
TU = os.path.dirname(os.path.abspath(__file__))
KOR = os.path.dirname(TU)
DOM = 'https://prolinknet.pl'
WER = '1'                                  # zmienić po edycji style.css/app.js (cache przeglądarek)
DZIS = datetime.date.today().isoformat()

TEL1, TEL1H = '733 800 337', '+48733800337'
MAIL = 'biuro@prolinknet.pl'
ADR = 'ul. Radzymińska 180, 05-205 Stary Kraszew'
MAPA = 'https://www.google.com/maps?q=Radzymi%C5%84ska+180,+05-205+Stary+Kraszew&z=15&output=embed'
MAPA_LINK = 'https://www.google.com/maps/search/?api=1&query=Radzymi%C5%84ska+180%2C+05-205+Stary+Kraszew'

# ---------------------------------------------------------------- drobne elementy
LM = '<svg class="link-mark" viewBox="0 0 64 12" aria-hidden="true"><circle cx="6" cy="6" r="4.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 6h40" stroke="currentColor" stroke-width="2" stroke-dasharray="4 4"/><circle cx="58" cy="6" r="4.5" fill="currentColor"/></svg>'
AR = '<svg class="ar" viewBox="0 0 30 10" aria-hidden="true"><path d="M0 5h24" stroke="currentColor" stroke-width="1.8"/><circle cx="25" cy="5" r="3.6" fill="currentColor"/></svg>'
I_TEL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M5 3h3.5l1.8 4.6-2.3 1.5a11 11 0 0 0 6.9 6.9l1.5-2.3L21 15.5V19a2 2 0 0 1-2.2 2A17 17 0 0 1 3 5.2 2 2 0 0 1 5 3z"/></svg>'
I_MAIL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5"/></svg>'
I_PIN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>'

BADGE_CSS = open(os.path.join(TU, '_badge_css.txt'), encoding='utf-8').read().strip()
BADGE = open(os.path.join(TU, '_badge_a.txt'), encoding='utf-8').read().strip()

MENU = [('radiolinie/', 'Radiolinie'), ('swiatlowody/', 'Światłowody'), ('konstrukcje-stalowe/', 'Konstrukcje'),
        ('utrzymanie-i-outsourcing/', 'Utrzymanie'), ('o-firmie/', 'O firmie'), ('kontakt/', 'Kontakt')]

def mini_css(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s*([{};:,>])\s*', r'\1', s)
    return s.replace(';}', '}').strip()

def fonty(B):
    pl = 'U+0104-0107,U+0118-0119,U+0141-0144,U+015A-015B,U+0179-017C'
    core = 'U+0020-007E,U+00A0,U+00A9,U+00AB,U+00B0,U+00B7,U+00BB,U+00D3,U+00D7,U+00F3,U+2013-2014,U+2019-201A,U+201C-201E,U+2022,U+2026,U+20AC,U+2122'
    out = ''
    for rod, wagi, plik in (('Raleway', '200 700', 'raleway'), ('Inter', '400 700', 'inter')):
        out += "@font-face{font-family:%s;font-style:normal;font-weight:%s;font-display:swap;src:url(%sfonts/%s-rdzen.woff2) format('woff2');unicode-range:%s}" % (rod, wagi, B, plik, core)
        out += "@font-face{font-family:%s;font-style:normal;font-weight:%s;font-display:swap;src:url(%sfonts/%s-pl.woff2) format('woff2');unicode-range:%s}" % (rod, wagi, B, plik, pl)
    return out

CSS = mini_css(open(os.path.join(TU, 'style.css'), encoding='utf-8').read())

# ---------------------------------------------------------------- dane strukturalne firmy
def org():
    return {
        '@type': 'LocalBusiness', '@id': DOM + '/#firma', 'name': 'ProlinkNET', 'legalName': 'PROLINKNET Sp. z o.o.',
        'description': 'Budowa i utrzymanie sieci telekomunikacyjnych: radiolinie punkt - punkt i punkt - wielopunkt, światłowody, konstrukcje stalowe, utrzymanie oraz outsourcing. Podwykonawca operatorów od 2003 roku.',
        'url': DOM + '/', 'telephone': TEL1H, 'email': MAIL,
        'logo': {'@type': 'ImageObject', 'url': DOM + '/ikony/logo-prolinknet-512.png', 'width': 512, 'height': 512},
        'image': DOM + '/img/og-prolinknet.jpg',
        'address': {'@type': 'PostalAddress', 'streetAddress': 'ul. Radzymińska 180', 'postalCode': '05-205', 'addressLocality': 'Stary Kraszew', 'addressRegion': 'mazowieckie', 'addressCountry': 'PL'},
        'areaServed': {'@type': 'Country', 'name': 'Polska'}, 'foundingDate': '2003',
        'taxID': '1251626648', 'vatID': 'PL1251626648', 'identifier': [{'@type': 'PropertyValue', 'propertyID': 'KRS', 'value': '0000514566'}, {'@type': 'PropertyValue', 'propertyID': 'REGON', 'value': '147306133'}],
        'contactPoint': [{'@type': 'ContactPoint', 'telephone': TEL1H, 'contactType': 'customer service', 'areaServed': 'PL', 'availableLanguage': 'pl'}],
        'knowsAbout': ['radiolinie', 'sieci radiowe punkt - punkt', 'punkt - wielopunkt', 'spawanie światłowodów', 'pomiary reflektometrem', 'konstrukcje wsporcze pod anteny', 'maszty telekomunikacyjne', 'GSM/UMTS/LTE'],
    }
def website():
    return {'@type': 'WebSite', '@id': DOM + '/#strona', 'url': DOM + '/', 'name': 'ProlinkNET', 'alternateName': ['PROLINKNET Sp. z o.o.', 'Prolinknet'], 'inLanguage': 'pl-PL', 'publisher': {'@id': DOM + '/#firma'}}

# ---------------------------------------------------------------- szkielet strony
def strona(B, prod, sciezka, tytul, opis, tresc, *, aktywne=None, okr=None, ld=None, preload='', og_typ='website'):
    can = DOM + '/' + sciezka
    robots = 'index,follow,max-image-preview:large' if prod else 'noindex,nofollow'
    graf = [website(), org()]
    if okr:
        el = [{'@type': 'ListItem', 'position': 1, 'name': 'Start', 'item': DOM + '/'}]
        for i, (n, u) in enumerate(okr, 2): el.append({'@type': 'ListItem', 'position': i, 'name': n, 'item': DOM + '/' + u})
        graf.append({'@type': 'BreadcrumbList', 'itemListElement': el})
    graf.append({'@type': 'WebPage', '@id': can + '#strona', 'url': can, 'name': tytul, 'description': opis, 'isPartOf': {'@id': DOM + '/#strona'}, 'about': {'@id': DOM + '/#firma'}, 'inLanguage': 'pl-PL'})
    if ld: graf += ld
    jsonld = json.dumps({'@context': 'https://schema.org', '@graph': graf}, ensure_ascii=False, separators=(',', ':'))
    nav = ''.join('<a href="%s%s"%s>%s</a>' % (B, u, ' aria-current="page"' if aktywne == u else '', n) for u, n in MENU)
    return f'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{tytul}</title>
<meta name="description" content="{opis}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{can}">
<meta name="theme-color" content="#ffffff">
<meta property="og:type" content="{og_typ}">
<meta property="og:locale" content="pl_PL">
<meta property="og:site_name" content="ProlinkNET">
<meta property="og:title" content="{tytul}">
<meta property="og:description" content="{opis}">
<meta property="og:url" content="{can}">
<meta property="og:image" content="{DOM}/img/og-prolinknet.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Maszt telekomunikacyjny z antenami radiolinii - ProlinkNET">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{B}favicon.ico" sizes="48x48">
<link rel="icon" href="{B}ikony/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{B}ikony/favicon-96.png" type="image/png" sizes="96x96">
<link rel="icon" href="{B}ikony/favicon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="{B}apple-touch-icon.png">
<link rel="manifest" href="{B}site.webmanifest">
<link rel="preload" href="{B}fonts/raleway-rdzen.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{B}fonts/inter-rdzen.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{B}fonts/raleway-pl.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{B}fonts/inter-pl.woff2" as="font" type="font/woff2" crossorigin>
{preload}<style>{fonty(B)}{CSS}{BADGE_CSS}</style>
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
<a class="skip" href="#tresc">Przejdź do treści</a>
<header class="top">
  <div class="wrap">
    <a class="logo" href="{B}" aria-label="ProlinkNET, strona główna"><b>Pro</b><span>linkNET</span><i></i></a>
    <nav class="nav" id="nav" aria-label="Menu główne">{nav}<a class="nav-cta" href="{B}kontakt/#zapytanie">Zapytaj o realizację</a></nav>
    <div class="hd-r">
      <a class="tel" href="tel:{TEL1H}" aria-label="Zadzwoń {TEL1}">{I_TEL}<span>{TEL1}</span></a>
      <a class="btn" href="{B}kontakt/#zapytanie">Zapytaj o realizację</a>
      <button id="burger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<main id="tresc">
{tresc}
</main>
<footer class="stopka">
  <div class="wrap">
    <div>
      <a class="logo" href="{B}" aria-label="ProlinkNET, strona główna"><b>Pro</b><span>linkNET</span><i></i></a>
      <p style="margin:14px 0 0;max-width:340px">Radiolinie, światłowody, konstrukcje stalowe oraz utrzymanie sieci telekomunikacyjnych. Działamy na terenie całej Polski od 2003 roku.</p>
      <p class="rej">PROLINKNET Sp. z o.o. · NIP 1251626648 · KRS 0000514566 · REGON 147306133</p>
    </div>
    <div><p class="sth">Oferta</p><ul><li><a href="{B}radiolinie/">Radiolinie</a></li><li><a href="{B}swiatlowody/">Światłowody</a></li><li><a href="{B}konstrukcje-stalowe/">Konstrukcje stalowe</a></li><li><a href="{B}utrzymanie-i-outsourcing/">Utrzymanie i outsourcing</a></li></ul></div>
    <div><p class="sth">Firma</p><ul><li><a href="{B}o-firmie/">O firmie</a></li><li><a href="{B}o-firmie/#partnerzy">Partnerzy</a></li><li><a href="{B}kontakt/">Kontakt</a></li><li><a href="{B}polityka-prywatnosci/">Polityka prywatności</a></li></ul></div>
    <div><p class="sth">Kontakt</p><ul><li><a href="tel:{TEL1H}">{TEL1}</a></li><li><a href="mailto:{MAIL}">{MAIL}</a></li><li><span>{ADR}</span></li></ul></div>
    <div class="linia"><span>© <span data-rok>{datetime.date.today().year}</span> ProlinkNET</span>{BADGE}</div>
  </div>
</footer>
<div class="mob" aria-label="Szybki kontakt"><a class="m1" href="tel:{TEL1H}">{I_TEL}Zadzwoń</a><a class="m2" href="{B}kontakt/#zapytanie">Zapytaj o realizację</a></div>
<div class="ck" role="region" aria-label="Pliki cookies" hidden><p>Mapę Google wczytujemy dopiero po zgodzie, bo Google może przy tym zapisać pliki cookies. Szczegóły w <a href="{B}polityka-prywatnosci/">polityce prywatności</a>.</p><div class="b"><button type="button" class="ok" data-z="wszystkie">Akceptuję</button><button type="button" data-z="niezbedne">Tylko niezbędne</button></div></div>
<script>try{{if(!localStorage.getItem('pl-zgody'))document.querySelector('.ck').hidden=false}}catch(e){{document.querySelector('.ck').hidden=false}}</script>
<script src="{B}app.js?v={WER}" defer></script>
</body>
</html>
'''

# ---------------------------------------------------------------- wspólne bloki treści
def okruszki(B, poz):
    li = '<li><a href="%s">Start</a></li>' % B
    for n, u in poz[:-1]: li += '<li><a href="%s%s">%s</a></li>' % (B, u, n)
    li += '<li><span aria-current="page">%s</span></li>' % poz[-1][0]
    return '<nav class="okr" aria-label="Jesteś tutaj"><ol>%s</ol></nav>' % li

def naglowek(B, poz, h1, lead, foto, alt, jasne=False, w=609, h=827, srcset=''):
    return f'''<section class="ph" data-mob-od>
  <div class="wrap">
    <div class="ph-tx">
      {okruszki(B, poz)}
      {LM}
      <h1>{h1}</h1>
      <p class="lead">{lead}</p>
      <a class="btn" href="{B}kontakt/#zapytanie">Zapytaj o realizację {AR}</a>
    </div>
  </div>
  <div class="ph-foto{' jasne' if jasne else ''}"><img src="{B}img/{foto}"{srcset} width="{w}" height="{h}" alt="{alt}" fetchpriority="high" decoding="async"></div>
</section>'''

def pas(B, h2):
    return f'''<section class="pas"><div class="wrap"><div><h2>{h2}</h2><p>Opisz zakres prac, a odpowiemy z propozycją realizacji.</p></div><div class="akcje"><a class="tel" href="tel:{TEL1H}">{I_TEL}<span style="display:inline">{TEL1}</span></a><a class="btn" href="{B}kontakt/#zapytanie">Zapytaj o realizację {AR}</a></div></div></section>'''

def formularz(B, prod, fid, naglowek_tag='h2'):
    akcja = B + 'wyslij.php'
    opcje = ''.join('<option>%s</option>' % o for o in ('Radiolinie', 'Światłowody', 'Konstrukcje stalowe', 'Utrzymanie i outsourcing', 'Inne'))
    return f'''<form class="zap" id="{fid}" action="{akcja}" method="post" novalidate>
  <{naglowek_tag} class="h3">Zapytanie o realizację</{naglowek_tag}>
  <div class="dwa"><div class="pole"><label for="{fid}-n">Imię i nazwisko / firma</label><input id="{fid}-n" name="imie" autocomplete="name" maxlength="100" required></div>
  <div class="pole"><label for="{fid}-u">Zakres prac</label><select id="{fid}-u" name="zakres">{opcje}</select></div></div>
  <div class="dwa"><div class="pole"><label for="{fid}-t">Telefon</label><input id="{fid}-t" name="telefon" type="tel" autocomplete="tel" maxlength="30" inputmode="tel"></div>
  <div class="pole"><label for="{fid}-e">E-mail</label><input id="{fid}-e" name="email" type="email" autocomplete="email" maxlength="120"></div></div>
  <div class="pole"><label for="{fid}-o">Opis: lokalizacja, termin, zakres prac</label><textarea id="{fid}-o" name="wiadomosc" maxlength="5000" required></textarea></div>
  <div class="hp" aria-hidden="true"><label for="{fid}-w">Strona www</label><input id="{fid}-w" name="strona_www" tabindex="-1" autocomplete="off"></div>
  <input type="hidden" name="_z" value="">
  <label class="zgoda"><input type="checkbox" name="zgoda" value="tak" required> <span>Zgadzam się na przetwarzanie podanych danych w celu odpowiedzi na zapytanie (szczegóły w <a href="{B}polityka-prywatnosci/">polityce prywatności</a>). Wystarczy telefon albo e-mail.</span></label>
  <div><button class="btn" type="submit">Wyślij zapytanie {AR}</button></div>
  <div class="info" role="status" aria-live="polite" tabindex="-1"></div>
</form>'''

def dane_kontaktowe():
    return f'''<ul class="dane">
      <li><a href="tel:{TEL1H}">{I_TEL}{TEL1}</a></li>
      <li><a href="mailto:{MAIL}">{I_MAIL}{MAIL}</a></li>
      <li><span>{I_PIN}{ADR}</span></li>
    </ul>'''

def mapa(h=320):
    return f'''<div class="mapa" style="height:{h}px" data-src="{MAPA}" data-tytul="Mapa dojazdu: Stary Kraszew, ul. Radzymińska 180"><div class="mapa-z"><p>ProlinkNET: {ADR}</p><button class="btn" type="button">Pokaż mapę Google</button><a href="{MAPA_LINK}" target="_blank" rel="noopener">Otwórz w Mapach Google</a></div></div>'''

def usluga_ld(nazwa, opis, sc):
    return {'@type': 'Service', 'name': nazwa, 'description': opis, 'serviceType': nazwa, 'provider': {'@id': DOM + '/#firma'}, 'areaServed': {'@type': 'Country', 'name': 'Polska'}, 'url': DOM + '/' + sc}

FAQ = [
    ('Na jakim terenie działa ProlinkNET?', 'Siedzibę mamy w Starym Kraszewie pod Warszawą, a realizacje prowadzimy na terenie całej Polski, jako podwykonawca operatorów telekomunikacyjnych i dla innych zleceniodawców.'),
    ('Jakie radiolinie budujecie?', 'Budujemy sieci radiowe typu punkt - punkt oraz punkt - wielopunkt (wielodostęp). Prowadzimy cały proces: wizję radiową, uzgodnienia, dokumentację, dostawę i montaż konstrukcji wsporczych, montaż anten i modułów ODU, instalację modułów IDU, konfigurację, pomiary transmisyjne i dokumentację powykonawczą.'),
    ('Czy wykonujecie spawanie i pomiary światłowodów?', 'Tak. Łączymy włókna mechanicznie (szybkozłączką) oraz spawaniem łukiem elektrycznym, spawarką Fujikura. Pomiary wykonujemy reflektometrem, zarówno dla nowych spawów, jak i istniejących połączeń w sieci.'),
    ('Czy projektujecie i montujecie konstrukcje pod anteny?', 'Tak. Projektujemy konstrukcje wsporcze, wykonujemy ich prefabrykację i montaż, także maszty, balustrady mostowe i rozwiązania niestandardowe. Wszystkie konstrukcje zabezpieczamy antykorozyjnie przez cynkowanie. Przy pracach na wysokości pracują u nas alpiniści.'),
    ('Czy zajmujecie się utrzymaniem istniejącej sieci?', 'Tak. Instalujemy dodatkowe urządzenia telekomunikacyjne, wykonujemy prace konfiguracyjne i serwisowe, konserwację zainstalowanych urządzeń oraz usuwamy awarie systemów radioliniowych.'),
    ('Jak zapytać o realizację?', f'Najprościej wysłać formularz zapytania z lokalizacją, terminem i zakresem prac albo zadzwonić: {TEL1}. Można też napisać na {MAIL}.'),
]

# ---------------------------------------------------------------- strony
def glowna(B, prod):
    karty = [
        ('radiolinie/', 'maszt-radiolinie-160.webp', 160, 458, 'Maszt kratowy z antenami radiolinii', True, 'Radiolinie', 'Budowa sieci radiowej typu punkt - punkt oraz punkt - wielopunkt: od wizji radiowej i uzgodnień po montaż, uruchomienie i pomiary.'),
        ('swiatlowody/', 'swiatlowody-420.webp', 420, 519, 'Włókna światłowodowe', False, 'Światłowody', 'Spawanie, pomiary reflektometrem, układanie i instalacja sieci światłowodowych, także w tunelach, z należytym zabezpieczeniem.'),
        ('konstrukcje-stalowe/', 'konstrukcje-rulony-360.webp', 360, 635, 'Rysunki konstrukcji stalowych', False, 'Konstrukcje stalowe', 'Konstrukcje wsporcze pod anteny, maszty, balustrady mostowe i rozwiązania niestandardowe. Zabezpieczenie antykorozyjne przez cynkowanie.'),
        ('utrzymanie-i-outsourcing/', 'serwerownia-600.webp', 600, 347, 'Serwerownia z szafami telekomunikacyjnymi', False, 'Utrzymanie oraz outsourcing', 'Usługi poinstalacyjne: instalacja dodatkowych urządzeń, prace konfiguracyjne i serwisowe, konserwacja i usuwanie awarii.'),
    ]
    k = ''.join(f'<a class="karta" href="{B}{u}"><div class="fot{" jasne" if j else ""}"><img src="{B}img/{f}" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async"></div><div class="tx"><h3>{t}</h3><p>{o}</p><span class="wiecej">Zakres prac {AR}</span></div></a>' for u, f, w, h, alt, j, t, o in karty)
    loga = ''.join(f'<div class="logo-p"><img src="{B}img/partner-{i}.webp" alt="{n}" width="{w}" height="{h}" loading="lazy" decoding="async"></div>' for i, n, w, h in PARTNERZY)
    faq = ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in FAQ)
    tresc = f'''<section class="hero">
  <div class="hero-foto"><picture><source media="(max-width:760px)" srcset="{B}img/maszt-mob-kadr-460.webp 460w, {B}img/maszt-mob-kadr.webp 609w" sizes="100vw" width="609" height="470"><img src="{B}img/maszt-niebo-1169.webp" srcset="{B}img/maszt-niebo-800.webp 800w, {B}img/maszt-niebo-1169.webp 1169w" sizes="100vw" width="1169" height="827" alt="Maszt telekomunikacyjny z antenami radiolinii na tle nieba" fetchpriority="high" decoding="async"></picture></div>
  <svg class="beam" viewBox="0 0 1169 827" preserveAspectRatio="xMaxYMid slice" style="inset:0;width:100%;height:100%" aria-hidden="true"><path d="M778 432 Q700 470 612 500" fill="none" stroke="currentColor" stroke-width="2.5"/><circle cx="778" cy="432" r="7" fill="none" stroke="currentColor" stroke-width="2.5"/><circle cx="608" cy="502" r="6" fill="currentColor"/></svg>
  <div class="hero-in"><div class="hero-tx">
    {LM}
    <h1>Radiolinie, światłowody i konstrukcje dla sieci telekomunikacyjnych</h1>
    <p class="lead">Od 2003 roku, jako podwykonawca największych operatorów w Polsce, budujemy, wdrażamy i utrzymujemy infrastrukturę teleinformatyczną. Siedziba w Starym Kraszewie pod Warszawą, realizacje w całej Polsce.</p>
    <div class="cta" data-mob-od><a class="btn" href="{B}kontakt/#zapytanie">Zapytaj o realizację {AR}</a><a class="btn ghost" href="#oferta">Zakres usług</a></div>
    <ul class="hero-fakty"><li>Od 2003 roku</li><li>Cała Polska</li><li>Podwykonawca operatorów</li></ul>
  </div></div>
</section>

<section class="sec alt" id="oferta"><div class="wrap">
  <div class="sec-hd"><div>{LM}<h2>Kompleksowe usługi telekomunikacyjne</h2><p>Od wizji radiowej i projektu, przez montaż i uruchomienie, po serwis istniejącej sieci.</p></div><div class="ctrl"><button type="button" data-prev="uslugi" aria-label="Poprzednie usługi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button><button type="button" data-next="uslugi" aria-label="Następne usługi"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button></div></div>
  <div class="tor" data-tor="uslugi">{k}</div>
  <div class="licz" data-licz="uslugi" aria-hidden="true">1 / 4</div>
</div></section>

<section class="sec"><div class="wrap">
  {LM}<h2>Radiolinia od wizji do dokumentacji</h2>
  <p style="max-width:640px;color:var(--mut)">Tam, gdzie trudno wybudować linię kablową, łączymy obiekty drogą radiową. Prowadzimy cały proces, punkt po punkcie.</p>
  <ol class="lacze">
    <li><h3>Wizja radiowa</h3><ul><li>wykaz obiektów i ich położenie</li><li>uzgodnienia z właścicielem lub administratorem</li><li>parametry obiektu oraz przęsła</li></ul></li>
    <li><h3>Dokumentacja</h3><ul><li>dokumentacja fotograficzna: miejsce montażu anteny, trasa kablowa do serwerowni</li><li>wymagania administracyjne, np. opłaty</li><li>dokumentacja przedwykonawcza</li></ul></li>
    <li><h3>Montaż</h3><ul><li>konstrukcje wsporcze: wsporniki antenowe, maszty wolnostojące</li><li>montaż anten, wizowanie, moduły ODU</li><li>kabel przesyłowy RG-8, CNT-300, CNT-400</li></ul></li>
    <li><h3>Uruchomienie</h3><ul><li>moduły IDU w szafach telekomunikacyjnych</li><li>konfiguracja i pomiary transmisyjne</li><li>dokumentacja powykonawcza</li></ul></li>
  </ol>
  <p style="margin-top:34px"><a class="btn ghost" href="{B}radiolinie/">Pełny zakres radiolinii {AR}</a></p>
</div></section>

<div class="sep" style="--x:62%"></div>

<section class="sec"><div class="wrap split">
  <div>
    {LM}<h2>Doświadczenie zdobyte przy sieciach operatorów</h2>
    <p>Firma ProlinkNET powstała w 2003 roku. Głównym zakresem naszego działania są usługi techniczne w branży telekomunikacyjnej. Wspieramy wdrażanie nowych rozwiązań i bierzemy udział w rozbudowie istniejącej infrastruktury.</p>
    <p>Siedzibę mamy w Starym Kraszewie pod Warszawą, a teren naszego działania obejmuje całą Polskę. Nasze największe atuty to:</p>
    <ul class="atuty"><li>doświadczenie w planowaniu i realizacji infrastruktury teleinformatycznej,</li><li>doświadczenie we współpracy z instytucjami regulującymi rynek telefonii w kwestiach licencji dla operatorów,</li><li>profesjonalizm i doświadczenie naszych pracowników.</li></ul>
    <p style="margin-top:26px"><a class="btn ghost" href="{B}o-firmie/">O firmie {AR}</a></p>
  </div>
  <figure class="split-foto" style="margin:0"><img src="{B}img/zasieg-600.webp" srcset="{B}img/zasieg-600.webp 600w, {B}img/zasieg-800.webp 800w, {B}img/zasieg.webp 1000w" sizes="(max-width:900px) 100vw, 50vw" width="1000" height="462" alt="Mapa połączeń sieci na terenie Polski" loading="lazy" decoding="async"><figcaption>Działamy na terenie całej Polski</figcaption></figure>
</div></section>

<section class="partnerzy" id="partnerzy"><div class="wrap">
  <div class="sec-hd"><div>{LM}<h2>Nasi partnerzy</h2><p>Pracowaliśmy przy sieciach i obiektach operatorów oraz dostawców infrastruktury.</p></div></div>
  <div class="loga" data-tor="loga">{loga}</div>
</div></section>

<section class="sec"><div class="wrap">
  {LM}<h2>Najczęstsze pytania</h2>
  <div class="faq">{faq}</div>
</div></section>

<section class="sec alt" id="kontakt"><div class="wrap kontakt-grid">
  <div>
    {LM}<h2>Kontakt</h2>
    <p>Zapraszamy do zapoznania się z naszą ofertą kompleksowych usług telekomunikacyjnych. Opisz obiekt i zakres prac, a odpowiemy z propozycją realizacji.</p>
    {dane_kontaktowe()}
    {mapa()}
  </div>
  {formularz(B, prod, 'zapytanie-start', 'h3')}
</div></section>'''
    faq_ld = {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]}
    pre = f'<link rel="preload" as="image" href="{B}img/maszt-mob-kadr.webp" imagesrcset="{B}img/maszt-mob-kadr-460.webp 460w, {B}img/maszt-mob-kadr.webp 609w" imagesizes="100vw" media="(max-width:760px)" fetchpriority="high">\n<link rel="preload" as="image" href="{B}img/maszt-niebo-1169.webp" imagesrcset="{B}img/maszt-niebo-800.webp 800w, {B}img/maszt-niebo-1169.webp 1169w" imagesizes="100vw" media="(min-width:761px)" fetchpriority="high">\n'
    return strona(B, prod, '', 'Radiolinie, światłowody, konstrukcje telekomunikacyjne | ProlinkNET, cała Polska',
                  'ProlinkNET: budowa i utrzymanie sieci telekomunikacyjnych od 2003 roku. Radiolinie punkt - punkt i punkt - wielopunkt, światłowody, konstrukcje stalowe. Stary Kraszew k. Warszawy, cała Polska.',
                  tresc, ld=[faq_ld], preload=pre)

PARTNERZY = [(2, 'Emitel', 200, 96), (3, 'NEC', 196, 53), (4, 'Plus', 189, 69), (5, 'Orange', 97, 98), (6, 'Netia', 185, 20), (7, 'Exatel', 181, 44)]

def pre_img(B, f, srcset=''):
    return f'<link rel="preload" as="image" href="{B}img/{f}"{srcset} fetchpriority="high">\n'

def radiolinie(B, prod):
    poz = [('Radiolinie', 'radiolinie/')]
    tresc = naglowek(B, poz, 'Radiolinie punkt - punkt i punkt - wielopunkt', 'Kompleksowa budowa sieci radiowej typu punkt - punkt oraz punkt - wielopunkt (wielodostęp), od wizji radiowej po dokumentację powykonawczą i serwis. Na terenie całej Polski.',
                     'maszt-mob-kadr-460.webp', 'Maszt telekomunikacyjny z antenami radiolinii', w=460, h=355, srcset=f' srcset="{B}img/maszt-mob-kadr-460.webp 460w, {B}img/maszt-mob-kadr.webp 609w" sizes="(max-width:900px) 100vw, 44vw"') + f'''
<section class="sec"><div class="wrap split">
  <div class="tekst">
    {LM}<h2>Czym jest radiolinia</h2>
    <p>Radiolinia to system urządzeń służących do nadawania i odbierania analogowych lub cyfrowych transmisji radiowych. Stosuje się ją na obszarach, gdzie utrudnione jest wybudowanie linii kablowych, aby umożliwić przesył sygnałów telekomunikacyjnych.</p>
    <p>Wiedza i kompetencja techniczna w połączeniu z nagromadzonym doświadczeniem pozwalają nam odpowiadać na potrzeby Klientów odpowiednimi rozwiązaniami. Zawsze koncentrujemy się na satysfakcji i efektywności kosztowej, a także na realizacji zobowiązań w zaplanowanym czasie.</p>
  </div>
  <figure class="split-foto" style="margin:0;background:#fff;min-height:440px"><img src="{B}img/maszt-radiolinie.webp" width="289" height="827" alt="Maszt kratowy z antenami radiolinii" loading="lazy" decoding="async" style="object-fit:contain"></figure>
</div></section>
<section class="sec alt"><div class="wrap">
  {LM}<h2>Zakres prac przy radiolinii</h2>
  <ol class="lacze">
    <li><h3>Wizja radiowa</h3><ul><li>szczegółowe wizje radiowe z wykazem obiektów</li><li>określenie położenia obiektu</li><li>wszystkie niezbędne uzgodnienia z właścicielem lub administratorem</li><li>określenie parametrów obiektu oraz przęsła</li></ul></li>
    <li><h3>Dokumentacja</h3><ul><li>szczegółowa dokumentacja fotograficzna obiektu: przy potwierdzonej widoczności miejsce montażu anteny i trasa kablowa do serwerowni</li><li>ustalenie wymagań administracyjnych, takich jak opłaty</li><li>dokumentacja przedwykonawcza</li></ul></li>
    <li><h3>Montaż</h3><ul><li>nowe instalacje radioliniowe punkt - punkt i punkt - wielopunkt</li><li>dostawa i montaż konstrukcji wsporczych: wsporniki antenowe, maszty wolnostojące</li><li>montaż anten na konstrukcjach, wizowanie, instalacja modułów ODU (Outdoor Unit)</li><li>doprowadzenie kabla przesyłowego (RG-8, CNT-300, CNT-400)</li></ul></li>
    <li><h3>Uruchomienie i serwis</h3><ul><li>instalacja modułów IDU (Indoor Unit) w szafach telekomunikacyjnych</li><li>konfiguracja i uruchomienie linii radiowej, pomiary transmisyjne</li><li>dokumentacja powykonawcza</li><li>eksploatacja i konserwacja urządzeń, usuwanie awarii systemów radioliniowych</li></ul></li>
  </ol>
</div></section>
<section class="sec"><div class="wrap tekst">
  {LM}<h2>Doświadczenie w sieciach GSM/UMTS/LTE</h2>
  <p>Nie boimy się wyzwań, bo to dzięki nim wypracowaliśmy najbardziej efektywne metody realizacji projektów z dziedziny radiowej komunikacji GSM/UMTS/LTE oraz linii radiowych. Pracując dla czołowych operatorów telefonii komórkowej w Polsce, zdobyliśmy szerokie doświadczenie w swojej branży.</p>
  <p>Do montażu anten i masztów dostarczamy także <a href="{B}konstrukcje-stalowe/">konstrukcje wsporcze</a>, a po uruchomieniu łącza zapewniamy <a href="{B}utrzymanie-i-outsourcing/">utrzymanie i serwis</a>.</p>
</div></section>
{pas(B, 'Potrzebujesz połączenia radiowego między obiektami?')}'''
    opis = 'Budowa radiolinii punkt - punkt i punkt - wielopunkt: wizja radiowa, uzgodnienia, montaż anten i konstrukcji, uruchomienie, pomiary i serwis. ProlinkNET, cała Polska.'
    return strona(B, prod, 'radiolinie/', 'Radiolinie punkt - punkt i punkt - wielopunkt, budowa i serwis | ProlinkNET', opis, tresc, aktywne='radiolinie/', okr=poz,
                  ld=[usluga_ld('Budowa radiolinii', opis, 'radiolinie/')], preload=pre_img(B, 'maszt-mob-kadr-460.webp', f' imagesrcset="{B}img/maszt-mob-kadr-460.webp 460w, {B}img/maszt-mob-kadr.webp 609w" imagesizes="(max-width:900px) 100vw, 44vw"'))

def swiatlowody(B, prod):
    poz = [('Światłowody', 'swiatlowody/')]
    tresc = naglowek(B, poz, 'Światłowody: spawanie, pomiary i instalacja sieci', 'Kompleksowe wykonanie sieci światłowodowych albo sama instalacja i montaż według przygotowanego projektu, a także adaptacja i modernizacja sieci już istniejących.',
                     'swiatlowody.webp', 'Włókna światłowodowe', w=669, h=827) + f'''
<section class="sec"><div class="wrap">
  {LM}<h2>Zakres usług światłowodowych</h2>
  <div class="uslugi4" style="margin-top:30px">
    <div class="usl"><h3>Spawanie światłowodów</h3><p>Specjalistyczna usługa łączenia włókien światłowodu: zarówno mechanicznie, szybkozłączką, jak i spawaniem łukiem elektrycznym o znacznie trwalszej strukturze. Pracujemy spawarką Fujikura, której używają największe firmy telekomunikacyjne w Europie.</p></div>
    <div class="usl"><h3>Pomiar światłowodów</h3><p>Stosujemy nowoczesny sprzęt pomiarowy gwarantujący dokładność i precyzję, które są standardem w telekomunikacji. Oferujemy pomiar reflektometrem z dużą dokładnością, zarówno włókien wymagających spawania, jak i istniejących połączeń w sieci.</p></div>
    <div class="usl"><h3>Układanie światłowodów</h3><p>Układamy światłowody na obiektach telekomunikacyjnych oraz innych obiektach budowlanych zgodnie z najwyższymi standardami, z dbałością o bezpieczeństwo i ochronę kabli przed uszkodzeniem.</p></div>
    <div class="usl"><h3>Instalacja sieci światłowodowych</h3><p>Realizujemy kompleksowe wykonanie sieci albo jedynie instalację i montaż według sporządzonego projektu i przygotowanych do podpięcia urządzeń. Wykonujemy instalację światłowodów w tunelach z należytym zabezpieczeniem.</p></div>
  </div>
</div></section>
<section class="sec alt"><div class="wrap split">
  <div class="tekst">
    {LM}<h2>Integracja z siecią telekomunikacyjną</h2>
    <p>Zapewniamy profesjonalną instalację sieci teleinformatycznych wraz z przystosowaniem i integracją z sieciami telekomunikacyjnymi.</p>
    <p>Oprócz wykonania nowych instalacji dokonujemy adaptacji i modernizacji już istniejących sieci światłowodowych.</p>
  </div>
  <figure class="split-foto" style="margin:0;background:#fff;min-height:420px"><img src="{B}img/zlacza.webp" width="329" height="530" alt="Złącza światłowodowe" loading="lazy" decoding="async" style="object-fit:contain"></figure>
</div></section>
{pas(B, 'Masz sieć światłowodową do wykonania lub pomiaru?')}'''
    opis = 'Spawanie światłowodów spawarką Fujikura, pomiary reflektometrem, układanie i instalacja sieci światłowodowych, także w tunelach. ProlinkNET, cała Polska.'
    return strona(B, prod, 'swiatlowody/', 'Spawanie i pomiary światłowodów, instalacja sieci światłowodowych | ProlinkNET', opis, tresc, aktywne='swiatlowody/', okr=poz,
                  ld=[usluga_ld('Spawanie, pomiary i instalacja światłowodów', opis, 'swiatlowody/')], preload=pre_img(B, 'swiatlowody.webp'))

def konstrukcje(B, prod):
    poz = [('Konstrukcje stalowe', 'konstrukcje-stalowe/')]
    tresc = naglowek(B, poz, 'Konstrukcje stalowe i maszty telekomunikacyjne', 'Projektujemy konstrukcje wsporcze pod anteny, wykonujemy ich prefabrykację i montaż. Wszystkie konstrukcje zabezpieczamy antykorozyjnie poprzez cynkowanie.',
                     'konstrukcje-rulony.webp', 'Rysunki konstrukcji stalowych', w=469, h=827) + f'''
<section class="sec"><div class="wrap split">
  <div class="tekst">
    {LM}<h2>Obiekty na terenie całego kraju</h2>
    <p>Od 2003 roku ProlinkNET uczestniczy w rozwoju polskiej telefonii komórkowej. Jako podwykonawca największych polskich firm telekomunikacyjnych wybudowaliśmy szereg obiektów na terenie całego kraju. Projektowaliśmy konstrukcje wsporcze, wykonywaliśmy ich prefabrykację i montaż, a także braliśmy udział w rozbudowie dużych stacji łączności radiofonicznej.</p>
    <p>Firma zatrudnia wykwalifikowanych pracowników i alpinistów oraz współpracuje z szeregiem doświadczonych specjalistów. Konsekwentna polityka firmy poparta wieloletnim doświadczeniem pozwoliła na coraz bardziej kompleksową realizację powierzanych zadań i rozszerzenie zakresu usług.</p>
  </div>
  <div class="usl">
    <h3>Zakres usług</h3>
    <ul class="lista2" style="columns:1;margin-top:14px">
      <li>raporty oddziaływania na środowisko</li><li>oceny stanu technicznego istniejących obiektów i obiektów budowlanych</li><li>prefabrykacja konstrukcji stalowych</li><li>montaż konstrukcji (prace budowlano-montażowe)</li><li>montaż oznakowania przeszkodowego wysokich obiektów</li><li>montaż instalacji odgromowych</li><li>nadzór nad całym okresem wykonywania prac budowlanych</li>
    </ul>
  </div>
</div></section>
<div class="wstega"><img src="{B}img/konstrukcje-rysunek.webp" width="1169" height="387" alt="Rysunek techniczny konstrukcji stalowej" loading="lazy" decoding="async"></div>
<section class="sec"><div class="wrap tekst">
  {LM}<h2>Konstrukcje przemysłowe i małogabarytowe</h2>
  <p>Wykonujemy różnego rodzaju konstrukcje przemysłowe i budowlane. Możemy wykonać także wszelkiego typu małogabarytowe konstrukcje stalowe, takie jak balustrady mostowe czy niestandardowe rozwiązania pod instalacje radiowe i nie tylko.</p>
  <p>Wszystkie konstrukcje zabezpieczamy antykorozyjnie poprzez cynkowanie. Na konstrukcjach montujemy też anteny i urządzenia <a href="{B}radiolinie/">radiolinii</a>.</p>
</div></section>
{pas(B, 'Potrzebujesz konstrukcji wsporczej lub masztu?')}'''
    opis = 'Projekt, prefabrykacja i montaż konstrukcji wsporczych pod anteny, maszty, balustrady mostowe, cynkowanie, instalacje odgromowe, oznakowanie przeszkodowe. ProlinkNET.'
    return strona(B, prod, 'konstrukcje-stalowe/', 'Konstrukcje stalowe, maszty i konstrukcje wsporcze pod anteny | ProlinkNET', opis, tresc, aktywne='konstrukcje-stalowe/', okr=poz,
                  ld=[usluga_ld('Konstrukcje stalowe i maszty telekomunikacyjne', opis, 'konstrukcje-stalowe/')], preload=pre_img(B, 'konstrukcje-rulony.webp'))

def utrzymanie(B, prod):
    poz = [('Utrzymanie oraz outsourcing', 'utrzymanie-i-outsourcing/')]
    tresc = naglowek(B, poz, 'Utrzymanie sieci telekomunikacyjnych oraz outsourcing', 'Naturalne rozszerzenie budowy sieci: szeroka gama usług poinstalacyjnych przy rozbudowie i eksploatacji istniejącej infrastruktury.',
                     'serwerownia-600.webp', 'Serwerownia z szafami telekomunikacyjnymi', w=600, h=347, srcset=f' srcset="{B}img/serwerownia-600.webp 600w, {B}img/serwerownia.webp 1000w" sizes="(max-width:900px) 100vw, 44vw"') + f'''
<section class="sec"><div class="wrap split">
  <div class="tekst">
    {LM}<h2>Opieka nad działającą siecią</h2>
    <p>W swojej ofercie ProlinkNET, jako naturalne rozszerzenie usług związanych z budową sieci telekomunikacyjnych, posiada szeroką gamę usług poinstalacyjnych. Usługi te, związane bezpośrednio z rozbudową istniejących sieci, obejmują instalację dodatkowych urządzeń telekomunikacyjnych, wszelkie prace konfiguracyjne oraz serwisowe.</p>
    <p>Wspieramy wdrażanie nowych rozwiązań i bierzemy udział w rozbudowie istniejącej infrastruktury.</p>
  </div>
  <div class="usl">
    <h3>Co obejmuje</h3>
    <ul class="lista2" style="columns:1;margin-top:14px">
      <li>instalacja dodatkowych urządzeń telekomunikacyjnych</li><li>prace konfiguracyjne</li><li>prace serwisowe</li><li>eksploatacja i konserwacja zainstalowanych urządzeń</li><li>usuwanie awarii systemów radioliniowych</li>
    </ul>
  </div>
</div></section>
<section class="sec alt"><div class="wrap tekst">
  {LM}<h2>Zespół</h2>
  <p>W skład naszej firmy wchodzą wykwalifikowani i doświadczeni pracownicy, którzy odbyli szereg szkoleń zarówno teoretycznych, jak i praktycznych w zakresie prac instalacyjno-uruchomieniowych i integracyjnych dotyczących usług telekomunikacyjnych, których rozwój wspieramy.</p>
  <p>Utrzymujemy sieci, które sami budujemy, i te wykonane przez innych: <a href="{B}radiolinie/">radiolinie</a>, <a href="{B}swiatlowody/">światłowody</a> i urządzenia w szafach telekomunikacyjnych.</p>
</div></section>
{pas(B, 'Szukasz partnera do utrzymania sieci?')}'''
    opis = 'Utrzymanie i outsourcing sieci telekomunikacyjnych: instalacja dodatkowych urządzeń, konfiguracja, serwis, konserwacja, usuwanie awarii radiolinii. ProlinkNET, cała Polska.'
    return strona(B, prod, 'utrzymanie-i-outsourcing/', 'Utrzymanie sieci telekomunikacyjnych i outsourcing, serwis radiolinii | ProlinkNET', opis, tresc, aktywne='utrzymanie-i-outsourcing/', okr=poz,
                  ld=[usluga_ld('Utrzymanie sieci telekomunikacyjnych i outsourcing', opis, 'utrzymanie-i-outsourcing/')],
                  preload=pre_img(B, 'serwerownia-600.webp', f' imagesrcset="{B}img/serwerownia-600.webp 600w, {B}img/serwerownia.webp 1000w" imagesizes="(max-width:900px) 100vw, 44vw"'))

def ofirmie(B, prod):
    poz = [('O firmie', 'o-firmie/')]
    loga = ''.join(f'<div class="logo-p"><img src="{B}img/partner-{i}.webp" alt="{n}" width="{w}" height="{h}" loading="lazy" decoding="async"></div>' for i, n, w, h in PARTNERZY)
    tresc = naglowek(B, poz, 'O firmie: Twój solidny partner teleinformatyczny', 'Jako firma działająca w sektorze telekomunikacyjnym od 2003 roku mamy bogate doświadczenie we współpracy z największymi operatorami w Polsce.',
                     'zasieg-600.webp', 'Mapa połączeń sieci na terenie Polski', w=600, h=277, srcset=f' srcset="{B}img/zasieg-600.webp 600w, {B}img/zasieg-800.webp 800w, {B}img/zasieg.webp 1000w" sizes="(max-width:900px) 100vw, 44vw"') + f'''
<section class="sec"><div class="wrap split">
  <div class="tekst">
    {LM}<h2>ProlinkNET</h2>
    <p>Firma ProlinkNET powstała w 2003 roku. Głównym zakresem naszego działania są usługi techniczne w branży telekomunikacyjnej. Wspieramy wdrażanie nowych rozwiązań i bierzemy udział w rozbudowie istniejącej infrastruktury. Siedzibę mamy w Starym Kraszewie pod Warszawą, a teren naszego działania obejmuje całą Polskę.</p>
    <p>W skład naszej firmy wchodzą wykwalifikowani i doświadczeni pracownicy, którzy odbyli szereg szkoleń teoretycznych i praktycznych w zakresie prac instalacyjno-uruchomieniowych i integracyjnych dotyczących usług telekomunikacyjnych.</p>
    <p>Jeśli szukają Państwo wszechstronnych rozwiązań w zakresie budowy i utrzymania sieci GSM/UMTS/LTE, znaleźli Państwo firmę dysponującą kompetentnym personelem i wieloletnim doświadczeniem w tej dziedzinie. Pracując dla operatorów telefonii stacjonarnej i komórkowej na rynku krajowym, zdobyliśmy szerokie doświadczenie w swojej branży.</p>
    <p>Klienci, którzy nam zaufają, mogą mieć pewność, że dzięki naszej wiedzy, doświadczeniu i profesjonalizmowi z sukcesem zrealizują swoje cele operacyjne.</p>
  </div>
  <figure class="split-foto" style="margin:0;min-height:460px"><img src="{B}img/maszt-niebo-mob-460.webp" srcset="{B}img/maszt-niebo-mob-460.webp 460w, {B}img/maszt-niebo-mob.webp 609w" sizes="(max-width:900px) 100vw, 45vw" width="609" height="827" alt="Maszt telekomunikacyjny z antenami radiolinii" loading="lazy" decoding="async"><figcaption>Od 2003 roku w polskiej telefonii komórkowej</figcaption></figure>
</div></section>
<section class="sec alt"><div class="wrap">
  {LM}<h2>Nasze najważniejsze atuty</h2>
  <ul class="atuty" style="max-width:760px"><li>doświadczenie w planowaniu i realizacji infrastruktury teleinformatycznej,</li><li>doświadczenie we współpracy z instytucjami regulującymi rynek telefonii w kwestiach licencji dla operatorów,</li><li>profesjonalizm i doświadczenie naszych pracowników.</li></ul>
  <ul class="obszar"><li><a href="{B}radiolinie/">Radiolinie</a></li><li><a href="{B}swiatlowody/">Światłowody</a></li><li><a href="{B}konstrukcje-stalowe/">Konstrukcje stalowe</a></li><li><a href="{B}utrzymanie-i-outsourcing/">Utrzymanie oraz outsourcing</a></li></ul>
</div></section>
<section class="partnerzy" id="partnerzy"><div class="wrap">
  <div class="sec-hd"><div>{LM}<h2>Nasi partnerzy</h2><p>Pracowaliśmy przy sieciach i obiektach operatorów oraz dostawców infrastruktury.</p></div></div>
  <div class="loga" data-tor="loga2">{loga}</div>
</div></section>
<section class="sec"><div class="wrap tekst">
  {LM}<h2>Dane firmy</h2>
  <p><strong>PROLINKNET Sp. z o.o.</strong><br>ul. Radzymińska 180, 05-205 Stary Kraszew<br>NIP 1251626648 · KRS 0000514566 · REGON 147306133</p>
</div></section>
{pas(B, 'Masz obiekt do połączenia lub sieć do utrzymania?')}'''
    opis = 'ProlinkNET (PROLINKNET Sp. z o.o.): od 2003 roku podwykonawca operatorów w budowie i utrzymaniu sieci GSM/UMTS/LTE. Atuty, partnerzy: Emitel, NEC, Plus, Orange, Netia, Exatel.'
    return strona(B, prod, 'o-firmie/', 'O firmie ProlinkNET - partner teleinformatyczny od 2003 roku, partnerzy', opis, tresc, aktywne='o-firmie/', okr=poz,
                  preload=pre_img(B, 'zasieg-600.webp', f' imagesrcset="{B}img/zasieg-600.webp 600w, {B}img/zasieg-800.webp 800w, {B}img/zasieg.webp 1000w" imagesizes="(max-width:900px) 100vw, 44vw"'), og_typ='website')

def kontakt(B, prod):
    poz = [('Kontakt', 'kontakt/')]
    tresc = f'''<section class="sec alt" data-mob-od style="padding-top:clamp(36px,5vw,72px)"><div class="wrap kontakt-grid">
  <div>
    {okruszki(B, poz)}
    {LM}<h1 style="font-size:clamp(34px,4vw,54px)">Kontakt</h1>
    <p style="margin-top:16px">Zapraszamy do zapoznania się z naszą ofertą kompleksowych usług telekomunikacyjnych. Opisz obiekt, lokalizację i zakres prac, a odpowiemy z propozycją realizacji.</p>
    {dane_kontaktowe()}
    <p class="rej" style="color:var(--mut);font-size:14px">PROLINKNET Sp. z o.o. · NIP 1251626648 · KRS 0000514566 · REGON 147306133</p>
  </div>
  {formularz(B, prod, 'zapytanie')}
</div></section>
<section class="sec" style="padding-top:0;background:var(--bg2)"><div class="wrap">{mapa(420)}</div></section>'''
    opis = 'Kontakt z ProlinkNET: tel. 733 800 337, biuro@prolinknet.pl, ul. Radzymińska 180, 05-205 Stary Kraszew. Formularz zapytania o radiolinie, światłowody i konstrukcje.'
    return strona(B, prod, 'kontakt/', 'Kontakt - ProlinkNET, zapytanie o realizację', opis, tresc, aktywne='kontakt/', okr=poz,
                  ld=[{'@type': 'ContactPage', 'url': DOM + '/kontakt/', 'about': {'@id': DOM + '/#firma'}}])

def polityka(B, prod):
    poz = [('Polityka prywatności', 'polityka-prywatnosci/')]
    tresc = f'''<section class="sec"><div class="wrap tekst pol">
  {okruszki(B, poz)}
  {LM}<h1 style="font-size:clamp(32px,3.6vw,48px)">Polityka prywatności</h1>
  <p style="margin-top:18px">Ta strona opisuje, jakie dane przetwarzamy w związku z korzystaniem ze strony prolinknet.pl i w jakim celu.</p>
  <h2>Administrator danych</h2>
  <p>Administratorem danych jest PROLINKNET Sp. z o.o. z siedzibą w Starym Kraszewie, ul. Radzymińska 180, 05-205 Stary Kraszew, NIP 1251626648, KRS 0000514566, REGON 147306133. Kontakt w sprawach danych osobowych: <a href="mailto:{MAIL}">{MAIL}</a>, tel. <a href="tel:{TEL1H}">{TEL1}</a>.</p>
  <h2>Formularz zapytania i korespondencja</h2>
  <p>Dane podane w formularzu (imię i nazwisko lub nazwa firmy, telefon, adres e-mail, treść zapytania) oraz w korespondencji przetwarzamy w celu odpowiedzi na zapytanie i przygotowania oferty (art. 6 ust. 1 lit. b RODO), a także w celu prowadzenia korespondencji i ewentualnego dochodzenia roszczeń (art. 6 ust. 1 lit. f RODO). Podanie danych jest dobrowolne, ale bez telefonu lub adresu e-mail nie możemy odpowiedzieć.</p>
  <p>Po wysłaniu formularza na podany adres e-mail wysyłamy automatyczne potwierdzenie otrzymania zapytania. Dane przechowujemy przez czas potrzebny do prowadzenia korespondencji i realizacji ewentualnej umowy, a następnie przez okres przedawnienia roszczeń.</p>
  <h2>Odbiorcy danych</h2>
  <p>Dane mogą być przekazywane wyłącznie podmiotom, które obsługują techniczną stronę naszej działalności: dostawcy hostingu i poczty elektronicznej (nazwa.pl). Nie sprzedajemy danych i nie przekazujemy ich poza Europejski Obszar Gospodarczy.</p>
  <h2>Pliki cookies i pamięć przeglądarki</h2>
  <p>Strona nie używa narzędzi analitycznych ani reklamowych. W pamięci przeglądarki zapisujemy tylko Twój wybór z banera zgód. Mapa Google na stronie kontaktowej wczytuje się dopiero po zgodzie albo kliknięciu przycisku „Pokaż mapę Google”; wtedy Google Ireland Limited może zapisać pliki cookies i otrzymać adres IP zgodnie ze swoją <a href="https://policies.google.com/privacy?hl=pl" rel="noopener" target="_blank">polityką prywatności</a>. Zgodę można wycofać, czyszcząc dane strony w ustawieniach przeglądarki.</p>
  <h2>Dane techniczne</h2>
  <p>Serwer hostingu automatycznie zapisuje w dziennikach podstawowe informacje o połączeniach (adres IP, data, adres podstrony, rodzaj przeglądarki) w celu zapewnienia bezpieczeństwa i prawidłowego działania strony (art. 6 ust. 1 lit. f RODO). Formularz chroni się przed spamem m.in. przez ograniczenie liczby wiadomości z jednej sieci; w tym celu adres IP zapisujemy wyłącznie w postaci zaszyfrowanego skrótu przez maksymalnie dobę.</p>
  <h2>Twoje prawa</h2>
  <p>Masz prawo dostępu do swoich danych, ich sprostowania, usunięcia, ograniczenia przetwarzania, przenoszenia oraz wniesienia sprzeciwu wobec przetwarzania. Przysługuje Ci także prawo wniesienia skargi do Prezesa Urzędu Ochrony Danych Osobowych (ul. Stawki 2, 00-193 Warszawa).</p>
  <p style="margin-top:28px;color:var(--mut);font-size:15px">Aktualizacja: {datetime.date.today().strftime('%d.%m.%Y')}</p>
</div></section>'''
    return strona(B, prod, 'polityka-prywatnosci/', 'Polityka prywatności - ProlinkNET', 'Polityka prywatności strony prolinknet.pl: administrator danych PROLINKNET Sp. z o.o., formularz zapytania, pliki cookies i mapa Google, prawa osób.', tresc, okr=poz)

def strona404(B, prod):
    tresc = f'''<section class="sec alt" style="min-height:60svh"><div class="wrap tekst">
  {LM}<h1 style="font-size:clamp(32px,4vw,52px)">Nie ma takiej strony</h1>
  <p style="margin-top:16px">Adres mógł się zmienić po przebudowie strony. Zapraszamy na stronę główną albo do oferty:</p>
  <ul class="obszar"><li><a href="{B}radiolinie/">Radiolinie</a></li><li><a href="{B}swiatlowody/">Światłowody</a></li><li><a href="{B}konstrukcje-stalowe/">Konstrukcje stalowe</a></li><li><a href="{B}utrzymanie-i-outsourcing/">Utrzymanie</a></li><li><a href="{B}kontakt/">Kontakt</a></li></ul>
  <p style="margin-top:28px"><a class="btn" href="{B}">Strona główna {AR}</a></p>
</div></section>'''
    s = strona(B, prod, '404.html', 'Nie ma takiej strony - ProlinkNET', 'Strona nie istnieje. Przejdź do strony głównej ProlinkNET.', tresc)
    return s.replace('content="index,follow,max-image-preview:large"', 'content="noindex,follow"')

STRONY = [('', glowna, '1.0'), ('radiolinie/', radiolinie, '0.9'), ('swiatlowody/', swiatlowody, '0.9'), ('konstrukcje-stalowe/', konstrukcje, '0.9'),
          ('utrzymanie-i-outsourcing/', utrzymanie, '0.9'), ('o-firmie/', ofirmie, '0.7'), ('kontakt/', kontakt, '0.8'), ('polityka-prywatnosci/', polityka, '0.2')]

LLMS = f'''# ProlinkNET (PROLINKNET Sp. z o.o.)

> Firma telekomunikacyjna ze Starego Kraszewa pod Warszawą, działająca od 2003 roku na terenie całej Polski jako podwykonawca operatorów. Budowa i utrzymanie infrastruktury teleinformatycznej: radiolinie punkt - punkt i punkt - wielopunkt, światłowody, konstrukcje stalowe i maszty, utrzymanie sieci oraz outsourcing.

## Dane kontaktowe
- Telefon: {TEL1}
- E-mail: {MAIL}
- Adres: ul. Radzymińska 180, 05-205 Stary Kraszew
- NIP 1251626648, KRS 0000514566, REGON 147306133
- Obszar działania: cała Polska

## Usługi
- [Radiolinie]({DOM}/radiolinie/): wizja radiowa, uzgodnienia, dokumentacja, montaż konstrukcji, anten i modułów ODU/IDU, uruchomienie, pomiary transmisyjne, dokumentacja powykonawcza, serwis.
- [Światłowody]({DOM}/swiatlowody/): spawanie (spawarka Fujikura) i łączenie mechaniczne, pomiary reflektometrem, układanie, instalacja sieci, także w tunelach, modernizacja istniejących sieci.
- [Konstrukcje stalowe]({DOM}/konstrukcje-stalowe/): projekt, prefabrykacja i montaż konstrukcji wsporczych pod anteny, maszty, balustrady mostowe, cynkowanie, instalacje odgromowe, oznakowanie przeszkodowe, oceny stanu technicznego.
- [Utrzymanie oraz outsourcing]({DOM}/utrzymanie-i-outsourcing/): instalacja dodatkowych urządzeń, konfiguracja, serwis, konserwacja, usuwanie awarii systemów radioliniowych.

## Firma
- [O firmie]({DOM}/o-firmie/): doświadczenie przy sieciach GSM/UMTS/LTE, partnerzy: Emitel, NEC, Plus, Orange, Netia, Exatel.
- [Kontakt i formularz zapytania]({DOM}/kontakt/)
'''

def zbuduj(cel, B, prod):
    if os.path.isdir(cel):
        for p in os.listdir(cel):
            if p in ('.git', '_limity'): continue
            q = os.path.join(cel, p)
            shutil.rmtree(q) if os.path.isdir(q) else os.remove(q)
    os.makedirs(cel, exist_ok=True)
    for sc, fn, _ in STRONY:
        d = os.path.join(cel, sc); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8', newline='\n').write(fn(B, prod))
    open(os.path.join(cel, '404.html'), 'w', encoding='utf-8', newline='\n').write(strona404(B, prod))
    for k in ('img', 'fonts', 'ikony'): shutil.copytree(os.path.join(TU, k), os.path.join(cel, k))
    shutil.copy(os.path.join(TU, 'ikony', 'favicon.ico'), os.path.join(cel, 'favicon.ico'))
    shutil.copy(os.path.join(TU, 'ikony', 'apple-touch-icon.png'), os.path.join(cel, 'apple-touch-icon.png'))
    open(os.path.join(cel, 'app.js'), 'w', encoding='utf-8', newline='\n').write(open(os.path.join(TU, 'app.js'), encoding='utf-8').read())
    man = {'name': 'ProlinkNET', 'short_name': 'ProlinkNET', 'start_url': B, 'scope': B, 'display': 'browser', 'background_color': '#ffffff', 'theme_color': '#0E1B3D',
           'icons': [{'src': B + 'ikony/favicon-192.png', 'sizes': '192x192', 'type': 'image/png'}, {'src': B + 'ikony/favicon-512.png', 'sizes': '512x512', 'type': 'image/png'}]}
    json.dump(man, open(os.path.join(cel, 'site.webmanifest'), 'w', encoding='utf-8'), ensure_ascii=False)
    if prod:
        open(os.path.join(cel, 'robots.txt'), 'w', newline='\n').write('User-agent: *\nAllow: /\nDisallow: /wyslij.php\n\nSitemap: %s/sitemap.xml\n' % DOM)
        sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for sc, _, pr in STRONY: sm += '  <url><loc>%s/%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n' % (DOM, sc, DZIS, pr)
        open(os.path.join(cel, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write(sm + '</urlset>\n')
        open(os.path.join(cel, 'llms.txt'), 'w', encoding='utf-8', newline='\n').write(LLMS)
        shutil.copy(os.path.join(TU, 'htaccess.txt'), os.path.join(cel, '.htaccess'))
        shutil.copy(os.path.join(TU, 'wyslij.php'), os.path.join(cel, 'wyslij.php'))
        shutil.copytree(os.path.join(TU, 'inc'), os.path.join(cel, 'inc'))
        open(os.path.join(cel, 'inc', '.htaccess'), 'w', newline='\n').write('Require all denied\n<IfModule !mod_authz_core.c>\nDeny from all\n</IfModule>\n')
        os.makedirs(os.path.join(cel, '_limity'), exist_ok=True)
        open(os.path.join(cel, '_limity', '.htaccess'), 'w', newline='\n').write('Require all denied\n<IfModule !mod_authz_core.c>\nDeny from all\n</IfModule>\n')
        shutil.copy(os.path.join(TU, 'google7a4ee7fb2ae7aff4.html'), os.path.join(cel, 'google7a4ee7fb2ae7aff4.html'))
    else:
        open(os.path.join(cel, 'robots.txt'), 'w', newline='\n').write('User-agent: *\nDisallow: /\n')
        open(os.path.join(cel, '.nojekyll'), 'w').write('')
    print(cel, 'OK')

if __name__ == '__main__':
    zbuduj(os.path.join(KOR, 'paczka', 'prolinknet.pl'), '/', True)
    zbuduj(os.path.join(KOR, 'docs'), '/prolinknet-strona/', False)
