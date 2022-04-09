import logging

import datetime
import math
import random
import time
import re
from pprint import pprint
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from datetime import timedelta
from itertools import count

from requests import HTTPError, ReadTimeout


# from orm_models import Lids
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

logger = logging.getLogger("check")
# engine = create_engine("postgresql+psycopg2://tesseractmaks:Vfrcvfrc1@localhost/parse")
# Session = sessionmaker(bind=engine)
# session = Session()


def prepare_period_start_segment(start_date_str):
    date_time_obj = datetime.datetime.strptime(start_date_str, '%d.%m.%Y')
    prepare_today_date_obj = datetime.datetime.today()
    prepare_period_obj = prepare_today_date_obj - date_time_obj
    prepare_start_segment_date_obj = prepare_today_date_obj - timedelta(days=prepare_period_obj.days)
    return prepare_start_segment_date_obj

# получаем страниц всего на отрезке
def get_total_pages(period_segment, start_date_str, per_page, page):
    prepare_start_segment_date_obj = prepare_period_start_segment(start_date_str)
    url = "https://zakupki.gov.ru/epz/eruz/search/results.html"
    # нужна пагинация
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
        # print(start_segment_date, '====')
        # print(end_segment_date, '++++')

        payload["registryDateFrom"] = start_segment_date
        payload["registryDateTo"] = end_segment_date

        response = requests.get(url, params=payload, headers=headers)
        # x=response.request.headers
        # pprint(x)
        # exit()
        response.raise_for_status()

        # print(response.url)

        soup = BeautifulSoup(response.text, "lxml")
        prepare_total_pages = soup.select_one(".search-results__total").get_text(strip=True)

        total_pages = re.sub(r"[^\d+]", "", prepare_total_pages)
        pages = (int(total_pages) + 1) / per_page
        return math.ceil(pages)


def get_content_by_segments(period_segment, start_date_str, page):
    prepare_start_segment_date_obj = prepare_period_start_segment(start_date_str)
    total_pages = get_total_pages(period_segment, start_date_str, per_page, page)
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
        start_segment_date_obj = prepare_start_segment_date_obj + timedelta(days=period_segment + segment)
        end_segment_date_obj = start_segment_date_obj + timedelta(days=period_segment - 1)
        start_segment_date = datetime.datetime.strftime(start_segment_date_obj, '%d.%m.%Y')
        end_segment_date = datetime.datetime.strftime(end_segment_date_obj, '%d.%m.%Y')

        payload["registryDateFrom"] = start_segment_date
        payload["registryDateTo"] = end_segment_date
        try:
            response = requests.get(url, params=payload, headers=headers, timeout=3)
        except ReadTimeout as exc:
            logger.error(f"{exc}")
        except HTTPError as exc:
            logger.error(f"{exc}")
        except ConnectionError as exc:
            logger.error(f"{exc}")
            time.sleep(15)

        if end_segment_date_obj > datetime.datetime.today():
            # if end_segment_date > "05.04.2019":
            break
        yield response
        # print(response.url)

        #--------------------------------------------------- получили страницу


def get_links_by_segments(period_segment, start_date_str, page):
    links = get_content_by_segments(period_segment, start_date_str, page)
    for link_text in links:
        soup = BeautifulSoup(link_text.text, "lxml")
        prepare_contaners = soup.select("div.search-registry-entry-block")

        host = "https://zakupki.gov.ru"

        contaner_links = [
            urljoin(host, i) for i in [link.select_one("div.registry-entry__body-href a")["href"]
                                       for link in prepare_contaners]
        ]

        # print(len(contaner_links))

        # pprint(contaner_links)

#----тут async
        for link in contaner_links:
            try:
                response = requests.get(link, headers=headers)
            # ooo = 'https://zakupki.gov.ru/epz/eruz/card/general-information.html?reestrNumber=19007263'
            # ip = 'https://zakupki.gov.ru/epz/eruz/card/general-information.html?reestrNumber=19007265'
                soup = BeautifulSoup(response.text, "lxml")
                # check_company = soup.select_one()
                yield soup
            except ReadTimeout as exc:
                logger.error(f"{exc}")
            except HTTPError as exc:
                logger.error(f"{exc}")
            except ConnectionError as exc:
                logger.error(f"{exc}")
                time.sleep(15)


            # print(response.url)


