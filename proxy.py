import random
import re
import time
from pprint import pprint

import requests

from requests import ReadTimeout, HTTPError
from bs4 import BeautifulSoup as bs
from requests.exceptions import ProxyError



def check_for_response(response):
    if 'error' in response:
        error_message = f"Error {response['error']['error_msg']}"
        raise HTTPError(error_message)


def get_free_proxies():
    print('-------------------------new\n')

    url = "https://free-proxy-list.net/"
    soup = bs(requests.get(url).text, "lxml")
    proxies = []
    for row in soup.select_one(".table-responsive").find_all("tr")[1:]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except IndexError:
            continue
    print(len(proxies))
    return proxies



def writs_file():
    proxies = get_free_proxies()
    for proxy in proxies:
        proxy_clean = re.search("([0-9]{1,3}[\.]){3}[0-9]{1,3}:[0-9]{2,4}", proxy).group()
        with open("proxies", 'a') as file:
            file.write('http://'+proxy_clean+'\n')



writs_file()
with open("proxies", 'r') as file:
    proxies=file.read().split('\n')
for i in proxies:
    print(i)

#---------------------------------------------------------------------------------------------------------
def get_session():
    standart_proxies = get_free_proxies()
    proxies = random.sample(standart_proxies, k=len(standart_proxies))
    # создать HTTP‑сеанс
    session = requests.Session()
    proxies_collection = []
    for pr in proxies:
        # print(pr,'1111111111111111111111')
        proxy = re.search("([0-9]{1,3}[\.]){3}[0-9]{1,3}:[0-9]{2,4}", pr).group()
        try:
            # print(proxy,'2222222222222222222222')
            session.proxies = {"http": 'http://'+proxy}

            response = session.get("http://icanhazip.com", timeout=1)
            # response = session.get("http://sitespy.ru/my-ip", timeout=1)

            if proxy and response.ok:
                proxies_collection.append(proxy)
                print(response.status_code)
                print(proxy,'--------------')
                print(response.text)
                if len(proxies_collection) == 5:
                    return proxies_collection
        except ReadTimeout as exc:
            # print(exc, '33300')
            pass
        except HTTPError as exc:
            pass
            # print(exc, '99900')
        except ConnectionError as exc:
            pass
            print(exc, '88800')
            time.sleep(5)
        except Exception as exc:
            pass

# get_session()

# def main():
#     v=0
#     while True:
#         v += 1
#         print(v)
#         get_session()
#         time.sleep(20)
#
#
# if __name__ == "__main__":
#     main()
#     print('start')
# if __name__ != "__main__":
#     proxies_res = get_session()





# c= ('41.76.155.26:80', '118.70.12.171:53281', '176.31.68.252')
# for i in c:
#     print(i)
#     p=re.search("([0-9]{1,3}[\.]){3}[0-9]{1,3}", i).group()
#     print(p)



