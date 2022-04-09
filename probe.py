import asyncio
import logging.config
import datetime
import os
import random
import shlex
import subprocess
import time
import re
import aiofiles
import aiohttp

from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from logging_config import dict_config
from orm_models import Lids


engine = create_engine("postgresql+psycopg2://tesseractmaks:Vfrcvfrc1@localhost/parse")
Session = sessionmaker(bind=engine)
session_base = Session()

logging.config.dictConfig(dict_config)
logger = logging.getLogger("check")

count_line = 0
async def headers_random():
    async with aiofiles.open("headers", 'r') as file:
        # proxies=file.read().split('\n')
        headers_list = await file.read()

        headers = str(headers_list).split('\n')

    head = {
        "User-Agent": f"{random.choice(headers)}",
    }
    return head


async def interface_of_paths_ip_ooo(session, semaphore, link, auth, proxy_):


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

    # rand = random.randint(3, 15)

    await asyncio.sleep(random.randint(0, 1))
    # await rand_sleep()

    async with semaphore:
        head = await headers_random()
        # print(head)
        try:
            await asyncio.sleep(random.randint(4, 7))
            # async with session.get(url=link, proxy_auth=auth, ssl=False, timeout=rand, proxy=proxy_, headers=head) as response:
            async with session.get(url=link, proxy_auth=auth, ssl=False, proxy=proxy_, headers=head) as response:
                soup = BeautifulSoup(await response.text(), "lxml")
                # print(soup)
                contaner_html = soup.select(".blockInfo__section")


                count_line += 1

                # print(link, count_line)
                print(count_line)

                if re.findall("индивидуальный предприниматель", str(contaner_html), flags=re.I):
                    await ip_data(contaner_html, link)
                if re.findall("Юридическое лицо", str(contaner_html), flags=re.I):
                    await ooo_data(contaner_html, link)
        except asyncio.exceptions.TimeoutError as exc:
            logger.warning(f"{link} -- {exc} asyncio.exceptions.TimeoutError")
        except aiohttp.ClientError as exc:
        # except Exception as exc:
            logger.warning(f"{link} -- {exc} aiohttp.ClientError")
        except aiohttp.ClientConnectorError as exc:
            await asyncio.sleep(15)
        # except Exception as exc:
            logger.warning(f"{link} -- {exc} aiohttp.ClientConnectorError")


# ----тут async
async def create_tasks_soap():

    async with aiofiles.open("logfile_links.txt") as file:
        contaner = await file.read()
        contaner_links = str(contaner).strip().split('\n')


    proxy_w = "http://185.29.127.235:45785"
    proxy_auth = aiohttp.BasicAuth("Seltesseractmaks", "R6l3EhG")

    # proxy_w = "http://185.113.137.118:1596"
    # proxy_auth = aiohttp.BasicAuth("user79669", "rlgxk8")

    rand_s = random.randint(20, 23)
    semaphore = asyncio.Semaphore(rand_s)
    rand_conn = random.randint(140, 160)
    # rand_conn = random.randint(170, 180)


    print(rand_conn, ' --conn |', rand_s, '--semaphore ')
    conn = aiohttp.TCPConnector(limit=rand_conn)


    async with aiohttp.ClientSession(connector=conn) as session:
    # async with aiohttp.ClientSession(connector=conn, timeout=aiohttp.ClientTimeout(1200)) as session:
    # tasks = [interface_of_paths_ip_ooo(session, link, semaphore, auth=proxy_auth, proxy_="http://185.29.127.235:45785") for link in contaner_links]
        tasks = [interface_of_paths_ip_ooo(session, semaphore, link, auth=proxy_auth, proxy_=proxy_w) for link in
                 contaner_links]
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


