import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import schedule
import time
import os
from datetime import datetime
import re

CHROME_DRIVER_PATH = "drivers/chromedriver.exe"


def normalize_text(text):
    return ' '.join(text.strip().split())

def table_to_json(html, case_number):
    लगाब_मुद्दाहरुको_विवरण = extract_from_table(html, "लगाब मुद्दाहरुको विवरण")
    मुद्दाको_स्थितीको_बिस्तृत_विवरण = extract_from_table(html, "मुद्दाको स्थितीको बिस्तृत विवरण")
    तारेख_विवरण = extract_from_table(html, "तारेख विवरण")
    पेशी_को_विवरण = extract_from_table(html, 'पेशी को विवरण')
    result={case_number: {"लगाब मुद्दाहरुको विवरण": लगाब_मुद्दाहरुको_विवरण, "मुद्दाको स्थितीको बिस्तृत विवरण": मुद्दाको_स्थितीको_बिस्तृत_विवरण,"तारेख विवरण": तारेख_विवरण, "पेशी को विवरण": पेशी_को_विवरण}}
    return result


def extract_from_table(html,text):
    soup = BeautifulSoup(html, "html.parser")
    normalized_text = normalize_text(text)
    element = soup.find(lambda tag: tag.name == 'th' and normalized_text in normalize_text(tag.text))

    if not element:
        print("No matching element found for the text:", text)
        return []
    
    table = element.find_next('table')
    if not table:
        print("No table found after the header with the text:", text)
        return []
    
    headers = [th.text.strip() for th in table.find('tr').find_all('td')]
    data = []
    for row in table.find_all('tr')[1:]:
        row_data = [td.text.strip() for td in row.find_all('td')]
        data.append(dict(zip(headers, row_data)))
    return data
    
def fetch_case_details(driver, registration_number):
    print("Opening the Nepal Supreme Court Website")
    url = "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details"
    driver.get(url)

    try:
        wait = WebDriverWait(driver, 3)
        print("Waiting for the input field")

        # Fill the registration number field
        regno_input = driver.find_element(By.ID, "regno")
        regno_input.send_keys(registration_number)

        # Click the submit button
        submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
        submit_button.click()

        # Wait until the table is visible
        print("Waiting for the table to load")
        table_tag = wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "table-bordered"))
        )

        # Locate the second row in the table
        rows = table_tag.find_elements(By.TAG_NAME, "tr")

        if len(rows) > 1:
            second_row = rows[1]  # Get the second row (index 1)

            # Find all the columns in the second row
            columns = second_row.find_elements(By.TAG_NAME, "td")

            # Ensure the last column contains an anchor tag and click it
            last_column = columns[-1]  # Get the last column
            anchor_tag = last_column.find_element(
                By.TAG_NAME, "a"
            )  # Find the anchor tag

            # Click on the anchor tag
            anchor_tag.click()
            print("Clicked the anchor tag in the last column")

            # Wait for the page to change
            next_page_table = wait.until(
                EC.visibility_of_element_located((By.TAG_NAME, "table"))
            )
            return next_page_table.get_attribute(
                "outerHTML"
            )  # Return HTML content as a string

        else:
            print("Table does not have enough rows")
            return None

    except Exception as e:
        print(f"An error occurred in search_and_click_result: {e}")
        return None


# Main execution
def scrape_case_details():
    hardcoded_case_numbers = [
        "080-CR-0202",
        # "080-CR-0126",
        # "080-CR-0199",
        # "080-CR-0187",
        # "080-CR-0190",
        # "080-CR-0202",
        # "080-CR-0212",
        # "080-CR-0001",
        # "080-CR-0002"
    ]

    # List to store all case details
    all_case_details = []

    print("Initializing WebDriver")

    service = Service(CHROME_DRIVER_PATH)
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # dynamic file name
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"case_details_{timestamp}.json"
    folder_name = "case_details"
    file_path = os.path.join(folder_name, file_name)

    try:
        for case_number in hardcoded_case_numbers:
            html_content = fetch_case_details(driver, case_number)

            if html_content:  # Check if we received valid HTML content
                case_details_json = table_to_json(html_content, case_number)
                all_case_details.append(case_details_json)  # Add to list

        # Save all case details to a single JSON file
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(all_case_details, json_file, ensure_ascii=False, indent=4)
        print("All case details have been saved to case_details.json")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()  # Ensure the browser closes in case of an exception


scrape_case_details()

# schedule.every().day.at("18:40").do(scrape_case_details)#have to wait a while like 16:53 and 50 seconds ma xa bhane you have to wait 10s
# schedule.every().day.at("18:42").do(scrape_case_details)

# while True:
#     print(f"Checking for pending jobs at {time.strftime('%H:%M:%S')}")
#     schedule.run_pending()
#     time.sleep(1)