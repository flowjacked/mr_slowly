from selenium import webdriver
import time
import argparse


def wait_for_cart_enabled(selector, driver, delay=None):
    """
    Finds the selector and if it can click it successfully, then exit
    :param selector:        CSS identifier in the HTML for selenium to know what you're looking for
    :param driver:          selenium driver you created in "start"
    :return:
    """
    wait = True
    while wait:
        try:
            element = driver.find_element_by_css_selector(selector)
            if element is not None and element.is_enabled():
                element.click()
                wait = False
            else:
                if delay is not None:
                    time.sleep(delay)
                driver.refresh()
        except Exception as ex:
            time.sleep(delay)
            driver.refresh()
            continue


def start_mr_slowly(user, password, security_code, product_url, delay=None):
    """
    Logs you in, visits the URL and refreshes the page until "Add to cart" shows up. It'll click the link
    then check if it sees "go to cart", if not, then starts again. GameStop may ban your IP if you let this run endlessly.
    If all goes well, it'll purchase the item for you. Reliability is questionable, so you probably should be watching
    it to save it from itself if it screws up. Still, if you have to visit the bathroom, there is a very good chance
    it'll complete the purchase without you (>80%).
    :param user:
    :param password:
    :param security_code:       CVV 3 digit code on your CC. Presumably you've already saved address and CC on your account
    :param product_url:         Product you're trying to purchase
    :param delay:               Delay between page refreshes
    :return:
    """
    # load gamestop
    driver = webdriver.Chrome()
    driver.get("https://www.gamestop.com")
    account = driver.find_element_by_css_selector("body > div.page > div.main-header-container.sticky-header-redesign > header > nav > div.header.container.header-redesign > div > div.header-options.col-3.col-lg-auto > div.account-header > div.header-account-options.tulsa-acclink-toggle > div.user > a > span.account-icon.account")
    account.click()
    time.sleep(1)

    # Sign in
    driver.find_element_by_css_selector("#signIn").click()
    time.sleep(1)
    driver.find_element_by_css_selector("input#login-form-email.form-control").send_keys(user)
    driver.find_element_by_css_selector("input#login-form-password.form-control.password-field").send_keys(password)
    driver.find_element_by_css_selector("#signinCheck > button").click()

    # Load product page
    driver.get(product_url)
    time.sleep(2)
    add_to_cart = "button.add-to-cart.btn.btn-primary"

    while True:
        wait_for_cart_enabled(add_to_cart, driver, delay)
        time.sleep(1)
        try:
            # Sometimes "add to cart" is clickable but gives you an error, so this next command would fail. if so, we start over...
            go_to_cart = "#addedToCartModal > div > div > div.modal-body > div.top.redesign-top.master-product > div.ready-to-checkout > div > div > a"
            go_to_cart_button = driver.find_element_by_css_selector(go_to_cart)
            go_to_cart_button.click()
        except Exception as e:
            continue

    # Click checkout button
    time.sleep(1)
    driver.find_element_by_css_selector("body > div.page > div.container.cart.cart-page.mb-3 > div.row.cart-rd.container.m-0.p-0 > div.col-12.col-lg-3.totals.cart-rd.mt-3.mt-lg-0 > div.row.p-2.bg-white.mb-3 > div.col-12.checkout-continue-redesign.p-0.tulsa-checkoutbutton-toggle > div > a").click()

    # Sign in again for checkout... thanks gamestop. Real slick
    time.sleep(1)
    driver.find_element_by_css_selector("input#login-form-email.form-control").send_keys(user)
    driver.find_element_by_css_selector("input#login-form-password.form-control.password-field").send_keys(password)
    driver.find_element_by_css_selector("#signinCheck > button").click()

    # Put in CVV code from credit card
    time.sleep(1)
    element = driver.find_element_by_css_selector("#checkout-main > div.row.no-gutters.next-step-button.justify-content-center.workflow-button > div > div > div > button.btn.btn-primary.btn-block.submit-shipping")
    element.click()
    time.sleep(2)
    cvv_selector = "input#saved-payment-security-code.form-control.saved-payment-security-code"
    driver.find_element_by_css_selector(cvv_selector).send_keys(security_code)
    order_review = "button.btn.btn-primary.btn-block.submit-payment"
    driver.find_element_by_css_selector(order_review).click()

    time.sleep(1)
    place_order = "button.btn.btn-primary.btn-block.place-order"
    #place_order = "#checkout-main > div:nth-child(2) > div.col-12.col-lg-3.order-summary-section.right-rail > div:nth-child(1) > div.card-body.order-total-summary > div.next-step-summary-button > button"
    place_order_button = driver.find_element_by_css_selector(place_order)
    time.sleep(1)
    place_order_button.click()


if __name__ == "__main__":
    """
    Simple selenium bot to complete purchase at GameStop for a product once "Add cart" is available. 
    
    NOTE: for any of this to work, setup a value gamstop.com account. Setup your shipping address. Save a credit card
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
    python turtlebot.py --user <your email or login> --password <your password> --CCcode <your CC code> --url https://www.gamestop.com/video-games/playstation-5/consoles/products/playstation-5-digital-edition-black-friday-system-bundle/B225171G.html>
    """
    parser = argparse.ArgumentParser("Start a gamestop selenium bot", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--user", dest='user', required=True, help="name of your gamestop user")
    parser.add_argument("--password", dest='password', required=True, help="password for your gamestop account")
    parser.add_argument("--CCcode", dest='security_code', required=True, help="security code for the CC you setup on gamstop")
    parser.add_argument("--url", dest='url', required=True, help="This the URL shown in the address bar of your browser for the product you want")
    parser.add_argument("--refresh-delay", dest='refresh_delay', required=False, help="how many seconds to wait between page refresh")
    args = parser.parse_args()
    start_mr_slowly(args.user, args.password, args.security_code, args.url, args.refresh_delay)