import asyncio
import logging

import datetime
import math
import random
import time
import re

from urllib.parse import urljoin

import aiofiles
import aiohttp
import requests

from bs4 import BeautifulSoup
from datetime import timedelta
from itertools import count

from requests import HTTPError, ReadTimeout
from requests.auth import HTTPProxyAuth

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# participantType_2 - ИП, participantType_0 - юр. лица
# url = "https://zakupki.gov.ru/epz/eruz/search/results.html?morphology=on&" \
#       "search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&" \
#       "pageNumber=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=BY_REGISTRY_DATE&" \
#       "participantType_0=on&participantType_2=on&participantType=0%2C2&registered=on&" \
#       "rejectReasonIdNameHidden=%7B%7D&countryRegIdNameHidden=%7B%7D"

# url2 = "https://zakupki.gov.ru/epz/eruz/search/results.html?&pageNumber=10&recordsPerPage=_500&participantType=0%2C2&registryDateFrom=01.04.2021&registryDateTo=14.04.2021"
from orm_models import Lids

logger = logging.getLogger("check")
engine = create_engine("postgresql+psycopg2://tesseractmaks:Vfrcvfrc1@localhost/parse")
Session = sessionmaker(bind=engine)
session_base = Session()

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/96.0.4{}.{} Safari/537.36",

}


def prepare_period_start_segment(start_date_str):
    date_time_obj = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    prepare_today_date_obj = datetime.datetime.today()
    prepare_period_obj = prepare_today_date_obj - date_time_obj
    prepare_start_segment_date_obj = prepare_today_date_obj - timedelta(days=prepare_period_obj.days)
    return prepare_start_segment_date_obj


# получаем страниц всего на отрезке
def get_total_pages(response, per_page):
    soup = BeautifulSoup(response.text, "lxml")
    prepare_total_pages = soup.select_one(".search-results__total").get_text(strip=True)
    total_pages = re.sub(r"[^\d+]", "", prepare_total_pages)
    pages = (int(total_pages) + 1) / per_page
    return math.ceil(pages)


def get_content_by_segments(period_segment, start_date_str, page, per_page):
    session = requests.Session()

    prepare_start_segment_date_obj = prepare_period_start_segment(start_date_str)
    auth_ = HTTPProxyAuth("Seltesseractmaks", "R6l3EhG")
    # proxy = {"http": "http://Seltesseractmaks:R6l3EhG@185.29.127.235:45785"}
    proxy = {"http": 'http://185.29.127.235:45785'}
    session.proxies = proxy
    session.auth = auth_

    # нужна пагинация
    # print(total_pages)
    url = "https://zakupki.gov.ru/epz/eruz/search/results.html"
    payload = {
        "pageNumber": page,
        "recordsPerPage": per_page,
        "participantType": "0,2",
        "registered": "on",

    }

    for segment in count(step=14):
        start_s = time.time()
        start_segment_date_obj = prepare_start_segment_date_obj + timedelta(days=period_segment + segment)
        end_segment_date_obj = start_segment_date_obj + timedelta(days=period_segment - 1)
        start_segment_date = datetime.datetime.strftime(start_segment_date_obj, '%d.%m.%Y')
        end_segment_date = datetime.datetime.strftime(end_segment_date_obj, '%d.%m.%Y')
        payload["registryDateFrom"] = start_segment_date
        payload["registryDateTo"] = end_segment_date

        response = session.get(url, params=payload, headers=headers, timeout=3)
        response.raise_for_status()
        total_pages = get_total_pages(response, per_page)
        print(start_segment_date, '-', end_segment_date)
        print('=========================================================================================')
        print(total_pages, 'total_pages')
        # print(response.url)

        for num_page in count(1):
            start_p = time.time()
            payload["pageNumber"] = num_page
            try:
                response = session.get(url, params=payload, headers=headers, timeout=3)
                response.raise_for_status()
                # print(response.url)
                print('*'*40)
                print(num_page, 'num_page')

                if num_page > total_pages:
                    break
                yield response
                print(time.time() - start_p,'-------page-------')



            except ReadTimeout as exc:
                logger.error(f"{exc}")
            except HTTPError as exc:
                logger.error(f"{exc}")
            except ConnectionError as exc:
                logger.error(f"{exc}")
                time.sleep(15)
            # print(response.url)
        print('-' * 40)
        print(time.time() - start_s, '--------------', start_segment_date, '-', end_segment_date)

        if end_segment_date_obj > datetime.datetime.today():
            print()
            print('end')
            # if end_segment_date > "05.04.2019":
            break



