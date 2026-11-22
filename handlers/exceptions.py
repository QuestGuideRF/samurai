import logging
from aiogram import Router
from aiogram .types import ErrorEvent
from aiogram .exceptions import (
TelegramUnauthorizedError ,
TelegramBadRequest ,
TelegramAPIError ,
TelegramRetryAfter ,
)
router =Router (name ="exceptions")
@router .error ()
async def error_handler (event :ErrorEvent )->bool :
    exception =event .exception
    update =event .update
    if isinstance (exception ,TelegramBadRequest )and "не могу понизить статус создателя чата"in str (exception ):
        logging .debug ("Не могу понизить статус создателя чата")
        return True
    if isinstance (exception ,TelegramBadRequest )and "сообщение не изменено"in str (exception ):
        logging .debug ("Сообщение не изменено")
        return True
    if isinstance (exception ,TelegramBadRequest )and "сообщение не может быть удалено"in str (exception ):
        logging .debug ("Сообщение не может быть удалено")
        return True
    if isinstance (exception ,TelegramBadRequest )and "сообщение для удаления не найдено"in str (exception ):
        logging .debug ("Сообщение для удаления не найдено")
        return True
    if isinstance (exception ,TelegramBadRequest )and "текст сообщения пуст"in str (exception ):
        logging .debug ("Текст сообщения пуст")
        return True
    if isinstance (exception ,TelegramUnauthorizedError ):
        logging .info (f"Unauthorized: {exception }")
        return True
    if isinstance (exception ,TelegramBadRequest )and "запрос слишком старый"in str (exception ):
        logging .debug (f"Invalid query ID: {exception }")
        return True
    if isinstance (exception ,TelegramRetryAfter ):
        logging .warning (f"Retry after {exception .retry_after } seconds")
        return True
    if isinstance (exception ,TelegramBadRequest )and "не могу разобрать сущности"in str (exception ):
        logging .exception (f"Can't parse entities: {exception }\nUpdate: {update }")
        return True
    if isinstance (exception ,TelegramAPIError ):
        logging .exception (f"TelegramAPIError: {exception }\nUpdate: {update }")
        return True
    logging .exception (f"Unhandled exception: {exception }\nUpdate: {update }")
    return False