async def ip_data(html, link):
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

    ip = {
        "number_in_reestr": None,
        "status_registration_eis": None,
        "date_registration_eis": None,
        "full_name": None,
        "inn": None,
        "ogrn": None,
        "date_registration_ifns": None,
        "email": None,
    }
    try:
        for key, value in title_ip.items():

            for record in html:
                soup = BeautifulSoup(record.text, "lxml")
                text = soup.select_one("html body p").get_text(strip=True)
                try:
                    title, data = text.strip().split('\n')
                except:
                    continue

                if value == title:
                    try:
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
                    except Exception as exc:
                        print(exc)
                        print('=======================================================')
        lid = Lids(
            category_id=2, created_on=datetime.date.today(), date_registration_eis=ip["date_registration_eis"],
            date_registration_ifns=ip["date_registration_ifns"], email=ip["email"], full_name=ip["full_name"],
            inn=ip["inn"], number_in_reestr=ip["number_in_reestr"], ogrn=ip["ogrn"],
            status_registration_eis=ip["status_registration_eis"],
        )
        session_base.add(lid)
        session_base.commit()

    except SQLAlchemyError as exc:
        session_base.rollback()
        logger.warning(f"{link} {exc} -- rollback - SQLAlchemyError")
    # except Exception as exc:
    #     session_base.rollback()
        # await correct_ip(ip, link)


async def ooo_data(html, link):
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

    ooo = {
         "number_in_reestr": None,
        "status_registration_eis": None,
        "date_registration_eis": None,
        "full_name": None,
        "short_name": None,
        "address_yur": None,
        "inn": None,
        "kpp": None,
        "date_registration_ifns": None,
        "ogrn": None,
        "email": None,
        "phone": None,
    }
    try:
        for key, value in title_ooo.items():

                for record in html:
                    soup = BeautifulSoup(record.text, "lxml")
                    text = soup.select_one("html body p").get_text(strip=True)
                    try:
                        title, data = text.strip().split('\n')
                    except:
                        continue
                    # except Exception as exc:
                    #     logger.warning(f" {link} {exc} ---")
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
        lid = Lids(
            category_id=1, created_on=datetime.date.today(),
            date_registration_ifns=ooo["date_registration_ifns"], email=ooo["email"], full_name=ooo["full_name"],
            short_name=ooo["short_name"], inn=ooo["inn"], number_in_reestr=ooo["number_in_reestr"],
            ogrn=ooo["ogrn"], date_registration_eis =ooo["date_registration_eis"],
            status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
            kpp=ooo["kpp"], phone=ooo["phone"],
        )
        session_base.add(lid)
        session_base.commit()
    except SQLAlchemyError as exc:
        session_base.rollback()
        logger.warning(f"{link} {exc} -- rollback - SQLAlchemyError")
        # await correct_ooo(ooo, link)
        # except Exception as exc:
        #     logger.warning(f"{link} {exc} -- rollback - SQLAlchemyError")
        #     session_base.rollback()
        #     await correct_ooo(ooo, link)


