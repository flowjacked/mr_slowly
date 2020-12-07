from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

import time
import argparse


class Page(object):
    @classmethod
    def check_for_element(cls, selector, driver):
        return len(driver.find_elements_by_css_selector(selector)) > 0


class PageOrderReview(Page):
    page = "https://www.target.com/co-review"
    cc_cvv_input = "#creditCardInput-cvv"
    apply_a_payment_method = "#STEP_PAYMENT > div > div:nth-child(2) > div > div > a"
    place_your_order_button = "#orderSummaryWrapperDiv > div > div > div.h-padding-h-tight > div > button"
    save_and_continue_button1 = "#STEP_PAYMENT > div > div:nth-child(2) > div > div.Col-favj32-0.gghFV > div > div > button"
    save_and_continue_button2 = "#STEP_PICKUP > div.Col-favj32-0.gghFV > div > div > button"
    thanks_for_order = "#viewport > div:nth-child(5) > div.h-bg-grayLightest.h-padding-a-jumbo > h1"

    def __init__(self, cvv):
        self.cvv = cvv
        self.order_of_operations = [
            PageOrderReview.apply_a_payment_method,
            PageOrderReview.cc_cvv_input,
            PageOrderReview.save_and_continue_button1,
            PageOrderReview.save_and_continue_button2,
            PageOrderReview.place_your_order_button
        ]
        self.task_map = self.create_tasks()

    def set_operation_order(self, ops):
        self.order_of_operations = ops

    def check_success(self, driver):
        button_not_found = bool(len(driver.find_elements_by_css_selector(PageOrderReview.place_your_order_button)) == 0)
        thanks_found = bool(len(driver.find_elements_by_css_selector(PageOrderReview.thanks_for_order)) == 1)
        return button_not_found and thanks_found

    def create_tasks(self):
        def enter_cvv(driver):
            e = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, PageOrderReview.cc_cvv_input)))
            e.send_keys(self.cvv)

        def place_order(driver):
            e = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, PageOrderReview.place_your_order_button)))
            e.click()

        def save_and_continue1(driver):
            e = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, PageOrderReview.save_and_continue_button1)))
            e.click()

        def save_and_continue2(driver):
            e = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, PageOrderReview.save_and_continue_button2)))
            e.click()

        def apply_payment_method(driver):
            e = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, PageOrderReview.apply_a_payment_method)))
            e.click()

        return {
            PageOrderReview.apply_a_payment_method: apply_payment_method,
            PageOrderReview.cc_cvv_input: enter_cvv,
            PageOrderReview.save_and_continue_button1: save_and_continue1,
            PageOrderReview.save_and_continue_button2: save_and_continue2,
            PageOrderReview.place_your_order_button: place_order
        }

    def go_to_page(self, driver):
        driver.get(PageOrderReview.page)
        self.title = driver.title

    def execute_tasks(self, driver, delay, progressive_delay=False, order_of_operations=None):
        if order_of_operations is None:
            order_of_operations = self.order_of_operations
        retries_before_refresh = 3
        tried = 0
        while True:
            try:
                for i in range(2):  # lots of fancy workflows here, let's look a couple times
                    for selector in order_of_operations:
                        if self.check_for_element(selector, driver):
                            self.task_map[selector](driver)
                if self.check_success(driver):
                    break
            except Exception:
                continue
            # refreshing the page can cause unnecessary delays, let's just try again
            if retries_before_refresh == 3:
                driver.refresh()
            else:
                tried += 1
                continue
            time.sleep(delay)
            if progressive_delay:
                delay += 1
        return


