import asyncio
from aiohttp import web
import json
import aiomysql
import random
import os
import re

goodbyes = ["Bye!", "Adios!", "Auf Wiedersehen!", "さようなら！", "再見！", "안녕히 가세요!"]

class Coleslaw:
    db = None
    ShowAPICalls = False

    @classmethod
    async def load_config(cls):
        if not os.path.exists("coleslaw.config"):
            with open("coleslaw.config", "w") as f:
                json.dump({"ShowAPICalls": False}, f, indent=4)
        else:
            with open("coleslaw.config", "r") as f:
                cfg = json.load(f)
            cls.ShowAPICalls = cfg.get("ShowAPICalls", False)

    @classmethod
    async def UseDBConnectionJSON(cls, json_file):
        if os.path.exists(json_file):
            with open(json_file, "r") as f:
                cfg = json.load(f)
            cls.db = ColeslawMySQL(
                host=cfg.get("host", "127.0.0.1"),
                port=cfg.get("port", 3306),
                user=cfg.get("user", ""),
                password=cfg.get("password", ""),
                database=cfg.get("database", "")
            )
            await cls.db.connect()
        else:
            default_cfg = {
                "host": "127.0.0.1",
                "port": 3306,
                "user": "root",
                "password": "",
                "database": "mydatabase",
                "ShowAPICalls": False
            }
            with open(json_file, "w") as f:
                json.dump(default_cfg, f, indent=4)
            cls.warn(f"{json_file} created. Please configure your database credentials.")

    def __init__(self, name):
        self.name = name
        self.routes = []

    @staticmethod
    def redirect(url: str, permanent=False):
        url = str(url)
        if permanent:
            return web.HTTPMovedPermanently(location=url)
        return web.HTTPFound(location=url)

    def info(self, message, duration_ms=None):
        if Coleslaw.ShowAPICalls:
            prefix = f"[{duration_ms}ms] " if duration_ms is not None else ""
            print(f"\x1b[1;37m[Coleslaw Server] [Info] {prefix}{message}\x1b[0m")

    def error(self, message, duration_ms=None):
        prefix = f"[{duration_ms}ms] " if duration_ms is not None else ""
        print(f"\x1b[1;31m[Coleslaw Server] [ERROR] {prefix}{message}\x1b[0m")

    def warn(self, message):
        print(f"\x1b[1;33m[Coleslaw Server] [WARN] {message}\x1b[0m")

    def route(self, path, methods=["GET"]):
        pattern, param_names = self._compile_path(path)
        self.routes.append((methods, pattern, param_names, path))
        def decorator(func):
            self.routes[-1] = (methods, pattern, param_names, func)
            return func
        return decorator

    def _compile_path(self, path):
        param_names = []
        regex = re.sub(r"{(\w+):(\w+)}", lambda m: self._replace_param(m, param_names), path)
        return re.compile(f"^{regex}$"), param_names

    def _replace_param(self, match, param_names):
        name, typ = match.groups()
        param_names.append((name, typ))
        if typ == "int":
            return r"(\d+)"
        return r"([^/]+)"

    async def handler(self, request):
        start_time = asyncio.get_event_loop().time()
        path = request.path
        method = request.method
        try:
            data = await request.json()
        except:
            data = {}
        query = {k: v for k, v in request.query.items()}

        Coleslaw.data = data
        Coleslaw.query = query

        for methods, pattern, param_names, func in self.routes:
            if method in methods and pattern.match(path):
                match = pattern.match(path)
                kwargs = {}
                for i, (name, typ) in enumerate(param_names):
                    value = match.group(i+1)
                    if typ == "int":
                        value = int(value)
                    kwargs[name] = value
                if asyncio.iscoroutinefunction(func):
                    resp = await func(**kwargs)
                else:
                    resp = func(**kwargs)
                duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
                if isinstance(resp, web.Response):
                    self.info(f"{method} {path} -> {resp.status}", duration_ms)
                    return resp
                self.info(f"{method} {path} -> 200 OK", duration_ms)
                return web.json_response(resp)

        duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
        self.error(f"{method} {path} -> 404 NOT FOUND", duration_ms)
        return web.Response(text="Not Found", status=404)

    async def run(self, host="0.0.0.0", port=8000):
        await self.load_config()
        app = web.Application()
        app.router.add_route("*", "/{tail:.*}", self.handler)
        self.info(f"Project.. {self.name} Initializing...")
        self.info(f"Server Listening on port {port}")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        try:
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            self.info(f"Shutting Down... {random.choice(goodbyes)}")

class ColeslawMySQL:
    def __init__(self, host="127.0.0.1", port=3306, user="", password="", database=""):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.pool = None
        self.conn = None
        self.cursor = None

    async def connect(self):
        self.pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.database,
            autocommit=True,
            charset='utf8mb4'
        )
        self.conn = await self.pool.acquire()
        self.cursor = await self.conn.cursor(aiomysql.DictCursor)
        print(f"[ColeslawMySQL] Connected to {self.host}:{self.port}/{self.database}")

    async def execute(self, query, params=None):
        if not self.cursor:
            raise RuntimeError("Not connected to the database.")
        if params is None:
            params = ()
        await self.cursor.execute(query, params)

    async def fetchone(self):
        if not self.cursor:
            raise RuntimeError("Not connected to the database.")
        return await self.cursor.fetchone()

    async def fetchall(self):
        if not self.cursor:
            raise RuntimeError("Not connected to the database.")
        return await self.cursor.fetchall()

    async def close(self):
        if self.cursor:
            await self.cursor.close()
        if self.conn:
            self.pool.release(self.conn)
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            print("[ColeslawMySQL] Connection Closed.")
