from typing import Any ,Awaitable ,Callable ,Dict
from aiogram import BaseMiddleware
from aiogram .types import TelegramObject ,User
from core .i18n import get_i18n
class I18nMiddleware (BaseMiddleware ):
    def __init__ (self ,default_locale :str ="ru")->None :
        self .default_locale =default_locale
        super ().__init__ ()
    async def __call__ (
    self ,
    handler :Callable [[TelegramObject ,Dict [str ,Any ]],Awaitable [Any ]],
    event :TelegramObject ,
    data :Dict [str ,Any ]
    )->Any :
        user :User |None =data .get ("event_from_user")
        locale =self .default_locale
        if user and user .language_code :
            i18n =get_i18n ()
            if user .language_code in i18n .available_locales :
                locale =user .language_code
            elif user .language_code [:2 ]in i18n .available_locales :
                locale =user .language_code [:2 ]
        i18n =get_i18n ()
        def translate (key :str ,**kwargs :Any )->str :
            return i18n .get (key ,locale =locale ,**kwargs )
        data ["i18n"]=translate
        data ["locale"]=locale
        return await handler (event ,data )