class PageProduct(Page):
    pick_it_up_button = "#viewport > div:nth-child(5) > div > div.Row-uds8za-0.fMgJXz > div:nth-child(3) > div:nth-child(1) > div > div:nth-child(1) > div > div.Row-uds8za-0.fMgJXz > div.Col-favj32-0.hJZtrh.h-padding-l-tiny > button"

    def __init__(self, product_url, login_page=None, product_count=1):
        self.login_page = login_page
        self.page = product_url
        self.order_of_operations = [
            PageProduct.pick_it_up_button
        ]
        self.product_count = product_count
        self.task_map = self.create_tasks()
        self.added_to_cart = 0

    def create_tasks(self):
        def pick_it_up(driver):
            driver.find_element_by_css_selector(PageProduct.pick_it_up_button).click()

        return {
            PageProduct.pick_it_up_button: pick_it_up
        }

    def check_success(self, driver):
        return self.added_to_cart == self.product_count

    def go_to_page(self, driver):
        driver.get(self.page)
        self.title = driver.title

    def execute_tasks(self, driver, delay, progressive_delay=False, order_of_operations=None):
        if order_of_operations is None:
            order_of_operations = self.order_of_operations
        wait = True
        while wait:
            for selector in order_of_operations:
                if self.check_for_element(selector, driver):
                    self.task_map[selector](driver)
                    self.added_to_cart += 1
            if self.check_success == True:
                break
            '''    
            # Login logic if I can get it working
            try:
                if self.login_page.is_logged_out(driver):
                    self.login_page.execute_tasks(driver, delay)
            except Exception:
                self.go_to_page(driver)
                continue
            '''
            driver.refresh()
            time.sleep(delay)
            if progressive_delay:
                delay += 1
        return


class PageLogin(Page):
    page = "https://login.target.com/gsp/static/v1/login/"
    sign_in_text = "#account > span.styles__AccountName-sc-1kk0q5l-0.hVhJPq"
    sign_in_menu = "#account > span.AccountLink__SvgUserWrapper-gx13jw-0.cpETQl > span > div > svg > path"
    sign_in_link = "#accountNav-signIn > a > div"
    keep_signed_in = "#root > div > div.styles__AuthContainerWrapper-sc-1eq9g2f-1.drifUu > div > form > div.sc-jzJRlG.fnsyem.sc-ibxdXY.btPybf.nds-checkbox > label > div"
    login_email_field = "#username"
    login_password_field = "#password"
    sign_out_completely = "#invalidateSession"
    submit_button = "#login"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.title = "Target Login"
        self.order_of_operations = [
            PageLogin.sign_in_menu,
            PageLogin.sign_in_link,
            PageLogin.sign_out_completely,
            PageLogin.login_email_field,
            PageLogin.login_password_field,
            PageLogin.submit_button
        ]
        self.task_map = self.create_tasks()

    def create_tasks(self):
        def open_menu(driver):
            e = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, PageLogin.sign_in_menu)))
            e.click()

        def go_to_login(driver):
            e = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, PageLogin.sign_in_link)))
            e.click()

        def sign_out_completely(driver):
            e = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, PageLogin.sign_out_completely)))
            e.click()

        def type_username(driver):
            e = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, PageLogin.login_email_field)))
            e.click()
            e.send_keys(self.username)

        def type_password(driver):
            e = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, PageLogin.login_password_field)))
            e.click()
            e.send_keys(self.password)

        def login_submit(driver):
            e = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, PageLogin.submit_button)))
            e.click()

        return {
            PageLogin.sign_in_menu: open_menu,
            PageLogin.sign_in_link: go_to_login,
            PageLogin.sign_out_completely: sign_out_completely,
            PageLogin.login_email_field: type_username,
            PageLogin.login_password_field: type_password,
            PageLogin.submit_button: login_submit
        }

    def is_logged_out(self, driver):
        e = driver.find_elements_by_css_selector(PageLogin.sign_in_text)
        if len(e) > 0:
            if e[0].text == "Sign in":
                return True
            else:
                return False
        return False

    def go_to_page(self, driver):
        driver.get(self.page)
        self.title = driver.title

    def check_success(self, driver):
        return driver.title != self.title

    def execute_tasks(self, driver, delay, progressive_delay=False, order_of_operations=None):
        if order_of_operations is None:
            order_of_operations = self.order_of_operations
        while True:
            for selector in order_of_operations:
                if self.check_for_element(selector, driver):
                    self.task_map[selector](driver)
            if self.check_success == True:
                break
            driver.refresh()
            time.sleep(delay)
            if progressive_delay:
                delay += 1
        return


