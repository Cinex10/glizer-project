import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import random
import logging
import stat


COOKIES_XPATH='/html[1]/body[1]/div[2]/div[1]/div[11]/div[3]/div[1]/div[1]/div[1]'


DETECT_PAGE_LOADED_XPATH='//div[@class="Banner_title__dnHBH"]'
SIGN_IN_BUTTON_SELECTOR='div.MobileNav_sign_in__qA2oK'
SIGN_IN_BUTTON_SELECTOR2='div.Button_icon_text__C-ysi'
SIGN_IN_BUTTON_XPATH_SELECTOR3="//span[contains(text(),'تسجيل الدخول')]"

IFRAME_XPATH='//iframe[contains(@src,"https://www.midasbuy.com/apps/login/home/sa")]'
CONTINUE_SIGN_IN_BUTTON_XPATH="//div[@class='btn comfirm-btn']"
EMAIL_ADDRESS_FIELD_XPATH='/html/body/div/div[1]/div/div[3]/div[1]/div/div[3]/div/div/div/div[1]/p/input'
PASSWORD_INPUT_FIELD_XPATH='/html/body/div/div[1]/div/div[3]/div[1]/div[1]/div[2]/div[2]/div/input'
FINAL_SIGN_IN_BUTTON_XPATH='/html/body/div/div[1]/div/div[3]/div[1]/div[2]/div'


PLAYER_ID_LOCATION_CSS='span[class*="UserTabBox_id__"]'
SIGN_IN_BUTTON_XPATH='//div[@class="MobileNav_sign_in__qA2oK"]'
PLAYER_ID_SWITCH_INITIATE_BUTTON_XPATH="//i[@class='i-midas:switch icon']"
PLAYER_ID_SWITCH_INITIATE_BUTTON_SELECTOR_NONE = 'div.Banner_user_tab_box__Bp6NY > div > div > div'
PLAYER_ID_INPUT_FIELD_XPATH="//div[contains(@class, 'SelectServerBox_input_wrap_box__')]//input"
PLAYER_ID_SWITCH_OK_BUTTON_XPATH="//div[contains(@class, 'BindLoginPop_btn_wrap__')]//div[contains(@class, 'Button_btn_wrap__')]//div[contains(@class, 'Button_btn__') and contains(@class, 'Button_btn_primary__')]//div//div[contains(@class, 'Button_icon_text__') and normalize-space()='OK']"
PLAYER_LOGIN_BTN_XPATH="//div[@class='MobileNav_sign_in__qA2oK MobileNav_imp__hchy7 false']"


# REDEEM_CODE_INPUT_BOX_XPATH = "//div[contains(@class, 'RedeemStepBox_input_box__') and contains(@class, 'RedeemStepBox_vip__')]//div[contains(@class, 'Input_input_box__')]//div[contains(@class, 'Input_input_wrap_box__')]//input[@type='text']"
REDEEM_CODE_INPUT_BOX_XPATH = "//input[@placeholder='يرجى إدخال رمز استرداد']"
REDEEM_INITIATE_BUTTON_XPATH = "//div[contains(@class,'RedeemStepBox_btn_wrap__')]//div[contains(@class,'Button_btn_wrap__')]"
# //*[@id="root"]/div/div[7]/div[3]/div/div[2]/div[2]/div[1]/div/div
CODE_ERROR_NOTICE_XPATH="//div[contains(@class, 'Input_error_text__')]//div[1]"

REDEEM_CONFIRM_POP_UP_XPATH = "//div[contains(@class,'PopStatusPrompt_active__')]"
REDEEM_CONFIRM_BTN_POP_UP_XPATH = "//div[contains(text(),'بالتأكيد')]"
# //div[@class='PopStatusPrompt_pop_mode_box__nSRlx PopStatusPrompt_active__GMZrj']//div[@class='Button_btn__P0ibl Button_btn_primary__1ncdM']//div//div[1]
# PopStatusPrompt_pop_mode_box__nSRlx PopStatusPrompt_active__GMZrj

REDEEM_CODE_POP_UP_XPATH = "//div[contains(@class, 'PopConfirmRedeem_pop_mode_box__')]"
REDEEM_CODE_POP_UP_CONTENT_XPATH = "//div[contains(@class, 'PopConfirmRedeem_mess_wrap')]"



