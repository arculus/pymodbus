"""HTTP server for modbus simulator."""
import asyncio
import importlib
import json
import logging
import os


try:
    from aiohttp import web
except ImportError:
    web = None

from pymodbus.datastore import ModbusServerContext, ModbusSimulatorContext
from pymodbus.server import (
    ModbusSerialServer,
    ModbusTcpServer,
    ModbusTlsServer,
    ModbusUdpServer,
)
from pymodbus.transaction import (
    ModbusAsciiFramer,
    ModbusBinaryFramer,
    ModbusRtuFramer,
    ModbusSocketFramer,
    ModbusTlsFramer,
)


_logger = logging.getLogger(__name__)


class ModbusSimulatorServer:
    """**ModbusSimulatorServer**.

    :param modbus_server: Server name in json file (default: "server")
    :param modbus_device: Device name in json file (default: "client")
    :param http_host: TCP host for HTTP (default: 8080)
    :param http_port: TCP port for HTTP (default: "localhost")
    :param json_file: setup file (default: "setup.json")
    :param custom_actions_module: python module with custom actions (default: none)

    if either http_port or http_host is none, HTTP will not be started.
    This class starts a http server, that serves a couple of endpoints:

    - **"<addr>/"** standard entry index.html (see html.py)
    - **"<addr>/web"** standard entry for web pages (see html.py)
    - **"<addr>/log"** standard entry for server log (see html.py)
    - **"<addr>/api"** REST-API general calls(see rest_api.py)
    - **"<addr>/api/register"** REST-API for register handling (uses datastore/simulator)
    - **"<addr>/api/function"** REST-API for function handling (uses Modbus<x>RequestHandler)

    Example::

        from pymodbus.server import StartAsyncSimulatorServer

        async def run():
            simulator = StartAsyncSimulatorServer(
                modbus_server="my server",
                modbus_device="my device",
                http_host="localhost",
                http_port=8080)
            await simulator.start()
            ...
            await simulator.close()
    """

    def __init__(
        self,
        modbus_server: str = "server",
        modbus_device: str = "device",
        http_host: str = "localhost",
        http_port: int = 8080,
        log_file: str = "server.log",
        json_file: str = "setup.json",
        custom_actions_module: str = None,
    ):
        """Initialize http interface."""
        if not web:
            raise RuntimeError("aiohttp not installed!")
        with open(json_file, encoding="utf-8") as file:
            setup = json.load(file)

        comm_class = {
            "serial": ModbusSerialServer,
            "tcp": ModbusTcpServer,
            "tls": ModbusTlsServer,
            "udp": ModbusUdpServer,
        }
        framer_class = {
            "ascii": ModbusAsciiFramer,
            "binary": ModbusBinaryFramer,
            "rtu": ModbusRtuFramer,
            "socket": ModbusSocketFramer,
            "tls": ModbusTlsFramer,
        }
        if custom_actions_module:
            actions_module = importlib.import_module(custom_actions_module)
            custom_actions_module = actions_module.custom_actions_dict
        server = setup["server_list"][modbus_server]
        device = setup["device_list"][modbus_device]
        context = ModbusSimulatorContext(device, custom_actions_module)
        self.datastore = ModbusServerContext(slaves=context, single=True)
        comm = comm_class[server.pop("comm")]
        framer = framer_class[server.pop("framer")]
        self.modbus_server = comm(framer=framer, context=self.datastore, **server)

        self.log_file = log_file
        self.site = None
        self.http_host = http_host
        self.http_port = http_port
        self.web_path = os.path.join(os.path.dirname(__file__), "web")
        self.web_app = web.Application()
        self.web_app.add_routes(
            [
                web.get("/{tail:.*}", self.handle_html),
                web.post("/api", self.handle_api),
                web.post("/api/data", self.handle_api_data),
                web.post("/api/request", self.handle_api_request),
            ]
        )
        self.web_app.on_startup.append(self.start_modbus_server)
        self.web_app.on_shutdown.append(self.stop_modbus_server)

    async def start_modbus_server(self, app):
        """Start Modbus server as asyncio task."""
        try:
            if getattr(self.modbus_server, "start", None):
                await self.modbus_server.start()
            app["modbus_server"] = asyncio.create_task(
                self.modbus_server.serve_forever()
            )
        except Exception as exc:
            txt = f"Error starting modbus server, reason: {exc}"
            _logger.error(txt)
            raise exc
        _logger.info("Modbus server started")

    async def stop_modbus_server(self, app):
        """Stop modbus server."""
        _logger.info("Stopping modbus server")
        app["modbus_server"].cancel()
        await app["modbus_server"]
        _logger.info("Modbus server Stopped")

    def run_forever(self):
        """Start modbus and http servers."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            runner = web.AppRunner(self.web_app)
            loop.run_until_complete(runner.setup())
            self.site = web.TCPSite(runner, self.http_host, self.http_port)
            loop.run_until_complete(self.site.start())
        except Exception as exc:
            txt = f"Error starting http server, reason: {exc}"
            _logger.error(txt)
            raise exc
        _logger.info("HTTP server started")
        loop.run_forever()

    async def stop(self):
        """Stop modbus and http servers."""
        self.site.stop()
        self.site = None

    async def handle_html(self, request):
        """Handle api request."""
        if (page := request.path[1:]) == "":  # pylint: disable=compare-to-empty-string
            page = "index.html"
        file = os.path.join(self.web_path, page)
        try:
            with open(file, encoding="utf-8"):
                return web.FileResponse(file)
        except (FileNotFoundError, IsADirectoryError) as exc:
            raise web.HTTPNotFound(reason="File not found") from exc

    async def handle_api(self, request):
        """Handle api request."""
        data = await request.post()
        return web.Response(text=f"got api {data}")

    async def handle_api_data(self, request):
        """Handle api data request."""
        data = await request.post()
        return web.Response(text="got api data")

    async def handle_api_request(self, request):
        """Handle api function request."""
        data = await request.post()
        return web.Response(text="got api request")
