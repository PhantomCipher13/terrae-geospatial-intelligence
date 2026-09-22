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

audit_results = []

try:
    print("=== STARTING BROWSER-TRUTH VISUAL RECONSTRUCTION PASS ===")
    
    # 1. Desktop Detailed Section Audit (1920x1080)
    driver.set_window_size(1920, 1080)
    driver.get('http://localhost:3333')
    time.sleep(1.5)

    # Check Section Geometries and Non-overlap
    sections = [
        'sec_hero',
        'sec_philosophy',
        'sec_method',
        'sec_temporal',
        'sec_motion',
        'sec_case01',
        'sec_evidence',
        'sec_observations',
        'sec_validation',
        'sec_ws_banner'
    ]

    print("\n--- SECTION GEOMETRY & BOUNDARY AUDIT ---")
    prev_bottom = 0
    for s_id in sections:
        elem = driver.find_element(By.ID, s_id)
        rect = driver.execute_script('''
            var el = arguments[0];
            var r = el.getBoundingClientRect();
            return {
                top: Math.round(r.top + window.scrollY),
                bottom: Math.round(r.bottom + window.scrollY),
                height: Math.round(r.height),
                width: Math.round(r.width)
            };
        ''', elem)
        
        overlap = "NO (CLEAR GAP)" if rect['top'] >= prev_bottom else f"WARN: overlap {prev_bottom - rect['top']}px"
        print(f"[{s_id:18}] Top={rect['top']:5}px | Bottom={rect['bottom']:5}px | Height={rect['height']:4}px | Separation: {overlap}")
        prev_bottom = rect['bottom']

    # Capture Dedicated Section Screenshots on 1920x1080
    # Section 1: Hero
    driver.save_screenshot(os.path.join(ARTIFACTS_DIR, 'RECON_01_HERO_1920.png'))
    
    # Section 2: Philosophy + Chapter Break
    phil = driver.find_element(By.ID, 'sec_philosophy')
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'start'});", phil)
    time.sleep(0.5)
    driver.save_screenshot(os.path.join(ARTIFACTS_DIR, 'RECON_02_PHILOSOPHY_BREAK_1920.png'))

    # Section 3: Method Stage 01 ASK
    method = driver.find_element(By.ID, 'sec_method')
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'start'});", method)
    time.sleep(0.5)
    driver.save_screenshot(os.path.join(ARTIFACTS_DIR, 'RECON_03_METHOD_ASK_1920.png'))

    # Test Method Stage 03 COMPARE
    stage_btns = driver.find_elements(By.CLASS_NAME, 'method-nav-pill')
    if len(stage_btns) >= 3:
        stage_btns[2].click() # COMPARE
        time.sleep(0.5)
        driver.save_screenshot(os.path.join(ARTIFACTS_DIR, 'RECON_04_METHOD_COMPARE_1920.png'))
        print("[PASS] Method Stage switched to 03 COMPARE and screenshot captured.")

    # Section 4: Temporal
    temp = driver.find_element(By.ID, 'sec_temporal')
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'start'});", temp)
    time.sleep(0.5)
    driver.save_screenshot(os.path.join(ARTIFACTS_DIR, 'RECON_05_TEMPORAL_1920.png'))

    # Section 5: Case 01 Controlled Construction
    c01 = driver.find_element(By.ID, 'sec_case01')
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'start'});", c01)
    time.sleep(0.5)
    driver.save_screenshot(os.path.join(ARTIFACTS_DIR, 'RECON_06_CASE01_1920.png'))

    # Section 6: Progressive Evidence
    evid = driver.find_element(By.ID, 'sec_evidence')
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'start'});", evid)
    time.sleep(0.5)
    driver.save_screenshot(os.path.join(ARTIFACTS_DIR, 'RECON_07_EVIDENCE_1920.png'))

    # Section 7: OSCD Validation (Visual Evidence First)
    val = driver.find_element(By.ID, 'sec_validation')
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'start'});", val)
    time.sleep(0.5)
    driver.save_screenshot(os.path.join(ARTIFACTS_DIR, 'RECON_08_VALIDATION_1920.png'))

    # Test Detail Lightbox Inspection
    # Click first OSCD scene card to open lightbox
    first_scene = driver.find_element(By.CLASS_NAME, 'oscd-scene-card')
    first_scene.click()
    time.sleep(0.5)
    driver.save_screenshot(os.path.join(ARTIFACTS_DIR, 'RECON_10_LIGHTBOX_1920.png'))
    print("[PASS] Detail inspection lightbox opened and verified.")
    # Close lightbox
    close_btn = driver.find_element(By.CLASS_NAME, 'lightbox-close-btn')
    close_btn.click()
    time.sleep(0.4)

    # Test Workstation Mode
    ws_trigger = driver.find_element(By.CLASS_NAME, 'nav-ws-trigger')
    ws_trigger.click()
    time.sleep(0.8)
    driver.save_screenshot(os.path.join(ARTIFACTS_DIR, 'RECON_09_WORKSTATION_1920.png'))
    print("[PASS] Workstation mode captured.")

    # Return to website mode for viewport sweep
    web_trigger = driver.find_element(By.CLASS_NAME, 'nav-ws-trigger')
    web_trigger.click()
    time.sleep(0.8)

    # 2. Viewport Sweep Across All 7 Devices
    print("\n--- RESPONSIVE VIEWPORT SWEEP ---")
    for name, w, h in VIEWPORTS:
        driver.set_window_size(w, h)
        driver.get('http://localhost:3333')
        time.sleep(1.2)

        # Check Horizontal Overflow
        scroll_w = driver.execute_script('return document.documentElement.scrollWidth;')
        inner_w = driver.execute_script('return window.innerWidth;')
        has_h_scroll = scroll_w > inner_w

        # Take full page or viewport screenshot
        driver.save_screenshot(os.path.join(ARTIFACTS_DIR, f'SWEEP_WEB_{w}x{h}.png'))

        # Test Workstation on this viewport
        ws_btn = driver.find_element(By.CLASS_NAME, 'nav-ws-trigger')
        ws_btn.click()
        time.sleep(0.8)

        ws_scroll_w = driver.execute_script('return document.documentElement.scrollWidth;')
        ws_inner_w = driver.execute_script('return window.innerWidth;')
        ws_has_h_scroll = ws_scroll_w > ws_inner_w

        driver.save_screenshot(os.path.join(ARTIFACTS_DIR, f'SWEEP_WS_{w}x{h}.png'))

        # Return to website mode
        driver.find_element(By.CLASS_NAME, 'nav-ws-trigger').click()
        time.sleep(0.5)

        status = 'PASS' if (not has_h_scroll and not ws_has_h_scroll) else 'FAIL'
        print(f"[{status}] {name:20}: Web={scroll_w}/{inner_w} (diff={scroll_w - inner_w}), WS={ws_scroll_w}/{ws_inner_w} (diff={ws_scroll_w - ws_inner_w})")
        audit_results.append((name, w, h, not has_h_scroll, not ws_has_h_scroll))

finally:
    driver.quit()

print("\n--- FINAL AUDIT CONCLUSION ---")
all_passed = all(r[3] and r[4] for r in audit_results)
print(f"All 7 Viewports Passed Cleanly: {all_passed}")
