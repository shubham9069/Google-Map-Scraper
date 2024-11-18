import os
import sys
import time
from selenium import webdriver
from extract_dealer_info import DealerInfoExtractor  # Importing the class


# Constants for HTTP headers and search parameters
HEADERS = {
    "Accept": "application/xhtml+xml, text/html, application/xml, */*; q=0.9,image/webp,image/apng, */*;",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com",
    "User-Agent": "PostmanRuntime/7.42.0"
}

# Configuration for scrolling behavior
SECONDS_BEFORE_SCROLL = 1
driver = None
def setup_webdriver():
    headOption = webdriver.FirefoxOptions()
    # headOption.add_argument("--headless")
    driver = webdriver.Firefox(options=headOption)
    return driver

# Initialize the WebDriver

def extract_html_content(base_url, search_query, pincode):
    formatted_search = search_query.replace("+", " ")
    print("Navigating to:", base_url)
    try:
        driver.get(base_url)
    except Exception as e:
        print(f"Error navigating to {base_url}: {e}")
        return []
    
    time.sleep(2)
    # Initialize the DealerInfoExtractor with the driver
    extractor = DealerInfoExtractor(driver, pincode)

    driver.execute_script("""
            var l = document.getElementsByClassName('DuI1J');
            if (l.length > 0) {
                l[0].parentNode.removeChild(l[0]);
            }
            """)

    results_div = extractor.find_element_by_attribute("div", "aria-label", f"Results for {formatted_search}")
    if not results_div:
        print("Results container not found.")
        return []
    
    extractor.scroll_bottom(results_div)

    dealer_list = extractor.get_all_dealers(results_div)
    return dealer_list

def handler():
    global driver
    driver = setup_webdriver()
    # print('Hello from AWS Lambda using Python' + sys.version + '!')
    # data = event['Records'][0]['body']
    
    zip_code = "122001" 
    print("Current zip code:", zip_code)
    if zip_code is None:
        print("No more zip codes to process. Exiting.")
        return
    try:
        SEARCH_QUERY = f"food+stores+in+{zip_code},india"
        BASE_URL = f"https://www.google.com/maps/search/{SEARCH_QUERY}"
        get_dealer = extract_html_content(BASE_URL, SEARCH_QUERY, zip_code)
            
        if get_dealer is not None and len(get_dealer) > 0:
            print(get_dealer)
        else:
            print(f"No dealers found for zip code: {zip_code}")
            
    except Exception as e:
        print(f"Error processing zip code {zip_code}: {e}")

if __name__ == "__main__":
    handler()

    

