from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random

def setup_undetectable_chrome(headless: bool = True):
    """Configure Chrome to be as undetectable as possible.

    Args:
        headless (bool): Run browser in headless mode (recommended for servers/containers).

    Returns:
        selenium.webdriver.Chrome: Configured Chrome driver.
    """
    import tempfile  # Local import so that the module is only needed when the function is called

    options = Options()

    # Headless mode to avoid opening a visible window and to prevent profile-lock issues
    if headless:
        # The "new" headless mode is preferred for Chrome >= 109, but the classic flag
        # is still accepted by older versions – passing both does not hurt.
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    # Disable automated browser notifications
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Realistic User-Agent
    options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Disable detection features
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")

    # Simulate a regular browser
    options.add_argument('--lang=fr-FR')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    
    driver = webdriver.Chrome(options=options)
    
    # Hide Selenium properties using JavaScript
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['fr-FR', 'fr']})")
    
    return driver

def human_wait(min_sec=0.5, max_sec=1.5):
    time.sleep(random.uniform(min_sec, max_sec))

def human_type(element, text):
    """Type text in a human-like manner"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))

def check_payment_result(driver, timeout=5):
    """
    Checks the payment result - SIMPLE: True or False
    
    Returns:
        bool: True on success, False on failure
    """
    try:
        wait = WebDriverWait(driver, timeout)
        
        # Specifically wait for the success text "تم إعادة الشحن بنجاح"
        success_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'تم إعادة الشحن بنجاح')]"))
        )
        
        print("✅ PAIEMENT RÉUSSI!")
        return True
            
    except Exception as e:
        print("❌ ÉCHEC DU PAIEMENT")
        return False

def yalla_pay_recharge(amount, itemType, playerId, pinCode):
    """
    Performs a recharge on YallaPay
    
    Args:
        amount (int): Amount in USD (5, 10, 25, etc.)
        itemType (str): Recharge type ("diamonds" or "golds")
        playerId (str): User ID
        pinCode (str): PIN code
        
    Returns:
        bool: True on success, False on failure
    """
    print(f"Recharging {amount} {itemType} for player {playerId} with pin {pinCode}")
    
    # time.sleep(5)
    # return bool(amount % 2)
    
    driver = setup_undetectable_chrome()
    
    try:
        driver.get('https://www.yallapay.live/recharge?fAppType=20')
        
        # Wait a bit for the page to fully load
        human_wait(2, 4)

        try:
            close_cookie = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".close.cookie-close-rtl"))
            )
            close_cookie.click()
        except:
            pass

        human_wait()

        # ID input field with human typing
        champ = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'checkUserInput'))
        )
        
        human_type(champ, playerId)
        human_wait()

        # OK button
        ok_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(@class, 'actionbtn') and .//span[text()='حسناً']]")
            )
        )
        driver.execute_script("arguments[0].click();", ok_btn)
        human_wait()

        # Gift button
        gift_btn = driver.find_element(
            By.XPATH,
            "//div[contains(@class, 'cursor-pointer') and .//p[text()='بطاقة الهدية']]"
        )
        driver.execute_script("arguments[0].click();", gift_btn)
        human_wait()

        # Choose 'diamonds' or 'golds'
        if itemType == "diamonds":
            btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//section[.//span[contains(text(), 'الماس ')]]"))
            )
            driver.execute_script("arguments[0].click();", btn)
        else:
            btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'قطع ذهبية ') and not(contains(@class, 'pointer-events-none'))]"))
            )
            driver.execute_script("arguments[0].click();", btn)

        human_wait(3, 6)

        # Select USD amount
        btn_usd = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//p[contains(text(), 'USD {amount}')]")
            )
        )
        btn_usd.click()
        human_wait()

        # Enter PIN with human typing
        pin_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pincodeTarget"))
        )
        human_type(pin_input, pinCode)
        human_wait()

        # Scroll and pay
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        human_wait()

        pay_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(@class, 'actionbtn') and .//span[text()='الدفع الان']]")
            )
        )
        driver.execute_script("arguments[0].click();", pay_btn)
        
        print("🔄 Paiement initié... Vérification du résultat...")
        
        # Check the payment result with a 15-second timeout
        result = check_payment_result(driver, timeout=15)
        
        return result
        
    except Exception as e:
        print(f"❌ Erreur durant le processus: {str(e)}")
        return False
    finally:
        driver.quit()

# Test in the main block
if __name__ == "__main__":
    # Test parameters
    usd_value = "2"  # or "5", "25", etc.
    choix = "almas"  # almas or dahab
    ID = "7915329"
    pin_code = "2Q1PG3QKKKGA"
    
    # Function call
    result = yalla_pay_recharge(usd_value, choix, ID, pin_code)
    
    # Display final result
    print("\n" + "="*50)
    print("RÉSULTAT FINAL:")
    if result:
        print("✅ SUCCÈS!")
    else:
        print("❌ ÉCHEC!")
    print("="*50)