# XPath basé sur la structure HTML du bouton "إرسال" (Send)
SUBMIT_REDEEM_CODE_BUTTON_XPATH="//div[contains(@class, 'Button_btn_P0ibl') and contains(@class, 'Button_btn_primary_1ncdM')]"
SUBMIT_REDEEM_CODE_BUTTON_XPATH2="//div[contains(@class, 'Button_text_WeIeb') and text()='إرسال']"
SUBMIT_REDEEM_CODE_BUTTON_XPATH3="//div[contains(@class, 'PopConfirmRedeem_btn_wrap_3RKFf')]//div[contains(@class, 'Button_btn_P0ibl')]"
SUBMIT_REDEEM_CODE_BUTTON_XPATH4="//div[contains(@class, 'Button_icon_text_C-ysi')]//div[contains(@class, 'Button_text_WeIeb') and text()='إرسال']"
SUBMIT_REDEEM_CODE_BUTTON_XPATH5="//div[contains(@class, 'PopConfirmRedeem_btn_wrap_3RKFf')]//div[contains(@class, 'Button_text_WeIeb') and text()='إرسال']"

REDEEM_ERROR_NOTICE_XPATH="//div[contains(@class, 'Input_error_text__')]//div[1]"
# XPath pour détecter le message de succès "تم استبداله بنجاح"
REDEEM_SUCCESS_NOTICE_XPATH = "//div[contains(@class, 'PurchaseContainer_text_OmIRF') and contains(text(),'تم استبداله بنجاح')]"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedemptionError(Exception):
    pass

class PlayerSwitchError(Exception):
    pass

