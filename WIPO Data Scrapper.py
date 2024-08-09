import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Set up Selenium with Chrome
chrome_options = Options()
service = Service()  # Replace with the path to your chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Function to save progress by writing the last successfully scraped application count to a file
def save_progress(app_count):
    with open('progress.txt', 'w') as f:
        f.write(str(app_count))

# Function to load the last saved application count from the progress file
def load_progress():
    if os.path.exists('progress.txt'):
        with open('progress.txt', 'r') as f:
            return int(f.read().strip())
    return 0  # Start from the first application if no progress file is found

# Function to extract text from an element
def extract_text(element):
    return element.get_text(strip=True) if element else "N/A"

# Function to get value by label using the new structure
def get_value_by_label(soup, label):
    parent_div = soup.find('div', class_='ps-biblio-data')
    if not parent_div:
        return "N/A"
    
    label_element = parent_div.find('span', class_='ps-field--label', string=lambda text: label in text)
    if label_element:
        value_element = label_element.find_next('span', class_='ps-field--value')
        return extract_text(value_element)
    
    return "N/A"

# Function to select a date from the dropdown
def select_date_from_dropdown(driver, date_value):
    try:
        dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.b-step__content select.b-input__dropdown-input"))
        )
        select = Select(dropdown)
        select.select_by_value(date_value)
        time.sleep(2)  # Wait for the page to update after selecting the date
    except Exception as e:
        print(f"Error selecting date {date_value}: {e}")

# Function to navigate to the next page
def navigate_to_next_page(driver):
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.ui-paginator-next"))
        )
        next_button.click()
        time.sleep(3)  # Wait for the next page to load
    except Exception as e:
        print(f"Error navigating to the next page: {e}")

# Function to process all applications on the current page
# Function to process all applications on the current page
def process_applications_on_page(driver, start_app_index):
    applications = driver.find_elements(By.CSS_SELECTOR, "div.ui-datatable-tablewrapper a.detail-link")
    
    for i in range(start_app_index, len(applications)):
        try:
            # Re-locate the application link to avoid StaleElementReferenceException
            applications = driver.find_elements(By.CSS_SELECTOR, "div.ui-datatable-tablewrapper a.detail-link")
            app_link = applications[i]
            app_link.click()
            time.sleep(3)  # Wait for the application details page to load
            
            app_soup = BeautifulSoup(driver.page_source, 'html.parser')
            publication_number = get_value_by_label(app_soup, 'Publication Number')
            publication_date = get_value_by_label(app_soup, 'Publication Date')
            applicants = get_value_by_label(app_soup, 'Applicants')
            inventors = get_value_by_label(app_soup, 'Inventors')
            agents = get_value_by_label(app_soup, 'Agents')
            title = get_value_by_label(app_soup, 'Title')
            priority_data = get_value_by_label(app_soup, 'Priority Data')
            publication_language = get_value_by_label(app_soup, 'Publication Language')
            filing_language = get_value_by_label(app_soup, 'Filing Language')
            international_application = get_value_by_label(app_soup, 'International Application No.')
            international_filing_date = get_value_by_label(app_soup, 'International Filing Date')

            scraped_data.append({
                'Publication Number': publication_number,
                'Publication Date': publication_date,
                'Applicants': applicants,
                'Inventors': inventors,
                'Agents': agents,
                'Title': title,
                'International Application No.': international_application,
                'International Filing Date': international_filing_date,
                'Priority Data': priority_data,
                'Publication Language': publication_language,
                'Filing Language': filing_language,
            })
            
            # Save every 80 applications
            if len(scraped_data) % 80 == 0:
                save_data()
                save_progress(i + 1)
            
            driver.back()  # Return to the main page
            time.sleep(3)  # Wait for the main page to load
        except Exception as e:
            print(f"Error processing application at index {i}: {e}")


# Function to save the scraped data to an Excel file
def save_data():
    output_df = pd.DataFrame(scraped_data)
    output_df.to_excel('scraped_data.xlsx', index=False)
    print("Data saved to 'scraped_data.xlsx'.")

# Initialize the list to store scraped data
scraped_data = []

# Load progress from the last saved application count
start_app_index = load_progress()

# Visit the main link
driver.get('https://patentscope.wipo.int/search/en/resultWeeklyBrowse.jsf')
time.sleep(5)  # Wait for the page to load

# Select the desired date from the dropdown (for example, "31/2024")
select_date_from_dropdown(driver, "31/2024")

while True:
    # Process all applications on the current page starting from the last unsaved application
    process_applications_on_page(driver, start_app_index)
    
    # Save data after processing the page
    save_data()

    # Reset the starting application index for the next page
    start_app_index = 0

    # Attempt to navigate to the next page
    try:
        navigate_to_next_page(driver)
    except:
        print("No more pages available.")
        break

# Close the browser
driver.quit()

print("Scraping completed.")
