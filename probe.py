import datetime
import re
from orm_models import Lids, Category

from sqlalchemy import Table, create_engine, Column, Integer, String, \
    UniqueConstraint, Index, Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# engine = create_engine("postgresql+psycopg2://tesseractmaks:Vfrcvfrc1@localhost/parse")
# Session = sessionmaker(bind=engine)
# session = Session()


# lid = Lids(full_name="vasyavasyavasya", inn=1231231232,
#            ogrn=123456123123, number_in_reestr=1234561, created_on=datetime.datetime.now(), category_id=1)

# lid = Lids()
# cat = Category(name="ooo")
# catip = Category(name="ip")
# session.add(cat)
# session.add(catip)
# session.commit()
#
#
# session.add(lid)
# session.commit()


z = ['19007263',
     'Зарегистрирован',
     'Юридическое лицо РФ',
     '21.01.2019',
     'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "КРОНА"',
     'ООО "КРОНА"',
     '199226, Г САНКТ-ПЕТЕРБУРГ, УЛ НАЛИЧНАЯ, ДОМ 30, ЛИТЕР А, ПОМЕЩЕНИЕ 4Н ОФИС 2 '
     'Р.М. 1',
     '43.3971.12.1341.1071.12.1142.2243.1243.3471.11.143.1347.1928.25.128.25.233.1271.11.271.12.147.52.743.9128.29.168.1068.3243.3168.3143.3246.13.242.2143.1143.3343.9943.99.143.2946.1942.9970.2271.1171.1273.1128.2568.10.146.9082.9968.2043.2143.2241.2042.9146.73Показать '
     'все',
     '7801342866',
     '780101001',
     '25.12.2017',
     '1177847413787',
     'Да',
     '199226, Санкт-Петербург, ул. Наличная, д.30, пом. 4н, оф. 1',
     'tender@gradstroy.spb.ru',
     '7 9119954433',
     'АО «Сбербанк-АСТ»АО "РАД"Национальная электронная площадкаЭТП '
     'ГазпромбанкРТС-тендерАГЗ РТАО «ЕЭТП»ЭТП ТЭК-Торг']

# if re.findall("Юридическое лицо", str(x), flags=re.I):
#     print(x)




title_ip = [
    {
        "number_in_reestr": 'Номер реестровой записи в ЕРУЗ',
        "status_registration_eis": 'Статус регистрации',
        "type_lids": 'Тип участника закупки',
        "date_registration_eis": 'Дата регистрации в ЕИС',
        "full_name": 'ФИО',
        "inn": 'ИНН',
        "ogrn": 'ОГРНИП',
        "date_registration_ifns": 'Дата постановки на учет в налоговом органе',
        "email": 'Адрес электронной почты',
    }
]

keys_ip = [

        "number_in_reestr",
        "status_registration_eis",
        "type_lids",
        "date_registration_eis",
        "full_name",
        "inn",
        "ogrn",
        "date_registration_ifns",
        "email",
]

keys_ooo = [
        "number_in_reestr",
        "status_registration_eis",
        "type_lids",
        "date_registration_eis",
        "full_name",
        "short_name",
        "address_yur",
        "inn",
        "kpp",
        "date_registration_ifns",
        "ogrn",
        "email",
        "phone",
    ]

title_ooo = [
    {
        "number_in_reestr": 'Номер реестровой записи в ЕРУЗ',
        "status_registration_eis": 'Статус регистрации',
        "type_lids": 'Тип участника закупки',
        "date_registration_eis": 'Дата регистрации в ЕИС',
        "full_name": "Полное наименование",
        "short_name": 'Сокращенное наименование',
        "address_yur": 'Адрес в пределах места нахождения',
        "inn": 'ИНН',
        "kpp": 'КПП',
        "date_registration_ifns": 'Дата постановки на учет в налоговом органе',
        "ogrn": 'ОГРН',
        "email": 'Адрес электронной почты',
        "phone": 'Контактный телефон',
    },
    {
        "number_in_reestr": 'Номер реестровой записи в ЕРУЗ',
        "status_registration_eis": 'Статус регистрации',
        "type_lids": 'Тип участника закупки',
        "date_registration_eis": 'Дата регистрации в ЕИС',
        "full_name": "Полное наименование",
        "short_name": 'Сокращенное наименование',
        "address_yur": 'Адрес в пределах места нахождения',
        "inn": 'ИНН',
        "kpp": 'КПП',
        "date_registration_ifns": 'Дата постановки на учет в налоговом органе',
        "ogrn": 'ОГРН',
        "email": 'Адрес электронной почты',
        "phone": 'Контактный телефон',
    },

]


# y=datetime.date.today()
# print(y)