def get_links_by_segments(period_segment, start_date_str, page, per_page):
    # --------------------------------------------------- получили html страницу c контейнером ссылок c одной страницы
    links = get_content_by_segments(period_segment, start_date_str, page, per_page)
    for link_text in links:
        soup = BeautifulSoup(link_text.text, "lxml")
        prepare_contaners = soup.select("div.search-registry-entry-block")

        host = "https://zakupki.gov.ru"
        # --------------------------------------------------- получили пулл ссылок
        contaner_links = [
            urljoin(host, i) for i in [link.select_one("div.registry-entry__body-href a")["href"]
                                       for link in prepare_contaners]
        ]

        print(len(contaner_links), '- contaner_links')

        # print(contaner_links)
        yield contaner_links


async def headers_random():
    async with aiofiles.open("headers", 'r') as file:
        # proxies=file.read().split('\n')
        headers_list = await file.read()

        headers = str(headers_list).split('\n')

    head = {
        "User-Agent": f"{random.choice(headers)}",
    }
    return head
# async def rand_sleep():
#    return await asyncio.sleep(random.randint(0, 1))

async def interface_of_paths_ip_ooo(session, semaphore, link, auth, proxy_):
    # async def interface_of_paths_ip_ooo(session, link, auth, proxy_):
    global count_line
    # head = {
    #     "User-Agent": f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    #                   f"Chrome/96.0.4{random.randint(10, 463)}4.{random.randint(10, 110)} Safari/537.36",
    #
    # }
    # head = {
    #     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"
    #
    # }

    # head = {
    #     "User-Agent": "*"
    #
    # }

    # async with aiofiles.open("proxy_clean", 'r') as file:
    # proxies_str = await file.read()
    # proxies_str = ['http://58.27.59.249:80', 'http://107.151.182.247:80', 'http://169.57.1.85:8123']
    # proxy_ = random.choice(proxies_str)

    rand = random.randint(4, 35)

    try:
        await asyncio.sleep(random.randint(1, 4))
        # await rand_sleep()

        async with semaphore:
            head = await headers_random()
            # print(head)
            async with session.get(url=link, proxy_auth=auth, ssl=False, proxy=proxy_, headers=head,
                                   timeout=rand) as response:

                soup = BeautifulSoup(await response.text(), "lxml")
                # print(soup)
                contaner_html = soup.select(".blockInfo__section")
                count_line += 1
                print(link, count_line)
                # print(count_line)

                if re.findall("индивидуальный предприниматель", str(contaner_html), flags=re.I):
                    # task = asyncio.create_task(ip_data(contaner_html))
                    # tasks_2.append(task)
                    await ip_data(contaner_html)

                if re.findall("Юридическое лицо", str(contaner_html), flags=re.I):
                    await ooo_data(contaner_html)

                    # task = asyncio.create_task(ooo_data(contaner_html))
                # tasks_2.append(task)
                # await asyncio.gather(*tasks_2)

    except asyncio.exceptions.TimeoutError as exc:
        pass
        # print(exc)
    except Exception as exc:
        pass
        # print(exc)


# async def interface_of_paths_ip_ooo(session, semaphore, link, auth, proxy_):
#     # Getter function with semaphore.
#     async with semaphore:
#     # await asyncio.sleep(.5)
#         return await paths_ip_ooo(session, semaphore, link, auth, proxy_)

# ----тут async
async def create_tasks_soap(period_segment, start_date_str, page, per_page):
    # print(links,'-=-=--')

    proxy_w = "http://185.29.127.235:45785"
    proxy_auth = aiohttp.BasicAuth("Seltesseractmaks", "R6l3EhG")

    # proxy_w = "http://185.113.137.118:1596"
    # proxy_auth = aiohttp.BasicAuth("user79669", "rlgxk8")

    rand_s = random.randint(20, 23)

    print(rand_s, 'semaphore')
    semaphore = asyncio.Semaphore(rand_s)
    rand_conn = random.randint(140, 160)
    # rand_conn = random.randint(170, 180)
    print(rand_conn, 'conn')
    conn = aiohttp.TCPConnector(limit=rand_conn)


    async with aiohttp.ClientSession(connector=conn) as session:
        contaner_links = get_links_by_segments(period_segment, start_date_str, page, per_page)
        for i in contaner_links:
        # tasks = [interface_of_paths_ip_ooo(session, link, semaphore, auth=proxy_auth, proxy_="http://185.29.127.235:45785") for link in contaner_links]
            tasks = [interface_of_paths_ip_ooo(session, semaphore, link, auth=proxy_auth, proxy_=proxy_w) for link in
                     i]
        await asyncio.gather(*tasks)

        # try:
        #     response = requests.get(link, headers=headers)
        # ooo = 'https://zakupki.gov.ru/epz/eruz/card/general-information.html?reestrNumber=19007263'
        # ip = 'https://zakupki.gov.ru/epz/eruz/card/general-information.html?reestrNumber=19007265'
        #     soup = BeautifulSoup(response.text, "lxml")
        # check_company = soup.select_one()
        # yield soup
        # except ReadTimeout as exc:
        #     logger.error(f"{exc}")
        # except HTTPError as exc:
        #     logger.error(f"{exc}")
        # except ConnectionError as exc:
        #     logger.error(f"{exc}")
        #     time.sleep(15)

        # print(response.url)


