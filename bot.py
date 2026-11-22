import asyncio
import logging
import sys
from contextlib import suppress
from aiogram import Bot ,Dispatcher
from aiogram .client .default import DefaultBotProperties
from aiogram .enums import ParseMode
from config import config
from db import init_db ,close_db
from handlers import register_all_handlers
from middlewares import register_all_middlewares
from services .announcements import set_bot as set_announcements_bot ,run_scheduler
from services .healthcheck import start_health_server ,stop_health_server ,get_health_server
from services .cache import start_batch_flush_task ,stop_batch_flush_task ,flush_member_updates
from services import ml_manager
logging .basicConfig (
level =logging .INFO ,
format ="%(asctime)s - %(имя)s - %(имя уровня)s - %(сообщение)s",
datefmt ="%Y-%m-%d %H:%M:%S"
)
logger =logging .getLogger (__name__ )
_scheduler_task :asyncio .Task |None =None
async def on_startup (bot :Bot )->None :
    global _scheduler_task
    logger .info ("Бот запускается...")
    await init_db ()
    logger .info ("База данных подключена")
    start_batch_flush_task ()
    logger .info ("Задача пакетной очистки запущена")
    set_announcements_bot (bot )
    _scheduler_task =asyncio .create_task (run_scheduler ())
    logger .info ("Объявления запланированы")
    ml_manager .start_monitor ()
    if config .healthcheck .enabled :
        get_health_server ().set_ready (True )
    logger .info (f"Bot version: {config .bot .version } ({config .bot .version_codename })")
async def on_shutdown (bot :Bot )->None :
    global _scheduler_task
    logger .info ("Бот отключается...")
    if config .healthcheck .enabled :
        get_health_server ().set_ready (False )
    ml_manager .stop_monitor ()
    if _scheduler_task and not _scheduler_task .done ():
        _scheduler_task .cancel ()
        with suppress (asyncio .CancelledError ):
            await _scheduler_task
        logger .info ("Планировщик остановлен")
    stop_batch_flush_task ()
    flushed =await flush_member_updates ()
    logger .info (f"Flushed {flushed } pending member updates")
    await close_db ()
    logger .info ("База данных отключена")
    if config .healthcheck .enabled :
        await stop_health_server ()
        logger .info ("Сервер проверки работоспособности остановлен")
async def main ()->None :
    if not config .bot .token .get_secret_value ():
        logger .error ("Токен бота не предоставлен.")
        sys .exit (1 )
    if config .healthcheck .enabled :
        await start_health_server (
        host =config .healthcheck .host ,
        port =config .healthcheck .port
        )
    bot =Bot (
    token =config .bot .token .get_secret_value (),
    default =DefaultBotProperties (parse_mode =ParseMode .HTML )
    )
    dp =Dispatcher ()
    register_all_handlers (dp )
    register_all_middlewares (
    dp ,
    default_locale =config .locale .default ,
    enable_throttling =config .throttling .enabled ,
    throttle_rate =config .throttling .rate_limit ,
    throttle_max_messages =config .throttling .max_messages ,
    throttle_time_window =config .throttling .time_window
    )
    dp .startup .register (on_startup )
    dp .shutdown .register (on_shutdown )
    logger .info ("Бот запущен")
    try :
        await dp .start_polling (bot ,skip_updates =True )
    finally :
        await bot .session .close ()
def run ()->None :
    asyncio .run (main ())
if __name__ =="__main__":
    run ()