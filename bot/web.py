from aiohttp import web


async def home(_: web.Request) -> web.Response:
    return web.Response(text="Bot is alive", status=200)


async def ping(_: web.Request) -> web.Response:
    return web.Response(text="pong", status=200)


def create_health_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", home)
    app.router.add_get("/ping", ping)
    return app


async def start_health_server(port: int) -> web.AppRunner:
    app = create_health_app()
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()

    return runner