class Browser:
    def __init__(self, email: str) -> None:
        logger.info("init ##")
        # GESTION SIMPLE COMME LE CODE DE RÉFÉRENCE
        url = os.getcwd()
        user_data = os.path.join(url, f'user-data-{email}')
        os.makedirs(user_data, mode=0o700, exist_ok=True)
        os.chmod(user_data, stat.S_IRWXU)
        
        options = Options()
        options.page_load_strategy = 'normal'  # Comme le code de référence
        options.add_argument(f"--user-data-dir={user_data}")
        
        # Ajouter quelques variations réalistes
        user_agents = [
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        # Ubuntu server compatibility arguments - EXACTEMENT COMME LE CODE DE RÉFÉRENCE
        # options.add_argument("--headless")  # Activé comme dans le code de référence
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--lang=ar")
        options.add_experimental_option("prefs", {
            "intl.accept_languages": "ar,ar-SA,en-US,en"
        })
        options.add_argument("--start-maximized")
                # Arguments spécifiques pour Docker - Solution 2
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-prompt-on-repost")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-component-extensions-with-background-pages")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-sync-preferences")
        options.add_argument("--disable-web-resources")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-permissions-api")
        options.add_argument("--disable-presentation-api")
        options.add_argument("--disable-print-preview")
        options.add_argument("--disable-speech-api")
        options.add_argument("--disable-file-system")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--disable-preconnect")
        options.add_argument("--disable-translate")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-features=VizDisplayCompositor,VizServiceDisplay")
        options.add_argument("--remote-debugging-port=0")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            # Test immédiat comme le code de référence
            self.driver.get("about:blank")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise Exception(f"Browser initialization failed: {e}")
        
        # Timeouts exactement comme le code de référence
        self.driver.set_page_load_timeout(random.randint(28, 32))
        self.driver.implicitly_wait(random.randint(9, 11))

    def human_delay(self, min_sec=0.5, max_sec=2.0):
        """Délai humain aléatoire"""
        time.sleep(random.uniform(min_sec, max_sec))

    def safe_click(self, locator, delay=15):
        """Click element with retries and JS fallback"""
        element = WebDriverWait(self.driver, delay).until(
            EC.element_to_be_clickable(locator))
        
        # Scroll avec position aléatoire
        scroll_pos = random.choice(['start', 'center', 'end'])
        self.driver.execute_script(f"arguments[0].scrollIntoView({{block: '{scroll_pos}', behavior: 'smooth'}});", element)
        self.human_delay(0.3, 0.8)
        
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)
        
        self.human_delay(0.2, 0.6)  # Pause après clic

    def is_session_valid(self):
        """Check if the current browser session is valid"""
        try:
            self.driver.current_url
            return True
        except:
            return False
    
    def visit_page(self):
        if not self.is_session_valid():
            raise Exception("Browser session is invalid - driver may have crashed")
        
        try:
            logger.info("Attempting to navigate to URL...")
            self.driver.get('https://www.midasbuy.com/midasbuy/sa/redeem/pubgm')
            logger.info(f"Current URL after navigation: {self.driver.current_url}")
            logger.info(f"Page title: {self.driver.title}")
            
            # Wait for page to load
            self.wait_for_page_load(timeout=30)
            logger.info("Page loaded successfully")
            
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            try:
                logger.info(f"Current URL: {self.driver.current_url}")
            except:
                logger.warning("Unable to get current URL - driver session may be invalid")
            raise Exception(f"Failed to navigate to page: {str(e)}")
        
        try:
            self.safe_click((By.XPATH, COOKIES_XPATH), delay=5)
            logger.info('Cookies accepted')
        except:
            logger.info("Cookies already accepted")
    
    def is_logged_in(self) -> bool:
        try:
            self.wait_for_page_load()
            self.driver.find_element(By.XPATH, PLAYER_LOGIN_BTN_XPATH)
            return False
        except:
            return True

    def sign_in(self, email_address, password):
        logger.info('Sign In')
        self.wait_for_page_load()

        logger.info('Page Loaded')
        status = self.driver.execute_script(f"document.querySelector('{SIGN_IN_BUTTON_SELECTOR}').click();return 'clicked login button'")
        time.sleep(random.uniform(1, 2.5))

        status = self.driver.execute_script(f"document.querySelector('{SIGN_IN_BUTTON_SELECTOR2}').click();return 'clicked login button'")
        
        logger.info(status)

        try:
            iframe = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, IFRAME_XPATH))
            )
            logger.info('iframe found')
            
            # Log iframe properties for debugging
            try:
                is_displayed = iframe.is_displayed()
                is_enabled = iframe.is_enabled()
                size = iframe.size
                logger.info(f'iframe - displayed: {is_displayed}, enabled: {is_enabled}, size: {size}')
            except Exception as debug_e:
                logger.warning(f'Failed to get iframe properties: {debug_e}')
            
            # Wait a bit more for iframe to be fully loaded
            time.sleep(2)
            
            # Try switching to iframe regardless of display/enabled status
            try:
                self.driver.switch_to.frame(iframe)
                logger.info('iframe switched successfully')
                
                # Validate we're actually in the iframe
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    logger.info('iframe content accessible')
                except:
                    logger.warning("Failed to find body in iframe, trying by index")
                    self.driver.switch_to.default_content()
                    # Try switching by index as fallback
                    self.driver.switch_to.frame(0)
                    logger.info('switched to iframe by index')
            except Exception as switch_e:
                logger.error(f'Failed to switch to iframe: {switch_e}')
                # Try switching by index as last resort
                try:
                    self.driver.switch_to.frame(0)
                    logger.info('switched to iframe by index as fallback')
                except Exception as index_e:
                    logger.error(f'Failed to switch by index: {index_e}')
                    raise Exception("All iframe switching methods failed")
        except Exception as e:
            logger.error(f"Iframe switching failed: {str(e)}")
            # Ensure we're back to default content if iframe switch failed
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            raise

        logger.info('iframe switched')
        
        time.sleep(random.uniform(1, 2.5))
        
        status = self.driver.find_element(By.XPATH, SIGN_IN_BUTTON_XPATH_SELECTOR3).click()
        time.sleep(random.uniform(1, 2.5))

        email_address_field=WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, EMAIL_ADDRESS_FIELD_XPATH))
        )
        
        logger.info('email_address_field')
        
        if email_address_field.get_attribute('value') != email_address:
            self.clear_and_type(email_address_field, email_address)
            logger.info('email filled')
        else:
            logger.info('Email Address is already filled. Skipping the step.')
        
        continue_button = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, CONTINUE_SIGN_IN_BUTTON_XPATH))
                )
        
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", continue_button)
        
        time.sleep(random.uniform(0.5, 1.2))

        try:
            # First attempt regular click
             continue_button.click()
        except:
            # Fallback to JavaScript click
            self.driver.execute_script("arguments[0].click();", continue_button)
        
        logger.info('continue_button')

        password_input_field = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH,PASSWORD_INPUT_FIELD_XPATH))
        )

        self.clear_and_type(password_input_field, password)
        
        logger.info('password_input_field')

        self.driver.find_element(By.XPATH, FINAL_SIGN_IN_BUTTON_XPATH).click()
        logger.info("Arrive ")
        time.sleep(3)
        
        # Try to handle different post-login scenarios
        try:
            # Check if we're already logged in successfully
            self.driver.switch_to.default_content()
            if self.is_signed_in():
                logger.info("Already signed in successfully")
                return
                
            # Switch back to iframe if still in login flow
            self.driver.switch_to.frame(0)
            
            # Look for passkey button with shorter timeout
            try:
                passkey_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/div/div[1]'))
                )
                logger.info('passkey_button found')
                self.driver.execute_script('arguments[0].click()', passkey_button)
                logger.info('passkey_button clicked')
                
            except TimeoutException:
                logger.warning("Passkey button not found, checking for other elements")
                
                # Look for alternative completion indicators
                alternative_selectors = [
                    "//button[contains(text(), 'Continue')]",
                    "//button[contains(text(), 'Skip')]", 
                    "//div[contains(@class, 'success')]",
                    "//div[contains(@class, 'complete')]"
                ]
                
                found_alternative = False
                for selector in alternative_selectors:
                    try:
                        element = WebDriverWait(self.driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        logger.info(f"Found alternative element: {selector}")
                        element.click()
                        found_alternative = True
                        break
                    except:
                        continue
                
                if not found_alternative:
                    logger.info("No post-login actions needed, checking login status")
                    
        except Exception as e:
            logger.error(f"Post-login handling error: {str(e)}")
            # Continue anyway as login might have succeeded
        logger.info('passkey_button clicked')

    def is_signed_in(self) -> bool:
        """Méthode manquante - ajoutée comme dans le code de référence"""
        try:
            self.wait_for_page_load()
            self.driver.find_element(By.XPATH, PLAYER_LOGIN_BTN_XPATH)
            return False
        except:
            return True

    def get_current_player_id(self):
        """Get current player ID if available, return None if not found"""
        try:
            original_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, PLAYER_ID_LOCATION_CSS))
                    )
            original_player_id = original_element.text.strip().replace('(','').replace(')','')
            return original_player_id        
        except Exception as e:
            logger.info(f"Could not find current player ID: {str(e)}")
            return None        
    
    def switch_player_id(self, player_id):
        """Switch to specified player ID - GARDE EXACTEMENT LA LOGIQUE DE VOTRE CODE ACTUEL"""
        
        try:
            if not str(player_id).isdigit():
                raise Exception("Invalid Player ID")

            self.driver.switch_to.default_content()
            
            # Check if we need to get current player ID or if we can proceed directly
            try:
                original_player_id = self.get_current_player_id()
                logger.info(f"Current player ID found: {original_player_id}")

                # Check if ID already matches
                if str(player_id) == original_player_id:
                    logger.info("Player ID already matches target ID")
                    return

                # If ID doesn't match, use the old service approach (switch icon method)
                logger.info(f"Current ID '{original_player_id}' doesn't match target '{player_id}', using switch icon method...")
                
                # Use the old service approach with switch icon
                switch_btn = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, PLAYER_ID_SWITCH_INITIATE_BUTTON_XPATH)))
                self.safe_click(switch_btn)
                logger.info("Player ID switch initiated with switch icon")

                # Handle ID input using old service approach
                id_input = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, PLAYER_ID_INPUT_FIELD_XPATH)))
                self.clear_and_type(id_input, str(player_id))

                # Confirm change using old service approach
                confirm_btn = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, PLAYER_ID_SWITCH_OK_BUTTON_XPATH)))
                self.safe_click(confirm_btn)

                # Verify change
                WebDriverWait(self.driver, 15).until(
                    lambda d: self.get_current_player_id() == str(player_id))
                logger.info("Player ID successfully changed using switch icon method")
                return
                    
            except Exception as e:
                logger.info(f"No current player ID found: {str(e)}")
                logger.info("Proceeding directly to player ID change with new method...")
                # Continue without checking current ID

            # Step 1: Find and click the "أدخل معرف اللاعب" button
            logger.info("Looking for 'أدخل معرف اللاعب' button...")
            
            # DEBUG: Prendre une capture d'écran avant de chercher le bouton
            debug_screenshot = f"screenshots/debug_before_player_id_button_search_{int(time.time())}.png"
            self.driver.save_screenshot(debug_screenshot)
            logger.info(f"Debug screenshot saved: {debug_screenshot}")
            
            # Debug: afficher tous les boutons disponibles sur la page
            try:
                all_buttons = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'Button')]")
                logger.info(f"Found {len(all_buttons)} button elements on page")
                for i, btn in enumerate(all_buttons[:15]):  # Limiter à 15 pour éviter le spam
                    try:
                        text = btn.text.strip()
                        classes = btn.get_attribute("class")
                        logger.info(f"Button {i+1}: text='{text}', classes='{classes}'")
                    except:
                        logger.info(f"Button {i+1}: could not read text/classes")
            except Exception as e:
                logger.warning(f"Could not list buttons: {str(e)}")
            
            # Debug: chercher spécifiquement les éléments avec le texte arabe
            try:
                arabic_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'أدخل معرف اللاعب')]")
                logger.info(f"Found {len(arabic_elements)} elements with 'أدخل معرف اللاعب' text")
                for i, elem in enumerate(arabic_elements):
                    try:
                        tag = elem.tag_name
                        classes = elem.get_attribute("class")
                        logger.info(f"Arabic element {i+1}: tag='{tag}', classes='{classes}'")
                    except:
                        logger.info(f"Arabic element {i+1}: could not read details")
            except Exception as e:
                logger.warning(f"Could not search for Arabic text: {str(e)}")
            
            enter_player_id_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'Button_text__WeIeb') and contains(text(), 'أدخل معرف اللاعب')]")))
            self.safe_click(enter_player_id_btn)
            logger.info("'أدخل معرف اللاعب' button clicked")
            
            # Wait for popup to appear
            self.human_delay(1.0, 2.0)
            
            # Step 2: Find and fill the player ID input field
            logger.info("Looking for player ID input field...")
            id_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='إدخال حساب معرف لاعب']")))
            
            # Clear and type the new player ID
            self.clear_and_type(id_input, str(player_id))
            logger.info(f"Player ID '{player_id}' entered")
            
            # Step 3: Find and click the OK button
            logger.info("Looking for OK button...")
            
            # DEBUG: Prendre une capture d'écran avant de chercher le bouton OK
            debug_screenshot = f"screenshots/debug_before_ok_button_search_{int(time.time())}.png"
            self.driver.save_screenshot(debug_screenshot)
            logger.info(f"Debug screenshot saved: {debug_screenshot}")
            
            # Debug: afficher tous les boutons disponibles sur la page
            try:
                all_buttons = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'Button')]")
                logger.info(f"Found {len(all_buttons)} button elements on page")
                for i, btn in enumerate(all_buttons[:15]):  # Limiter à 15 pour éviter le spam
                    try:
                        text = btn.text.strip()
                        classes = btn.get_attribute("class")
                        logger.info(f"Button {i+1}: text='{text}', classes='{classes}'")
                    except:
                        logger.info(f"Button {i+1}: could not read text/classes")
            except Exception as e:
                logger.warning(f"Could not list buttons: {str(e)}")
            
            # Debug: chercher spécifiquement les éléments avec le texte "OK"
            try:
                ok_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'OK')]")
                logger.info(f"Found {len(ok_elements)} elements with 'OK' text")
                for i, elem in enumerate(ok_elements):
                    try:
                        tag = elem.tag_name
                        classes = elem.get_attribute("class")
                        logger.info(f"OK element {i+1}: tag='{tag}', classes='{classes}'")
                    except:
                        logger.info(f"OK element {i+1}: could not read details")
            except Exception as e:
                logger.warning(f"Could not search for OK text: {str(e)}")
            
            # Essayer plusieurs sélecteurs pour le bouton OK
            ok_selectors = [
                "//div[contains(@class, 'Button_text_WeIeb') and contains(text(), 'OK')]",
                "//div[contains(@class, 'Button_text__WeIeb') and contains(text(), 'OK')]",
                "//div[contains(@class, 'Button_btn') and contains(text(), 'OK')]",
                "//div[contains(@class, 'Button') and contains(text(), 'OK')]",
                "//*[contains(text(), 'OK') and contains(@class, 'Button')]",
                "//button[contains(text(), 'OK')]",
                "//div[text()='OK']"
            ]
            
            ok_btn = None
            for selector in ok_selectors:
                try:
                    logger.info(f"Trying OK button selector: {selector}")
                    ok_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector)))
                    logger.info(f"OK button found with selector: {selector}")
                    break
                except Exception as e:
                    logger.info(f"Selector '{selector}' failed: {str(e)}")
                    continue
            
            if ok_btn is None:
                raise Exception("OK button not found with any selector")
                
            self.safe_click(ok_btn)
            logger.info("OK button clicked")
            
            # Wait for the change to take effect
            self.human_delay(2.0, 3.0)
            
            # Step 4: Verify the change (optional if no current ID)
            try:
                new_player_id = self.get_current_player_id()
                if new_player_id is not None:
                    if str(player_id) == new_player_id:
                        logger.info("Player ID successfully changed and verified")
                    else:
                        logger.warning(f"Player ID verification failed. Expected: {player_id}, Got: {new_player_id}")
                else:
                    logger.info("Player ID change completed (verification not possible - no current ID display)")
            except Exception as e:
                logger.warning(f"Could not verify player ID change: {str(e)}")
                # Continue anyway as the change might have succeeded
                
        except Exception as e:
            logger.error(f"Player switch failed: {str(e)}")
            screenshot_file = "screenshots/Player switch failed.png"
            self.driver.save_screenshot(screenshot_file)
            logger.info(f"Screenshot saved as: {screenshot_file}")
            raise Exception(f"Player switch failed: {str(e)}")

    def redeem_code(self, redeem_code):
        """Redeem code - GARDE EXACTEMENT LA LOGIQUE DE VOTRE CODE ACTUEL"""
        try:
            logger.info(f"Starting redemption for code: {redeem_code}")
            
            # Délai avant de commencer
            self.human_delay(1.0, 2.5)
            
            # Enter redemption code
            redeem_input = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, REDEEM_CODE_INPUT_BOX_XPATH))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", redeem_input)
                                       
            # Wait for visibility before interacting
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of(redeem_input)
            )
            
            # Cliquer d'abord sur le champ
            redeem_input.click()
            self.human_delay(0.3, 0.7)
            
            self.clear_and_type(redeem_input, redeem_code)
            logger.info("Code entered")
            
            # Pause comme un humain qui vérifie le code
            self.human_delay(1.0, 2.0)
            
            # Initiate redemption
            logger.info("Clicking redeem button...")
            self.driver.execute_script('document.querySelector("#root > div.App.app-wrap__relative > div.container_wrap > div.redeem_modules_box.default_box > div > div.RedeemStepBox_step_box__kecmM.RedeemStepBox_redeem_step__Cb6tE > div.RedeemStepBox_mess__6gbK6 > div.RedeemStepBox_btn_wrap__wEKY9 > div > div").click()')
            
            # Attendre après clic
            self.human_delay(1.5, 3.0)
            
            try:
                error_element = WebDriverWait(self.driver, 4).until(
                    EC.presence_of_element_located((By.XPATH, CODE_ERROR_NOTICE_XPATH)))
                raise Exception(error_element.text)
            except TimeoutException:
                pass
                
            try:
                WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, REDEEM_CODE_POP_UP_XPATH))
                )
                logger.info("Popup appeared")
                self.human_scroll()
                self.human_delay(1.0, 2.0)  # Pause après scroll

                # Prendre une capture d'écran avant de chercher le bouton pour débogage
                debug_screenshot = f"screenshots/debug_before_button_search_{int(time.time())}.png"
                self.driver.save_screenshot(debug_screenshot)
                logger.info(f"Debug screenshot saved: {debug_screenshot}")
                
                # Debug: afficher tous les boutons disponibles sur la page
                try:
                    all_buttons = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'Button')]")
                    logger.info(f"Found {len(all_buttons)} button elements on page")
                    for i, btn in enumerate(all_buttons[:10]):  # Limiter à 10 pour éviter le spam
                        try:
                            text = btn.text.strip()
                            classes = btn.get_attribute("class")
                            logger.info(f"Button {i+1}: text='{text}', classes='{classes}'")
                        except:
                            logger.info(f"Button {i+1}: could not read text/classes")
                except Exception as e:
                    logger.warning(f"Could not enumerate buttons: {str(e)}")

                # Handle submission
                self.handle_redemption_submission()
                
                logger.info('Redemption submitted')
            except TimeoutException:
                try:
                    ok_btn = WebDriverWait(self.driver, 4).until(
                    EC.element_to_be_clickable((By.XPATH, REDEEM_CONFIRM_BTN_POP_UP_XPATH))
                    )
                    self.safe_click(ok_btn)
                    logger.info("Clicked OK button")
                except TimeoutException:
                    try:
                        error_element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, CODE_ERROR_NOTICE_XPATH)))
                        raise Exception(error_element.text)
                    except TimeoutException:
                        raise Exception('unknown error')

            # Check outcome avec temps d'inspection étendu
            return self.check_redemption_outcome()

        except Exception as e:
            raise e

    def clear_and_type(self, element, text):
        """Clear field and type text with human-like intervals"""
        element.clear()
        self.human_delay(0.2, 0.5)
        
        for char in text:
            element.send_keys(char)
            # Variation dans la vitesse de frappe
            time.sleep(random.uniform(0.05, 0.25))
            
            # Pause occasionnelle (comme réflexion)
            if random.random() < 0.08:  # 8% chance
                time.sleep(random.uniform(0.3, 0.8))

    def wait_for_page_load(self, timeout=30):
        """Wait for page to fully load"""
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def handle_redemption_submission(self):
        """Handle different submission scenarios - GARDE EXACTEMENT VOTRE LOGIQUE"""
        logger.info("Trying to find and click submit button...")
        
        # Approche simple et directe : chercher tous les boutons avec la classe Button_text__WeIeb
        try:
            logger.info("Trying simple approach: find all Button_text__WeIeb elements")
            
            # Attendre que les boutons soient présents
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.Button_text__WeIeb"))
            )
            
            # Trouver tous les boutons avec cette classe
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "div.Button_text__WeIeb")
            logger.info(f"Found {len(buttons)} buttons with Button_text__WeIeb class")
            
            # Chercher le bouton qui contient "إرسال" ou qui est cliquable
            for i, btn in enumerate(buttons):
                try:
                    # Essayer de lire le texte
                    text = btn.text.strip()
                    logger.info(f"Button {i+1} text: '{text}'")
                    
                    # Si on trouve "إرسال", cliquer dessus
                    if text == "إرسال":
                        logger.info(f"Found button with text 'إرسال', clicking...")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                        time.sleep(1)
                        self.safe_click(btn)
                        logger.info("Successfully clicked button with text 'إرسال'")
                        return
                        
                except Exception as e:
                    logger.warning(f"Could not read button {i+1}: {str(e)}")
                    continue
            
            # Si aucun bouton avec "إرسال" n'est trouvé, essayer de cliquer sur le premier bouton cliquable
            logger.info("No button with 'إرسال' text found, trying first clickable button...")
            for i, btn in enumerate(buttons):
                try:
                    if btn.is_enabled() and btn.is_displayed():
                        logger.info(f"Trying to click button {i+1} (enabled and displayed)")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                        time.sleep(1)
                        self.safe_click(btn)
                        logger.info(f"Successfully clicked button {i+1}")
                        return
                except Exception as e:
                    logger.warning(f"Could not click button {i+1}: {str(e)}")
                    continue
            
        except Exception as e:
            logger.warning(f"Simple approach failed: {str(e)}")
        
        # Fallback: essayer de cliquer directement avec JavaScript
        try:
            logger.info("Trying JavaScript fallback...")
            js_script = """
            var buttons = document.querySelectorAll('div.Button_text__WeIeb');
            if (buttons.length > 0) {
                // Essayer de cliquer sur le premier bouton visible
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].offsetParent !== null) { // Vérifier si visible
                        buttons[i].click();
                        return true;
                    }
                }
            }
            return false;
            """
            result = self.driver.execute_script(js_script)
            if result:
                logger.info("Successfully clicked button using JavaScript fallback")
                return
        except Exception as e:
            logger.warning(f"JavaScript fallback failed: {str(e)}")
        
        raise RedemptionError("Could not find or click submit button")

    def check_redemption_outcome(self):
        """Check and return redemption result - GARDE EXACTEMENT VOTRE LOGIQUE"""
        logger.info("🔍 Waiting 5 seconds to inspect redemption outcome...")
        
        # Temps d'inspection étendu
        inspection_time = random.uniform(4.0, 7.0)
        time.sleep(inspection_time)
        logger.info(f"Inspection completed after {inspection_time:.1f} seconds")
        
        # Prendre une capture d'écran pour débogage
        screenshot_path = f"screenshots/redeem_outcome_check_{int(time.time())}.png"
        self.driver.save_screenshot(screenshot_path)
        logger.info(f"📸 Outcome check screenshot saved: {screenshot_path}")
        
        try:
            # Attendre et chercher le message de succès "تم استبداله بنجاح"
            logger.info("Looking for success message: 'تم استبداله بنجاح'")
            success_element = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, REDEEM_SUCCESS_NOTICE_XPATH)))
            
            # Corriger l'escape sequence du CSS selector
            try:
                self.driver.execute_script('document.querySelector("#root > div > div.PaymentResult_container_wrap__ddHmB > div > div.PurchaseContainer_btn_box__7kd\\+o > div > div > div > div > div").click()')
            except Exception as e:
                logger.warning(f"Could not click continue button: {e}")
            
            # Lire le texte du message de succès
            success_text = success_element.text.strip()
            logger.info(f"✅ SUCCESS message found: '{success_text}'")
            
            # Vérifier que c'est bien le bon message
            if "تم استبداله بنجاح" in success_text:
                logger.info("✅ SUCCESS: Code redeemed successfully!")
                return True
            else:
                logger.warning(f"Unexpected success message: '{success_text}'")
                return False
                
        except TimeoutException:
            logger.warning("Could not find success message with XPath")
            
            # Essayer de chercher le message de succès avec d'autres méthodes
            try:
                logger.info("Trying alternative method to find success message...")
                possible_success_elements = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'تم استبداله بنجاح')]")
                
                if possible_success_elements:
                    success_text = possible_success_elements[0].text.strip()
                    logger.info(f"✅ SUCCESS found with alternative method: '{success_text}'")
                    return True
                    
            except Exception as e2:
                logger.warning(f"Alternative method also failed: {str(e2)}")
            
            # Prendre une capture d'écran d'erreur
            error_screenshot = f"screenshots/redeem_error_{int(time.time())}.png"
            self.driver.save_screenshot(error_screenshot)
            logger.info(f"📸 Error screenshot saved: {error_screenshot}")
            
            # Essayer de trouver un message d'erreur
            try:
                error_element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, CODE_ERROR_NOTICE_XPATH)))
                error_text = error_element.text.strip()
                logger.error(f"❌ ERROR found: '{error_text}'")
                raise Exception(error_text)
            except TimeoutException:
                logger.error("❌ No success or error message found - unknown outcome")
                raise Exception("Unknown redemption outcome")

    def human_scroll(self, selector=REDEEM_CODE_POP_UP_CONTENT_XPATH, portion=2):
        """Simulate human-like scrolling behavior - GARDE EXACTEMENT VOTRE LOGIQUE"""
        scroll_pause_time = random.uniform(0.5, 1.2)
        scroll_amount = random.randint(200, 400)
        
        # Get scrollable container (adjust selector if needed)
        scroll_container = self.driver.find_element(
            By.XPATH, selector
        )

        last_height = self.driver.execute_script(
            "return arguments[0].scrollHeight", scroll_container
        )

        while True:
            # Randomize scroll direction and amount
            current_scroll = self.driver.execute_script(
                "return arguments[0].scrollTop", scroll_container
            )
            self.driver.execute_script(
                f"arguments[0].scrollBy(0, {scroll_amount})", scroll_container
            )
            
            time.sleep(scroll_pause_time * random.uniform(0.8, 1.2))
            
            new_height = self.driver.execute_script(
                "return arguments[0].scrollHeight", scroll_container
            )
            
            # Random chance to scroll back up slightly
            if random.random() < 0.15:
                self.driver.execute_script(
                    f"arguments[0].scrollBy(0, -{scroll_amount//portion})", scroll_container
                )
                time.sleep(scroll_pause_time)
            
            # Break if we've reached bottom
            if current_scroll + scroll_container.size['height'] >= new_height:
                break
                
            # Update last height and randomize parameters
            last_height = new_height
            scroll_amount = random.randint(150, 300)
            scroll_pause_time = random.uniform(0.3, 0.8)
    

