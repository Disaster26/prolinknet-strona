# Przygotowanie obrazów, ikon i logo PNG (python -I obrazy.py)
import os, shutil
from PIL import Image, ImageDraw, ImageFont
TU = os.path.dirname(os.path.abspath(__file__))
Z = os.path.join(TU, 'img_zrodla'); IMG = os.path.join(TU, 'img'); IK = os.path.join(TU, 'ikony')
NAVY = (14, 27, 61); CY = (16, 187, 241)

def webp(src, dst, w=None, q=80, crop=None):
    im = Image.open(os.path.join(Z, src)).convert('RGB')
    if crop: im = im.crop(crop)
    if w and im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(os.path.join(IMG, dst), 'WEBP', quality=q, method=6)
    print(dst, im.size, os.path.getsize(os.path.join(IMG, dst)))

# zdjęcia (przekodowane, bez metadanych)
webp('maszt-niebo.webp', 'maszt-niebo-1169.webp', q=78)
webp('maszt-niebo.webp', 'maszt-niebo-800.webp', 800, q=78)
webp('maszt-niebo-mob.webp', 'maszt-niebo-mob.webp', q=76)
webp('maszt-niebo-mob.webp', 'maszt-niebo-mob-460.webp', 460, q=74)
for n, w in [('maszt-radiolinie', None), ('swiatlowody', None), ('konstrukcje-rulony', None), ('konstrukcje-rysunek', None),
             ('serwerownia', 1000), ('zasieg', 1000), ('zlacza', None)]:
    webp(n + '.webp', n + '.webp', w)
webp('serwerownia.webp', 'serwerownia-600.webp', 600)
webp('zasieg.webp', 'zasieg-600.webp', 600)
for i in range(2, 8):
    im = Image.open(os.path.join(Z, 'partner-%d.webp' % i)).convert('RGBA')
    im.save(os.path.join(IMG, 'partner-%d.webp' % i), 'WEBP', quality=90, method=6, lossless=True)

# og:image 1200x630 JPG (Facebook, LinkedIn, Google)
im = Image.open(os.path.join(Z, 'maszt-niebo.webp')).convert('RGB')
h = round(im.width * 630 / 1200); top = max(0, round((im.height - h) * .35))
im.crop((0, top, im.width, top + h)).resize((1200, 630), Image.LANCZOS).save(os.path.join(IMG, 'og-prolinknet.jpg'), 'JPEG', quality=84, optimize=True, progressive=True)

# sygnet: dwa węzły połączone linią (jak favicon.svg)
def sygnet(n, tlo=True):
    S = 4; N = n * S
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if tlo: d.rounded_rectangle((0, 0, N - 1, N - 1), radius=round(N * 6 / 32), fill=NAVY)
    k = N / 32; lw = max(1, round(2.2 * k))
    d.ellipse((9 * k - 3.5 * k, 16 * k - 3.5 * k, 9 * k + 3.5 * k, 16 * k + 3.5 * k), outline=CY, width=lw)
    x = 13 * k
    while x < 20 * k:
        d.line((x, 16 * k, min(x + 2.5 * k, 20 * k), 16 * k), fill=CY, width=lw); x += 4.5 * k
    d.ellipse((23.5 * k - 3.5 * k, 16 * k - 3.5 * k, 23.5 * k + 3.5 * k, 16 * k + 3.5 * k), fill=CY)
    return im.resize((n, n), Image.LANCZOS)
for n in (48, 96, 192, 512):
    sygnet(n).save(os.path.join(IK, 'favicon-%d.png' % n))
a = sygnet(180).convert('RGB'); a.save(os.path.join(IK, 'apple-touch-icon.png'))
sygnet(48).save(os.path.join(IK, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])

# logo-napis PNG: "Pro" Raleway 600 + "linkNET" Raleway 300 + błękitny węzeł
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
def font_ttf(waga):
    p = os.path.join(TU, '_tmp_raleway_%d.ttf' % waga)
    if not os.path.exists(p):
        src = os.path.join(TU, '..', '_narzedzia', 'raleway-latin-wght-normal.woff2')
        f = TTFont(src); f = instancer.instantiateVariableFont(f, {'wght': waga}); f.flavor = None; f.save(p)
    return p
def napis(rozm, kolor, tlo, pad, plik, kw=None):
    f1 = ImageFont.truetype(font_ttf(600), rozm); f2 = ImageFont.truetype(font_ttf(300), rozm)
    w1 = f1.getlength('Pro'); w2 = f2.getlength('linkNET'); asc, desc = f1.getmetrics()
    dot = rozm * .26; W = int(w1 + w2 + dot * 1.9 + pad * 2); H = int(asc + desc * .35 + pad * 2)
    if kw: W, H = kw
    im = Image.new('RGBA', (W, H), tlo); d = ImageDraw.Draw(im)
    x0 = (W - (w1 + w2 + dot * 1.9)) / 2; y0 = (H - (asc + desc * .35)) / 2
    d.text((x0, y0), 'Pro', font=f1, fill=kolor); d.text((x0 + w1, y0), 'linkNET', font=f2, fill=kolor)
    cx = x0 + w1 + w2 + dot * .7 + dot / 2; cy = y0 + rozm * .28
    d.ellipse((cx - dot / 2, cy - dot / 2, cx + dot / 2, cy + dot / 2), fill=CY)
    im.save(os.path.join(IK, plik)); print(plik, im.size)
napis(64, (255, 255, 255, 255), NAVY + (255,), 22, 'logo-mail.png')            # nagłówek maili (granat)
napis(92, NAVY + (255,), (255, 255, 255, 255), 0, 'logo-prolinknet-512.png', kw=(512, 512))   # dane strukturalne
napis(80, NAVY + (255,), (255, 255, 255, 255), 30, 'logo-prolinknet.png')
for p in os.listdir(TU):
    if p.startswith('_tmp_raleway'): os.remove(os.path.join(TU, p))

# wersje do kart na głównej i mobilny kadr pierwszego ekranu
webp('swiatlowody.webp', 'swiatlowody-420.webp', 420)
webp('konstrukcje-rulony.webp', 'konstrukcje-rulony-360.webp', 360)
webp('maszt-radiolinie.webp', 'maszt-radiolinie-160.webp', 160)
im = Image.open(os.path.join(Z, 'maszt-niebo-mob.webp')).convert('RGB')
top = round((im.height - 470) * .25)
k = im.crop((0, top, im.width, top + 470))
k.save(os.path.join(IMG, 'maszt-mob-kadr.webp'), 'WEBP', quality=76, method=6)
k.resize((460, round(470 * 460 / 609)), Image.LANCZOS).save(os.path.join(IMG, 'maszt-mob-kadr-460.webp'), 'WEBP', quality=74, method=6)
print('kadr', k.size)
webp('zasieg.webp', 'zasieg-800.webp', 800)
webp('maszt-radiolinie.webp', 'maszt-radiolinie.webp', q=68)