async def ip_data(html):
    # title_ip = [
    #     'ФИО',
    #     'ИНН',
    #     'ОГРНИП',
    #     'Номер реестровой записи в ЕРУЗ',
    #     'Статус регистрации',
    #     'Дата регистрации в ЕИС',
    #     'Дата постановки на учет в налоговом органе',
    #     'Адрес электронной почты',
    # ]

    title_ip = {
        "number_in_reestr": 'Номер реестровой записи в ЕРУЗ',
        "status_registration_eis": 'Статус регистрации',
        "date_registration_eis": 'Дата регистрации в ЕИС',
        "full_name": 'ФИО',
        "inn": 'ИНН',
        "ogrn": 'ОГРНИП',
        "date_registration_ifns": 'Дата постановки на учет в налоговом органе',
        "email": 'Адрес электронной почты',
    }

    # keys_ip = [
    #     "full_name",
    #     "inn",
    #     "ogrn",
    #     "number_in_reestr",
    #     "status_registration_eis",
    #     "date_registration_eis",
    #     "date_registration_ifns",
    #     "email",
    # ]

    ip = {}
    for key, value in title_ip.items():
        try:
            for record in html:
                soup = BeautifulSoup(record.text, "lxml")
                text = soup.select_one("html body p").get_text(strip=True)
                try:
                    title, data = text.strip().split('\n')
                except:
                    continue
                if value == title:
                    if key == "full_name":
                        ip["full_name"] = data.upper()
                    elif key == "inn":
                        ip["inn"] = int(data)
                    elif key == "ogrn":
                        ip["ogrn"] = int(data)
                    elif key == "number_in_reestr":
                        ip["number_in_reestr"] = int(data)
                    elif key == "status_registration_eis":
                        ip["status_registration_eis"] = data
                    elif key == "date_registration_eis":
                        ip["date_registration_eis"] = datetime.datetime.strptime(data, "%d.%m.%Y").date()
                    elif key == "date_registration_ifns":
                        ip["date_registration_ifns"] = datetime.datetime.strptime(data, "%d.%m.%Y").date()
                    elif key == "email":
                        ip["email"] = data
        except ValueError:
            continue

    try:
        lid = Lids(
            category_id=2, created_on=datetime.date.today(), date_registration_eis=ip["date_registration_eis"],
            date_registration_ifns=ip["date_registration_ifns"], email=ip["email"], full_name=ip["full_name"],
            inn=ip["inn"], number_in_reestr=ip["number_in_reestr"], ogrn=ip["ogrn"],
            status_registration_eis=ip["status_registration_eis"],
        )
        session_base.add(lid)
        session_base.commit()

    except SQLAlchemyError as exc:
        # print(title, data)
        # print(exc, '99999', ip["date_registration_ifns"])
        # print()
        # print(html)
        # exit()
        session_base.rollback()


