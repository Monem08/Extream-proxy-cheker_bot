import aiohttp
import asyncio

# ⚙️ CONFIG
TIMEOUT = 5
CONCURRENT_LIMIT = 50


async def check_proxy(session, proxy):
    proxy = proxy.strip()

    if not proxy:
        return (proxy, False)

    # ensure format
    if "://" not in proxy:
        proxy_url = f"http://{proxy}"
    else:
        proxy_url = proxy

    try:
        async with session.get(
            "http://httpbin.org/ip",
            proxy=proxy_url,
            timeout=aiohttp.ClientTimeout(total=TIMEOUT),
        ) as resp:
            if resp.status == 200:
                return (proxy, True)
    except:
        pass

    return (proxy, False)


async def run_scan(proxies):
    connector = aiohttp.TCPConnector(ssl=False)
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:

        semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)

        async def bound_check(proxy):
            async with semaphore:
                return await check_proxy(session, proxy)

        tasks = [bound_check(p) for p in proxies if p.strip()]

        results = await asyncio.gather(*tasks)

    return results
