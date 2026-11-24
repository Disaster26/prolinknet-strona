<?php
/* =====================================================================
   PROLINKNET - wysyłka formularza "Zapytanie o realizację" (strona główna i /kontakt/)
   Wysyła 2 maile z serwera nazwa.pl (bez usług zewnętrznych), biblioteką PHPMailer (inc/):
     1) zapytanie do ProlinkNET (ODBIORCA), Reply-To = adres klienta,
        więc "Odpowiedz" w poczcie od razu odpisuje klientowi,
     2) potwierdzenie dla klienta (gdy podał e-mail).
   Oba maile w kolorach strony (granat + błękit), HTML + wersja tekstowa.
   Podpis DKIM (selektor "dm"): klucz tworzy się sam w _limity/ przy pierwszym użyciu,
   rekord DNS do dodania pokazuje adres https://prolinknet.pl/wyslij.php?dkim=1 (to klucz publiczny),
   a maile są podpisywane automatycznie, gdy rekord jest już w DNS.

   USTAWIENIA - tylko te linijki zmienia się przy przenosinach:   */
define('ODBIORCA', 'biuro@prolinknet.pl');          // tu przychodzą zapytania
define('NADAWCA', 'biuro@prolinknet.pl');           // From: ISTNIEJĄCA skrzynka w domenie prolinknet.pl (nazwa.pl)
define('NADAWCA_NAZWA', 'Strona prolinknet.pl');
define('FIRMA', 'ProlinkNET');
define('TELEFON', '733 800 337');
define('TELEFON_LINK', '+48733800337');
define('ADRES_STRONY', 'https://prolinknet.pl/');
define('DOMENA', 'prolinknet.pl');
define('DKIM_SELEKTOR', 'dm');
define('DOMENY', '#^https?://(www\.)?prolinknet\.pl(:\d+)?$#');   // skąd wolno wysyłać formularz
/* ---------------------------------------------------------------------
   Ochrona przed spamem: ukryte pole-pułapka (strona_www), podpisany znacznik czasu
   (min. 3 s od otwarcia formularza, jednorazowy), sprawdzanie Origin, limit 5 zapytań/h
   i 12/dobę z jednej sieci oraz 40/dobę łącznie. Liczniki, sekret i klucz DKIM: katalog _limity
   (zablokowany w .htaccess, tworzy się sam). Zgodność: PHP 5.5 - 8.x.
   Test lokalny: zmienna środowiskowa PL_MAIL_DO_PLIKU=<katalog> zapisuje maile jako .eml.
   ===================================================================== */
define('LIMIT_H', 5);
define('LIMIT_D', 12);
define('LIMIT_GLOBALNY_D', 40);
define('LIMIT_POTW_H', 10);
define('ZNACZNIK_MIN', 3);
define('ZNACZNIK_MAX', 7200);

date_default_timezone_set('Europe/Warsaw');
header('X-Robots-Tag: noindex');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');
if (function_exists('header_remove')) header_remove('X-Powered-By');

$DEV = (string) getenv('PL_MAIL_DO_PLIKU');
$METODA = isset($_SERVER['REQUEST_METHOD']) ? $_SERVER['REQUEST_METHOD'] : '';
$JSON = (isset($_SERVER['HTTP_ACCEPT']) && stripos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false) || isset($_GET['znacznik']);