def interface_of_paths_ip_ooo(period_segment, start_date_str, page):

    # headers = {
    #     "Accept": "*/*",
    #     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    #                   " Chrome/96.0.4664.110 Safari/537.36",
    #     "Accept-Encoding": "gzip, deflate, br",
    #
    # }
    soup_obj = get_links_by_segments(period_segment, start_date_str, page)
    count_ooo = 0
    count_ip = 0
    total = 0
    for soup in soup_obj:
        # ooo = 'https://zakupki.gov.ru/epz/eruz/card/general-information.html?reestrNumber=19007263'
        # ip = 'https://zakupki.gov.ru/epz/eruz/card/general-information.html?reestrNumber=19007265'

        # response = requests.get(ip, headers=headers)
        # response = requests.get(ip, headers=headers)
        # response = requests.get(ooo, headers=headers)

        # soup = BeautifulSoup(response.text, "lxml")

        # with open("ip.html", "w", encoding='utf-8') as file:
        #     file.write(str(soup))
        # with open('index.html', 'r', encoding='utf-8') as file:
        #     hendler_src3 = file.read()

        # html = soup.select(".blockInfo__section")
        # check_company = [item.select_one("span.section__title").get_text(strip=True) for item in html]
        # pprint(check_company)
        #
        # exit()
        contaner_html = soup.select(".blockInfo__section")
        total += 1
        print("total ----------", total)
        if re.findall("Юридическое лицо", str(contaner_html), flags=re.I):
            count_ooo += 1
            print("ooo - ", count_ooo)
            #_______запись в базу
            # ooo_data(contaner_html)

        if re.findall("индивидуальный предприниматель", str(contaner_html), flags=re.I):
            count_ip += 1
            print("ip - ", count_ip)
            # _______запись в базу
            # ip_data(contaner_html)
        exit()



def ip_data(html):
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
        for record in html:
            soup = BeautifulSoup(record.text, "lxml")
            text = soup.select_one("html body p").get_text(strip=True)
            # print(text.split('\n'))
            try:
                title, data = text.split('\n')
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

    try:
        lid = Lids(
            category_id=2, created_on=datetime.date.today(), date_registration_eis=ip["date_registration_eis"],
            date_registration_ifns=ip["date_registration_ifns"], email=ip["email"], full_name=ip["full_name"],
            inn=ip["inn"], number_in_reestr=ip["number_in_reestr"], ogrn=ip["ogrn"],
            status_registration_eis=ip["status_registration_eis"],
        )
        session.add(lid)
        session.commit()

    except SQLAlchemyError as exc:
        print(exc, '99999')
        session.rollback()


def ooo_data(html):
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
        for record in html:
            soup = BeautifulSoup(record.text, "lxml")
            text = soup.select_one("html body p").get_text(strip=True)
            # print(text.split('\n'))
            try:
                title, data = text.split('\n')
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
                    ooo["date_registration_eis"] = datetime.datetime.strptime(data, "%d.%m.%Y").date()
                elif key == "date_registration_ifns":
                    ooo["date_registration_ifns"] = datetime.datetime.strptime(data, "%d.%m.%Y").date()
                elif key == "email":
                    ooo["email"] = data
                elif key == "phone":
                    ooo["phone"] = data,

    try:
        lid = Lids(
            category_id=1, created_on=datetime.date.today(), date_registration_eis=ooo["date_registration_eis"],
            date_registration_ifns=ooo["date_registration_ifns"], email=ooo["email"], full_name=ooo["full_name"],
            short_name=ooo["short_name"], inn=ooo["inn"], number_in_reestr=ooo["number_in_reestr"], ogrn=ooo["ogrn"],
            status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
            kpp=ooo["kpp"], phone=ooo["phone"],
        )
        session.add(lid)
        session.commit()

    except SQLAlchemyError as exc:
        print(exc, '--888888888')
        session.rollback()
    # exit()

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






# def get_free_proxies():
#     url = "https://free-proxy-list.net/"
#     soup = bs(requests.get(url).text, "lxml")
#     proxies = []
#     for row in soup.select_one(".table-responsive").find_all("tr")[1:]:
#         tds = row.find_all("td")
#         try:
#             ip = tds[0].text.strip()
#             port = tds[1].text.strip()
#             host = f"{ip}:{port}"
#             proxies.append(host)
#         except IndexError:
#             continue
#     return proxies
#
#
# def get_session(proxies):
#     # создать HTTP‑сеанс
#     session = requests.Session()
#     for proxy in proxies:
#         session.proxies = {"http": proxy, "https": proxy}
#         try:
#             response = session.get("http://icanhazip.com", timeout=1)
#             if re.search("([0-9]{1,3}[\.]){3}[0-9]{1,3}", response.text):
#                 if response.ok:
#                     return response.text
#         except ReadTimeout as exc:
#             pass
#         except HTTPError as exc:
#             pass
#         except ConnectionError as exc:
#             print(exc)
#             time.sleep(10)
#         except Exception as exc:
#             pass







if __name__ == "__main__":

    logging.basicConfig(
        level=logging.WARNING,
        filename='logs.log',
        filemode='w',
        format='%(asctime)s - [%(levelname)s] - %(funcName)s() - [line %(lineno)d] - %(message)s',
    )

    # proxies = get_free_proxies()

    # proxy номер:
    # get_session(proxies)



    headers = {
        "Accept": "*/*",
        "User-Agent": f"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
                      f"Chrome/96.0.{random.randint(10,463)}4.110 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br",
    }
    host = "https://zakupki.gov.ru/"

    page = 1
    per_page = 500

    start_date_str = '25.12.2018'
    period_segment = 14
    try:
        interface_of_paths_ip_ooo(period_segment, start_date_str, page)
    except ReadTimeout as exc:
        logger.error(f"{exc}")
    except HTTPError as exc:
        logger.error(f"{exc}")
    except ConnectionError as exc:
        logger.error(f"{exc}")
        time.sleep(15)
    # get_links_by_segments(period_segment, start_date_str, page)
