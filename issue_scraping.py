from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

CHROME_DRIVER_PATH = 'drivers/chromedriver.exe'

def search_and_click_result(driver, registration_number):
    print("Opening the Nepal Supreme Court Website")
    url = "https://supremecourt.gov.np/web/index.php/index"
    url_to_casedetails = "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details"
    driver.get(url)

    try:
        driver.find_element()
        # print("Filling the Registration Number")

        # # Locate the input field for registration number
        # regno_input = driver.find_element(By.ID, 'regno')
        # regno_input.send_keys(registration_number)

        # # Submit the form (adjust the selector if necessary)
        # submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
        # submit_button.click()

        # time.sleep(2)  # Wait for the results to load

        # # Locate the result table (adjust the selector if necessary)
        # print("Locating the result table")
        # table = driver.find_element(By.CSS_SELECTOR, 'table')  # Assuming the results are in a table

        # # Get the first row
        # first_row = table.find_element(By.TAG_NAME, 'tr')

        # # Extract the first column (adjust the selector if necessary)
        # first_column_value = first_row.find_element(By.TAG_NAME, 'td').text
        # print(f"First Column Value: {first_column_value}")

        # # Click on the last column of the first row
        # print("Clicking the last column")
        # last_column = first_row.find_elements(By.TAG_NAME, 'td')[-1]  # Last column
        # last_column.click()

        # # You can add further actions after clicking, like scraping or navigating to a new page
        # print("Successfully clicked the last column")

    except Exception as e:
        print(f"An error occurred in search_and_click_result: {e}")

def extract_table_data(driver):
    try:
        # Wait for the page to load
        time.sleep(3)

        # Locate the main table using its class name (or you can use XPath if more specific)
        table = driver.find_element(By.CSS_SELECTOR, 'table.table-hover')

        # Extract all rows within the table
        rows = table.find_elements(By.TAG_NAME, 'tr')
        
        rows[1]

        # Iterate through the rows and extract the content of each cell
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            cell_data = [cell.text for cell in cells]
            print(cell_data)  # You can process this data further as needed

    except Exception as e:
        print(f"An error occurred in extract_table_data: {e}")

# Main execution
if __name__ == "__main__":
    print("Initializing WebDriver")
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    try:
        # First, search and click the result
        registration_number = '080-CR-0199'
        search_and_click_result(driver, registration_number)

        # Now, extract the table data after clicking
        extract_table_data(driver)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()  # Ensure the browser closes in case of an exception