function wez($t, $k, $d = '') { return (is_array($t) && isset($t[$k])) ? $t[$k] : $d; }
function h($s) { return htmlspecialchars((string) $s, ENT_QUOTES, 'UTF-8'); }
function losowe($n) {
    if (function_exists('random_bytes')) { try { return random_bytes($n); } catch (Exception $e) {} }
    if (function_exists('openssl_random_pseudo_bytes')) return openssl_random_pseudo_bytes($n);
    $b = ''; for ($i = 0; $i < $n; $i++) $b .= chr(mt_rand(0, 255)); return $b;
}
function rowne($a, $b) {
    if (function_exists('hash_equals')) return hash_equals((string) $a, (string) $b);
    if (strlen($a) !== strlen($b)) return false;
    $r = 0; for ($i = 0; $i < strlen($a); $i++) $r |= ord($a[$i]) ^ ord($b[$i]); return $r === 0;
}
function kod($k) {
    if (function_exists('http_response_code')) { http_response_code($k); return; }
    header('HTTP/1.1 ' . $k . ' Status', true, $k);
}
// odpowiedź: JSON dla skryptu strony, prosta strona HTML gdy JavaScript jest wyłączony
function odpowiedz($ok, $k, $komunikat) {
    global $JSON;
    kod($k);
    if ($JSON) {
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(array('success' => $ok, 'komunikat' => $komunikat));
        exit;
    }
    header('Content-Type: text/html; charset=utf-8');
    echo '<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
       . '<meta name="robots" content="noindex"><title>' . ($ok ? 'Wysłano' : 'Nie wysłano') . ' - ' . FIRMA . '</title></head>'
       . '<body style="margin:0;padding:40px 16px;background:#EEF3F7;font:17px/1.6 Arial,sans-serif;color:#0E1B3D">'
       . '<main style="max-width:560px;margin:0 auto;background:#ffffff;border-top:6px solid #10BBF1;padding:28px 24px">'
       . '<p style="margin:0 0 18px;font-weight:bold">' . h($komunikat) . '</p>'
       . '<p style="margin:0"><a href="/" style="color:#0786b3">Wróć na stronę ' . FIRMA . '</a></p></main></body></html>';
    exit;
}

// ---------------------------------------------------------------- katalog limitów i sekret
function katalog() {
    $k = getenv('PL_KATALOG_LIMITOW');
    if (!$k) $k = __DIR__ . '/_limity';
    if (!is_dir($k)) @mkdir($k, 0750, true);
    return $k;
}
function sekret() {
    static $s = null;
    if ($s !== null) return $s;
    $p = katalog() . '/_sekret.php';
    if (is_file($p)) { $s = (string) include $p; if (strlen($s) >= 32) return $s; }
    $s = bin2hex(losowe(32));
    @file_put_contents($p, "<?php return '" . $s . "';\n", LOCK_EX);
    return $s;
}
function siec() {
    $ip = (string) wez($_SERVER, 'REMOTE_ADDR', '0.0.0.0');
    if (strpos($ip, ':') !== false) {
        $b = @inet_pton($ip);
        if ($b !== false) return bin2hex(substr($b, 0, 8));
    }
    return $ip;
}
function z_plikiem($nazwa, $fn) {
    $p = katalog() . '/' . $nazwa;
    $f = @fopen($p, 'c+');
    if (!$f) return true;
    flock($f, LOCK_EX);
    $tresc = stream_get_contents($f);
    $dane = json_decode($tresc ? $tresc : '{}', true);
    if (!is_array($dane)) $dane = array();
    $wynik = $fn($dane);
    ftruncate($f, 0); rewind($f); fwrite($f, json_encode($dane)); fflush($f);
    flock($f, LOCK_UN); fclose($f);
    return $wynik;
}