# async def correct_ooo(ooo, link):
#     logger.warning(f"{link} =======")
#     lid = None
#     try:
#         if not ooo["date_registration_eis"]:
#             lid = Lids(
#                 category_id=1, created_on=datetime.date.today(),
#                 date_registration_ifns=ooo["date_registration_ifns"], email=ooo["email"], full_name=ooo["full_name"],
#                 short_name=ooo["short_name"], inn=ooo["inn"], number_in_reestr=ooo["number_in_reestr"],
#                 ogrn=ooo["ogrn"], status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
#                 kpp=ooo["kpp"], phone=ooo["phone"],
#             )
#         #     session_base.add(lid)
#         #     session_base.commit()
#         #     logger.warning(f"{link}---------------- -- {ooo['full_name']}")
#         # except SQLAlchemyError as exc:
#         #     session_base.rollback()
#         #     logger.warning(f"{link}---------------- -- rollback - SQLAlchemyError")
#         elif not ooo["date_registration_ifns"]:
#             # try:
#             lid = Lids(
#                 category_id=1, created_on=datetime.date.today(), date_registration_eis=ooo["date_registration_eis"],
#                 email=ooo["email"], full_name=ooo["full_name"],
#                 short_name=ooo["short_name"], inn=ooo["inn"], number_in_reestr=ooo["number_in_reestr"],
#                 ogrn=ooo["ogrn"],
#                 status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
#                 kpp=ooo["kpp"], phone=ooo["phone"],
#             )
#             #     session_base.add(lid)
#             #     session_base.commit()
#             #     logger.warning(f"{link}---------------- -- {ooo['full_name']}")
#             # except SQLAlchemyError as exc:
#             #     session_base.rollback()
#             #     logger.warning(f"{link} ------------------- rollback - SQLAlchemyError")
#         elif not ooo["email"]:
#             # try:
#             lid = Lids(
#                 category_id=1, created_on=datetime.date.today(), date_registration_eis=ooo["date_registration_eis"],
#                 date_registration_ifns=ooo["date_registration_ifns"], full_name=ooo["full_name"],
#                 short_name=ooo["short_name"], inn=ooo["inn"], number_in_reestr=ooo["number_in_reestr"], ogrn=ooo["ogrn"],
#                 status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
#                 kpp=ooo["kpp"], phone=ooo["phone"],
#             )
#             #     session_base.add(lid)
#             #     session_base.commit()
#             # except SQLAlchemyError as exc:
#             #     session_base.rollback()
#             #     logger.warning(f"{link} -------------------- rollback - SQLAlchemyError")
#             #     logger.warning(f"{link}---------------- -- {ooo['full_name']}")
#         elif not ooo["full_name"]:
#             # try:
#             lid = Lids(
#                 category_id=1, created_on=datetime.date.today(), date_registration_eis=ooo["date_registration_eis"],
#                 date_registration_ifns=ooo["date_registration_ifns"], email=ooo["email"],
#                 short_name=ooo["short_name"], inn=ooo["inn"], number_in_reestr=ooo["number_in_reestr"], ogrn=ooo["ogrn"],
#                 status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
#                 kpp=ooo["kpp"], phone=ooo["phone"],
#             )
#             #     session_base.add(lid)
#             #     session_base.commit()
#             # except SQLAlchemyError as exc:
#             #     session_base.rollback()
#             #     logger.warning(f"{link} ------------------ rollback - SQLAlchemyError")
#         elif not ooo["short_name"]:
#             # try:
#             lid = Lids(
#                 category_id=1, created_on=datetime.date.today(), date_registration_eis=ooo["date_registration_eis"],
#                 date_registration_ifns=ooo["date_registration_ifns"], email=ooo["email"], full_name=ooo["full_name"],
#                 inn=ooo["inn"], number_in_reestr=ooo["number_in_reestr"], ogrn=ooo["ogrn"],
#                 status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
#                 kpp=ooo["kpp"], phone=ooo["phone"],
#             )
#             #     session_base.add(lid)
#             #     session_base.commit()
#             #     logger.warning(f"{link}---------------- -- {ooo['full_name']}")
#             # except SQLAlchemyError as exc:
#             #     session_base.rollback()
#             #     logger.warning(f"{link}------------- rollback - SQLAlchemyError")
#         elif not ooo["ogrn"]:
#             # try:
#             lid = Lids(
#                 category_id=1, created_on=datetime.date.today(), date_registration_eis=ooo["date_registration_eis"],
#                 date_registration_ifns=ooo["date_registration_ifns"], email=ooo["email"], full_name=ooo["full_name"],
#                 short_name=ooo["short_name"], inn=ooo["inn"], number_in_reestr=ooo["number_in_reestr"],
#                 status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
#                 kpp=ooo["kpp"], phone=ooo["phone"],
#             )
#             #     session_base.add(lid)
#             #     session_base.commit()
#             #     logger.warning(f"{link}---------------- -- {ooo['full_name']}")
#             # except SQLAlchemyError as exc:
#             #     session_base.rollback()
#             #     logger.warning(f"{link} ----------- rollback - SQLAlchemyError")
#         elif not ooo["inn"]:
#             # try:
#             lid = Lids(
#                 category_id=1, created_on=datetime.date.today(), date_registration_eis=ooo["date_registration_eis"],
#                 date_registration_ifns=ooo["date_registration_ifns"], email=ooo["email"], full_name=ooo["full_name"],
#                 short_name=ooo["short_name"], number_in_reestr=ooo["number_in_reestr"],
#                 ogrn=ooo["ogrn"],
#                 status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
#                 kpp=ooo["kpp"], phone=ooo["phone"],
#             )
#             #     session_base.add(lid)
#             #     session_base.commit()
#             #     logger.warning(f"{link}---------------- -- {ooo['full_name']}")
#             # except SQLAlchemyError as exc:
#             #     session_base.rollback()
#             #     logger.warning(f"{link}--------------- rollback - SQLAlchemyError")
#
#         elif not ooo["kpp"]:
#             # try:
#             lid = Lids(
#                 category_id=1, created_on=datetime.date.today(), date_registration_eis=ooo["date_registration_eis"],
#                 date_registration_ifns=ooo["date_registration_ifns"], email=ooo["email"], full_name=ooo["full_name"],
#                 short_name=ooo["short_name"], inn=ooo["inn"], number_in_reestr=ooo["number_in_reestr"],
#                 ogrn=ooo["ogrn"],
#                 status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
#                 phone=ooo["phone"],
#             )
#             #     session_base.add(lid)
#             #     session_base.commit()
#             #     logger.warning(f"{link}---------------- -- {ooo['full_name']}")
#             # except SQLAlchemyError as exc:
#             #     session_base.rollback()
#             #     logger.warning(f"{link} ------------ rollback - SQLAlchemyError")
#         elif not ooo["number_in_reestr"]:
#             # try:
#             lid = Lids(
#                 category_id=1, created_on=datetime.date.today(), date_registration_eis=ooo["date_registration_eis"],
#                 date_registration_ifns=ooo["date_registration_ifns"], email=ooo["email"], full_name=ooo["full_name"],
#                 short_name=ooo["short_name"], inn=ooo["inn"],
#                 ogrn=ooo["ogrn"],
#                 status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
#                 kpp=ooo["kpp"], phone=ooo["phone"],
#             )
#             #     session_base.add(lid)
#             #     session_base.commit()
#             #     logger.warning(f"{link}---------------- -- {ooo['full_name']}")
#             # except SQLAlchemyError as exc:
#             #     session_base.rollback()
#             #     logger.warning(f"{link} ------------- rollback - SQLAlchemyError")
#         elif not ooo["status_registration_eis"]:
#             # try:
#             lid = Lids(
#                 category_id=1, created_on=datetime.date.today(),
#                 date_registration_ifns=ooo["date_registration_ifns"], email=ooo["email"], full_name=ooo["full_name"],
#                 short_name=ooo["short_name"], inn=ooo["inn"], number_in_reestr=ooo["number_in_reestr"],
#                 ogrn=ooo["ogrn"],
#                 status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
#                 kpp=ooo["kpp"], phone=ooo["phone"],
#             )
#             #     session_base.add(lid)
#             #     session_base.commit()
#             #     logger.warning(f"{link}---------------- -- {ooo['full_name']}")
#             # except SQLAlchemyError as exc:
#             #     session_base.rollback()
#             #     logger.warning(f"{link} ---------- rollback - SQLAlchemyError")
#         elif not ooo["address_yur"]:
#             # try:
#             lid = Lids(
#                 category_id=1, created_on=datetime.date.today(), date_registration_eis=ooo["date_registration_eis"],
#                 date_registration_ifns=ooo["date_registration_ifns"], email=ooo["email"], full_name=ooo["full_name"],
#                 short_name=ooo["short_name"], inn=ooo["inn"], number_in_reestr=ooo["number_in_reestr"],
#                 ogrn=ooo["ogrn"],
#                 status_registration_eis=ooo["status_registration_eis"], kpp=ooo["kpp"], phone=ooo["phone"],
#             )
#                 # session_base.add(lid)
#                 # session_base.commit()
#                 # logger.warning(f"{link}---------------- -- {ooo['full_name']}")
#             # except SQLAlchemyError as exc:
#             #     session_base.rollback()
#             #     logger.warning(f"{link} ----------- -- rollback - SQLAlchemyError")
#         elif not ooo["phone"]:
#             # try:
#             lid = Lids(
#                 category_id=1, created_on=datetime.date.today(), date_registration_eis=ooo["date_registration_eis"],
#                 date_registration_ifns=ooo["date_registration_ifns"], email=ooo["email"], full_name=ooo["full_name"],
#                 short_name=ooo["short_name"], inn=ooo["inn"], number_in_reestr=ooo["number_in_reestr"],
#                 ogrn=ooo["ogrn"],
#                 status_registration_eis=ooo["status_registration_eis"], address_yur=ooo["address_yur"],
#                 kpp=ooo["kpp"]
#             )
#         session_base.add(lid)
#         session_base.commit()
#         logger.warning(f"{link}---------------- -- {ooo['full_name']}")
#     except SQLAlchemyError as exc:
#         session_base.rollback()
#         logger.warning(f"{link} ---------- -- rollback - SQLAlchemyError")


