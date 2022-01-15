import datetime

from sqlalchemy import Table, create_engine, Column, Integer, String,\
    UniqueConstraint, Index, Date, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine("postgresql+psycopg2://tesseractmaks:Vfrcvfrc1@localhost/parse")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Lids(Base):
    __tablename__ = "lids"

    # __tableargs__ = (Index("common_index", "short_name", "full_name", "inn", "ogrn", "email",
    #                        "phone", "type_lids", "status_registration_eis", "date_registration_eis",
    #                        "created_on", "updated_on", "address_yur", "address_postal"))

    id = Column(Integer, primary_key=True)
    short_name = Column(String(100), index=True)
    full_name = Column(String(300), nullable=False, index=True)
    inn = Column(Integer, nullable=False, index=True)
    kpp = Column(Integer, index=True)
    ogrn = Column(Integer, nullable=False, unique=True, index=True)
    email = Column(String(40))
    phone = Column(Integer)
    type_lids = Column(String(100), index=True)
    number_in_reestr = Column(Integer, nullable=False)
    date_registration_ifns = Column(Date())
    status_registration_eis = Column(String(20), index=True)
    date_registration_eis = Column(Date(), index=True)
    created_on = Column(Date(), default=datetime.datetime.now, nullable=False, index=True)
    updated_on = Column(Date(), DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now, index=True)
    address_yur = Column(String(400), index=True)
    address_postal = Column(String(400), index=True)









# lids = Table("lids")
x=default=datetime.date.today()
print(x)
print(len("7705860470"))