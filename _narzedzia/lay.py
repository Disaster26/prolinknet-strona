import sys
from playwright.sync_api import sync_playwright
url=sys.argv[1]; hide=sys.argv[2:] 
with sync_playwright() as p:
    b=p.chromium.launch(channel='chrome'); c=b.new_context(viewport={'width':412,'height':823},is_mobile=True,device_scale_factor=1.75)
    pg=c.new_page(); s=c.new_cdp_session(pg); s.send('Performance.enable'); s.send('Emulation.setCPUThrottlingRate',{'rate':4})
    if hide: pg.add_init_script("document.addEventListener('DOMContentLoaded',()=>{%s})"%''.join("document.querySelectorAll('%s').forEach(e=>e.remove());"%h for h in hide))
    pg.goto(url,wait_until='networkidle'); pg.wait_for_timeout(1500)
    m={x['name']:x['value'] for x in s.send('Performance.getMetrics')['metrics']}
    print(hide or 'pelna', 'Layout %.0fms x%d  Style %.0fms  nodes %d'%(m['LayoutDuration']*1000,m['LayoutCount'],m['RecalcStyleDuration']*1000,m['Nodes']))
    b.close()