// ---------------------------------------------------------------- DKIM (klucz tworzony na serwerze, nigdy w repozytorium)
function dkim_klucz() {
    $p = katalog() . '/dkim_' . DKIM_SELEKTOR . '.key';
    if (!is_file($p) && function_exists('openssl_pkey_new')) {
        $k = @openssl_pkey_new(array('private_key_bits' => 2048, 'private_key_type' => OPENSSL_KEYTYPE_RSA));
        if ($k && @openssl_pkey_export($k, $pem)) { @file_put_contents($p, $pem, LOCK_EX); @chmod($p, 0600); }
    }
    return is_file($p) ? $p : '';
}
function dkim_publiczny() {
    $p = dkim_klucz(); if ($p === '') return '';
    $k = @openssl_pkey_get_private(file_get_contents($p)); if (!$k) return '';
    $d = openssl_pkey_get_details($k);
    return preg_replace('/-----[^-]+-----|\s+/', '', $d['key']);
}
// podpisujemy tylko wtedy, gdy rekord jest już w DNS (sprawdzane raz na godzinę)
function dkim_gotowy() {
    $pub = dkim_publiczny(); if ($pub === '') return false;
    $plik = katalog() . '/dkim_dns.json';
    $st = is_file($plik) ? json_decode((string) @file_get_contents($plik), true) : null;
    if (is_array($st) && isset($st['t'], $st['ok']) && $st['t'] > time() - 3600) return (bool) $st['ok'];
    $ok = false;
    if (function_exists('dns_get_record')) {
        $r = @dns_get_record(DKIM_SELEKTOR . '._domainkey.' . DOMENA, DNS_TXT);
        if (is_array($r)) foreach ($r as $w) {
            $txt = isset($w['txt']) ? $w['txt'] : (isset($w['entries']) ? implode('', $w['entries']) : '');
            if (strpos(preg_replace('/\s+/', '', $txt), 'p=' . $pub) !== false) $ok = true;
        }
    }
    @file_put_contents($plik, json_encode(array('t' => time(), 'ok' => $ok)), LOCK_EX);
    return $ok;
}

// ---------------------------------------------------------------- GET ?dkim=1: rekord DNS do dodania (klucz publiczny)
if ($METODA === 'GET' && isset($_GET['dkim'])) {
    header('Content-Type: text/plain; charset=utf-8');
    $pub = dkim_publiczny();
    echo $pub === '' ? "Brak OpenSSL na serwerze - DKIM niedostępny.\n"
        : "Rekord TXT do dodania w DNS domeny " . DOMENA . ":\nnazwa: " . DKIM_SELEKTOR . "._domainkey\nwartość: v=DKIM1; k=rsa; p=" . $pub . "\n\nStan: " . (dkim_gotowy() ? 'rekord widoczny w DNS, maile są podpisywane' : 'rekordu jeszcze nie widać w DNS (sprawdzane co godzinę)') . "\n";
    exit;
}

// ---------------------------------------------------------------- Origin
$origin = (string) wez($_SERVER, 'HTTP_ORIGIN', '');
$originOk = $origin !== '' && (preg_match(DOMENY, $origin) || ($DEV !== '' && preg_match('#^http://(localhost|127\.0\.0\.1)(:\d+)?$#', $origin)));
if ($origin !== '' && !$originOk) odpowiedz(false, 403, 'Wiadomość odrzucona.');

// ---------------------------------------------------------------- GET: znacznik czasu
if ($METODA === 'GET' && isset($_GET['znacznik'])) {
    $t = (string) time();
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(array('z' => $t . '.' . substr(hash_hmac('sha256', 'pl|' . $t . '|' . siec(), sekret()), 0, 40)));
    exit;
}
if ($METODA !== 'POST') { header('Allow: GET, POST'); odpowiedz(false, 405, 'Ten adres przyjmuje tylko wiadomości z formularza.'); }
if ((int) wez($_SERVER, 'CONTENT_LENGTH', 0) > 100000) odpowiedz(false, 413, 'Wiadomość jest za długa.');

// ---------------------------------------------------------------- pułapka i znacznik
if (trim((string) wez($_POST, 'strona_www')) !== '') odpowiedz(true, 200, 'Dziękujemy, zapytanie zostało wysłane.');   // robot: udajemy sukces
$z = (string) wez($_POST, '_z');
$teraz = time();
$zOk = false;
if (preg_match('/^(\d{9,11})\.([0-9a-f]{40})$/', $z, $m)) {
    $wiek = $teraz - (int) $m[1];
    $zOk = rowne(substr(hash_hmac('sha256', 'pl|' . $m[1] . '|' . siec(), sekret()), 0, 40), $m[2]) && $wiek >= ZNACZNIK_MIN && $wiek <= ZNACZNIK_MAX;
    if ($zOk) {
        $zOk = z_plikiem('zuzyte.json', function (&$d) use ($z, $teraz) {
            foreach ($d as $k => $t) if ($t < $teraz - ZNACZNIK_MAX) unset($d[$k]);
            $k = sha1($z);
            if (isset($d[$k])) return false;
            $d[$k] = $teraz; return true;
        });
    }
}
if (!$zOk && !$originOk) odpowiedz(false, 403, 'Formularz wysłano zbyt szybko albo strona była otwarta zbyt długo. Prosimy odświeżyć stronę i spróbować ponownie albo zadzwonić: ' . TELEFON . '.');

