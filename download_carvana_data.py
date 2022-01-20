import lxml.html
import requests
import re
from datetime import datetime
import json
import random
from random import randint
from time import sleep
from requests_ip_rotator import ApiGateway, EXTRA_REGIONS


def get_end_page(url):
    page = requests.get(url)
    tree = lxml.html.fromstring(page.text)
    pages = tree.xpath('//*[@id="pagination"]/li[2]/span')[0]
    end_page = (pages.text_content()).split(' ')[3]
    return int(end_page)


def gather_carvana_data(url, num_of_pages, filename):
    r = list(range(num_of_pages+1))
    random.shuffle(r)
    for page_num in r:
        sleep(randint(10, 100))
        page_url = url + "?page=" + str(page_num)
        page = requests.get(page_url)
        tree = lxml.html.fromstring(page.text)
        try:
            info_1 = tree.xpath('//*[@id="results-section"]')[0]
        except IndexError:
            print(IndexError)
            continue
        preprocess_data = info_1.text_content()
        clean_data_1 = preprocess_data.split('Carvana Certified')
        clean_data_2 = []
        counter = 0
        for i in clean_data_1:
            j = re.findall(r'[/\w , $ /. •]+Free Shipping', i)
            clean_data_2.append(j)
        for i in clean_data_2:
            result = ''
            counter += 1
            timestamp_now = datetime.now().strftime('%Y%m%d%H%M%S')
            id = timestamp_now + str(counter)
            model_year = re.findall(r'[\d]{4}', str(i))
            model_info = re.findall(r'Volkswagen[\w .]+', str(i))
            miles = re.findall(r'[\d ,]+miles', str(i))
            odometer = re.findall(r'[\d]+',str(re.findall(r'[\d ,]+', str(miles))).replace(',', '').replace(' ', ''))
            price = re.findall(r'[\d]+',str(re.findall(r'[0-9,]+', str(re.findall(r'\${1}[0-9,]+Est', str(i))))).replace(',', ''))
            monthly = re.findall(r'[0-9]+', str(re.findall(r'[0-9]+/', str(re.findall(r'[\$0-9\/mo]+ c', str(i))))))
            cash_down = re.findall(r'[0-9]+',str(re.findall(r'[0-9,]+', str(re.findall(r'[\d ]+cash down', str(i))))).replace(',', ''))
            if len(model_year) > 0:
                result = {'record_number': id,
                          'page_number': page_num,
                              'model_year': model_year[0],
                              'model_info': model_info[0],
                              'odometer': odometer[0],
                              'price': price[0],
                              'monthly': monthly[0],
                              'cash_down': cash_down[0]}
                print(result)
                dump_to_file_as_json(result, filename)

def dump_to_file_as_json(data, filename):
    with open(filename, "a") as f:
        print("I am inside the file writer")
        json.dump(data, f)
    f.close()


start_url = 'https://www.carvana.com/cars/volkswagen?page=1'
num_of_pages = get_end_page(start_url)
base_url = 'https://www.carvana.com/cars/volkswagen'
json_output_file = "carvana_vw_data_2.json"
gather_carvana_data(base_url, num_of_pages,json_output_file)

