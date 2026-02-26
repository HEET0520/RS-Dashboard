"""
Advanced Website Inspector - Deep inspection of NIFTY website structure
Run this to discover actual element selectors and HTML structure
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

def deep_inspect_website():
    """Deep inspect the website structure and save results"""
    
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("Opening NIFTY website...")
        driver.get("https://www.niftyindices.com/reports/historical-data")
        time.sleep(5)  # Give page time to fully load
        
        print("\n" + "="*80)
        print("ADVANCED ELEMENT INSPECTION")
        print("="*80)
        
        # Get page source analysis
        print("\n1. PAGE STRUCTURE ANALYSIS:")
        page_source = driver.page_source
        
        # Find all form elements
        print("\n   A. ALL SELECT ELEMENTS:")
        selects = driver.find_elements(By.TAG_NAME, "select")
        print(f"      Found {len(selects)} select elements:")
        for idx, select in enumerate(selects):
            try:
                select_id = select.get_attribute("id")
                select_name = select.get_attribute("name")
                select_class = select.get_attribute("class")
                options_count = len(select.find_elements(By.TAG_NAME, "option"))
                print(f"      [{idx}] ID: {select_id} | Name: {select_name} | Class: {select_class} | Options: {options_count}")
            except Exception as e:
                print(f"      [{idx}] Error: {e}")
        
        print("\n   B. ALL INPUT ELEMENTS:")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"      Found {len(inputs)} input elements:")
        for idx, input_elem in enumerate(inputs):
            try:
                input_type = input_elem.get_attribute("type")
                input_id = input_elem.get_attribute("id")
                input_name = input_elem.get_attribute("name")
                input_placeholder = input_elem.get_attribute("placeholder")
                input_class = input_elem.get_attribute("class")
                print(f"      [{idx}] Type: {input_type} | ID: {input_id} | Name: {input_name} | Placeholder: {input_placeholder} | Class: {input_class}")
            except Exception as e:
                print(f"      [{idx}] Error: {e}")
        
        print("\n   C. ALL BUTTON ELEMENTS:")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"      Found {len(buttons)} button elements:")
        for idx, button in enumerate(buttons):
            try:
                btn_text = button.text
                btn_id = button.get_attribute("id")
                btn_name = button.get_attribute("name")
                btn_class = button.get_attribute("class")
                btn_type = button.get_attribute("type")
                print(f"      [{idx}] Text: '{btn_text}' | ID: {btn_id} | Name: {btn_name} | Type: {btn_type} | Class: {btn_class}")
            except Exception as e:
                print(f"      [{idx}] Error: {e}")
        
        print("\n   D. DIVS WITH SPECIFIC ROLES/CLASSES:")
        divs = driver.find_elements(By.TAG_NAME, "div")
        print(f"      Total DIVs found: {len(divs)}")
        important_divs = []
        for div in divs:
            role = div.get_attribute("role")
            class_attr = div.get_attribute("class")
            if role or (class_attr and any(x in class_attr.lower() for x in ['date', 'picker', 'calendar', 'select', 'dropdown', 'form', 'index'])):
                important_divs.append({
                    'role': role,
                    'class': class_attr,
                    'text': div.text[:50] if div.text else ''
                })
        
        if important_divs:
            print(f"      Found {len(important_divs)} important DIVs:")
            for idx, div_info in enumerate(important_divs):
                print(f"      [{idx}] Role: {div_info['role']} | Class: {div_info['class']} | Text: {div_info['text']}")
        
        # Try to interact with dropdowns
        print("\n2. DROPDOWN ANALYSIS:")
        if selects:
            print(f"\n   First SELECT element details:")
            first_select = selects[0]
            options = first_select.find_elements(By.TAG_NAME, "option")
            print(f"   - Total options: {len(options)}")
            print(f"   - Options list (first 5):")
            for idx, opt in enumerate(options[:5]):
                print(f"     [{idx}] {opt.text} (value: {opt.get_attribute('value')})")
        
        # Look for any visible form containers
        print("\n3. FORM ELEMENTS AND CONTAINERS:")
        forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"   Found {len(forms)} form elements")
        
        # Look for labels which might indicate field purposes
        labels = driver.find_elements(By.TAG_NAME, "label")
        print(f"   Found {len(labels)} label elements:")
        for idx, label in enumerate(labels[:10]):
            print(f"   [{idx}] {label.text}")
        
        # Inspect all clickable elements
        print("\n4. CLICKABLE ELEMENTS (buttons, links with onclick, etc):")
        clickables = driver.find_elements(By.XPATH, "//*[@onclick or self::button or self::a[@href]]")
        print(f"   Found {len(clickables)} clickable elements")
        print(f"   First 10 clickables:")
        for idx, elem in enumerate(clickables[:10]):
            try:
                text = elem.text
                elem_type = elem.tag_name
                onclick = elem.get_attribute("onclick")
                href = elem.get_attribute("href")
                print(f"   [{idx}] Type: {elem_type} | Text: '{text}' | OnClick: {onclick[:50] if onclick else 'None'} | Href: {href}")
            except:
                pass
        
        # Save full HTML to file for manual inspection
        print("\n5. SAVING PAGE DATA FOR MANUAL INSPECTION...")
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print("   ✓ Saved: page_source.html")
        
        # Take screenshot
        driver.save_screenshot("page_screenshot.png")
        print("   ✓ Saved: page_screenshot.png")
        
        # Get all visible text
        visible_text = driver.find_element(By.TAG_NAME, "body").text
        with open("page_text.txt", "w", encoding="utf-8") as f:
            f.write(visible_text)
        print("   ✓ Saved: page_text.txt")
        
        print("\n" + "="*80)
        print("INSPECTION COMPLETE")
        print("="*80)
        print("\nFiles saved for analysis:")
        print("  1. page_source.html - Full HTML source")
        print("  2. page_screenshot.png - Screenshot of page")
        print("  3. page_text.txt - All visible text")
        print("\nBrowser will stay open for 30 seconds for manual inspection...")
        print("Use Developer Tools (F12) to inspect elements manually.")
        
        time.sleep(30)
        
    except Exception as e:
        print(f"Error during inspection: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("\nBrowser closed.")

if __name__ == "__main__":
    deep_inspect_website()
