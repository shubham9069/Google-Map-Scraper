import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import copy
from selenium.common.exceptions import StaleElementReferenceException
import traceback
import re
from urllib.parse import urlparse, parse_qs


class DealerInfoExtractor:
    def __init__(self, driver, pincode):
        self.driver = driver
        self.pincode = pincode
        self.retryMap = {}

    def is_last_element_visible(self):
        try:
            end_marker = self.driver.find_element(By.CLASS_NAME, 'HlvSq')
            return end_marker.is_displayed()
        except Exception:
            return False

    def clean_text(self, text):
        """Remove unwanted Unicode characters, extra spaces, but keep printable and rating-related characters."""
        if text:
            # Allow certain rating symbols like stars (★/☆) while removing unwanted non-printable characters
            # Use regex to remove only specific non-printable characters, while keeping stars
            text = re.sub(r'[^\x20-\x7E★☆]', '', text)  # Allow ASCII + common rating symbols (★, ☆)
            # Remove extra spaces
            return text.strip()
        return None

        
    # def parse_html_into_json(self, html_content):
    #     soup = BeautifulSoup(html_content, 'html.parser')
    #     dealer_info = {"pincode": self.pincode}

    #     dealer_info['name'] = self.get_text(soup,True)
    #     dealer_info['rating'], dealer_info['reviews'] = self.get_rating_and_reviews(soup)
    #     dealer_info['dealer_type'] = self.get_text(soup.find('button', class_='DkEaL'))
    #     dealer_info['website'] = self.get_website(soup)
    #     dealer_info['address'] = self.get_text(soup.find('button', class_='CsEnBe', attrs={'data-tooltip': 'Copy address'}))
    #     dealer_info['plus_code'] = self.get_text(soup.find('button', class_='CsEnBe', attrs={'data-tooltip': 'Copy plus code'}))
    #     dealer_info['phone'] = self.get_text(soup.find('button', class_='CsEnBe', attrs={'data-tooltip': 'Copy phone number'}))
    #     print(dealer_info)
    #     return dealer_info

    def get_text_old(self, element, name = False):
        if name:
            text_element = element.find('h1', class_='DUwDvf')
            return text_element.text.strip() if text_element else None
        if element:
            text_element = element.find('div', class_='fontBodyMedium')
            print(text_element)
            return text_element.text.strip() if text_element else None
        return None

    def get_rating_and_reviews_old(self, soup):
        rating = None
        reviews = None
        rating_elements = soup.find('div', class_='F7nice').find_all('span')
        for span in rating_elements:
            if span.get('aria-hidden') == 'true':
                rating = span.text.strip()
            if span.get('aria-label') and 'review' in span.get('aria-label'):
                reviews = span.text.strip().replace('(', '').replace(')', '')
        return rating, reviews

    def get_text(self, element):
        """Helper function to get text from an element."""
        return self.clean_text(element.get_text(strip=True)) if element else None
    
    def get_rating_and_reviews(self, soup):
        """Extract rating and review count from the parsed HTML soup."""
    
        # First, let's try to extract the rating
        rating_element = soup.find('span', class_='F7nice')  # This is the class that often holds the rating
        rating = self.get_text(rating_element)
        
        # Extract the reviews count
        review_element = soup.find('span', {'aria-label': lambda x: x and 'reviews' in x})
        reviews = self.get_text(review_element)
        
        return rating, reviews
    
    def get_dealer_place_id(self, url):

        parsed_url = urlparse(url)
        path_params = parsed_url.path.split("/")[-1]
        data_params = path_params.split("data=")[1] if "data=" in path_params else None
        extracted_data = {}
    
    # Parse coordinates if present
        if data_params:
            # Split components by "!"
            components = data_params.split("!")
            for component in components:
                if component.startswith("3d"):  # Latitude
                    extracted_data['latitude'] = component[2:]
                elif component.startswith("4d"):  # Longitude
                    extracted_data['longitude'] = component[2:]
                elif component.startswith("1s"):  # Place ID
                    extracted_data['place_id'] = component[2:]
        
        # Return a dictionary with all extracted info
        return extracted_data
            
    
    def parse_html_into_json(self, html_content,dealer_url):
        html = html_content
        
        """Parse dealer information from the HTML."""
        soup = BeautifulSoup(html, 'html.parser')

        # Extract name
        dealer_name = self.get_text(soup.find('h1', class_='DUwDvf'))
        dealer_url = dealer_url
        
        # Extract rating and reviews
        rating, reviews = self.get_rating_and_reviews_old(soup)
        
        # Extract category
        category_element = soup.find('button', class_='DkEaL')
        category = self.get_text(category_element)
        
        # Extract website
        website_element = soup.find('a', attrs={'aria-label': lambda x: x and 'Website' in x})
        website = website_element['href'] if website_element else None
        
        # Extract address
        address_element = soup.find('button', class_='CsEnBe', attrs={'data-item-id': 'address'})
        address = self.get_text(address_element)
        
        # Extract plus code
        plus_code_element = soup.find('button', class_='CsEnBe', attrs={'data-tooltip': 'Copy plus code'})
        plus_code = self.get_text(plus_code_element)
        
        # Extract phone
        phone = self.get_text_old(soup.find('button', class_='CsEnBe', attrs={'data-tooltip': 'Copy phone number'}))
        dealer_place_id_data = self.get_dealer_place_id(dealer_url)

        # Return the extracted information in a dictionary
        
        dealer_info = {
            'pincode': self.pincode,    
            'name': dealer_name,
            'address': address,
            'phone': phone,
            'website': website,
             "metadata": {
                    "plus_code": plus_code,
                    "rating": rating,
                    "reviews": reviews,
                    "dealer_type": category,
                    "dealer_url":dealer_url,
                    **dealer_place_id_data


                }        }
        print(dealer_info)
        return dealer_info
 


    def get_website(self, soup):
        website_link = soup.find('a', class_='CsEnBe', attrs={'data-tooltip': 'Open website'})
        if website_link and 'href' in website_link.attrs:
            return website_link['href'].split('=')[1] if '=' in website_link['href'] else website_link['href']
        return None

    def extract_dealer_information(self, dealer_element):
        dealer_name = dealer_element.get_attribute('aria-label')
        dealer_url = dealer_element.get_attribute('href')
        if not dealer_name:
            print("Dealer name attribute missing.")
            return None
        dealer_name = dealer_name.split("·")[0].strip()
        try:
            dealer_details_element = self.find_element_by_attribute('div', 'aria-label', dealer_name)
            if dealer_details_element and dealer_details_element.get_attribute('role') == 'main':
                html_content = dealer_details_element.get_attribute('innerHTML')
                return self.parse_html_into_json(html_content,dealer_url)
        except Exception as e:
            print(f"Error extracting dealer information: {e}")
        return None

    def get_all_dealers(self, results_div):
        dealers_details = []
        retry_array = []
        try:
            dealer_elements = WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "hfpxzc")))
            self.process_dealer_elements(dealer_elements, dealers_details, retry_array)
            if retry_array:
                print(f"Retrying {len(retry_array)} elements")
                self.process_dealer_elements(retry_array, dealers_details, retry_array, delay=1)
        except Exception as e:
            print(f"Error finding dealer elements: {e}")
        return dealers_details

    def process_dealer_elements(self, elements, dealers_details, retry_array, delay=0):
        for dealer_element in elements:
            try:
                open_button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(dealer_element))
                time.sleep(delay)
                self.driver.execute_script("arguments[0].click()", open_button)
                dealer_info = self.extract_dealer_information(open_button)
                if dealer_info:
                    dealers_details.append(dealer_info)
            except Exception as e:
                retry_array.append(dealer_element)
                print(f"Error processing dealer element: {e}")

    def scroll_bottom(self, element):
        max_scroll_attempts = 10
        last_height = self.driver.execute_script("return arguments[0].scrollHeight;", element)
        for _ in range(max_scroll_attempts):
            try:
                self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", element)
                time.sleep(2)
                new_height = self.driver.execute_script("return arguments[0].scrollHeight;", element)
                if new_height == last_height:
                    print("Reached the bottom of the scrollable element.")
                    break
                last_height = new_height
            except Exception as e:
                traceback.print_exc()
                print(f"Error during scrolling: {e}")
                break


    def find_element_by_attribute(self, tag, attr_name, attr_value):
        try:
            return WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'{tag}[{attr_name}="{attr_value}"]')))
        except Exception:
            return None

    def remove_back_to_top_button(self):
        try:
            self.driver.execute_script("""
            var l = document.querySelectorAll('[aria-label="Back to top"]');
            if (l.length > 0) {
                l[0].parentNode.removeChild(l[0]);
            }
            """)
        except Exception:
            pass