// ---------------------------------------------------------------- pola formularza
function pole($k, $max) {
    $v = str_replace("\0", '', (string) wez($_POST, $k));
    $v = function_exists('mb_substr') ? mb_substr($v, 0, $max, 'UTF-8') : substr($v, 0, $max * 2);
    return trim($v);
}
function linia($s) { return trim(preg_replace('/[\r\n\t]+/', ' ', $s)); }
$imie = linia(pole('imie', 100));
$email = linia(pole('email', 120));
$tel = linia(pole('telefon', 30));
$zakres = linia(pole('zakres', 60));
$tresc = pole('wiadomosc', 5000);
$ZAKRESY = array('Radiolinie', 'Światłowody', 'Konstrukcje stalowe', 'Utrzymanie i outsourcing', 'Inne');
if (!in_array($zakres, $ZAKRESY, true)) $zakres = 'Inne';
$bledy = array();
if (strlen($imie) < 2) $bledy[] = 'imię i nazwisko lub firma';
if ($email === '' && $tel === '') $bledy[] = 'telefon lub e-mail';
if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) $bledy[] = 'adres e-mail';
if ($tel !== '' && !preg_match('/^[0-9 +()\-\.\/]{7,30}$/', $tel)) $bledy[] = 'numer telefonu';
if (strlen($tresc) < 3) $bledy[] = 'opis zakresu prac';
if (wez($_POST, 'zgoda') !== 'tak') $bledy[] = 'zgoda na przetwarzanie danych';
if (preg_match_all('#https?://#i', $tresc) > 3) $bledy[] = 'opis (za dużo linków)';
if ($bledy) odpowiedz(false, 422, 'Prosimy sprawdzić pola: ' . implode(', ', $bledy) . '.');

// ---------------------------------------------------------------- limity
$ip = hash_hmac('sha256', 'ip|' . siec(), sekret());
$wolno = z_plikiem('ip.json', function (&$d) use ($ip, $teraz) {
    foreach ($d as $k => $l) { $d[$k] = array_values(array_filter((array) $l, function ($t) use ($teraz) { return $t > $teraz - 86400; })); if (!$d[$k]) unset($d[$k]); }
    $moje = isset($d[$ip]) ? $d[$ip] : array();
    $godz = count(array_filter($moje, function ($t) use ($teraz) { return $t > $teraz - 3600; }));
    if ($godz >= LIMIT_H || count($moje) >= LIMIT_D) return false;
    $moje[] = $teraz; $d[$ip] = $moje; return true;
});
if (!$wolno) odpowiedz(false, 429, 'Wysłano już kilka wiadomości. Prosimy spróbować później albo zadzwonić: ' . TELEFON . '.');
$wolnoG = z_plikiem('globalny.json', function (&$d) use ($teraz) {
    $d = array_values(array_filter($d, function ($t) use ($teraz) { return $t > $teraz - 86400; }));
    if (count($d) >= LIMIT_GLOBALNY_D) return false;
    $d[] = $teraz; return true;
});
if (!$wolnoG) odpowiedz(false, 429, 'Formularz jest chwilowo niedostępny. Prosimy zadzwonić: ' . TELEFON . ' albo napisać na ' . ODBIORCA . '.');

