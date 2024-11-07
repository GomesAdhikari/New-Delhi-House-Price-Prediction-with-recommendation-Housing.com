import requests
import random
import os
import time
from bs4 import BeautifulSoup
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from src.logger import logger


@dataclass
class DataSource:
    """Making a class to store data link and data path."""
    link: str = "https://housing.com/in/buy/new_delhi/new_delhi?page="
    data_path: str = os.path.join(os.getcwd(), "data", "new_delhi_data.csv")


class PageScrapper:
    """This class contains all functions to scrape data from the URL."""
    
    def __init__(self):
        self.link = DataSource()
        self.links_list = []
        self.lxml_list = []
        self.all_property_links = []
        logger.info("Data objects Created.")
    
    def scrap_pages(self, proxy_list):
        """Function to extract URLs of multiple pages and their lxml text using threading and proxies."""
        
        def fetch_page(i):
            # Choose a random proxy from the proxy list
            proxy = random.choice(proxy_list)
            proxies = {"http": proxy, "https": proxy}
            logger.info(f"Page Scrapping Has been Started with proxies {proxy_list} [fetching each page]")
            try:
                url = f"{self.link.link}{i}"
                response = requests.get(url, proxies=proxies, timeout=5)
                response.raise_for_status()  # Raise an error for bad responses
                soup = BeautifulSoup(response.text, "lxml")
                print(f"Successfully scraped page {i} with proxy {proxy}")
                return url, soup
            except (requests.RequestException, Exception) as e:
                print(f"Failed to scrape page {i} with proxy {proxy}: {e}")
                return None, None

        with ThreadPoolExecutor(max_workers=10) as executor:  # Adjust max_workers based on your system capacity
            future_to_page = {executor.submit(fetch_page, i): i for i in range(2, 10000)}
            
            for future in as_completed(future_to_page):
                url, soup = future.result()
                if url and soup:
                    self.links_list.append(url)
                    self.lxml_list.append(soup)

    def remove_duplicates(self):
        """Function to remove duplicates from lxmls"""
        logger.info("Removing Duplicates from Data objects")

        seen = set()
        unique_list = []
    
        for item in self.links_list:
            if item not in seen:
               unique_list.append(item)
               seen.add(item)
        self.links_list = unique_list
        
        seen_lxml = set()
        unique_list_lxml = []
    
        for item in self.lxml_list:
            if item not in seen_lxml:
               unique_list_lxml.append(item)
               seen.add(item)
        self.lxml_list = unique_list_lxml

    def extract_each_property(self):
        """Extract links of each property from each page"""
        logger.info('Extracting link of each property.')
        links_list = []

        for tree in self.lxml_list:
            # Extract all links matching the specific class using XPath
            links = tree.xpath('//a[contains(@class, "_j31f9d _c8dlk8 _g3l52n _csbfng _frwh2y T_e4485809 _ks15vq _vv1q9c _sq1l2s T_091c165f")]/@href')
            # Add extracted links to the list
            for link in links:
               links_list.append(link)

        # Create a full list with absolute URLs
        full_list = ['https://housing.com' + link for link in links_list]
        self.all_property_links = full_list
        logger.info("Link extraction of each property has been completed")

    def extract_property_data(self, soup, property_headers):
        """Extract property data from the page."""
        property_data = {header: None for header in property_headers}
        for header in property_headers:
            th_tag = soup.find('th', text=header)
            if th_tag:
                td_tag = th_tag.find_next_sibling('td')
                if td_tag:
                    property_data[header] = td_tag.get_text(strip=True)
        return property_data

    def find_distance(self, soup, category):
        """Find distance for given category (school, hospital, etc.)"""
        category_div = soup.find('div', text=lambda t: t and category.lower() in t.lower())
        if category_div:
            distance_div = category_div.find_next('div', class_='_h31y44 _csbfng _c819bv _r3usic _vy1osq T_e080fff7')
            if distance_div:
                return distance_div.get_text(strip=True)
        return None

    def save_to_csv(self, data, file_path):
        """Save the scraped data to CSV."""
        df_property_data = pd.DataFrame([data])
        df_property_data.to_csv(file_path, mode='a', header=not pd.io.common.file_exists(file_path), index=False)
        logger.info("Data added to CSV.")

    def scrape_property(self, url, proxies, property_headers = ['Price', 'Carpet Area', 'Bedrooms', 'Bathrooms', 'Parking', 'Balcony']):
        """Scrape and save data for a given property URL."""
        user_agents = [
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
                        ]
        try:
            # Randomly select a proxy
            proxy = random.choice(proxies)
            proxies_dict = {"http": proxy, "https": proxy}
            headers = {"User-Agent": random.choice(user_agents)}

            # Request property page data
            response = requests.get(url, headers=headers, proxies=proxies_dict, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')

                # Extract property data
                data = self.extract_property_data(soup, property_headers)

                # Extract additional data
                data['Location'] = soup.find('div', class_='css-1ty5xzi').text if soup.find('div', class_='css-1ty5xzi') else None
                data['Star_emi'] = soup.find('a', class_="css-0", attrs={'href': '/home-loans-emi-calculator'}).text if soup.find('a', class_="css-0", attrs={'href': '/home-loans-emi-calculator'}) else None
                data['school_distance'] = self.find_distance(soup, 'School')
                data['hospital_distance'] = self.find_distance(soup, 'Hospital')
                data['link'] = url
                data['About_property'] = soup.find('div', class_='T_5255c66f _lorj18uv _v1ivgktf _g31tcg _7l9wsg _h3f6fq T_a3fd8ac3 _1ln11vji').get_text() if soup.find('div', class_='T_5255c66f _lorj18uv _v1ivgktf _g31tcg _7l9wsg _h3f6fq T_a3fd8ac3 _1ln11vji') else None

                # Save data to CSV
                self.save_to_csv(data, self.link.data_path)
                logger.info(f"Data for {url} added to CSV.")
            else:
                logger.error(f"Failed to retrieve data for {url} with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error occurred while scraping {url}: {e}")

    def scrape_all_properties(self, proxy_list, property_headers):
        """Scrape all properties and save them."""
        with ThreadPoolExecutor(max_workers=10) as executor:
            for url in self.all_property_links:
                executor.submit(self.scrape_property, url, proxy_list, property_headers)
