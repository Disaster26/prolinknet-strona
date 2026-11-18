# Zrzuty stron (Playwright, czysty profil) + pomiar pierwszego ekranu, zrzuty maili z formularza
import sys, os, glob, email, json
from email import policy
from playwright.sync_api import sync_playwright
BAZA = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8833/'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_zrzuty')
STRONY = ['', 'radiolinie/', 'swiatlowody/', 'konstrukcje-stalowe/', 'utrzymanie-i-outsourcing/', 'o-firmie/', 'kontakt/', 'polityka-prywatnosci/']
ROZM = [(360, 640), (390, 664), (390, 844), (412, 740), (414, 896), (768, 1024), (1366, 768), (1920, 1080), (2000, 950)]
tryb = sys.argv[2] if len(sys.argv) > 2 else 'wszystko'
with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome')
    wyn = []
    if tryb in ('wszystko', 'strony'):
        for w, h in ROZM:
            c = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1, accept_downloads=False, is_mobile=w < 760, has_touch=w < 760)
            c.add_init_script("try{localStorage.setItem('pl-zgody','niezbedne')}catch(e){}")
            pg = c.new_page(); bledy = []
            pg.on('console', lambda m: bledy.append(m.text) if m.type == 'error' else None)
            pg.on('pageerror', lambda e: bledy.append(str(e)))
            for s in STRONY:
                pg.goto(BAZA + s, wait_until='networkidle')
                pg.wait_for_timeout(250)
                m = pg.evaluate('''() => { const r = x => x ? x.getBoundingClientRect() : null;
                  const h1 = document.querySelector('h1'), btn = document.querySelector('.hero .cta .btn, .ph .btn'), lead = document.querySelector('.hero .lead, .ph .lead');
                  return {sw: document.documentElement.scrollWidth, vw: innerWidth, vh: innerHeight, btnBottom: btn ? Math.round(r(btn).bottom) : null, gap: (btn && lead) ? Math.round(r(btn).top - r(lead).bottom) : null, h1: h1 ? h1.textContent.slice(0, 40) : ''} }''')
                m.update({'roz': '%dx%d' % (w, h), 'str': s or '/'})
                wyn.append(m)
                nazwa = (s.strip('/') or 'glowna') + '_%dx%d' % (w, h)
                if (w, h) in ((390, 844), (1366, 768), (360, 640), (1920, 1080)) or s == '':
                    pg.screenshot(path=os.path.join(OUT, nazwa + '.png'))
                if (w, h) in ((390, 844), (1366, 768)):
                    pg.screenshot(path=os.path.join(OUT, nazwa + '_cala.png'), full_page=True)
            if w == 390 and h == 844:
                pg.goto(BAZA, wait_until='networkidle'); pg.click('#burger'); pg.wait_for_timeout(400)
                pg.screenshot(path=os.path.join(OUT, 'menu_390x844.png'))
            for e in set(bledy): print('BŁĄD KONSOLI', w, e[:160])
            c.close()
        for m in wyn:
            uw = []
            if m['sw'] > m['vw']: uw.append('PRZEWIJANIE W BOK %d' % m['sw'])
            if m['btnBottom'] is not None and m['btnBottom'] > m['vh']: uw.append('PRZYCISK POD EKRANEM %d>%d' % (m['btnBottom'], m['vh']))
            if m['gap'] is not None and m['gap'] < 24: uw.append('ODSTĘP opis-przycisk %d' % m['gap'])
            if uw or m['vw']<500: print(m['roz'], m['str'], 'btn', m['btnBottom'], 'gap', m['gap'], ' '.join(uw))
    if tryb in ('wszystko', 'maile'):
        for f in sorted(glob.glob(sys.argv[3] + '/*.eml')) if len(sys.argv) > 3 else []:
            msg = email.message_from_bytes(open(f, 'rb').read(), policy=policy.default)
            html = msg.get_body(preferencelist=('html',)).get_content()
            html = html.replace('https://prolinknet.pl/', BAZA)
            for w, suf in ((680, 'komputer'), (390, 'telefon')):
                c = b.new_context(viewport={'width': w, 'height': 900}); pg = c.new_page(); pg.set_content(html, wait_until='networkidle')
                kto = 'klient' if 'otrzymali' in str(msg['Subject']) else 'wlasciciel'
                pg.screenshot(path=os.path.join(OUT, 'mail_%s_%s.png' % (kto, suf)), full_page=True); c.close()
                print('mail', kto, suf)
    b.close()
