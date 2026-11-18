#!/bin/bash
# użycie: lh.sh URL nazwa [desktop]
URL=$1; N=$2; FF=mobile; EXTRA="--form-factor=mobile"
if [ "$3" = "desktop" ]; then FF=desktop; EXTRA="--preset=desktop"; fi
cd /c/Users/Admin/Downloads/Prolinknet_strona/_lh
PROF="C:\Users\Admin\AppData\Local\Temp\lighthouse.prolink$$"
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu --disable-renderer-backgrounding --disable-backgrounding-occluded-windows \
  --remote-debugging-port=9334 --user-data-dir="$PROF" --no-first-run --no-default-browser-check about:blank >/dev/null 2>&1 &
sleep 3
npx -y lighthouse@12 "$URL" --port=9334 --quiet --output=json --output-path="$N-$FF.json" $EXTRA >/dev/null 2>&1
powershell.exe -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | Where-Object { \$_.CommandLine -match 'lighthouse.prolink' } | ForEach-Object { Stop-Process -Id \$_.ProcessId -Force -ErrorAction SilentlyContinue }" 2>/dev/null
sleep 1
python -I -c "
import json
d=json.load(open('$N-$FF.json',encoding='utf-8'))
c=d['categories']; a=d['audits']
print('$N $FF', {k:round(v['score']*100) for k,v in c.items()}, 'FCP',a['first-contentful-paint']['displayValue'],'LCP',a['largest-contentful-paint']['displayValue'],'SI',a['speed-index']['displayValue'],'TBT',a['total-blocking-time']['displayValue'],'CLS',a['cumulative-layout-shift']['displayValue'])
for k,v in a.items():
    if v.get('score') is not None and v['score']<0.9 and v.get('scoreDisplayMode') in ('binary','numeric','metricSavings'): print('   ',k,v['score'],v.get('displayValue',''))
"
