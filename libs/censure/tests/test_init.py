from __future__ import unicode_literals
from censure .tests .base import *
class CensorLangTestCase (CoreTestCase ):
    def test_lang_setup (self ):
        c =Censor .get ()
        self .assertEqual (c .lang ,'ru')
        c =Censor .get (lang ='ru')
        self .assertEqual (c .lang ,'ru')
        c =Censor .get (lang ='en')
        self .assertEqual (c .lang ,'en')
        lang ='ar'
        self .assertNotIn ('ar',Censor .supported_langs )
        self .assertRaises (CensorException ,Censor .get ,lang =lang )