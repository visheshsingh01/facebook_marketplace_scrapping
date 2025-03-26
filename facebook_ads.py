import time
import json
import logging
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Set up Selenium WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return browser

# Generate dynamic Facebook Ads Library URL
def get_facebook_ads_url(keyword, country="IN"):
    encoded_keyword = urllib.parse.quote(keyword)
    return f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={country}&is_targeted_country=false&media_type=all&q={encoded_keyword}&search_type=keyword_unordered"

# Scroll function to load more ads
def scroll_page(browser, scrolls=5):
    last_height = browser.execute_script("return document.body.scrollHeight")
    for _ in range(scrolls):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for content to load
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            logging.info("✅ No more content to load.")
            break
        last_height = new_height

# Extract ad details and handle the popup
def extract_ads(browser):
    try:
        # Wait until the page is fully loaded
        WebDriverWait(browser, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        print("Page has fully loaded!")
       
        # Get the list of ad elements using the CSS selector
        ads_elements = browser.find_elements(
            By.CSS_SELECTOR, 
            "div.x193iq5w.xxymvpz.xeuugli.x78zum5.x1iyjqo2.xs83m0k.x1d52u69.xktsk01.x1yztbdb.x1gslohp"
        )
        ads_count = len(ads_elements)
        print(f"Number of ads: {ads_count}")

        # Iterate over the actual elements
        for ad in ads_elements:
            try:                
                # Attempt to find the "See ad details" element
                try:
                    WebDriverWait(browser, 10).until(
                        lambda d: d.execute_script("return document.readyState") == "complete"
                    )

                    see_ad_details = ad.find_element(By.XPATH, ".//div[contains(text(), 'See ad details')]")
                    
                    # Scroll the element into view
                    browser.execute_script("arguments[0].scrollIntoView(true);", see_ad_details)
                    
                    # Wait until the element is clickable
                    WebDriverWait(browser, 10).until(
                        EC.element_to_be_clickable((By.XPATH, ".//div[contains(text(), 'See ad details')]"))
                    )
                    
                    # Click using JavaScript to bypass click interception
                    browser.execute_script("arguments[0].click();", see_ad_details)
                    
                    print("See ad details clicked, popover opened")
                    time.sleep(3)
                except Exception as click_exception:
                    print("Unable to click 'See ad details':", click_exception)

                try: 
                    title = browser.find_element(By.CSS_SELECTOR, "div.x2izyaf.x1lq5wgf.xgqcy7u.x30kzoy.x9jhf4c.xyamay9.x1pi30zi.x1l90r2v.x1swvt13.x1741yl6.x1xqjhkw span.x8t9es0.xw23nyj.x63nzvj.x1fp01tm.xq9mrsl.x1h4wwuj.x117nqv4.xeuugli.x1i64zmx")
                    print("the title is ", title.text)

                

                
                except Exception as e : 
                    print("No title found",)

                try : 
                    pop_ad_container = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.x2izyaf.x1lq5wgf.xgqcy7u.x30kzoy.x9jhf4c.xyamay9.x1pi30zi.x1l90r2v.x1swvt13.x1741yl6.x1xqjhkw")))
                    library_id = pop_ad_container.find_element(By.XPATH, ".//span[contains(text(), 'Library ID:')]")
                    print(library_id.text)
                except Exception as e: 
                    print("No library id found")

                try: 
                    pop_ad_container = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.x2izyaf.x1lq5wgf.xgqcy7u.x30kzoy.x9jhf4c.xyamay9.x1pi30zi.x1l90r2v.x1swvt13.x1741yl6.x1xqjhkw")))
                    library_id = pop_ad_container.find_element(By.XPATH, ".//span[contains(text(), 'Started running on')]")
                    print(library_id.text)
                except Exception as e:
                    print("No started running on found")
                

                try : 
                    ad_text = WebDriverWait(browser, 10).until(
                                    EC.visibility_of_element_located(
                                        (By.CSS_SELECTOR, 'div.x178xt8z.xm81vs4.xso031l.xy80clv.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x15bcfbt.xolcy6v.x3ckiwt.xc2dlm9.x2izyaf.x1lq5wgf.xgqcy7u.x30kzoy.x9jhf4c.x1t2gpz5.x9f619.x6ikm8r.x10wlt62.x1n2onr6 div[style="white-space: pre-wrap;"] span')
                                    )
                                )
                    text = ad_text.text
                    print("ad text: ", text)

                except Exception as e : 
                    print("no text  found for the ad")

                try : 
                    about_ad = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.x6s0dn4.x1ypdohk.x78zum5.x1q0g3np.x1p5oq8j.xxbr6pl.xwxc41k.xbbxn1n")))
                    browser.execute_script("arguments[0].scrollIntoView(true);", about_ad)
                    about_ad.click()

                    try : 
                        about_advertiser = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.x78zum5.xwxc41k.x7a106z span.x8t9es0.x1uxerd5.xrohxju.x108nfp6.xq9mrsl.x1h4wwuj.x117nqv4.xeuugli")))
                        if about_advertiser: 
                            print("about advertiser is found", about_advertiser.text)

                    except Exception as e : 

                        print('about advertiser is not found')

                    try:
                        advertiser_logo_element = WebDriverWait(browser, 10).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.x78zum5.xwxc41k.x7a106z img"))
                        )
                        advertiser_logo = advertiser_logo_element.get_attribute('src')
                        print("This is advertiser image:", advertiser_logo)

                    except Exception as e:
                        print("No image is found for the advertiser. Error:", str(e))

                    
                except Exception as e : 
                    print("Dropdown for the ad bio is not found")

                    


                
                # Pause to let the popover load or for any additional actions
                time.sleep(5)
                try:
                    close_button = WebDriverWait(browser, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.x7a106z.x78zum5.x2lah0s.x9otpla.x1wsgfga.x1n0m28w"))
                    )
                    if close_button:
                        browser.execute_script("arguments[0].scrollIntoView(true);", close_button)
                        print("Close button found for current pop-up, clicking to close it.")
                        close_button.click()
                        time.sleep(5)
                except Exception as e:
                        print("No close button found for current pop-up:", e)

                
                

                    

                    


                

            except Exception as e:
                print("Error processing ad:", e)


                
                
    except Exception as e:
        print("Unable to find ad elements:", e)



# Main function
def main():
    keyword = "caterpillar"
    fb_ads_url = get_facebook_ads_url(keyword)

    browser = setup_driver()
    browser.get(fb_ads_url)
    time.sleep(5)

    scroll_page(browser, scrolls=5)  # Ensure more ads are loaded
    extract_ads(browser)

    browser.quit()

if __name__ == "__main__":
    main()