# async def correct_ip(ip, link):
#     logger.warning(f"{link} =======")
#     if not ip["date_registration_eis"]:
#         try:
#             lid = Lids(
#                 category_id=2, created_on=datetime.date.today(),
#                 date_registration_ifns=ip["date_registration_ifns"], email=ip["email"], full_name=ip["full_name"],
#                 inn=ip["inn"], number_in_reestr=ip["number_in_reestr"], ogrn=ip["ogrn"],
#                 status_registration_eis=ip["status_registration_eis"],
#             )
#             session_base.add(lid)
#             session_base.commit()
#         except SQLAlchemyError as exc:
#             session_base.rollback()
#             logger.warning(f"{link} {exc} -- rollback - SQLAlchemyError")
#     if not ip["date_registration_ifns"]:
#         try:
#             lid = Lids(
#                 category_id=2, created_on=datetime.date.today(), date_registration_eis=ip["date_registration_eis"],
#                 email=ip["email"], full_name=ip["full_name"],
#                 inn=ip["inn"], number_in_reestr=ip["number_in_reestr"], ogrn=ip["ogrn"],
#                 status_registration_eis=ip["status_registration_eis"],
#             )
#             session_base.add(lid)
#             session_base.commit()
#         except SQLAlchemyError as exc:
#             session_base.rollback()
#             logger.warning(f"{link} {exc} -- rollback - SQLAlchemyError")
#     if not ip["email"]:
#         try:
#             lid = Lids(
#                 category_id=2, created_on=datetime.date.today(), date_registration_eis=ip["date_registration_eis"],
#                 date_registration_ifns=ip["date_registration_ifns"], full_name=ip["full_name"],
#                 inn=ip["inn"], number_in_reestr=ip["number_in_reestr"], ogrn=ip["ogrn"],
#                 status_registration_eis=ip["status_registration_eis"],
#             )
#             session_base.add(lid)
#             session_base.commit()
#         except SQLAlchemyError as exc:
#             session_base.rollback()
#             logger.warning(f"{link} {exc} -- rollback - SQLAlchemyError")
#     if not ip["full_name"]:
#         try:
#             lid = Lids(
#                 category_id=2, created_on=datetime.date.today(), date_registration_eis=ip["date_registration_eis"],
#                 date_registration_ifns=ip["date_registration_ifns"], email=ip["email"],
#                 inn=ip["inn"], number_in_reestr=ip["number_in_reestr"], ogrn=ip["ogrn"],
#                 status_registration_eis=ip["status_registration_eis"],
#             )
#             session_base.add(lid)
#             session_base.commit()
#         except SQLAlchemyError as exc:
#             session_base.rollback()
#             logger.warning(f"{link} {exc} -- rollback - SQLAlchemyError")
#     if not ip["ogrn"]:
#         try:
#             lid = Lids(
#                 category_id=2, created_on=datetime.date.today(), date_registration_eis=ip["date_registration_eis"],
#                 date_registration_ifns=ip["date_registration_ifns"], email=ip["email"], full_name=ip["full_name"],
#                 inn=ip["inn"], number_in_reestr=ip["number_in_reestr"],
#                 status_registration_eis=ip["status_registration_eis"],
#             )
#             session_base.add(lid)
#             session_base.commit()
#         except SQLAlchemyError as exc:
#             session_base.rollback()
#             logger.warning(f"{link} {exc} -- rollback - SQLAlchemyError")
#     if not ip["inn"]:
#         try:
#             lid = Lids(
#                 category_id=2, created_on=datetime.date.today(), date_registration_eis=ip["date_registration_eis"],
#                 date_registration_ifns=ip["date_registration_ifns"], email=ip["email"], full_name=ip["full_name"],
#                 number_in_reestr=ip["number_in_reestr"], ogrn=ip["ogrn"],
#                 status_registration_eis=ip["status_registration_eis"],
#             )
#             session_base.add(lid)
#             session_base.commit()
#             session_base.add(lid)
#             session_base.commit()
#         except SQLAlchemyError as exc:
#             session_base.rollback()
#             logger.warning(f"{link} {exc} -- rollback - SQLAlchemyError")
#     if not ip["number_in_reestr"]:
#         try:
#             lid = Lids(
#                 category_id=2, created_on=datetime.date.today(), date_registration_eis=ip["date_registration_eis"],
#                 date_registration_ifns=ip["date_registration_ifns"], email=ip["email"], full_name=ip["full_name"],
#                 inn=ip["inn"], ogrn=ip["ogrn"],
#                 status_registration_eis=ip["status_registration_eis"],
#             )
#             session_base.add(lid)
#             session_base.commit()
#         except SQLAlchemyError as exc:
#             session_base.rollback()
#             logger.warning(f"{link} {exc} -- rollback - SQLAlchemyError")
#     if not ip["status_registration_eis"]:
#         try:
#             lid = Lids(
#                 category_id=2, created_on=datetime.date.today(), date_registration_eis=ip["date_registration_eis"],
#                 date_registration_ifns=ip["date_registration_ifns"], email=ip["email"], full_name=ip["full_name"],
#                 inn=ip["inn"], number_in_reestr=ip["number_in_reestr"], ogrn=ip["ogrn"],
#             )
#             session_base.add(lid)
#             session_base.commit()
#         except SQLAlchemyError as exc:
#             session_base.rollback()
#             logger.warning(f"{link} {exc} -- rollback - SQLAlchemyError")


def main():
    get_links_from_logfiles()
    logger.warning("--- Start probe!--- ")

    start = time.time()

    # per_page = 10
    # while True:

    # while True:
    # contaner_links = get_links_by_segments(period_segment, start_date_str, page, per_page)

    asyncio.run(create_tasks_soap())

    print(time.time() - start)
    print('end============================================================')


def get_links_from_logfiles():
    """ Получает ссылки  из лог файла для повторной обработки """

    file_name = os.path.abspath('logfile.txt')
    command_str = f"awk '{{print $10}}' {file_name}"
    comman = shlex.split(command_str)
    popen = subprocess.Popen(comman, stdout=subprocess.PIPE, universal_newlines=True)
    std = popen.stdout.read().strip()
    memory = std.split('\n')

    with open('logfile_links.txt', 'a') as file:
        for i in memory:
            if i:
                file.write(i + '\n')
    # os.remove(file_name)


if __name__ == "__main__":
    count_line = 0
    try:
        main()
    except Exception as exc:
        logger.exception('Common exception!', exc_info=exc)
        print('end')







