exit ("ПРОкомментируйте эту строку, чтобы повторно инициализировать таблицы базы данных.")
import asyncio
import logging
logging .basicConfig (level =logging .INFO )
logger =logging .getLogger (__name__ )
from db .database import ormar_config
from db .models import Member ,Spam
async def reinit_db_tables ()->None :
    logger .info ("Подключение к базе данных...")
    if not ormar_config .database .is_connected :
        await ormar_config .database .connect ()
    logger .warning ("Удаление всех таблиц...")
    async with ormar_config .engine .begin ()as conn :
        await conn .run_sync (ormar_config .metadata .drop_all )
    logger .info ("Создание таблиц...")
    async with ormar_config .engine .begin ()as conn :
        await conn .run_sync (ormar_config .metadata .create_all )
    await ormar_config .database .disconnect ()
    await ormar_config .engine .dispose ()
    logger .info ("Таблицы базы данных успешно воссозданы!")
if __name__ =="__main__":
    asyncio .run (reinit_db_tables ())
    exit ("DONE")