from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Mahsulot(Base):
    __tablename__ = "mahsulotlar"
    id = Column(Integer, primary_key=True, index=True)
    nomi = Column(String, nullable=False)
    kod = Column(String, unique=True, index=True)
    kategoriya = Column(String, default="Boshqa")
    narx = Column(Float, default=0)
    miqdor = Column(Integer, default=0)
    min_miqdor = Column(Integer, default=5)
    birlik = Column(String, default="dona")
    izoh = Column(Text, nullable=True)
    yaratilgan = Column(DateTime, default=datetime.utcnow)
    sotuv_itemlar = relationship("SotuvItem", back_populates="mahsulot")


class Sotuv(Base):
    __tablename__ = "sotuvlar"
    id = Column(Integer, primary_key=True, index=True)
    mijoz = Column(String, default="Noma'lum")
    jami = Column(Float, default=0)
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
    qarz = Column(Float, default=0)
    telefon = Column(String, nullable=True)
    yaratilgan = Column(DateTime, default=datetime.utcnow)