// ---------------------------------------------------------------- szata maili (kolory strony)
$F = 'font-family:Arial,Helvetica,sans-serif;';
function szkielet($tytul, $srodek) {
    global $F;
    return '<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>' . h($tytul) . '</title></head>'
        . '<body style="margin:0;padding:0;background:#EEF3F7">'
        . '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#EEF3F7"><tr><td align="center" style="padding:24px 12px">'
        . '<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;background:#ffffff">'
        // nagłówek: granat z logo (jak stopka strony) i błękitna linia "punkt - punkt"
        . '<tr><td style="background:#0E1B3D;padding:16px 28px"><a href="' . ADRES_STRONY . '" style="text-decoration:none"><img src="' . ADRES_STRONY . 'ikony/logo-mail.png" width="203" height="55" alt="ProlinkNET" style="display:block;border:0;' . $F . 'color:#ffffff;font-size:24px;font-weight:bold"></a></td></tr>'
        . '<tr><td style="background:#10BBF1;height:4px;line-height:4px;font-size:0">&nbsp;</td></tr>'
        . $srodek
        . '<tr><td style="padding:18px 28px 24px;border-top:1px solid #D6DEE8;' . $F . 'font-size:13px;line-height:1.6;color:#33415F">'
        . '<strong style="color:#0E1B3D">PROLINKNET Sp. z o.o.</strong> &middot; radiolinie, światłowody, konstrukcje stalowe, utrzymanie sieci<br>ul. Radzymińska 180, 05-205 Stary Kraszew<br>'
        . '<a href="tel:' . TELEFON_LINK . '" style="color:#0E1B3D">' . TELEFON . '</a> &middot; <a href="mailto:' . ODBIORCA . '" style="color:#0E1B3D">' . ODBIORCA . '</a> &middot; '
        . '<a href="' . ADRES_STRONY . '" style="color:#0E1B3D">prolinknet.pl</a></td></tr>'
        . '</table></td></tr></table></body></html>';
}
function wiersz($k, $v) {
    return '<tr><td style="padding:10px 0;border-bottom:1px solid #EEF3F7;width:150px;vertical-align:top;font:bold 14px/1.5 Arial,Helvetica,sans-serif;color:#33415F">' . h($k) . '</td>'
         . '<td style="padding:10px 0;border-bottom:1px solid #EEF3F7;font:15px/1.5 Arial,Helvetica,sans-serif;color:#0E1B3D">' . $v . '</td></tr>';
}
function przycisk($href, $tekst) {
    return '<table role="presentation" cellpadding="0" cellspacing="0" style="margin:16px 0 4px"><tr><td style="background:#10BBF1;border-radius:6px">'
         . '<a href="' . h($href) . '" style="display:inline-block;padding:13px 22px;font:bold 15px/1 Arial,Helvetica,sans-serif;color:#04263A;text-decoration:none">' . h($tekst) . '</a></td></tr></table>';
}

function wyslij_mail($do, $doNazwa, $temat, $html, $tekst, $replyTo = '', $replyNazwa = '', $auto = false) {
    global $DEV;
    require_once __DIR__ . '/inc/Exception.php';
    require_once __DIR__ . '/inc/PHPMailer.php';
    $m = new PHPMailer\PHPMailer\PHPMailer(true);
    try {
        $m->CharSet = 'UTF-8';
        $m->Encoding = 'base64';
        $m->isMail();
        $m->setFrom(NADAWCA, $auto ? FIRMA : NADAWCA_NAZWA, false);
        $m->Sender = NADAWCA;                 // koperta (Return-Path) = nadawca -> SPF
        $m->addAddress($do, $doNazwa);
        if ($replyTo !== '') $m->addReplyTo($replyTo, $replyNazwa);
        $m->Subject = $temat;
        $m->isHTML(true);
        $m->Body = $html;
        $m->AltBody = $tekst;
        $m->XMailer = 'prolinknet-formularz';
        if ($auto) $m->addCustomHeader('Auto-Submitted', 'auto-replied');
        $klucz = dkim_klucz();
        if ($klucz !== '' && ($DEV !== '' || dkim_gotowy())) {
            $m->DKIM_domain = DOMENA;
            $m->DKIM_private = $klucz;
            $m->DKIM_selector = DKIM_SELEKTOR;
            $m->DKIM_identity = NADAWCA;
            $m->DKIM_passphrase = '';
        }
        if ($DEV !== '') {
            if (!is_dir($DEV)) @mkdir($DEV, 0777, true);
            $m->preSend();
            $plik = rtrim($DEV, '/\\') . '/' . date('Ymd-His') . '-' . bin2hex(losowe(3)) . '.eml';
            return (bool) file_put_contents($plik, $m->getSentMIMEMessage());
        }
        return $m->send();
    } catch (Exception $e) {
        error_log('prolinknet formularz: ' . $m->ErrorInfo);
        return false;
    }
}