class PageCart(Page):
    page = "https://www.target.com/co-cart"
    ready_to_checkout_button = "#orderSummaryWrapperDiv > div > div > div.h-padding-h-tight.h-margin-b-default > button"

    def __init__(self):
        self.order_of_operations = [
            PageCart.ready_to_checkout_button
        ]
        self.task_map = self.create_tasks()
        self.added_to_cart = 0

    def create_tasks(self):
        def ready_to_checkout(driver):
            driver.find_element_by_css_selector(PageCart.ready_to_checkout_button).click()

        return {
            PageCart.ready_to_checkout_button: ready_to_checkout
        }

    def check_success(self, driver):
        return driver.title != self.title

    def go_to_page(self, driver):
        driver.get(PageCart.page)
        self.title = driver.title

    def execute_tasks(self, driver, delay, progressive_delay=False, order_of_operations=None):
        if order_of_operations is None:
            order_of_operations = self.order_of_operations
        wait = True
        while wait:
            for selector in order_of_operations:
                if self.check_for_element(selector, driver):
                    self.task_map[selector](driver)
            if self.check_success:
                wait = False
            if not wait:
                break
            driver.refresh()
            time.sleep(delay)
            if progressive_delay:
                delay += 1
        return


def start_mr_slowly(product_url, cvv, username, password, order_count=1, delay=5):
    """
    Login manually during the 30 second wait. It'll loop endlessly waiting for the "pick it up" button to appear
    it should complete the purchase

    :param product_url:         Product you're trying to purchase
    :param cvv:                 CVV 3 digit code on your CC. Presumably you've already saved address and CC on your account
    :param delay:               Delay between page refreshes
    :return:
    """
    count = 0
    driver = webdriver.Chrome()
    login = PageLogin(username, password)
    product = PageProduct(product_url, login)
    cart = PageCart()
    order_review = PageOrderReview(cvv)
    driver.get("https://www.target.com")
    time.sleep(45)  # gives you time to login
    #login.execute_tasks(driver, delay)
    while count < order_count:
        product.go_to_page(driver)
        # Product purchase should be 3 to 4 seconds after this point
        product.execute_tasks(driver, delay)
        cart.go_to_page(driver)
        cart.execute_tasks(driver, delay)
        order_review.go_to_page(driver)
        order_review.execute_tasks(driver, delay)
        count += 1
    driver.close()


if __name__ == "__main__":
    """
    Simple selenium bot to complete purchase at Target for a product once "Pick it up" is available. 
    
    NOTE: for any of this to work, setup an account on target.com. Setup your shipping address. Save a credit card
          the script doesn't put any of the info in when you checkout.
          
    Software setup:      
    - Install python for your O/S (Windows, Linux, macos)
    - Install selenium from command line like: 
        - python -m pip install selenium
        - ... or python -m pip3 install selenium
    - Install webdriver for chrome (ex. Windows)
        1. Download the GeckoDriver
        2. Extract it using WinRar or any application you may have.
        3. Add it to Path using Command Prompt
             - setx path "%path%;c:/user/eliote/Desktop/geckodriver-v0.26.0-win64/geckodriver.exe"
             NOTE: the path in this example might be a little different depending on where it installed
    
    Usage:
    "< ... >" in the example denote what's inside is user provided. Do not put in angle brackets or quotes
    python target.py  --refresh-delay <delay between page refreshes> --cvv <your CC code> --url <ps5 url>
    """
    parser = argparse.ArgumentParser("Start a target selenium bot", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cvv", dest='cvv', required=True, help="security code for the CC you setup on target")
    parser.add_argument("--user", dest='user', required=False, help="user")
    parser.add_argument("--pass", dest='password', required=False, help="password")
    parser.add_argument("--order-count", dest='order_count', required=False, help="1 product per order, will try for multiple orders", default=1)
    parser.add_argument("--url", dest="url", required=True, help="This the URL shown in the address bar of your browser for the product you want")
    parser.add_argument("--refresh-delay", dest='refresh_delay', required=False, help="how many seconds to wait between page refresh", default=5)
    args = parser.parse_args()
    start_mr_slowly(args.url, args.cvv, args.user, args.password, int(args.order_count), int(args.refresh_delay))