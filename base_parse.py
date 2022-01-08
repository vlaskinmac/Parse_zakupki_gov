import logging

import datetime
import math
import time
import re
from pprint import pprint
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from datetime import timedelta
from itertools import count



# participantType_2 - ИП, participantType_0 - юр. лица
# url = "https://zakupki.gov.ru/epz/eruz/search/results.html?morphology=on&" \
#       "search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&" \
#       "pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=BY_REGISTRY_DATE&" \
#       "participantType_0=on&participantType_2=on&participantType=0%2C2&registered=on&" \
#       "rejectReasonIdNameHidden=%7B%7D&countryRegIdNameHidden=%7B%7D"

# url2 = "https://zakupki.gov.ru/epz/eruz/search/results.html?&pageNumber=10&recordsPerPage=_500&participantType=0%2C2&registryDateFrom=01.04.2021&registryDateTo=14.04.2021"



def prepare_period_start_segment(start_date_str):
    date_time_obj = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    prepare_today_date_obj = datetime.datetime.today()
    prepare_period_obj = prepare_today_date_obj - date_time_obj
    prepare_start_segment_date_obj = prepare_today_date_obj - timedelta(days=prepare_period_obj.days)
    return prepare_start_segment_date_obj


def get_total_pages(period_segment, start_date_str, per_page, page):
    prepare_start_segment_date_obj = prepare_period_start_segment(start_date_str)
    url = "https://zakupki.gov.ru/epz/eruz/search/results.html"
    payload = {
        "pageNumber": page,
        "recordsPerPage": 5,
        "participantType": "0,2",
    }

    for segment in count(step=14):
        start_segment_date_obj = prepare_start_segment_date_obj + timedelta(days=period_segment + segment)
        end_segment_date_obj = start_segment_date_obj + timedelta(days=period_segment - 1)
        start_segment_date = datetime.datetime.strftime(start_segment_date_obj, '%d.%m.%Y')
        end_segment_date = datetime.datetime.strftime(end_segment_date_obj, '%d.%m.%Y')
        print(start_segment_date, '====')
        print(end_segment_date, '++++')

        payload["registryDateFrom"] = start_segment_date
        payload["registryDateTo"] = end_segment_date

        response = requests.get(url, params=payload, headers=headers)
        print(response.url)

        soup = BeautifulSoup(response.text, "lxml")
        prepare_total_pages = soup.select_one(".search-results__total").get_text(strip=True)

        total_pages = re.sub(r"[^\d+]", "", prepare_total_pages)
        pages = (int(total_pages) + 1) / per_page
        return math.ceil(pages)


def get_segment_date(period_segment, start_date_str, page):
    prepare_start_segment_date_obj = prepare_period_start_segment(start_date_str)
    total_pages = get_total_pages(period_segment, start_date_str, per_page, page)

    url = "https://zakupki.gov.ru/epz/eruz/search/results.html"
    payload = {
        "pageNumber": page,
        "recordsPerPage": per_page,
        "participantType": "0,2",
    }

    for segment in count(step=14):
        start_segment_date_obj = prepare_start_segment_date_obj + timedelta(days=period_segment + segment)
        end_segment_date_obj = start_segment_date_obj + timedelta(days=period_segment - 1)
        start_segment_date = datetime.datetime.strftime(start_segment_date_obj, '%d.%m.%Y')
        end_segment_date = datetime.datetime.strftime(end_segment_date_obj, '%d.%m.%Y')
        print(start_segment_date, '====')
        print(end_segment_date, '++++')

        payload["registryDateFrom"] = start_segment_date
        payload["registryDateTo"] = end_segment_date

        response = requests.get(url, params=payload, headers=headers)
        print(response.url)
        soup = BeautifulSoup(response.text, "lxml")
        prepare_contaners = soup.select("div.search-registry-entry-block")
        # print(prepare_contaners)
        host = "https://zakupki.gov.ru"

        contaner_links = [
            urljoin(host, i) for i in [link.select_one("div.registry-entry__body-href a")["href"]
                                       for link in prepare_contaners]
        ]
        # contaners = [link.select_one("div.registry-entry__body-href a")["href"] for link in prepare_contaners]
        print(len(contaner_links))
        pprint(contaner_links)
        exit()




        if end_segment_date_obj > datetime.datetime.today():
        # if end_segment_date > "05.04.2019":
            break







    # print(start_segment_date)
    # print(end_segment_date)
    # period = str(period_pre.days)
    # print(period)

# get_segment_date(period_segment, start_date_str)





# def movement_of_segments():
#     prepare_start_segment_date_obj = prepare_today_date_obj - timedelta(days=prepare_period_obj.days)
#     prepare_end_segment_date = prepare_start_segment_date_obj + timedelta(days=period_segment)

    # start_date = datetime.datetime.strftime(start_date, '%d.%m.%Y')
    # start_segment_date = datetime.datetime.strftime(prepare_start_segment_date_obj, '%d.%m.%Y')
    # end_segment_date = datetime.datetime.strftime(prepare_end_segment_date, '%d.%m.%Y')


def get_links_contaner():
    pass





if __name__ == "__main__":


    logging.basicConfig(
        level=logging.WARNING,
        filename='logs.log',
        filemode='w',
        format='%(asctime)s - [%(levelname)s] - %(funcName)s() - [line %(lineno)d] - %(message)s',
    )

    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/96.0.4664.110 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",

    }
    host = "https://zakupki.gov.ru/"

    page = 1
    per_page = 500

    start_date_str = '25.12.2018'
    period_segment = 14
    get_segment_date(period_segment, start_date_str, page)