def process_pubg_recharge(emailAddress, password, playerId, redeemCodes):
    # GESTION SIMPLE EXACTEMENT COMME LE CODE DE RÉFÉRENCE
    browser = Browser(email=emailAddress)
    result = {}
    
    browser.visit_page()
    try:
        is_logged_in = browser.is_logged_in()
        logger.info(f'is logged in: {is_logged_in}')
        if not is_logged_in:
            browser.sign_in(email_address=emailAddress, password=password)
        
    except Exception as e:
        logger.error(f"Sign in error: {str(e)}")
        screenshot_file = f"screenshots/screenshot_sign_in.png"
        browser.driver.save_screenshot(screenshot_file)
        logger.info(f"Screenshot saved as: {screenshot_file}")
        raise Exception("Failed to sign in")

    try:
        browser.switch_player_id(player_id=playerId)
        
        # Traiter les codes avec délais entre eux
        for i, code in enumerate(redeemCodes):
            try:
                logger.info(f"📝 Processing code {i+1}/{len(redeemCodes)}: {code}")
                
                # Délai entre codes (sauf pour le premier)
                if i > 0:
                    delay = random.uniform(3.0, 8.0)
                    logger.info(f"⏱️ Waiting {delay:.1f} seconds before next code...")
                    time.sleep(delay)
                
                redeem_status = browser.redeem_code(redeem_code=code)
                result[code] = redeem_status
                logger.info(f"✅ Code {code} processed successfully")
                
            except Exception as err:
                logger.error(f"❌ Failed to process code {code}: {str(err)}")
                result[code] = str(err)
                
                # Délai même après erreur
                browser.human_delay(2.0, 4.0)
                continue
        
        logger.info("🎉 All redemptions completed!")
        
    except Exception as err:
        logger.error(f"Redeem code error: {str(err)}")
        raise Exception(f"Failed to redeem code: {str(err)}")
    finally:
        # Délai avant fermeture
        browser.human_delay(1.0, 3.0)
        try:
            browser.driver.quit()
        except:
            pass
        return result

# Garder le main pour les tests - EXACTEMENT COMME LE CODE DE RÉFÉRENCE
if __name__ == "__main__":
    r = process_pubg_recharge(emailAddress="Abdull82ah@hotmail.com", password="ZXCVzxcv@1010", playerId="533938203", redeemCodes=["gxNcMmj72s2a4eGfQ8"])   
    print(r)