import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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



SUBMIT_REDEEM_CODE_BUTTON_XPATH='/html/body/div[2]/div/div[7]/div[7]/div[2]/div/div[6]/div[1]/div/div/div/div/div'
SUBMIT_REDEEM_CODE_BUTTON_XPATH2='/html/body/div[2]/div/div[7]/div[7]/div[2]/div/div[7]/div[1]/div/div/div/div/div'
SUBMIT_REDEEM_CODE_BUTTON_XPATH3="//div[contains(@class, 'Button_icon_text__')][contains(text(),'إرسال')]"

REDEEM_ERROR_NOTICE_XPATH="//div[contains(@class, 'Input_error_text__')]//div[1]"
# REDEEM_SUCCESS_NOTICE_XPATH = '/html/body/div[2]/div/div[3]/div/div[1]/div/div[1]'
REDEEM_SUCCESS_NOTICE_XPATH = "//div[contains(@class, 'PurchaseContainer_text__')][contains(text(),'نجاح')]"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedemptionError(Exception):
    pass

class PlayerSwitchError(Exception):
    pass

class Browser:
    def __init__(self, email:str) -> None:
        logger.info("init ##")
        url = os.getcwd()
        user_data = os.path.join(url, f'user-data-{email}')
        os.makedirs(user_data, mode=0o700, exist_ok=True)
        os.chmod(user_data, stat.S_IRWXU)
        options = Options()
        options.page_load_strategy = 'normal'  # Changed from 'none' to ensure page loads
        options.add_argument(f"--user-data-dir={user_data}")
        
        # Ubuntu server compatibility arguments
        options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")  # Required for Docker/server environments
        options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        options.add_argument("--disable-gpu")  # Disable GPU acceleration
        options.add_argument("--disable-extensions")  # Disable extensions
        options.add_argument("--disable-plugins")  # Disable plugins
        options.add_argument("--window-size=1920,1080")  # Set window size for headless mode
        options.add_argument("--disable-web-security")  # Disable web security for iframe issues
        options.add_argument("--disable-features=VizDisplayCompositor")  # Fix rendering issues
        options.add_argument("--disable-background-timer-throttling")  # Prevent iframe throttling
        options.add_argument("--disable-renderer-backgrounding")  # Keep iframe rendering active
        options.add_argument("--lang=ar")  # Set language to Arabic
        options.add_experimental_option("prefs", {
            "intl.accept_languages": "ar,ar-SA,en-US,en"
        })
        
        # Keep maximized for non-headless environments (will be ignored in headless mode)
        options.add_argument("--start-maximized")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            # Test the session immediately
            self.driver.get("about:blank")
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise Exception(f"Browser initialization failed: {e}")
        
        # Set timeouts to prevent hanging
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(10)
        # self.driver = webdriver.Chrome(options=options)
    
    def safe_click(self, locator, delay=15):
        """Click element with retries and JS fallback"""
        element = WebDriverWait(self.driver, delay).until(
            EC.element_to_be_clickable(locator))
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

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

    def get_current_player_id(self):
        original_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, PLAYER_ID_LOCATION_CSS))
                )
        original_player_id = original_element.text.strip().replace('(','').replace(')','')
        return original_player_id        
    
    def switch_player_id(self, player_id):
        """Switch to specified player ID with improved error handling"""
        
        try:
            if not str(player_id).isdigit():
                raise Exception("Invalid Player ID")

            self.driver.switch_to.default_content()
            
            # Get current player ID
            try:
                original_player_id = self.get_current_player_id()
            except Exception:
                raise Exception("Player ID element not found")

            if str(player_id) == original_player_id:
                logger.info("Player ID already matches target ID")
                return

            # Initiate player ID change
            switch_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, PLAYER_ID_SWITCH_INITIATE_BUTTON_XPATH)))
            self.safe_click(switch_btn)
            logger.info("Player ID switch initiated")

            # Handle ID input
            id_input = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, PLAYER_ID_INPUT_FIELD_XPATH)))
            self.clear_and_type(id_input, str(player_id))

            # Confirm change
            confirm_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, PLAYER_ID_SWITCH_OK_BUTTON_XPATH)))
            self.safe_click(confirm_btn)

            # Verify change
            WebDriverWait(self.driver, 15).until(
                lambda d: self.get_current_player_id() == str(player_id))
            logger.info("Player ID successfully changed") 
        except Exception as e:
            logger.error(f"Player switch failed: {str(e)}")
            screenshot_file = "screenshots/Player switch failed.png"
            self.driver.save_screenshot(screenshot_file)
            logger.info(f"Screenshot saved as: {screenshot_file}")
            raise Exception("Invalid Player ID")

    def redeem_code(self, redeem_code):
        """Redeem code with proper error handling and status tracking"""
        try:
            # Enter redemption code
            redeem_input = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.XPATH, REDEEM_CODE_INPUT_BOX_XPATH))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", redeem_input)
                                       
            # Wait for visibility before interacting
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of(redeem_input)
            )
            
            self.clear_and_type(redeem_input, redeem_code)
            time.sleep(random.uniform(0.5, 1.2))
            
            
            # Initiate redemption
            self.driver.execute_script('document.querySelector("#root > div.App.app-wrap__relative > div.container_wrap > div.redeem_modules_box.default_box > div > div.RedeemStepBox_step_box__kecmM.RedeemStepBox_redeem_step__Cb6tE > div.RedeemStepBox_mess__6gbK6 > div.RedeemStepBox_btn_wrap__wEKY9 > div > div").click()')
            
            try:
                error_element = WebDriverWait(self.driver, 4).until(
                    EC.presence_of_element_located((By.XPATH, CODE_ERROR_NOTICE_XPATH)))

                raise Exception(error_element.text)
            except:
                pass
                
            try:
                WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, REDEEM_CODE_POP_UP_XPATH))
                )
                self.human_scroll()

                # Handle submission
                self.handle_redemption_submission()
                
                logger.info('Redemption submitted')
            except Exception:
                try:
                    ok_btn = WebDriverWait(self.driver, 4).until(
                    EC.element_to_be_clickable((By.XPATH, REDEEM_CONFIRM_BTN_POP_UP_XPATH))
                    )
                    # ok_btn = self.driver.find_element(By.XPATH, REDEEM_CONFIRM_BTN_POP_UP_XPATH)
                    self.safe_click(ok_btn)
                except Exception:
                    try:
                        error_element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, CODE_ERROR_NOTICE_XPATH)))
                        raise Exception(error_element.text)
                    except:
                        raise Exception('unknown error')
                

            # Check outcome
            return self.check_redemption_outcome()

        except Exception as e:
            raise e

    # Helper methods
    def clear_and_type(self, element, text):
        """Clear field and type text with human-like intervals"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2))

    def wait_for_page_load(self, timeout=30):
        """Wait for page to fully load"""
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def handle_redemption_submission(self):
        """Handle different submission scenarios"""
        for locator in [SUBMIT_REDEEM_CODE_BUTTON_XPATH3, SUBMIT_REDEEM_CODE_BUTTON_XPATH, SUBMIT_REDEEM_CODE_BUTTON_XPATH2]:
            try:
                btn = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, locator)))
                self.safe_click(btn)
                return
            except TimeoutException:
                continue
        raise RedemptionError("No valid submit button found")

    def check_redemption_outcome(self):
        """Check and return redemption result"""
        screenshot_path = f"screenshots/redeem_success_{int(time.time())}.png"
        self.driver.save_screenshot(screenshot_path)
        logger.info(f"Screenshot saved to {screenshot_path}")
        try:
            success_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, REDEEM_SUCCESS_NOTICE_XPATH)))
            self.driver.execute_script('#root > div > div.PaymentResult_container_wrap__ddHmB > div > div.PurchaseContainer_btn_box__7kd\+o > div > div > div > div > div')
            return True
        except Exception:
            screenshot_path = f"screenshots/redeem_success_2_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved to {screenshot_path}")
            try:
                ok_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, REDEEM_CONFIRM_BTN_POP_UP_XPATH))
                        )
                self.safe_click(ok_btn)
                
                success_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, REDEEM_SUCCESS_NOTICE_XPATH)))
                return True
            
            except Exception:
                screenshot_path = f"screenshots/redeem_success_2_{int(time.time())}.png"
                self.driver.full_Screenshot(screenshot_path)
                logger.info(f"Screenshot saved to {screenshot_path}")
                error_element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, CODE_ERROR_NOTICE_XPATH)))
                raise Exception(error_element.text)
    
    def human_scroll(self, selector=REDEEM_CODE_POP_UP_CONTENT_XPATH, portion=2):
        """Simulate human-like scrolling behavior"""
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

    browser = Browser(email=emailAddress)

    result = {}
    
    browser.visit_page()
    try:
        #
        #browser.implicitly_wait(10)
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
        for code in redeemCodes:
            try:
                redeem_status = browser.redeem_code(redeem_code=code)
                #  result['code'] = 'Successfully redeemed code'
                result[code] = redeem_status
            except Exception as err:
                result[code] = str(err)
            finally:
                continue
    except Exception as err:
        logger.error(f"Redeem code error: {code}, {str(err)}")
        raise Exception(f"Failed to redeem code: {str(err), result}")
    finally:
        return result
    
    
    

if __name__ == "__main__":
    r = process_pubg_recharge(emailAddress="nijoj40533@saierw.com", password="mMzZ8H922M6xL82c", playerId="512590258", redeemCodes=["gxNcMpjP29254cH6S8"])
    print(r)