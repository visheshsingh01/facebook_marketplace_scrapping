# Reddit Scraper Initial Setup

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

# Set up Selenium WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-notifications")
    browser = webdriver.Chrome(options=options)
    browser.maximize_window()
    return browser

keyword = 'caterpillar'
search_scrolls = 5


def search_and_scrap(browser, keyword) :
    try : 
        browser.get(f"https://www.reddit.com/search/?q={keyword}")
        time.sleep(5)

        try:
            last_height = browser.execute_script("return document.body.scrollHeight")
            for _ in range(search_scrolls):
                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)
                new_height = browser.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print("✅ No more content to load. Performing final scroll attempt... 🔄")
                    time.sleep(3)
                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)
                    break
                last_height = new_height
        except Exception as e:
            print("❌ Error in scrolling:", e)

        # search_bar = WebDriverWait(browser, 10).until(
        # EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='q']"))
        #                             )
        # search_bar.send_keys(keyword)

        # search_bar = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.input-container.activated input[name='q']"))).send_keys(keyword)

        posts = WebDriverWait(browser, 10).until(EC.visibility_of_all_elements_located((By.XPATH, "//a[@data-testid='post-title']")))
        if posts : 
            print(f"all posts found {len(posts)}")
        else: 
            print("The class for the products not found :")
        
    except Exception as e: 
        print("No posts found",e)
 
    try:
            
            for idx, post in enumerate(posts):
                print(f"\n🔍 Processing product {idx + 1}/{len(posts)}...")
                actions = ActionChains(browser)
                actions.move_to_element(post).perform()
                time.sleep(1)
                
                # Scroll the product into view before clicking
                browser.execute_script("arguments[0].scrollIntoView(true);", post)
                time.sleep(1)
                
                # Click the product
                try:
                    post.click()
                    print("👉 Clicked on the product")
                except Exception as click_error:
                    print("❌ Error clicking the product:", click_error)
                    continue  # Skip to the next product if click fails
                time.sleep(5)

                browser.back()
                WebDriverWait(browser, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")


                time.sleep(3)

    except Exception as e: 
        print("Error in clicking the products",e)
        

    


# Main function to start scraping
def main():
    browser = setup_driver()
    browser.get("https://www.reddit.com")
    WebDriverWait(browser, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
    search_and_scrap(browser, keyword)
    
    browser.quit()
    

if __name__ == "__main__":
    main()
