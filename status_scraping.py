from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import schedule, time, csv , os


CHROME_DRIVER_PATH = 'drivers/chromedriver.exe'
CSV_FILE_PATH = 'case_status.csv'

def extract_casestatus():
    print("Initializing WebDriver")
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    url = "https://supremecourt.gov.np/web/index.php/index"
    
    print("Opening the Nepal Supreme Court Website")
    driver.get(url)
    
    try:
        print("Scraping Case Status")
        
        case_status_div = driver.find_element(By.CSS_SELECTOR, '.col-md-4.daily-status')
        table_rows = case_status_div.find_elements(By.TAG_NAME, 'tr')
        
        case_status_data = {}
        for row in table_rows:
            header = row.find_element(By.TAG_NAME, 'th').text
            value = row.find_element(By.TAG_NAME, 'td').text
            case_status_data[header] = value
        
        print("Today's Case Status:")
        print(case_status_data)

        casestatus_csv(case_status_data)

    except Exception as e:
        print(f"An error occurred: {e}")
    
    driver.quit()

def casestatus_csv(data):
    file_exists = os.path.isfile(CSV_FILE_PATH)

    with open(CSV_FILE_PATH, mode='a', newline='') as csvfile:
        fieldnames = data.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader() 

        writer.writerow(data)
        print(f"The extracted datas are saved to {CSV_FILE_PATH}")

schedule.every().day.at("20:13").do(extract_casestatus)
# schedule.every().day.at("17:30").do(extract_casestatus)

while True:
    schedule.run_pending()
    time.sleep(1)
