import re  
import time
import json
import os 
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException


# Set up logging to file "error_log.txt" at ERROR level
logging.basicConfig(
    filename="error_log.txt",
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Global scraping configurations
search_scrolls = 2  # (Not used directly here; scroll limits are defined later)
search_keyword = "caterpillar"
facebook_username = "vishesh@brancosoft.com"
facebook_password = "Brancosoft@1234"

def selenium_config():
    """
    Setup Selenium with Chrome using specific options.
    - Ignores certificate errors.
    - Sets log level to suppress extra output.
    - Maximizes the browser window.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-notifications")
    browser = webdriver.Chrome(options=options)
    browser.maximize_window()
    return browser

def facebook_login(browser):
    """
    Log into Facebook using the provided credentials.
    Waits for the page to load completely.
    """
    try:
        # Navigate to Facebook login page
        browser.get("https://www.facebook.com/")
        # Wait for page to fully load
        WebDriverWait(browser, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
        # Wait for and locate the email and password input fields
        username = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
        password = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))
        # Clear any pre-filled data and enter credentials
        username.clear()
        username.send_keys(facebook_username)
        password.clear()
        password.send_keys(facebook_password)
        # Click the login button
        WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        # Wait for the page after login to load completely
        WebDriverWait(browser, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")
        print("✅ Login successful!")
        time.sleep(20)  # Extra wait to allow manual captcha if necessary
        return True
    except Exception as e:
        print("❌ Login failed:", e)
        logging.error("Login failed: %s", e)
        return False

def navigate_to_marketplace(browser, search_keyword):
    try : 
        marketplace_url = f"https://www.facebook.com/marketplace/delhi/search/?query={search_keyword}"
        browser.get(marketplace_url)
        WebDriverWait(browser, 10).until(lambda d : d.execute_script("return document.readyState") == "complete")
        print("✅ Succesfully navigated to marketplace")
        return True
       
        
    except Exception as e: 
        print("⚠️ Error in reaching to marketplace")
        return False
    
import time

def scrape_products(browser, search_scrolls): 
    """
    Scrolls down the page multiple times to load more products.
    
    Parameters:
    - browser (WebDriver): Selenium WebDriver instance.
    - search_scrolls (int): Number of times to scroll down.
    
    Returns:
    - None (Modifies the browser state)
    """
    try:
        # Scroll to load products
        try: 
            last_height = browser.execute_script("return document.body.scrollHeight")
            for _ in range(search_scrolls):  
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")  
                time.sleep(5)  
                new_height = browser.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print("✅ No more content to load. Stopping scrolling.")
                    break  
                last_height = new_height
        except Exception as e: 
            print("Error in scrolling:", e)

        # Save the page source
        html_content = browser.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        file_path = "parsed_page.html"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(soup))
            print(f"HTML saved to {file_path}")

        # Get all products
        products = WebDriverWait(browser, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".x3ct3a4"))
        )
        print(f"✅ Retrieved {len(products)} products from the marketplace.")

        try:
            image_arr = []
            for product in products: 
                actions = ActionChains(browser)
                actions.move_to_element(product).perform()
                
                # Click the product
                try:
                    product.click()
                    print("Clicked on the product")
                except Exception as click_error:
                    print("Error clicking the product:", click_error)
                    continue  # Skip to the next product if click fails

                time.sleep(5)

                # Extract title
                try:
                    title = browser.find_element(By.CSS_SELECTOR, "h1 span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x14z4hjw.x3x7a5m.xngnso2.x1qb5hxa.x1xlr1w8.xzsf02u")
                    print("Title:", title.text)
                except Exception as e:
                    print("Title not found:", e)

                # Extract price
                try:
                    price = browser.find_element(By.CSS_SELECTOR, "div.xyamay9.x1pi30zi.x18d9i69.x1swvt13 span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x1lliihq.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.xudqn12.x676frb.x1lkfr7t.x1lbecb7.x1s688f.xzsf02u")
                    print("Price:", price.text)
                except Exception as e:
                    print("Price not found:", e)

                # Extract description
                try:
                    description = WebDriverWait(browser, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".xz9dl7a.x4uap5.xsag5q8.xkhd6sd.x126k92a"))
                    )
                    browser.execute_script("arguments[0].scrollIntoView(true);", description)
                    print("Description:", description.text)
                except Exception as e:
                    print("Description not found:", e)

                # Extract location
                try:
                    location = WebDriverWait(browser, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.x14vqqas.x11i5rnm.xod5an3.x1mh8g0r span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x6prxxf.xvq8zen.x1s688f.xzsf02u"))
                    )
                    browser.execute_script("arguments[0].scrollIntoView(true);", location)
                    print("Location:", location.text)
                except Exception as e:
                    print("Location not found:", e)

                # Extract images and carousel images
                try:
                    initial_image = WebDriverWait(browser, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "span.x78zum5.x1vjfegm img"))
                    )
                    initial_image_url = initial_image.get_attribute("src")
                    if initial_image_url:
                        image_arr.append(initial_image_url)
                        while True: 
                            try:
                                carousel_button = WebDriverWait(browser, 10).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".__fb-light-mode.x1afcbsf.x10l6tqk.x1i018f6.x1ja2u2z.x160vmok"))
                                )
                                print("Carousel button found:", carousel_button)
                                carousel_button.click()
                                print("Carousel button clicked")
                                time.sleep(2)
                                new_image = WebDriverWait(browser, 10).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "span.x78zum5.x1vjfegm img"))
                                )
                                new_image_url = new_image.get_attribute("src")
                                if new_image_url != initial_image_url:
                                    image_arr.append(new_image_url)
                                else:
                                    break 
                            except Exception as e:
                                print("No carousel button found for this product:", e)
                                break
                    else:
                        print("Image URL not found")
                except Exception as e:
                    print("Error processing images:", e)

                browser.back()
                time.sleep(3)  # Wait for page to load before processing next product

        except Exception as e:
            print("Error in processing products:", e)
        
        

    except Exception as e: 
        print("⚠️ Error in getting the products:", e)




    



def scrape_facebook_data():
    """
    Main function to run the Facebook Marketplace scraper.
    Logs in, navigates to the Marketplace, scrolls to load products,
    then iterates through each product to open and close it while extracting data.
    """
    browser = selenium_config()
    success = facebook_login(browser)
    if not success:
        print("❌ Stopping scraper due to login failure.")
        browser.quit()
        return
    
    if not navigate_to_marketplace(browser, search_keyword):
        print("❌ Stopping scraper due to navigation failure.")
        browser.quit()
        return
    
    scrape_products(browser, search_scrolls)
    
    

    browser.quit()

# Run the scraper
scrape_facebook_data()
