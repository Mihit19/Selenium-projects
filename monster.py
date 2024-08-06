"""Monster Daily update - Using Chrome"""

import os
import sys
import time
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime


# Update your Monster username and password here before running
username = "xxxxxxxxxxxx"
password = "xxxxxxxx"



# Set login URL
MonsterURL = "https://www.foundit.in/rio/login"
MonsterProfileURL = "https://www.foundit.in/seeker/profile?application_source=organic&"
logfile = "E:\\ProfileUpdatePgms\\monster.log"

logging.basicConfig(
    level=logging.INFO, filename=logfile, format="%(asctime)s    : %(message)s"
)
# logging.disable(logging.CRITICAL)
os.environ['WDM_LOCAL'] = "1"
os.environ["WDM_LOG_LEVEL"] = "0"


def log_msg(message):
    """Print to console and store to Log"""
    print(message)
    logging.info(message)


def catch(error):
    """Method to catch errors and log error details"""
    exc_type, exc_obj, exc_tb = sys.exc_info()
    lineNo = str(exc_tb.tb_lineno)
    msg = "%s : %s at Line %s." % (type(error), error, lineNo)
    print(msg)
    logging.error(msg)


def getObj(locatorType):
    """This map defines how elements are identified"""
    map = {
        "ID" : By.ID,
        "NAME" : By.NAME,
        "XPATH" : By.XPATH,
        "TAG" : By.TAG_NAME,
        "CLASS" : By.CLASS_NAME,
        "CSS" : By.CSS_SELECTOR,
        "LINKTEXT" : By.LINK_TEXT
    }
    return map[locatorType]


def GetElement(driver, elementTag, locator="ID"):
    """Wait max 15 secs for element and then select when it is available"""
    try:
        def _get_element(_tag, _locator):
            _by = getObj(_locator)
            if is_element_present(driver, _by, _tag):
                return WebDriverWait(driver, 15).until(
                    lambda d: driver.find_element(_by, _tag))

        element = _get_element(elementTag, locator.upper())
        if element:
            return element
        else:
            log_msg("Element not found with %s : %s" % (locator, elementTag))
            return None
    except Exception as e:
        catch(e)
    return None


def is_element_present(driver, how, what):
    """Returns True if element is present"""
    try:
        driver.find_element(by=how, value=what)
    except NoSuchElementException:
        return False
    return True


def WaitTillElementPresent(driver, elementTag, locator="ID", timeout=30):
    """Wait till element present. Default 30 seconds"""
    result = False
    driver.implicitly_wait(0)
    locator = locator.upper()

    for i in range(timeout):
        '''time.sleep(0.99)'''
        try:
            if is_element_present(driver, getObj(locator), elementTag):
                result = True
                break
        except Exception as e:
            log_msg('Exception when WaitTillElementPresent : %s' %e)
            pass

    if not result:
        log_msg("Element not found with %s : %s" % (locator, elementTag))
    driver.implicitly_wait(3)
    return result


def tearDown(driver):
    try:
        driver.close()
        log_msg("Driver Closed Successfully")
    except Exception as e:
        catch(e)
        pass

    try:
        driver.quit()
        log_msg("Driver Quit Successfully")
    except Exception as e:
        catch(e)
        pass



def LoadMonster(headless):
    """Open Chrome to load Monster.com"""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")  # ("--kiosk") for MAC
    options.add_argument("--disable-popups")
    options.add_argument("--disable-gpu")
    if headless:
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("headless")

    # updated to use ChromeDriverManager to match correct chromedriver automatically
    driver = None
    try:
        driver = webdriver.Chrome(executable_path=CM().install(), options=options)
    except:
        driver = webdriver.Chrome(options=options)
    log_msg("Google Chrome Launched!")

    driver.implicitly_wait(3)
    driver.get(MonsterURL)
    return driver

#all code ok till here
def LoginMonster(headless = False):
    """ Open Chrome browser and Login to Monster.com"""
    status = False
    driver = None

    try:
        driver = LoadMonster(headless)

        if "foundit" in driver.title.lower():
            log_msg("Website Loaded Successfully.")

        emailFieldElement = None
        loginViaPasswordXpath = "//div[@class='loginWith']"
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, loginViaPasswordXpath)))
        loginViaPasswordButton = GetElement(driver, loginViaPasswordXpath, locator="XPATH")
        loginViaPasswordButton.click()
        if is_element_present(driver, By.ID, "signInName"):
            emailFieldElement = GetElement(driver, "signInName", locator="ID")
            time.sleep(1)
            passFieldElement = GetElement(driver, "password", locator="ID")
            time.sleep(1)
            loginXpath = "//*[@type='submit' and @value='Login']"
            loginButton = GetElement(driver, loginXpath, locator="XPATH")


        if emailFieldElement is not None:
            emailFieldElement.clear()
            emailFieldElement.send_keys(username)
            time.sleep(1)
            passFieldElement.clear()
            passFieldElement.send_keys(password)
            time.sleep(1)
            loginButton.send_keys(Keys.ENTER)
            time.sleep(5)

            return (True, driver)

    except Exception as e:
        catch(e)
    return (status, driver)


def UpdateProfile(driver):
    try:
        saveXpath = "//button[@class='btn pmedium pTB10 wt-100']"
        editXpath = "//i[@class='mqfisrp-edit']"

        #WaitTillElementPresent(driver, profeditXpath, "XPATH", 20)
        '''profElement = GetElement(driver, profeditXpath, locator="XPATH")
        profElement.click()'''
        driver.get(MonsterProfileURL)
        driver.implicitly_wait(2)

        #WaitTillElementPresent(driver, editXpath + " | " + saveXpath, "XPATH", 20)
        if is_element_present(driver, By.XPATH, editXpath):
            editElement = GetElement(driver, editXpath, locator="XPATH")
            editElement.click()


            saveFieldElement = GetElement(driver, saveXpath, locator="XPATH")
            saveFieldElement.send_keys(Keys.ENTER)
            driver.implicitly_wait(3)

            WaitTillElementPresent(driver, "//p[text()='Section updated successfully']", "XPATH", 10)
            if is_element_present(driver, By.XPATH, "//p[text()='Section updated successfully']"):
                log_msg("Profile Update Successful")
            else:
                log_msg("Profile Update Failed")


        time.sleep(5)

    except Exception as e:
        catch(e)





def main():
    #log_msg("Execution count "+str(ExcecutionCount)+ "  -----Monster.py Script Run Begin-----")
    driver = None
    
    with open(logfile, 'r') as file:
        lines = file.readlines()
        if lines:
            last_line = lines[-2].strip()
            log_msg("Program last ran on "+last_line[:10])
    
    today_date = datetime.now().strftime("%Y-%m-%d")
    log_msg("program started running on " + today_date)
    alwaysRun = True
    
    if alwaysRun : #today_date != last_line[:10] : 
        try :
            status, driver = LoginMonster()
            if status:
                UpdateProfile(driver)
            
        except Exception as e:
            catch(e)

        finally:
            tearDown(driver)

    log_msg("  -----Monster.py Script Run Ended-----\n")


if __name__ == "__main__": 
   #while True:
       main()