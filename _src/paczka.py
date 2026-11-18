# Pakuje stronę do ZIP (pliki od razu w katalogu głównym archiwum, razem z .htaccess). python -I paczka.py
import os, zipfile
TU = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(TU, '..', 'paczka', 'prolinknet.pl')
DST = os.path.join(TU, '..', 'paczka', 'prolinknet.pl-strona.zip')
n = 0
with zipfile.ZipFile(DST, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for kat, _, pliki in os.walk(SRC):
        for p in pliki:
            pelna = os.path.join(kat, p); rel = os.path.relpath(pelna, SRC).replace(os.sep, '/')
            if rel.startswith('_limity/') and rel != '_limity/.htaccess': continue
            z.write(pelna, rel); n += 1
print(n, 'plików ->', os.path.abspath(DST), round(os.path.getsize(DST) / 1024), 'KB')
