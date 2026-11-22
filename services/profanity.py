import sys
import re
import unicodedata
sys .path .insert (0 ,"./libs")
from libs .censure import Censor
censor_ru =Censor .get (lang ='ru')
censor_en =Censor .get (lang ='en')
def prepare_word (word :str )->str :
    word =word .lower ()
    word =word .strip ()
    return censor_ru .prepare_word (word )
def detect_name_language (name :str )->str :
    russian_chars =set ('абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
    english_chars =set ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    russian_count =sum (1 for char in name if char in russian_chars )
    english_count =sum (1 for char in name if char in english_chars )
    total_letters =russian_count +english_count
    if total_letters ==0 :
        return 'unknown'
    elif russian_count >english_count :
        return 'russian'
    elif english_count >russian_count :
        return 'english'
    else :
        return 'unknown'
def check_for_profanity (text :str ,lang :str ="ru")->tuple [bool ,str |None ,tuple ]:
    _profanity_detected =False
    _word =None
    if lang =="ru"or lang =="russian":
        line_info =censor_ru .clean_line (text )
    else :
        line_info =censor_en .clean_line (text )
    if line_info [1 ]or line_info [2 ]:
        if line_info [1 ]:
            _word =line_info [3 ][0 ]
        else :
            _word =line_info [4 ][0 ]
        _profanity_detected =True
    return _profanity_detected ,_word ,line_info
def check_for_profanity_all (text :str )->tuple [bool ,str |None ]:
    _del =False
    _word =None
    _del ,_word ,_ =check_for_profanity (text ,lang ="ru")
    if not _del :
        _del ,_word ,_ =check_for_profanity (text ,lang ="en")
    return _del ,_word
def check_name_for_violations (name :str )->bool :
    blacklist_words =[
    "профиль",
    "посмотри",
    "кликай",
    "загляни",
    "проф"
    ]
    prepared_name =prepare_word (name )
    is_clean =not any (sub .lower ()in prepared_name .lower ()for sub in blacklist_words )
    profanity_detected ,_ ,_ =check_for_profanity (prepared_name ,detect_name_language (name ))
    return not profanity_detected and is_clean