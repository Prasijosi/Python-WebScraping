import requests
from bs4 import BeautifulSoup
import json
import schedule
import time

def parse_table_to_json(html):
    soup = BeautifulSoup(html, 'html.parser')
    result = {}
    current_parent = None

    for row in soup.find_all('tr'):
        header = row.find('th')
        if header:
            current_parent = header.text.strip().replace('\n', '')
            result[current_parent] = {}
        else:
            cells = row.find_all('td')
            if cells:
                for i in range(0, len(cells), 2):  # Take pairs of cells
                    key = cells[i].get_text(strip=True).replace('\n', '').strip()
                    value = cells[i + 1].get_text(strip=True) if (i + 1) < len(cells) else None
                    if current_parent:
                        result[current_parent][key] = value

    return result

def search_and_click_result(registration_number):
    print("Opening the Nepal Supreme Court Website")
    url = "https://supremecourt.gov.np/lic/sys.php?d=reports&f=case_details"
    
    # Simulate the form submission by passing the registration number as data
    payload = {'regno': registration_number}
    
    try:
        # Send the POST request to the server
        response = requests.post(url, data=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            print(f"Successfully retrieved data for {registration_number}")
            return response.text  # Return HTML content as a string
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred in search_and_click_result: {e}")
        return None

# Main execution
def scrape_case_details():
    hardcoded_case_numbers = [
        "080-CR-0096",
        "080-CR-0126",
        "080-CR-0199",
        "080-CR-0187",
        "080-CR-0190",
        "080-CR-0202",
        "080-CR-0212",
        "080-CR-0001",
        "080-CR-0002"
    ]
    
    all_case_details = []  # List to store all case details

    try:
        for number in hardcoded_case_numbers:
            html_content = search_and_click_result(number)
            
            if html_content:  # Check if we received valid HTML content
                case_details_json = parse_table_to_json(html_content)
                all_case_details.append(case_details_json)  # Add to list

        # Save all case details to a single JSON file
        with open('case_details.json', 'w', encoding='utf-8') as json_file:
            json.dump(all_case_details, json_file, ensure_ascii=False, indent=4)
        print("All case details have been saved to case_details.json")

    except Exception as e:
        print(f"An error occurred: {e}")

# Scheduling the scraping
schedule.every().day.at("16:45").do(scrape_case_details)
# schedule.every().day.at("17:30").do(scrape_case_details)

while True:
    schedule.run_pending()
    time.sleep(1)
