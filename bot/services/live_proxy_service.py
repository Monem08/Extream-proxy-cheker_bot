import aiohttp

APIS = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
]

async def fetch_proxies():
    proxies = set()

    async with aiohttp.ClientSession() as session:
        for url in APIS:
            try:
                async with session.get(url, timeout=5) as res:
                    text = await res.text()
                    for line in text.splitlines():
                        if ":" in line:
                            proxies.add(line.strip())
            except:
                pass

    return list(proxies)
