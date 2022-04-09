
import asyncio
import aiofiles
import aiohttp
from aiohttp import BaseConnector


async def get_proxy(session, proxy_str):
    URL = "http://icanhazip.com"
    try:
        async with session.get(URL, proxy=proxy_str) as response:
            if response.ok:
                result = await response.text()
                # print(result.strip())
                print(proxy_str)
                with open("proxy_clean", 'a') as file:
                    file.write(proxy_str + '\n')

    except Exception as exc:
        pass
        # print(exc)
    # return result


async def get_tasks():
    async with aiofiles.open("proxies", 'r') as file:
        proxies_str = await file.read()
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(5)) as session:
        tasks = [get_proxy(session, proxy) for proxy in proxies_str.split()]
        return await asyncio.gather(*tasks)


def main():
    res = asyncio.run(get_tasks())
    print(len(res))
    print(res)


if __name__ == "__main__":
    main()








# async def get_proxy(session, proxy):
#     URL = "http://icanhazip.com"
#     async with session.get(URL) as response:
#         print(response.status)
#         result = await response.text()
#         print(result)
#         return result
#
#
# async def get_tasks():
#     async with aiofiles.open("proxies", 'r') as file:
#         proxies_str = await file.read()
#
#     async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(10)) as session:
#         tasks = [get_proxy(session, proxy) for proxy in proxies_str.split()]
#
#         return await asyncio.gather(*tasks)
#
#
# def main():
#     res = asyncio.run(get_tasks())
#     print(len(res))
#
#
# if __name__ == "__main__":
#     main()