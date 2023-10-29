import os.path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import WebDriverException
import platform


def get_chrome_bin_loc():
    return os.path.join(os.getcwd(), "binaries", "chrome", "chrome")


def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--ignore-ssl-errors=yes")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.AcceptInsecureCertificates = True
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.accept_insecure_certs = True
    if platform.system().lower() == "linux":
        chrome_options.binary_location = get_chrome_bin_loc()
    return chrome_options


def get_redirected_url(url: str) -> (bool, str):
    chrome_service = ChromeService(executable_path=os.path.join(os.getcwd(), "binaries", "chromedriver"))
    driver = webdriver.Chrome(service=chrome_service, options=get_chrome_options())
    # Check for redirection
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(ec.presence_of_element_located((By.TAG_NAME, 'body')))
        cur_url = driver.current_url

        return True, cur_url
    except WebDriverException as e:
        return False, e.msg
    finally:
        driver.quit()
