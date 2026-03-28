import aiohttp
import asyncio

async def check_proxy(proxy):
    url = "http://httpbin.org/ip"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=f"http://{proxy}", timeout=5):
                return proxy, True
    except:
        return proxy, False


async def run_scan(proxy_list):
    tasks = [check_proxy(p) for p in proxy_list]
    return await asyncio.gather(*tasks)
