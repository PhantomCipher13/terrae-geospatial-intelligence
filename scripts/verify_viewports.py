import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

sys.stdout.reconfigure(encoding='utf-8')

VIEWPORTS = [
    ('Desktop 1920x1080', 1920, 1080),
    ('Desktop 1536x864', 1536, 864),
    ('Desktop 1366x768', 1366, 768),
    ('Tablet 768x1024', 768, 1024),
    ('Mobile 430x932', 430, 932),
    ('Mobile 390x844', 390, 844),
    ('Mobile 375x812', 375, 812),
]

ARTIFACTS_DIR = r'C:\Users\Admin\.gemini\antigravity\brain\d1a1e5ad-c438-4104-985b-ec757632f80e\terrae_qa'
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=opts)

results = []

try:
    for name, w, h in VIEWPORTS:
        driver.set_window_size(w, h)
        driver.get('http://localhost:3333')
        time.sleep(1.2)
        
        # Test Website Mode
        scroll_w = driver.execute_script('return document.documentElement.scrollWidth;')
        inner_w = driver.execute_script('return window.innerWidth;')
        has_h_scroll = driver.execute_script(
            'return document.documentElement.scrollWidth > window.innerWidth;'
        )
        
        # Find any overflowing elements
        overflowing_elements = driver.execute_script('''
            var docWidth = window.innerWidth;
            var elems = document.querySelectorAll('*');
            var over = [];
            for (var i = 0; i < elems.length; i++) {
                var r = elems[i].getBoundingClientRect();
                if (r.right > docWidth + 1) { // 1px threshold for sub-pixel anti-aliasing
                    over.push({
                        tag: elems[i].tagName,
                        className: elems[i].className,
                        id: elems[i].id,
                        right: Math.round(r.right),
                        width: Math.round(r.width)
                    });
                }
            }
            return over.slice(0, 5);
        ''')
        
        # Check slider handle size in website mode
        slider_handle = driver.execute_script('''
            var h = document.querySelector('#baDivider > div');
            if (h) {
                var r = h.getBoundingClientRect();
                return { width: Math.round(r.width), height: Math.round(r.height) };
            }
            return null;
        ''')

        # Take screenshot in Website Mode
        shot_path_web = os.path.join(ARTIFACTS_DIR, f'WEB_{w}x{h}.png')
        driver.save_screenshot(shot_path_web)

        # Test Workstation Mode
        ws_btn = driver.find_element(By.CLASS_NAME, 'nav-ws-trigger')
        ws_btn.click()
        time.sleep(0.8)

        ws_scroll_w = driver.execute_script('return document.documentElement.scrollWidth;')
        ws_inner_w = driver.execute_script('return window.innerWidth;')
        ws_has_h_scroll = driver.execute_script(
            'return document.documentElement.scrollWidth > window.innerWidth;'
        )

        shot_path_ws = os.path.join(ARTIFACTS_DIR, f'WS_{w}x{h}.png')
        driver.save_screenshot(shot_path_ws)

        res = {
            'viewport': name,
            'w': w,
            'h': h,
            'web_scroll_w': scroll_w,
            'web_inner_w': inner_w,
            'web_overflow': scroll_w - inner_w,
            'web_has_h_scroll': has_h_scroll,
            'ws_scroll_w': ws_scroll_w,
            'ws_inner_w': ws_inner_w,
            'ws_overflow': ws_scroll_w - ws_inner_w,
            'ws_has_h_scroll': ws_has_h_scroll,
            'overflowing_elements': overflowing_elements,
            'slider_handle': slider_handle,
        }
        results.append(res)
        
        status = 'PASS' if (not has_h_scroll and not ws_has_h_scroll) else 'FAIL'
        print(f"[{status}] {name}: Web scrollWidth={scroll_w}/{inner_w} (diff={scroll_w - inner_w}), WS scrollWidth={ws_scroll_w}/{ws_inner_w} (diff={ws_scroll_w - ws_inner_w})")
        if overflowing_elements:
            print(f"    Overflowing elements: {overflowing_elements}")
        if slider_handle:
            print(f"    Slider handle size: {slider_handle['width']}x{slider_handle['height']}px")

finally:
    driver.quit()

print("\n--- SUMMARY OF BROWSER-TRUTH AUDIT ---")
all_passed = all(not r['web_has_h_scroll'] and not r['ws_has_h_scroll'] for r in results)
print(f"All 7 Viewports Passed Invariant: {all_passed}")