// ---------------------------------------------------------------- 1) mail do ProlinkNET
$data = date('d.m.Y, H:i');
$zrodlo = (string) wez($_SERVER, 'HTTP_REFERER', '');
if (!preg_match('#^https?://[^\s<>"]+$#', $zrodlo)) $zrodlo = '';
$telHref = preg_replace('/[^0-9+]/', '', $tel);
if ($telHref !== '' && $telHref[0] !== '+' && strlen($telHref) === 9) $telHref = '+48' . $telHref;
$rows = wiersz('Klient', h($imie))
      . wiersz('Telefon', $tel !== '' ? '<a href="tel:' . h($telHref) . '" style="color:#0E1B3D;font-weight:bold">' . h($tel) . '</a>' : '-')
      . wiersz('E-mail', $email !== '' ? '<a href="mailto:' . h($email) . '" style="color:#0E1B3D;font-weight:bold">' . h($email) . '</a>' : '-')
      . wiersz('Zakres prac', '<strong>' . h($zakres) . '</strong>')
      . wiersz('Wysłano', h($data) . ($zrodlo !== '' ? '<br><span style="font-size:13px;color:#5B6780">' . h($zrodlo) . '</span>' : ''));
$srodek = '<tr><td style="padding:24px 28px 4px;font:bold 21px/1.3 Arial,Helvetica,sans-serif;color:#0E1B3D">Nowe zapytanie o realizację: ' . h($zakres) . '</td></tr>'
        . '<tr><td style="padding:6px 28px 4px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">' . $rows . '</table></td></tr>'
        . '<tr><td style="padding:16px 28px 6px;font:bold 14px/1.5 Arial,Helvetica,sans-serif;color:#33415F">Opis: lokalizacja, termin, zakres prac</td></tr>'
        . '<tr><td style="padding:0 28px 22px"><div style="border-left:5px solid #10BBF1;padding:10px 16px;background:#EEF3F7;font:15px/1.6 Arial,Helvetica,sans-serif;color:#0E1B3D">' . nl2br(h($tresc)) . '</div>'
        . ($telHref !== '' ? przycisk('tel:' . $telHref, 'Zadzwoń: ' . $tel) : '')
        . ($email !== '' ? '<p style="margin:14px 0 0;font:13px/1.5 Arial,Helvetica,sans-serif;color:#5B6780">Odpowiedź na tę wiadomość trafi prosto do klienta (' . h($email) . ').</p>' : '')
        . '</td></tr>';
$html = szkielet('Nowe zapytanie o realizację', $srodek);
$tekst = "Nowe zapytanie o realizację ze strony prolinknet.pl\r\n\r\nImię i nazwisko / firma: $imie\r\nTelefon: " . ($tel !== '' ? $tel : '-') . "\r\nE-mail: " . ($email !== '' ? $email : '-')
       . "\r\nZakres prac: $zakres\r\nWysłano: $data\r\n\r\nOpis:\r\n" . $tresc . "\r\n";
