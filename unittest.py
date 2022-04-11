import requests
from bs4 import BeautifulSoup
from time import sleep
import re
import time

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
           'Accept-Language': 'en-US, en;q=0.5'}


def scraper(base_url):
    """This scraper function scrap the product url,product price ,review from the ecommerce website"""
    total_pages = 1
    next_page = "Next"
    while next_page != "":
        response = requests.get(base_url + '&page={0}'.format(total_pages), headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            next_page = soup.find('a', {
                'class': 's-pagination-item s-pagination-next s-pagination-button s-pagination-separator'}).text
        except AttributeError:
            break
        total_pages += 1


    for page in range(1, total_pages + 1):
        # print('Processing {0}...'.format(base_url + '&page={0}'.format(page)))
        response = requests.get(base_url + '&page={0}'.format(page), headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        results = soup.find_all('div', {'class': 's-result-item', 'data-component-type': 's-search-result'})

        items = []  # collecting list of records in this list
        for result in results:
            product_name = result.h2.text
            # creating record of each product
            try:
                rating = result.find('i', {'class': 'a-icon'}).text
                print(rating)
                total_rating_count = result.find('span', {'class': 'a-size-base'}).text
            except AttributeError:
                continue

                try:
                    current_price = result.find('span', {'class': 'a-price-whole'}).text
                    actual_price = result.find('span', {'class': 'a-price a-text-price'}).text
                    actual_price = re.sub("^₹.*₹", "_", actual_price).strip("_")
                    product_url = 'https://amazon.in' + result.h2.a['href']

                    print(product_url)
                    review, confidence = sentiment(product_url)
                    print(review, confidence)
                    items.append([product_name, rating, total_rating_count, current_price, actual_price, product_url,
                                  review, confidence])


                except AttributeError:
                    continue
print(scraper.__doc__)


def itemlist(search_list):

    for i in search_list:
        search_query = i.replace(' ', '+')
        base_url = 'https://www.amazon.in/s?k={0}'.format(search_query)
        return scraper(base_url)
itemlist(['iphone'])