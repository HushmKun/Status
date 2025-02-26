import traceback
from aiohttp import web
import ssl
import os

from lib.config import config
from lib.machine import Machine
from lib.cache import Cache


# machine = Machine()
# cache = Cache()

working_dir = os.path.dirname(os.path.realpath(__file__))


def get_status():
	# if cache.should_update():
	# 	info = await machine.get_full_info()
	# 	cache.update(info)
	data = {"cpu": {"model": "Intel(R) Celeron(R) J6412 @ 2.00GHz", "utilisation": 0.0, "temperatures": {"Core 0": [34.0, 105.0], "Core 1": [35.0, 105.0], "Core 2": [34.0, 105.0], "Core 3": [34.0, 105.0]}, "frequencies": {"cpu0": {"now": 800, "min": 800, "base": null, "max": 2001}, "cpu1": {"now": 800, "min": 800, "base": null, "max": 2001}, "cpu2": {"now": 800, "min": 800, "base": null, "max": 2001}, "cpu3": {"now": 800, "min": 800, "base": null, "max": 2001}}, "count": 4, "cache": 4096, "cores": 4}, "memory": {"total": 7626637, "available": 6814392, "cached": 2099818, "swap_total": 4294963, "swap_available": 4294963, "processes": 142}, "storage": {"OS": {"icon": "settings", "total": 62763018649.6, "available": 49809514496}, "1722": {"icon": "folder", "total": 77463552, "available": 0}, "2963": {"icon": "folder", "total": 146407424, "available": 0}, "23545": {"icon": "folder", "total": 46661632, "available": 0}}, "network": {"interface": "enp3s0", "speed": 100, "rx": 876229956, "tx": 207546253}, "host": {"uptime": 430295.94, "os": "Ubuntu 24.10", "hostname": "home_server", "app_memory": "32064", "loadavg": [0.0, 0.01, 0.0]}} 
	return data


routes = web.RouteTableDef()


@routes.get("/")
async def index(request):
	return web.FileResponse("html/index.html")


@routes.get("/api/status")
async def api(request):
	try:
		return web.json_response(get_status())
	except:
		report = traceback.format_exc().replace(f"{working_dir}/", "")
		return web.Response(text=report, status=500)


@web.middleware
async def redirector(request, handler):
	try:
		resp = await handler(request)
		if config.get("server", "enable_cors"):
			resp.headers["Access-Control-Allow-Origin"] = "*"
		return resp

	except (web.HTTPInternalServerError, web.HTTPForbidden, web.HTTPNotFound):
		raise web.HTTPFound(location="/")


routes.static("/", "html")
app = web.Application(middlewares=[redirector])
app.logger.manager.disable = 100 * config.get("misc", "debug")
app.add_routes(routes)

ssl_context = None

if config.get("server", "domain"):
	ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
	ssl_dir = f"/etc/letsencrypt/live/{config.get('server', 'domain')}"

	pubkey = config.get("server", "tls_cert_path")
	if not pubkey:
		pubkey = f"{ssl_dir}/fullchain.pem"

	privkey = config.get("server", "tls_key_path")
	if not privkey:
		privkey = f"{ssl_dir}/privkey.pem"

	ssl_context.load_cert_chain(pubkey, privkey)


web.run_app(app,
	host=config.get("server", "address"),
	port=int(config.get("server", "port")),
	ssl_context=ssl_context
)
