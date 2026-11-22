from typing import Union
from aiogram .filters import BaseFilter
from aiogram .types import Message ,CallbackQuery
class ChatIdFilter (BaseFilter ):
    def __init__ (self ,chat_id :int )->None :
        self .chat_id =chat_id
    async def __call__ (self ,event :Union [Message ,CallbackQuery ])->bool :
        if isinstance (event ,CallbackQuery ):
            if event .message is None :
                return False
            return event .message .chat .id ==self .chat_id
        return event .chat .id ==self .chat_id