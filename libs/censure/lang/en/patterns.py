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
PATTERNS_REPLACEMENTS =(
(PAT_EUML ,'e'),
(PAT_IUML ,'u'),
(PAT_AUML ,'a'),
(PAT_OUML ,'o'),
(PAT_YUML ,'y'),
(PAT_CODE120 ,'x'),
(PAT_CODE121 ,'y'),
(PAT_CODE203 ,'e'),
(PAT_CENT ,'c'),
(PAT_CODE162 ,'c'),
)