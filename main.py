import boto3
import requests
from bs4 import BeautifulSoup
from time import sleep
import re
import time
import mysql.connector


client = boto3.client('rds', region_name='us-east-1')
response = client.describe_db_instances()
dict1 = {}
for db_instance in response['DBInstances']:
    if db_instance['DBInstanceIdentifier'] == 'projectdatabase':
        dict1['DBInstanceIdentifier'] = db_instance['DBInstanceIdentifier']
        dict1['Endpoint'] = db_instance['Endpoint']["Address"]


print(dict1['Endpoint'])
mydb = mysql.connector.connect(
    host=dict1['Endpoint'],
    user="vitaproject",
    password="vitafinalproject",
    database="ProjectDatabase"
)

create_table = mydb.cursor()
create_table.execute("""CREATE TABLE IF NOT EXISTS amazon_products3(Product_name VARCHAR(255),Rating VARCHAR(255),
Total_rating_count int,Discounted_price int,Original_price VARCHAR(20),Product_url VARCHAR(500),Time VARCHAR(20))""")



headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
           'Accept-Language': 'en-US, en;q=0.5'}

# search_query = 'iphone'.replace(' ','+')
# base_url = 'https://www.amazon.in/s?k={0}'.format(search_query)


counter = 0  # Global counter to count submitted records


def stream_records(items):
    global mydb
    insert_in = mydb.cursor()
    for i in range(len(items)):
        named_tuple = time.localtime()  # get struct_time
        time_string = time.strftime("%m-%d-%Y %H:%M:%S", named_tuple)

        sql = "INSERT INTO amazon_products3 VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (items[i][0], items[i][1], items[i][2], items[i][3], items[i][4], items[i][5],time_string)
        insert_in.execute(sql, val)
        mydb.commit()

        global counter
        counter = counter + 1

        print('Message sent #' + str(counter))


def Scraper(base_url):
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
                total_rating_count = result.find('span', {'class': 'a-size-base'}).text
            except AttributeError:
                continue

            try:
                current_price = result.find('span', {'class': 'a-price-whole'}).text
                actual_price = result.find('span', {'class': 'a-price a-text-price'}).text
                actual_price = re.sub("^₹.*₹", "_", actual_price).strip("_")
                product_url = 'https://amazon.in' + result.h2.a['href']
                items.append([product_name, rating, total_rating_count, current_price, actual_price, product_url])
            except AttributeError:
                continue
        stream_records(items)  # calling function to push records to kinesis streams
        # print(items)
        sleep(1.5)


# df = pd.DataFrame(items, columns=['product', 'rating', 'rating count', 'price1', 'price2', 'product url'])
# df.to_csv('{0}.csv'.format(search_query), index=False)


def itemlist(search_list):

    for i in search_list:
        search_query = i.replace(' ', '+')
        base_url = 'https://www.amazon.in/s?k={0}'.format(search_query)
        Scraper(base_url)


if __name__ == '__main__':

    lst = open('itemlist.txt', "r", encoding='utf-8').readlines()
    list1 = []
    for i in lst:
        list1.append(i.strip())

    print(type(list1), "Program Insialized")
    for i in range(1):
        itemlist(list1) # calling amazon code
        print("Amazon Updated")
        print("Iteration Complete")
        for i in range(1, 61):
            time.sleep(60)  # Delay for 1 minute (60 seconds)
            print(f"{i}minute")

