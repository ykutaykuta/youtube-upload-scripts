import json
import time
from typing import Dict, List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

""" Login module """


def domain_to_url(domain: str) -> str:
    """ Converts a (partial) domain to valid URL """
    if domain.startswith("."):
        domain = "www" + domain
    return "http://" + domain


def login_using_cookie_file(driver: WebDriver, cookie_file: str):
    domain_cookies: Dict[str, List[object]] = {}
    with open(cookie_file) as file:
        cookies: List = json.load(file)
        # Sort cookies by domain, because we need to visit to domain to add cookies
        for cookie in cookies:
            try:
                domain_cookies[cookie["domain"]].append(cookie)
            except KeyError:
                domain_cookies[cookie["domain"]] = [cookie]

    for domain, cookies in domain_cookies.items():
        driver.get(domain_to_url(domain + "/robots.txt"))
        time.sleep(1)
        for cookie in cookies:
            cookie.pop("sameSite", None)  # Attribute should be available in Selenium > 4
            cookie.pop("storeId", None)  # Firefox container attribute
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"Couldn't set cookie {cookie['name']} for {domain} Exception: {e}")


def confirm_logged_in(driver: WebDriver) -> bool:
    """ Confirm that the user is logged in. The browser needs to be navigated to a YouTube page. """
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "avatar-btn")))
        return True
    except TimeoutError:
        return False
