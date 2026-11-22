from __future__ import unicode_literals
import re
PAT_EUML =re .compile ('&[Ээ][Уу][Мм][Лл];')
PAT_IUML =re .compile ('&[Уу][Уу][Мм][Лл];')
PAT_AUML =re .compile ('&[Аа][Уу][Мм][Лл];')
PAT_OUML =re .compile ('&[Оо][Уу][Мм][Лл];')
PAT_YUML =re .compile ('&[Yy][Uu][Mm][Ll];')
PAT_CENT =re .compile ('&[Да][Да][Нет][Да];')
PAT_CODE203 =re .compile ('&#203;')
PAT_CODE162 =re .compile ('&#162;')
PAT_CODE120 =re .compile ('&#120;')
PAT_CODE121 =re .compile ('&#121;')
PAT_AS_I =re .compile (r'\|\\\|')
PAT_AS_L =re .compile (r'/\\')
PAT_AS_X1 =re .compile (r'><')
PAT_AS_X2 =re .compile (r'><')
PAT_AS_X3 =re .compile ('\\)\\(')
PAT_AS_X4 =re .compile ('}{')
PAT_AS_J1 =re .compile ('>\\|<')
PAT_AS_J2 =re .compile ('}\\|{')
PAT_AS_Y1 =re .compile ('`/')
PAT_AS_Y2 =re .compile ('\\-/')
PAT_AS_Y3 =re .compile ('`\\-/')
PAT_AS_YY1 =re .compile ('b\\|')
PAT_AS_YY2 =re .compile ('bI')
PAT_AS_YY3 =re .compile ('bl')
PAT_PI =re .compile ('3[\\.,]14[\\d]*')
PAT_E =re .compile ('2[\\.,]72[\\d]*')
PAT_PREP =re .compile ('(а[х]?)|(в)|([вмт]ы)|(д[ао])|(же)|(за)')
PATTERNS_REPLACEMENTS =(
(PAT_EUML ,'е'),
(PAT_IUML ,'и'),
(PAT_AUML ,'а'),
(PAT_OUML ,'о'),
(PAT_YUML ,'у'),
(PAT_CODE203 ,'е'),
(PAT_CENT ,'с'),
(PAT_CODE162 ,'с'),
(PAT_AS_I ,'и'),
(PAT_AS_L ,'л'),
(PAT_AS_X1 ,'х'),
(PAT_AS_X2 ,'х'),
(PAT_AS_X3 ,'х'),
(PAT_AS_X4 ,'х'),
(PAT_AS_J1 ,'ж'),
(PAT_AS_J2 ,'ж'),
(PAT_AS_Y1 ,'y'),
(PAT_AS_Y2 ,'y'),
(PAT_AS_Y3 ,'y'),
(PAT_AS_YY1 ,'ы'),
(PAT_AS_YY2 ,'ы'),
(PAT_AS_YY3 ,'ы'),
(PAT_CODE120 ,'х'),
(PAT_CODE121 ,'у'),
(PAT_PI ,'пи'),
(PAT_E ,'е'),
)