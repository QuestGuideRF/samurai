import random
from pathlib import Path
from typing import Any
from fluent_compiler .bundle import FluentBundle
class FluentLocalization :
    def __init__ (
    self ,
    locales_dir :str |Path ="locales",
    default_locale :str ="ru"
    )->None :
        self .locales_dir =Path (locales_dir )
        self .default_locale =default_locale
        self .bundles :dict [str ,FluentBundle ]={}
        self ._load_locales ()
    def _load_locales (self )->None :
        if not self .locales_dir .exists ():
            raise FileNotFoundError (f"Locales directory not found: {self .locales_dir }")
        for locale_dir in self .locales_dir .iterdir ():
            if not locale_dir .is_dir ():
                continue
            locale_code =locale_dir .name
            ftl_content =""
            for ftl_file in locale_dir .glob ("*.ftl"):
                ftl_content +=ftl_file .read_text (encoding ="utf-8")+"\n"
            if ftl_content :
                bundle =FluentBundle .from_string (locale_code ,ftl_content )
                self .bundles [locale_code ]=bundle
        if not self .bundles :
            raise ValueError (f"No locales found in {self .locales_dir }")
        if self .default_locale not in self .bundles :
            self .default_locale =next (iter (self .bundles .keys ()))
    def get (
    self ,
    key :str ,
    locale :str |None =None ,
    **kwargs :Any
    )->str :
        locale =locale or self .default_locale
        bundle =self .bundles .get (locale )
        if bundle :
            try :
                result =bundle .format (key ,kwargs )
                if result and result [0 ]:
                    return result [0 ]
            except KeyError :
                pass
        if locale !=self .default_locale :
            bundle =self .bundles .get (self .default_locale )
            if bundle :
                try :
                    result =bundle .format (key ,kwargs )
                    if result and result [0 ]:
                        return result [0 ]
                except KeyError :
                    pass
        return key
    def get_random (
    self ,
    key :str ,
    locale :str |None =None ,
    **kwargs :Any
    )->str :
        result =self .get (key ,locale ,**kwargs )
        if result ==key :
            return result
        items =[item .strip ()for item in result .split ("---")if item .strip ()]
        if not items :
            return key
        return random .choice (items )
    def __call__ (
    self ,
    key :str ,
    locale :str |None =None ,
    **kwargs :Any
    )->str :
        return self .get (key ,locale ,**kwargs )
    @property
    def available_locales (self )->list [str ]:
        return list (self .bundles .keys ())
_i18n :FluentLocalization |None =None
def get_i18n ()->FluentLocalization :
    global _i18n
    if _i18n is None :
        from config import config
        _i18n =FluentLocalization (
        locales_dir ="locales",
        default_locale =config .locale .default
        )
    return _i18n
def _ (key :str ,locale :str |None =None ,**kwargs :Any )->str :
    return get_i18n ().get (key ,locale ,**kwargs )
def _random (key :str ,locale :str |None =None ,**kwargs :Any )->str :
    return get_i18n ().get_random (key ,locale ,**kwargs )
def get_string (key :str ,**kwargs :Any )->str :
    fluent_key =key .replace ("_","-")
    return _ (fluent_key ,**kwargs )