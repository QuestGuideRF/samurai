from __future__ import unicode_literals ,print_function
import os
import codecs
from censure .base import Censor
class CensorHelper :
    do_compile =True
    def __init__ (self ,lang ='ru',do_compile =None ):
        if do_compile is None :
            do_compile =self .do_compile
        self .lang =lang
        self .c =Censor .get (lang =lang ,do_compile =do_compile )
    def censure_text (self ,text ):
        count =0
        result =[]
        for line in text .splitlines ():
            new_line ,bad_words_count ,bad_phrases_count =self .c .clean_line (line )
            count +=bad_words_count +bad_phrases_count
            result .append (new_line )
        return '\n'.join (result ),count
    def test (self ):
        d =os .path .dirname (os .path .abspath (__file__ ))
        in_file =os .path .join (d ,'data','{}_in.txt'.format (self .lang ))
        out_file =os .path .join (d ,'data','{}_out.txt'.format (self .lang ))
        with codecs .open (in_file ,'r','utf-8')as in_fs ,codecs .open (out_file ,'w','utf-8')as out_fs :
            text =in_fs .read ()
            cleaned_text ,count =self .censure_text (text )
            print ('Количество найденных и замененных: {}'.format (count ))
            out_fs .write (cleaned_text )
def ru_just_test ():
    c =CensorHelper (lang ='ru',do_compile =False )
    c .test ()
def en_just_test ():
    c =CensorHelper (lang ='en',do_compile =False )
    c .test ()
def show_examples ():
    beep ='[цензура]'
    print ('Русские примеры:')
    censor_ru =Censor .get (lang ='ru',do_compile =False )
    line ='ебанамат бляд'
    print ('Проверка строки: "{}"'.format (line ))
    line_info =censor_ru .check_line (line )
    print ('Есть ли в строке нецензурные слова? - {}'.format (not line_info ['is_good']))
    print ('Первое плохое слово: {}, шаблон плохого слова: {}'.format (
    line_info ['bad_word_info']['word'],line_info ['bad_word_info']['accuse'][0 ]))
    print ('Очистка линии со звуковым сигналом word={}'.format (line ,beep ))
    cleaned_line ,bad_words_count ,bad_phrases_count =censor_ru .clean_line (line ,beep =beep )
    print ('в результате очищена строка: "{}", количество плохих слов: {}, количество плохих фраз: {}'.format (
    cleaned_line ,bad_words_count ,bad_phrases_count ))
    print ('\n')
    print ('Английские примеры:')
    censor_en =Censor .get (lang ='en',do_compile =False )
    line ='чертово дерьмо'
    line_info =censor_en .check_line (line )
    print ('Есть ли в строке нецензурные слова? - {}'.format (not line_info ['is_good']))
    print ('Первое плохое слово: {}, шаблон плохого слова: {}'.format (
    line_info ['bad_word_info']['word'],line_info ['bad_word_info']['accuse'][0 ]))
    print ('строка очистки: {} со звуковым сигналом word={}'.format (line ,beep ))
    cleaned_line ,bad_words_count ,bad_phrases_count =censor_en .clean_line (line ,beep =beep )
    print ('Результат: очищенная строка: "{}", количество плохих слов: {}, количество плохих фраз: {}'.format (
    cleaned_line ,bad_words_count ,bad_phrases_count ))
    print ('\n')
    line ='полотенце с верблюжьей лапкой'
    print ('Пример плохой фразы на английском языке: "{}"'.format (line ))
    line_info =censor_en .check_line (line )
    print ('Содержит ли строка нецензурные слова/фразы? - {}'.format (not line_info ['is_good']))
    print ('Первый образец обвинения: {}'.format (
    line_info ['accuse'][0 ]))
    print ('Очистка строки с неверными фразами звуковым сигналом word={}'.format (beep ))
    cleaned_line ,bad_words_count ,bad_phrases_count =censor_en .clean_line (line ,beep =beep )
    print ('Результат: очищенная строка: "{}", количество плохих слов: {}, количество плохих фраз: {}'.format (
    cleaned_line ,bad_words_count ,bad_phrases_count ))
    html_line ='<b><span>bitch</i> whore</b>fu<div>ck</li>'
    print ('\n')
    print ('Очистка английской HTML-строки, содержащей нецензурные слова: "{}"'.format (html_line ))
    cleaned_line ,bad_words_count =censor_en .clean_html_line (
    html_line ,beep =beep )
    print ('Результат: очищенная строка html: "{}", количество плохих слов: {}'.format (
    cleaned_line ,bad_words_count ))
if __name__ =='__main__':
    show_examples ()