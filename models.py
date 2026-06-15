from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import enum

class TolovTuri(str, enum.Enum):
    naqt = "naqt"
    karta = "karta"
    nasiya = "nasiya"

class Mahsulot(Base):
    __tablename__ = "mahsulotlar"
    id = Column(Integer, primary_key=True, index=True)
    nomi = Column(String, nullable=False)
    kod = Column(String, unique=True, index=True, nullable=True)
    kategoriya = Column(String, default="Boshqa")
    narx = Column(Float, default=0)
    miqdor = Column(Integer, default=0)
    min_miqdor = Column(Integer, default=5)
    birlik = Column(String, default="dona")
    izoh = Column(Text, nullable=True)
    yaratilgan = Column(DateTime, default=datetime.utcnow)
    sotuv_itemlar = relationship("SotuvItem", back_populates="mahsulot")
    kirim_tarix = relationship("KirimTarix", back_populates="mahsulot")

class Sotuv(Base):
    __tablename__ = "sotuvlar"
    id = Column(Integer, primary_key=True, index=True)
    mijoz = Column(String, default="Mijoz")
    mijoz_tel = Column(String, nullable=True)
    jami = Column(Float, default=0)
    tolov_turi = Column(String, default="naqt")
    izoh = Column(Text, nullable=True)
    sana = Column(DateTime, default=datetime.utcnow)
    itemlar = relationship("SotuvItem", back_populates="sotuv", cascade="all, delete")

class SotuvItem(Base):
    __tablename__ = "sotuv_itemlar"
    id = Column(Integer, primary_key=True, index=True)
    sotuv_id = Column(Integer, ForeignKey("sotuvlar.id"))
    mahsulot_id = Column(Integer, ForeignKey("mahsulotlar.id"))
    miqdor = Column(Integer)
    narx = Column(Float)
    summa = Column(Float)
    sotuv = relationship("Sotuv", back_populates="itemlar")
    mahsulot = relationship("Mahsulot", back_populates="sotuv_itemlar")

class Qarzdor(Base):
    __tablename__ = "qarzdorlar"
    id = Column(Integer, primary_key=True, index=True)
    mijoz = Column(String, nullable=False, unique=True)
    mijoz_tel = Column(String, nullable=True)
    qarz = Column(Float, default=0)
    yaratilgan = Column(DateTime, default=datetime.utcnow)
    tolovlar = relationship("QarzTolov", back_populates="qarzdor", cascade="all, delete")

class QarzTolov(Base):
    __tablename__ = "qarz_tolovlar"
    id = Column(Integer, primary_key=True, index=True)
    qarzdor_id = Column(Integer, ForeignKey("qarzdorlar.id"))
    summa = Column(Float)
    izoh = Column(Text, nullable=True)
    sana = Column(DateTime, default=datetime.utcnow)
    qarzdor = relationship("Qarzdor", back_populates="tolovlar")

class KirimTarix(Base):
    __tablename__ = "kirim_tarix"
    id = Column(Integer, primary_key=True, index=True)
    mahsulot_id = Column(Integer, ForeignKey("mahsulotlar.id"))
    miqdor = Column(Integer)
    narx = Column(Float)
    izoh = Column(Text, nullable=True)
    sana = Column(DateTime, default=datetime.utcnow)
    mahsulot = relationship("Mahsulot", back_populates="kirim_tarix")
