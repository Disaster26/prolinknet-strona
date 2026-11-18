# ProlinkNET - wdrożenie na nazwa.pl (prolinknet.pl)

Strona statyczna (HTML + formularz PHP), bez WordPressa - umowa (§ 2) nie przewiduje panelu do edycji; drobne aktualizacje robimy my (§ 7, 12 mies.).
Źródła: `C:\Users\Admin\Downloads\Prolinknet_strona\_src\` (buduj.py -> `paczka\prolinknet.pl\` + `docs\` = wersja testowa).
Paczka: `paczka\prolinknet.pl-strona.zip` (pliki w katalogu głównym archiwum, razem z `.htaccess`).

## 0. Przed wgraniem (panel nazwa.pl od klienta)
- [ ] Dostęp zapisany w `Odrobimy_kampania\klienci\_DOSTEPY_KLIENTOW.md` (loguje się user).
- [ ] Sprawdzić usługi: hosting + domena prolinknet.pl, daty ważności, brak "rezygnacji".
- [ ] Kopia obecnej strony (katalog domeny przez Menedżer plików / FTP) do `Prolinknet_strona\_kopia_stara_strona\`.
- [ ] NIE ruszać poczty ani rekordów MX. DNS zmieniamy tylko o TXT (DKIM, ewent. SPF/DMARC).
- [ ] PHP 8.x dla domeny (panel: Ustawienia PHP), rozszerzenia openssl włączone (domyślnie są).

## 1. Wgranie
- [ ] Usunąć stare pliki strony z katalogu domeny (po kopii): index.html, css/, js/, images/, partners/, upload/, oferta_firmy_Prolinknet.pdf.
- [ ] Rozpakować ZIP do katalogu domeny (musi być `.htaccess`, `wyslij.php`, `inc/`, `_limity/.htaccess`).
- [ ] Certyfikat SSL dla prolinknet.pl i www.prolinknet.pl w panelu nazwa.pl (darmowy SSL) - aktywny.
- [ ] curl: `http://prolinknet.pl`, `http://www.prolinknet.pl`, `https://www.prolinknet.pl` -> 301 na `https://prolinknet.pl/`.
- [ ] Stare adresy -> 301: `/index.html` -> `/`, `/oferta_firmy_Prolinknet.pdf` -> `/o-firmie/`, `/partners/2.png` -> `/o-firmie/`, `/images/logo.png` -> `/`.
- [ ] `/inc/PHPMailer.php` i `/_limity/` -> 403. `/favicon.ico` = sygnet ProlinkNET.

## 2. Formularz i maile (BRAMKA przed mailem o uruchomieniu)
- [ ] `https://prolinknet.pl/wyslij.php?dkim=1` -> skopiować wartość rekordu.
- [ ] DNS nazwa.pl: TXT `dm._domainkey` = `v=DKIM1; k=rsa; p=...` (z kroku wyżej).
- [ ] SPF: sprawdzić istniejący TXT `v=spf1 ...` (nazwa.pl zwykle `include:_spf.nazwa.pl`); jeśli brak - dodać `v=spf1 a mx include:_spf.nazwa.pl ~all`. Nie dublować rekordu SPF.
- [ ] DMARC: jeśli brak - TXT `_dmarc` = `v=DMARC1; p=none; rua=mailto:biuro@prolinknet.pl`.
- [ ] Po propagacji `?dkim=1` pokazuje "rekord widoczny w DNS" (sprawdzane co godzinę; można usunąć `_limity/dkim_dns.json`, żeby sprawdzić od razu).
- [ ] Test: w `wyslij.php` tymczasowo `ODBIORCA` = odrobimy@gmail.com, potwierdzić odczytem pliku z serwera; wysłać formularz na żywo (strona główna i /kontakt/), e-mail zgłaszającego = odrobimy@gmail.com.
- [ ] Gmail: oba maile w ODEBRANYCH (nie Spam), logo widać (także w aplikacji na telefonie), "Pokaż oryginał": SPF=PASS, DKIM=PASS (prolinknet.pl), DMARC=PASS.
- [ ] Przywrócić `ODBIORCA` = biuro@prolinknet.pl i potwierdzić odczytem z serwera.
- [ ] Zrzuty obu maili do instrukcji PDF (wzór lokalny: `_zrzuty\mail_wlasciciel_*.png`, `mail_klient_*.png`).

## 3. Widoczność w Google
- [ ] GSC (konto odrobimy@gmail.com, authuser=2): usługa `https://prolinknet.pl/`, weryfikacja plikiem `google7a4ee7fb2ae7aff4.html` (jest w paczce).
- [ ] Sitemap `https://prolinknet.pl/sitemap.xml` zgłoszona; "Poproś o zindeksowanie" dla / i 4 podstron usług.
- [ ] Test wyników z elementami rozszerzonymi (LocalBusiness, FAQPage, BreadcrumbList) - bez błędów.
- [ ] `robots.txt` (Allow + Sitemap), `llms.txt`, meta robots index na wszystkich podstronach (404 = noindex).
- [ ] Tagów ze starej strony nie było (brak GA/GTM/Pixel/GSC) - nic do przeniesienia.

## 4. Pomiary i kontrola
- [ ] PageSpeed (pagespeed.web.dev) komórka i komputer: / , /o-firmie/, /radiolinie/ - cel 100/100/100/100, zrzuty do PDF.
- [ ] Zrzuty pierwszego ekranu na żywo: 360x640, 390x844, 414x896, 1366, 1920 - hero z przyciskiem w całości.
- [ ] Mapa Google ładuje się po zgodzie/kliknięciu; baner cookies działa; menu mobilne.
- [ ] Znak "wykonanie: Wylinka" w stopce (rozmiar jak © ).

## 5. Po uruchomieniu
- [ ] Instrukcja PDF w stylu Wylinki (strona, formularz ze zrzutami obu maili, PageSpeed, co zmieniono) + mail do klienta.
- [ ] Zlecenie zamknięte: realizacja na wylinka.pl (`Wylinka\strona\src\data\klienci.ts`), planer (zadania + rozliczenia).
- [ ] Wersja testowa GitHub Pages zostaje z noindex (albo do usunięcia po odbiorze).
