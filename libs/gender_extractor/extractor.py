import os
import re
import pickle
import pkgutil
class GenderExtractor :
    def __init__ (self ):
        self .countries_encoding ={}
        self .names_lists =pkgutil .get_data (__name__ ,"nameLists/list.txt").decode ().split (',')
        for fname in self .names_lists :
            text =os .path .split (fname .replace ("\\","/"))[-1 ]
            split =re .sub ('([A-Z][a-z]+)',r' \1',re .sub ('([А–Я]+)',r' \1',text )).split ()
            country =split [0 ].lower ()
            self .countries_encoding [country ]=len (self .countries_encoding )-1
        self .gender_encoding ={"Male":0 ,"Female":1 }
        try :
            self .name_freq =pickle .loads (pkgutil .get_data (__name__ ,"data.pickle"))
        except FileNotFoundError :
            self ._create_pickle ()
    def _create_pickle (self ):
        self .name_freq ={}
        for fname in self .names_lists :
            fname =fname .strip ().replace ("\\","/")
            text =os .path .split (fname )[-1 ]
            split =re .sub ('([A-Z][a-z]+)',r' \1',re .sub ('([А–Я]+)',r' \1',text )).split ()
            country =split [0 ].lower ()
            gender =split [1 ]
            gender_idx =self .gender_encoding [gender ]
            country_idx =self .countries_encoding [country ]
            names =pkgutil .get_data (__name__ ,fname ).decode (
            encoding ='utf-8').replace ("\r","").split ('\n')
            processed =[]
            for name in names :
                name_data =name .split (';')
                name =name_data [0 ].lower ().strip ()
                try :
                    count =int (name_data [1 ].strip ().replace ('.',''))
                except IndexError :
                    if name in processed :
                        continue
                    count =1
                try :
                    self .name_freq [name ][gender_idx ][country_idx ]+=count
                except KeyError :
                    self .name_freq [name ]=[[0 ]*
                    len (self .countries_encoding ),[0 ]*
                    len (self .countries_encoding )]
                    self .name_freq [name ][gender_idx ][country_idx ]+=count
        save_loc =os .path .realpath (__file__ )
        save_loc =os .path .dirname (save_loc )
        with open (save_loc +"/data.pickle","wb")as f :
            pickle .dump (self .name_freq ,f )
    def extract_gender (self ,name ,country =None ):
        if not isinstance (name ,str ):
            raise TypeError ("Имя должно быть строкой")
        if country is not None and not isinstance (country ,str ):
            raise TypeError ("Страна должна быть строкой или нет.")
        name =name .lower ().strip ()
        if not name :
            raise ValueError ("Имя не может быть пустым или содержать только пробелы.")
        if country is not None :
            country =country .lower ().strip ()
            country_code =self .countries_encoding [country ]
        else :
            country_code =None
        try :
            m_counts =self .name_freq [name ][0 ]
            f_counts =self .name_freq [name ][1 ]
        except KeyError :
            return "ambiguous"
        epsilon =1e-6
        if country_code is not None :
            m_count =m_counts [country_code ]+epsilon
            f_count =f_counts [country_code ]+epsilon
        else :
            m_count =sum (m_counts )+epsilon
            f_count =sum (f_counts )+epsilon
        if m_count ==epsilon and f_count ==epsilon :
            return "ambiguous"
        female_ratio =f_count /m_count
        male_ratio =m_count /f_count
        if female_ratio ==male_ratio :
            return "женский и мужской"
        elif female_ratio >9 :
            return "female"
        elif female_ratio >1.5 :
            return "в основном женщины"
        elif male_ratio >9 :
            return "male"
        elif male_ratio >1.5 :
            return "в основном мужчины"
        else :
            return "ambiguous"
if __name__ =="__main__":
    ext =GenderExtractor ()