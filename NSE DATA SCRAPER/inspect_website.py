"""
Website Inspector - Debug script to inspect NIFTY website structure
Run this to find the correct element selectors
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def inspect_website():
    """Inspect the website structure"""
    
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("Opening NIFTY website...")
        driver.get("https://www.niftyindices.com/reports/historical-data")
        time.sleep(3)
        
        print("\n" + "="*70)
        print("ELEMENT INSPECTION RESULTS")
        print("="*70)
        
        # Inspect dropdowns
        print("\n1. INDEX TYPE DROPDOWN:")
        try:
            index_type = driver.find_element(By.ID, "selectIndexType")
            print(f"   ✓ Found: selectIndexType")
            print(f"   Tag: {index_type.tag_name}")
        except:
            print("   ✗ Not found with ID 'selectIndexType'")
        
        print("\n2. SUB-INDEX TYPE DROPDOWN:")
        try:
            sub_index = driver.find_element(By.ID, "selectSubIndexType")
            print(f"   ✓ Found: selectSubIndexType")
            print(f"   Tag: {sub_index.tag_name}")
        except:
            print("   ✗ Not found with ID 'selectSubIndexType'")
        
        print("\n3. INDEX DROPDOWN:")
        try:
            index = driver.find_element(By.ID, "selectIndex")
            print(f"   ✓ Found: selectIndex")
            print(f"   Tag: {index.tag_name}")
        except:
            print("   ✗ Not found with ID 'selectIndex'")
        
        # Inspect date fields
        print("\n4. DATE FIELDS:")
        try:
            start_date = driver.find_element(By.XPATH, "//input[@placeholder='Start Date']")
            print(f"   ✓ Found start date input")
            print(f"   Type: {start_date.get_attribute('type')}")
            print(f"   Placeholder: {start_date.get_attribute('placeholder')}")
        except:
            print("   ✗ Not found with Start Date placeholder")
        
        try:
            end_date = driver.find_element(By.XPATH, "//input[@placeholder='End Date']")
            print(f"   ✓ Found end date input")
            print(f"   Type: {end_date.get_attribute('type')}")
            print(f"   Placeholder: {end_date.get_attribute('placeholder')}")
        except:
            print("   ✗ Not found with End Date placeholder")
        
        # Inspect submit button
        print("\n5. SUBMIT BUTTON:")
        try:
            submit = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
            print(f"   ✓ Found submit button")
            print(f"   Text: {submit.text}")
        except:
            print("   ✗ Not found with 'Submit' text")
        
        # Inspect calendar when opened
        print("\n6. CALENDAR PICKER (if visible):")
        try:
            start_input = driver.find_element(By.XPATH, "//input[@placeholder='Start Date']")
            start_input.click()
            time.sleep(1)
            
            # Look for month selector
            try:
                month_dropdown = driver.find_element(By.XPATH, "//select[contains(@class, 'month')]")
                print(f"   ✓ Found month dropdown with class 'month'")
            except:
                try:
                    month_dropdown = driver.find_element(By.TAG_NAME, "select")
                    print(f"   ✓ Found select element (might be month/year selector)")
                except:
                    print(f"   ✗ Could not find month dropdown")
            
            # Look for day buttons
            try:
                days = driver.find_elements(By.XPATH, "//td[contains(@class, 'day')]")
                print(f"   ✓ Found {len(days)} day elements with class 'day'")
                if len(days) > 0:
                    print(f"     Sample: {days[0].text}")
            except:
                try:
                    days = driver.find_elements(By.XPATH, "//td")
                    if days:
                        print(f"   ✓ Found {len(days)} td elements (might include days)")
                except:
                    print(f"   ✗ Could not find day elements")
        
        except Exception as e:
            print(f"   Error inspecting calendar: {e}")
        
        # Inspect results table
        print("\n7. RESULTS TABLE:")
        try:
            table = driver.find_element(By.XPATH, "//table")
            print(f"   ✓ Found table")
            
            rows = table.find_elements(By.XPATH, ".//tbody/tr")
            print(f"   ✓ Found {len(rows)} rows in tbody")
            
            if len(rows) > 0:
                cells = rows[0].find_elements(By.TAG_NAME, "td")
                print(f"   ✓ First row has {len(cells)} columns")
                print(f"     Columns: {[cell.text for cell in cells]}")
        except:
            print("   ✗ Could not find table")
        
        # Inspect CSV download link
        print("\n8. CSV DOWNLOAD:")
        try:
            csv_link = driver.find_element(By.XPATH, "//a[contains(text(), 'csv format')]")
            print(f"   ✓ Found CSV download link")
            print(f"   Text: {csv_link.text}")
        except:
            try:
                csv_link = driver.find_element(By.XPATH, "//a[contains(text(), 'csv')]")
                print(f"   ✓ Found CSV link (partial match)")
            except:
                print("   ✗ Could not find CSV download link")
        
        print("\n" + "="*70)
        print("INSPECTION COMPLETE")
        print("="*70)
        print("\nNow manually interact with the page to verify elements...")
        print("Browser will stay open for 60 seconds. Check the page structure.")
        print("Press Ctrl+Shift+I to open Developer Tools and inspect elements.")
        
        time.sleep(60)
        
    except Exception as e:
        print(f"Error during inspection: {e}")
    finally:
        driver.quit()
        print("\nBrowser closed.")

if __name__ == "__main__":
    inspect_website()
