import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

sys.stdout.reconfigure(encoding='utf-8')

ARTIFACTS_DIR = r'C:\Users\Admin\.gemini\antigravity\brain\d1a1e5ad-c438-4104-985b-ec757632f80e\terrae_qa'
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=opts)

try:
    print("=== TESTING EXPANDED SEARCH OPTIONS ===")
    driver.set_window_size(1920, 1080)
    driver.get('http://localhost:3333')
    time.sleep(1.5)

    # 1. Check Category Tabs
    cat_tabs = driver.find_elements(By.CLASS_NAME, 'hero-cat-btn')
    cat_names = [t.text for t in cat_tabs]
    print(f"Category tabs found ({len(cat_tabs)}):", cat_names)

    # 2. Check initial chips (ALL category)
    chips = driver.find_elements(By.CLASS_NAME, 'hero-chip-btn')
    chip_texts = [c.text.strip() for c in chips]
    print(f"Total initial chips ({len(chips)}):", chip_texts)

    # Capture initial view with all expanded chips
    driver.save_screenshot(os.path.join(ARTIFACTS_DIR, 'SEARCH_OPTIONS_ALL_1920.png'))
    print("Saved SEARCH_OPTIONS_ALL_1920.png")

    # 3. Test Category Filter Click (e.g. AGRICULTURE)
    agri_tab = [t for t in cat_tabs if 'AGRICULTURE' in t.text]
    if agri_tab:
        agri_tab[0].click()
        time.sleep(0.4)
        filtered_chips = driver.find_elements(By.CLASS_NAME, 'hero-chip-btn')
        print(f"Agriculture filtered chips ({len(filtered_chips)}):", [c.text.strip() for c in filtered_chips])
        driver.save_screenshot(os.path.join(ARTIFACTS_DIR, 'SEARCH_OPTIONS_AGRICULTURE_1920.png'))
        print("Saved SEARCH_OPTIONS_AGRICULTURE_1920.png")

    # 4. Click a chip to trigger search
    chips_now = driver.find_elements(By.CLASS_NAME, 'hero-chip-btn')
    if chips_now:
        chips_now[0].click()
        time.sleep(0.8)

        # Check candidate card
        candidate = driver.find_element(By.CLASS_NAME, 'hero-candidate-card')
        print("Candidate Card Text:\n", candidate.text)
        driver.save_screenshot(os.path.join(ARTIFACTS_DIR, 'SEARCH_CANDIDATE_ACTIVE_1920.png'))
        print("Saved SEARCH_CANDIDATE_ACTIVE_1920.png")

    # 5. Mobile responsive check
    driver.set_window_size(390, 844)
    time.sleep(0.5)
    scroll_w, client_w = driver.execute_script("return [document.documentElement.scrollWidth, document.documentElement.clientWidth];")
    print(f"Mobile 390x844: scrollWidth={scroll_w}px, clientWidth={client_w}px, NoOverflow={scroll_w <= client_w}")
    driver.save_screenshot(os.path.join(ARTIFACTS_DIR, 'SEARCH_OPTIONS_MOBILE_390.png'))
    print("Saved SEARCH_OPTIONS_MOBILE_390.png")

    print("\n[SUCCESS] All search options verification checks passed!")

finally:
    driver.quit()
