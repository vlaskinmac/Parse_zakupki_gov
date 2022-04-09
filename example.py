
# import asyncio
# import aiohttp
# from aiohttp_socks import ProxyType, ProxyConnector, ChainProxyConnector
#
# async def main():
#     connector = ProxyConnector.from_url('socks5://log:pass@ip:port')
#     async with aiohttp.ClientSession(connector=connector) as session:
#         async with session.get("http://2ip.ru") as response:
#             print(response)
#
# asyncio.get_event_loop().run_until_complete(main())

#-------------------------------------


# import asyncio
#
# from aiohttp import ClientSession
# from ip_pool.MongoDB import mongodb
# import requests
#
# class ProxyValidator(object):
#
#     def __init__(self):
#         self.url='https://www.zhihu.com/'
#         self.headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36'}
#         self.timeout=3.05
#         self.coro_count=500
#         self.proxyqueue=None
#         self.useableProxy=set()
#
#     async def _validator(self, proxy_queue):     #Test agent's coroutine, scheduled by the event loop, and transferred to the asynchronous queue of the public pending agent
#         if isinstance(proxy_queue,asyncio.Queue):
#             async with ClientSession() as session:
#                 while not self.proxyqueue.empty():
#                     try:
#                         proxy = await proxy_queue.get()
#                         proxystr = 'http://' + proxy['http']
#                         async with session.get(self.url, headers=self.headers,
#                                                proxy=proxystr, timeout=self.timeout) as resp:
#                             if resp.status == 200:
#                                 # text=await resp.text()
#                                 # print(text)
#                                 # if'knowledge' in text:
#                                 # print(resp.headers)
#                                 self.useableProxy.add(proxy['http'])
#                                 print(proxystr)
#
#
#
#                     except asyncio.TimeoutError:
#                         pass
#                     except Exception as e:
#                         pass
#
#     async def _get_proxyqueue(self):
#         mongo=mongodb()
#         proxy_iterator = mongo.find_from_mongodb({}, {'http': 1, '_id': 0}).skip(26000)
#         proxyqueue=asyncio.Queue()
#         for proxy in proxy_iterator:
#             await proxyqueue.put(proxy)
#         self.proxyqueue=proxyqueue
#         return proxyqueue
#
#     async def test_reportor(self):
#         total=self.proxyqueue.qsize()
#         time.clock()
#         while not self.proxyqueue.empty():
#             total_lastsec=self.proxyqueue.qsize()
#             await asyncio.sleep(1)
#             validated_num=total_lastsec-self.proxyqueue.qsize()
#             print('%d validated  %d item/sec; useable proxy: %d  ;%d item to  validate' % ((total-self.proxyqueue.qsize()),validated_num,len(self.useableProxy),self.proxyqueue.qsize()))
#         print('cost %f' % time.clock())
#
#
#     async def start(self):
#         proxy_queue= await self._get_proxyqueue()
#         to_validate=[self._validator(proxy_queue) for _ in range(self.coro_count)]
#         to_validate.append(self.test_reportor())
#         await asyncio.wait(to_validate)
#
#     def proxy_validator_run(self):
#         # loop = asyncio.new_event_loop()
#         # asyncio.set_event_loop(loop)
#         loop=asyncio.get_event_loop()
#         try:
#             loop.run_until_complete(self.start())
#         except Exception as e:
#             print(e)
#
# if __name__ == '__main__':
#     validator=ProxyValidator()
#     validator.proxy_validator_run()

#-----------------------------------------------------------

# Парс прокси
# import aiohttp
# from aiohttp_proxy import ProxyConnector, ProxyType
# import asyncio
# import sys
# import numpy
#
# if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#
# async def fetch(url, proxy):
#     host, port = proxy.split(':')[0], proxy.split(':')[1]
#     connector = ProxyConnector(
#          proxy_type=ProxyType.HTTP,
#          host=host,
#          port= int(port),
#     )
#     async with aiohttp.ClientSession(connector=connector,trust_env=True) as session:
#         async with session.get(url) as response:
#             return await response.text()
#
# if __name__ == "__main__":
#     data = numpy.load('file.npy')
#     loop = asyncio.get_event_loop()
#     l = loop.run_until_complete(fetch('http://api.hh.ru/', data[-1]))
#     print(l)
#     loop.run_until_complete(asyncio.sleep(0.1))
#     loop.close()
