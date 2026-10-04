"""tools/logo_nasu.html をブラウザで描いて assets/img/logo_nasu.png に書き出す（2倍の解像度）。
使い方：python tools/make_logo.py（Playwright と Chromium が要る。フォントは Google Fonts から読む）"""
import os
from playwright.sync_api import sync_playwright
here=os.path.dirname(os.path.abspath(__file__))
with sync_playwright() as p:
    b=p.chromium.launch()
    pg=b.new_page(device_scale_factor=2)
    pg.goto('file:///'+os.path.join(here,'logo_nasu.html').replace('\\','/'))
    pg.evaluate('document.fonts.ready');pg.wait_for_timeout(1500)
    pg.locator('#logo').screenshot(path=os.path.join(here,'..','assets','img','logo_nasu.png'),omit_background=True)
    b.close()
print('ok')
