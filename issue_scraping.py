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

CHROME_DRIVER_PATH = 'drivers/chromedriver.exe'
CSV_FILE_PATH = 'issue_numbers.csv'
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def clean_key(key):
    """Helper function to clean keys by removing extra spaces and periods."""
    return ' '.join(key.split()).replace(".", "").strip()  # Remove extra spaces and periods

def clean_value(value):
    """Helper function to clean values by removing extra spaces."""
    return ' '.join(value.split()) if isinstance(value, str) else value  # Clean only if it's a string

def table_to_json(html):
    soup = BeautifulSoup(html, 'html.parser')
    result = {}
    current_parent = None

    for row in soup.find_all('tr'):
        header = row.find('th')
        if header:
            # Set the current parent based on header
            current_parent = clean_key(header.text.strip().replace('\n', ''))
            # Initialize with an empty list for "लगाब मुद्दाहरुको विवरण"
            if current_parent == "लगाब मुद्दाहरुको विवरण":
                result[current_parent] = []  # Initialize as a list
        else:
            cells = row.find_all('td')
            if cells and current_parent == "लगाब मुद्दाहरुको विवरण":
                # Prepare a new entry for this specific section
                entry = {}
                # Ensure we have pairs of cells
                for i in range(0, len(cells), 2):  
                    key = clean_key(cells[i].get_text(strip=True).replace('\n', ''))
                    # Get the next cell as value, if it exists
                    value = clean_value(cells[i + 1].get_text(strip=True).replace('\n', '')) if (i + 1) < len(cells) else ""

                    # Add to entry if the key is not empty
                    if key and value:
                        entry[key] = value

                # Append the entry only if it's not empty
                if entry:
                    result[current_parent].append(entry)
            elif cells:
                # For other sections, treat the data as key-value pairs
                for i in range(0, len(cells), 2):  # Process pairs of cells
                    key = clean_key(cells[i].get_text(strip=True).replace('\n', ''))
                    value = clean_value(cells[i + 1].get_text(strip=True).replace('\n', '')) if (i + 1) < len(cells) else None
                    
                    # Only add non-empty keys and values
                    if key and value and current_parent:
                        if current_parent not in result:
                            result[current_parent] = {}  # Ensure the parent exists
                        result[current_parent][key] = value

    # Merging keys into a single structure
    if "लगाब मुद्दाहरुको विवरण" in result:
        merged_data = {}
        for entry in result["लगाब मुद्दाहरुको विवरण"]:
            for key, value in entry.items():
                merged_data[key] = value  # Assign last value for each key

        result["लगाब मुद्दाहरुको विवरण"] = merged_data  # Replace list with merged data

    return result

def replace_null_with_empty(data):
    """Recursively replace None values with empty strings in the JSON data."""
    if isinstance(data, dict):
        return {k: replace_null_with_empty(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_null_with_empty(item) for item in data]
    elif data is None:
        return ""
    else:
        return data
    
def fetch_case_details(driver, registration_number):
    print("Opening the Nepal Supreme Court Website")
    url = "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details"
    driver.get(url)

    try:
        wait = WebDriverWait(driver, 10)  # Increased wait time
        print("Waiting for the input field")

        # Fill the registration number field
        regno_input = driver.find_element(By.ID, "regno")
        regno_input.send_keys(registration_number)

        # Click the submit button
        submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
        submit_button.click()

        # Wait until the table is visible
        print("Waiting for the table to load")
        table_tag = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "table-bordered")))

        # Locate the second row in the table
        rows = table_tag.find_elements(By.TAG_NAME, "tr")

        if len(rows) > 1:
            second_row = rows[1]  # Get the second row (index 1)

            # Find all the columns in the second row
            columns = second_row.find_elements(By.TAG_NAME, 'td')

            # Ensure the last column contains an anchor tag and click it
            last_column = columns[-1]  # Get the last column
            anchor_tag = last_column.find_element(By.TAG_NAME, 'a')  # Find the anchor tag

            # Click on the anchor tag
            anchor_tag.click()
            print("Clicked the anchor tag in the last column")

            # Wait for the table to load on the new page
            next_page_table = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "table")))
            return next_page_table.get_attribute('outerHTML')  # Return HTML content as a string

        else:
            print("Table does not have enough rows")
            return None

    except Exception as e:
        print(f"An error occurred in fetch_case_details: {e}")
        return None

# Main execution
def scrape_case_details():
    print("Initializing WebDriver")
    
    service = Service(CHROME_DRIVER_PATH)
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Create folder if it doesn't exist
    folder_name = "case_details"
    os.makedirs(folder_name, exist_ok=True)

    # Dynamic file name
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    file_name = f'case_details_{timestamp}.json'
    file_path = os.path.join(folder_name, file_name)

    all_case_details = []

    try:
        with open(CSV_FILE_PATH, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                case_number = row['case_number']
                html_content = fetch_case_details(driver, case_number)

                if html_content:
                    case_details_json = table_to_json(html_content)
                    case_details_json = replace_null_with_empty(case_details_json)  # Clean the data
                    all_case_details.append(case_details_json)

        # Save all case details to a single JSON file
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(all_case_details, json_file, ensure_ascii=False, indent=4)
        print(f"All case details have been saved to {file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:    
        driver.quit()  # Ensure the browser closes in case of an exception

scrape_case_details()
# schedule.every().day.at("10:30").do(scrape_case_details)
# schedule.every().day.at("17:30").do(scrape_case_details)

# Start the scheduling loop
while True:
    schedule.run_pending()
    time.sleep(1)  