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

def search_and_scrap(browser, keyword):
    try: 
        browser.get(f"https://www.reddit.com/search/?q={keyword}")
        time.sleep(5)

        # Scroll to load more posts
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

        # Find posts
        posts = WebDriverWait(browser, 10).until(
            EC.visibility_of_all_elements_located((By.XPATH, "//a[@data-testid='post-title']"))
        )

        print(f"✅ Found {len(posts)} posts.")

    except Exception as e: 
        print("❌ No posts found:", e)
        return  # Exit if no posts found

    # Loop through posts
    for idx in range(len(posts)):
        try:
            # Re-fetch the posts list after each navigation
            posts = WebDriverWait(browser, 10).until(
                EC.visibility_of_all_elements_located((By.XPATH, "//a[@data-testid='post-title']"))
            )

            if idx >= len(posts):  
                print(f"⚠️ Skipping post {idx + 1}, list updated and index out of range.")
                continue

            post = posts[idx]

            # Click the post
            actions = ActionChains(browser)
            actions.move_to_element(post).perform()
            browser.execute_script("arguments[0].scrollIntoView();", post)
            time.sleep(1)
            browser.execute_script("arguments[0].click();", post)
            print(f"👉 Clicked on post {idx + 1}")
            time.sleep(5)  # Process the post details

            try : 
                subreddit_name = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.subreddit-name.whitespace-nowrap.text-12.text-neutral-content.font-bold.cursor-pointer")))
                subreddit_name = subreddit_name.text
                print(f"📚 Subreddit name: {subreddit_name}")
            except Exception as e : 
                print(f"❌ Subreddit name not found",e)
                subreddit_name = "Not found"

            try : 
                author_name = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.author-name.whitespace-nowrap.text-neutral-content")))
                author_name = author_name.text
                print(f"👥 Author name: {author_name}")
            
            except Exception as e : 
                print("Author name is not found")
                author_name = "Not found"


            try : 
                                # Using CSS selector with an ID:
                title = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[aria-label^="Post Title:"]'))
                )

                title = title.text
                print(title)
            except Exception as e : 
                print("no title found")
            # Go back to the search results page

            try :
                 
                video_elem = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))

)
                
                image_elem = WebDriverWait(browser, 10).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "img#post-image"))
                )


                if video_elem:

                    video_src = video_elem.get_attribute("src")
                    print("Video Source:", video_src)

                elif image_elem:
                    image_src = image_elem.get_attribute("src")
                    print("imgae source :",image_src)
                elif not image_elem and not video_elem: 
                    print("Neither video not image is available for this post")
            except : 
                print("No video or image is available for this post")



                



            browser.back()
            WebDriverWait(browser, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
            
            time.sleep(3)

            

            


            # try : 
            #     author_name = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "")))
            #     author_name = author_name.text
            #     print(f"👥 Author name: {author_name}")
            
            # except Exception as e : 
            #     print("Author name is not found")
            #     author_name = "Not found"

            
        
                




        except Exception as e:
            print(f"❌ Error processing post {idx + 1}:", e)
            





# Main function to start scraping
def main():
    browser = setup_driver()
    browser.get("https://www.reddit.com")
    WebDriverWait(browser, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
    search_and_scrap(browser, keyword)
    browser.quit()

if __name__ == "__main__":
    main()
