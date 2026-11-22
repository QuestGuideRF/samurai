import asyncio
import logging
from aiohttp import web
logger =logging .getLogger (__name__ )
class HealthCheckServer :
    def __init__ (self ,host :str ="0.0.0.0",port :int =8080 )->None :
        self .host =host
        self .port =port
        self .app =web .Application ()
        self .runner :web .AppRunner |None =None
        self ._is_ready =False
        self .app .router .add_get ("/health",self ._health_handler )
        self .app .router .add_get ("/ready",self ._ready_handler )
        self .app .router .add_get ("/",self ._health_handler )
    async def _health_handler (self ,request :web .Request )->web .Response :
        return web .json_response ({"status":"healthy"})
    async def _ready_handler (self ,request :web .Request )->web .Response :
        if self ._is_ready :
            return web .json_response ({"status":"ready"})
        return web .json_response (
        {"status":"не готов"},
        status =503
        )
    def set_ready (self ,ready :bool =True )->None :
        self ._is_ready =ready
    async def start (self )->None :
        self .runner =web .AppRunner (self .app )
        await self .runner .setup ()
        site =web .TCPSite (self .runner ,self .host ,self .port )
        await site .start ()
        logger .info (f"Health check server started on {self .host }:{self .port }")
    async def stop (self )->None :
        if self .runner :
            await self .runner .cleanup ()
            logger .info ("Сервер проверки работоспособности остановлен")
_health_server :HealthCheckServer |None =None
def get_health_server (host :str ="0.0.0.0",port :int =8080 )->HealthCheckServer :
    global _health_server
    if _health_server is None :
        _health_server =HealthCheckServer (host =host ,port =port )
    return _health_server
async def start_health_server (host :str ="0.0.0.0",port :int =8080 )->HealthCheckServer :
    server =get_health_server (host ,port )
    await server .start ()
    return server
async def stop_health_server ()->None :
    global _health_server
    if _health_server :
        await _health_server .stop ()
        _health_server =None