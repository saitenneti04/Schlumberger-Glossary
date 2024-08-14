import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

# Set up Chrome options for Selenium
options = webdriver.ChromeOptions()
options.add_argument('--headless')  
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920x1080') 

# Initialise the WebDriver with Chrome options
driver = webdriver.Chrome(options=options)

# Open the glossary search page 
driver.get("https://glossary.slb.com/en/search#sort=relevancy")

# Opens CSV file for writing
with open('alphabetical_terms.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Title row
    writer.writerow(['Word', 'Definition'])

    # Function to extract titles and descriptions from the current page
    def extract_titles_and_descriptions():
        # Waiting so that the search results are fully loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "row-thumbs__wrapper"))
        )

        # The elements with class "glossary-title thumb__title CoveoFieldValue" represent the words
        titles = driver.find_elements(By.CLASS_NAME, "glossary-title.thumb__title.CoveoFieldValue")

        # The elements with class "thumb__desc CoveoFieldValue" represent the definitions
        descriptions = driver.find_elements(By.CLASS_NAME, "thumb__desc.CoveoFieldValue")

        # For testing purposes
        if not titles:
            print("No titles found on this page.")
        else:
            print(f"Found {len(titles)} titles on this page.")

        # Write each word and its definition to the CSV file
        for title, description in zip(titles, descriptions):
            writer.writerow([title.text, description.text])

    # Tracks the no. of pages processed so far
    page_counter = 0

    # Loops until there's no more pages
    while True:
        print(f"Processing page {page_counter + 1}...")
        #called for each page to write word and def for all words on a single page
        extract_titles_and_descriptions()

        # Handles any cookie consent popups - was an issue initially so had to include
        try:
            cookie_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Accept All Cookies"]')
            cookie_button.click()
            print("Cookie consent accepted.")
        except NoSuchElementException:
            print("No cookie consent popup found.")
            pass

        try:
            # Look for "Next" button and click it if present
            next_button = driver.find_element(By.CSS_SELECTOR, 'li.coveo-pager-next span[aria-label="Next"]')
            print("Next button found. Clicking...")
            
            # Use JavaScript to click the "Next" button
            driver.execute_script("arguments[0].click();", next_button)
            
            # Pause for next page to load
            WebDriverWait(driver, 10).until(
                EC.staleness_of(next_button)
            )
            
            page_counter += 1
            # delay to avoid pushing the server too much
            time.sleep(3)  

        except NoSuchElementException:
            print("No more pages to navigate.")
            break

        except ElementClickInterceptedException:
            print("Element click was intercepted. Trying to scroll into view and click again.")
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            driver.execute_script("arguments[0].click();", next_button)

driver.quit()
