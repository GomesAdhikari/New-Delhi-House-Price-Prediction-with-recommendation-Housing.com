import requests
from bs4 import BeautifulSoup
import time
from dataclasses import dataclass

@dataclass
class DataSource:
    '''
    making class for managing soup the content of pages'''
    link

class PageScrapper(DataSource):

    def __init__(self):
        self.soup = BeautifulSoup(DataSource('https://housing.com/in/buy/new_delhi/new_delhi?page='))

    def extract_pages(self):


        

