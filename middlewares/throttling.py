from typing import Any ,Awaitable ,Callable ,Dict
from aiogram import BaseMiddleware
from aiogram .types import Message ,TelegramObject
from cachetools import TTLCache
class ThrottlingMiddleware (BaseMiddleware ):
    def __init__ (
    self ,
    rate_limit :float =0.5 ,
    max_messages :int =20 ,
    time_window :int =60
    )->None :
        self .rate_limit =rate_limit
        self .max_messages =max_messages
        self .time_window =time_window
        self .last_message_cache :TTLCache =TTLCache (
        maxsize =10000 ,
        ttl =rate_limit *2
        )
        self .message_count_cache :TTLCache =TTLCache (
        maxsize =10000 ,
        ttl =time_window
        )
        super ().__init__ ()
    async def __call__ (
    self ,
    handler :Callable [[TelegramObject ,Dict [str ,Any ]],Awaitable [Any ]],
    event :TelegramObject ,
    data :Dict [str ,Any ]
    )->Any :
        if not isinstance (event ,Message ):
            return await handler (event ,data )
        if event .chat .type !="private":
            return await handler (event ,data )
        user_id =event .from_user .id
        import time
        current_time =time .time ()
        last_time =self .last_message_cache .get (user_id ,0 )
        if current_time -last_time <self .rate_limit :
            return None
        count =self .message_count_cache .get (user_id ,0 )
        if count >=self .max_messages :
            if count ==self .max_messages :
                await event .answer (
                "⚠️ Слишком много сообщений. Подождите немного."
                )
            self .message_count_cache [user_id ]=count +1
            return None
        self .last_message_cache [user_id ]=current_time
        self .message_count_cache [user_id ]=count +1
        return await handler (event ,data )