if (!wyslij_mail(ODBIORCA, FIRMA, 'Zapytanie ze strony: ' . $zakres . ' - ' . $imie, $html, $tekst, $email, $imie)) {
    odpowiedz(false, 500, 'Nie udało się wysłać zapytania. Prosimy zadzwonić: ' . TELEFON . ' albo napisać na ' . ODBIORCA . '.');
}

// ---------------------------------------------------------------- 2) potwierdzenie dla klienta
if ($email !== '' && ($zOk || $DEV !== '')) {
    $adr = hash_hmac('sha256', 'mail|' . strtolower($email), sekret());
    $mozna = z_plikiem('potwierdzenia.json', function (&$d) use ($adr, $teraz) {
        foreach ($d as $k => $t) if ($k !== '_h' && $t < $teraz - 86400) unset($d[$k]);
        $hh = isset($d['_h']) ? array_values(array_filter((array) $d['_h'], function ($t) use ($teraz) { return $t > $teraz - 3600; })) : array();
        if (isset($d[$adr]) || count($hh) >= LIMIT_POTW_H) { $d['_h'] = $hh; return false; }
        $d[$adr] = $teraz; $hh[] = $teraz; $d['_h'] = $hh; return true;
    });
    if ($mozna) {
        $s2 = '<tr><td style="padding:24px 28px 4px;font:bold 21px/1.3 Arial,Helvetica,sans-serif;color:#0E1B3D">Dziękujemy za zapytanie</td></tr>'
            . '<tr><td style="padding:8px 28px 6px;font:15px/1.6 Arial,Helvetica,sans-serif;color:#0E1B3D">'
            . '<p style="margin:0 0 12px">Dzień dobry,<br>otrzymaliśmy zapytanie wysłane przez formularz na stronie prolinknet.pl. Zapoznamy się z opisem i odpowiemy najszybciej, jak to możliwe.</p></td></tr>'
            . '<tr><td style="padding:0 28px 8px"><div style="border-left:5px solid #10BBF1;padding:12px 16px;background:#EEF3F7;font:15px/1.6 Arial,Helvetica,sans-serif;color:#0E1B3D">'
            . '<strong>Zakres prac:</strong> ' . h($zakres) . '<br><strong>Opis:</strong> ' . nl2br(h(function_exists('mb_strimwidth') ? mb_strimwidth($tresc, 0, 600, '...', 'UTF-8') : $tresc)) . '</div>'
            . '<p style="margin:14px 0 0;font:15px/1.6 Arial,Helvetica,sans-serif;color:#0E1B3D">W pilnej sprawie prosimy dzwonić: <a href="tel:' . TELEFON_LINK . '" style="color:#0E1B3D;font-weight:bold">' . TELEFON . '</a>.</p></td></tr>'
            . '<tr><td style="padding:4px 28px 24px">' . przycisk(ADRES_STRONY . '#oferta', 'Zakres naszych usług') . '</td></tr>';
        $h2 = szkielet('Dziękujemy za zapytanie', $s2);
        $t2 = "Dziękujemy za zapytanie.\r\n\r\nOtrzymaliśmy zapytanie wysłane przez formularz na stronie prolinknet.pl. Zapoznamy się z opisem i odpowiemy najszybciej, jak to możliwe.\r\n\r\n"
            . "Zakres prac: $zakres\r\nW pilnej sprawie prosimy dzwonić: " . TELEFON . ".\r\n\r\nPROLINKNET Sp. z o.o., ul. Radzymińska 180, 05-205 Stary Kraszew\r\n" . ADRES_STRONY . "\r\n";
        wyslij_mail($email, $imie, 'ProlinkNET: otrzymaliśmy Twoje zapytanie', $h2, $t2, ODBIORCA, FIRMA, true);
    }
}
odpowiedz(true, 200, 'Dziękujemy, zapytanie zostało wysłane. Odpowiemy najszybciej, jak to możliwe. Na podany e-mail wysłaliśmy potwierdzenie - jeśli go nie widać, prosimy zajrzeć do folderu Spam (Oferty, Inne).');