async def ooo_data(html):
    # print(html)
    # title_ooo = [
    #     'Номер реестровой записи в ЕРУЗ',
    #     'Статус регистрации',
    #     'Тип участника закупки',
    #     'Дата регистрации в ЕИС',
    #     'Полное наименование',
    #     'Сокращенное наименование',
    #     'Адрес в пределах места нахождения',
    #     'ИНН',
    #     'КПП',
    #     'Дата постановки на учет в налоговом органе',
    #     'ОГРН',
    #     'Адрес электронной почты',
    #     'Контактный телефон',
    # ]

    title_ooo = {
        "number_in_reestr": 'Номер реестровой записи в ЕРУЗ',
        "status_registration_eis": 'Статус регистрации',
        "date_registration_eis": 'Дата регистрации в ЕИС',
        "full_name": "Полное наименование",
        "short_name": 'Сокращенное наименование',
        "address_yur": 'Адрес в пределах места нахождения',
        "inn": 'ИНН',
        "kpp": 'КПП',
        "date_registration_ifns": 'Дата постановки на учет в налоговом органе',
        "ogrn": 'ОГРН',
        "email": 'Адрес электронной почты',
        "phone": 'Контактный телефон',
    }

    ooo = {}

    for key, value in title_ooo.items():
        try:
            for record in html:
                soup = BeautifulSoup(record.text, "lxml")
                text = soup.select_one("html body p").get_text(strip=True)
                try:
                    title, data = text.strip().split('\n')
                except:
                    continue
                if value == title:
                    if key == "full_name":
                        ooo["full_name"] = data.upper()
                    elif key == "short_name":
                        ooo["short_name"] = data
                    elif key == "address_yur":
                        ooo["address_yur"] = data
                    elif key == "inn":
                        ooo["inn"] = int(data)
                    elif key == "kpp":
                        ooo["kpp"] = int(data)
                    elif key == "ogrn":
                        ooo["ogrn"] = int(data)
                    elif key == "number_in_reestr":
                        ooo["number_in_reestr"] = int(data)
                    elif key == "status_registration_eis":
                        ooo["status_registration_eis"] = data
                    elif key == "date_registration_eis":
                        ooo["date_registration_eis"] = datetime.datetime.strptime(data.strip(), "%d.%m.%Y").date()
                    elif key == "date_registration_ifns":
                        ooo["date_registration_ifns"] = datetime.datetime.strptime(data.strip(), "%d.%m.%Y").date()
                    elif key == "email":
                        ooo["email"] = data
                    elif key == "phone":
                        ooo["phone"] = data
        except ValueError:
            continue

    try:
        lid = Lids(
            category_id=1, created_on=datetime.date.today(), date_registration_eis=ooo["date_registration_eis"],
            date_registration_ifns=ooo["date_registration_ifns"], email=ooo["email"], full_name=ooo["full_name"],
            short_name=ooo["short_name"], inn=ooo["inn"], number_in_reestr=ooo["number_in_reestr"], ogrn=ooo["ogrn"],
            status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
            kpp=ooo["kpp"], phone=ooo["phone"],
        )
        session_base.add(lid)
        session_base.commit()

    except SQLAlchemyError as exc:
        pass
    except Exception as exc:
        print(exc, '--888888888')
        session_base.rollback()

    # print(start_segment_date)
    # print(end_segment_date)
    # period = str(period_pre.days)
    # print(period)


def main():
    start = time.time()
    period_segment = 14

    start_date_str = '25.12.2018'
    page = 1
    per_page = 500
    # per_page = 10
    # while True:

    # while True:
    # contaner_links = get_links_by_segments(period_segment, start_date_str, page, per_page)


    res = asyncio.run(create_tasks_soap(period_segment, start_date_str, page, per_page))

    print(len(res))
    print(time.time() - start)
    print(count_line)


# if __name__ == "__main__":
#     count_line = 0
#     main()



import probe

probe.main()
# if __name__ == "__main__":
#
#     logging.basicConfig(
#         level=logging.WARNING,
#         filename='logs.log',
#         filemode='w',
#         format='%(asctime)s - [%(levelname)s] - %(funcName)s() - [line %(lineno)d] - %(message)s',
#     )
#
#     # proxies = get_free_proxies()
#
#     # proxy номер:
#     # get_session(proxies)
#
#
#
#     headers = {
#         "Accept": "*/*",
#         "User-Agent": f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
#                       f"Chrome/96.0.{random.randint(10,463)}4.110 Safari/537.36",
#         "Accept-Encoding": "gzip, deflate, br",
#     }
#     host = "https://zakupki.gov.ru/"

# page = 1
# per_page = 500
#
# start_date_str = '25.12.2018'
# period_segment = 14
# try:
#     interface_of_paths_ip_ooo(period_segment, start_date_str, page=1)
# except ReadTimeout as exc:
#     logger.error(f"{exc}")
# except HTTPError as exc:
#     logger.error(f"{exc}")
# except ConnectionError as exc:
#     logger.error(f"{exc}")
#     time.sleep(15)
# get_links_by_segments(period_segment, start_date_str, page)
