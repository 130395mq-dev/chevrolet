from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MahsulotCreate(BaseModel):
    nomi: str
    kod: Optional[str] = None
    kategoriya: str = "Boshqa"
    narx: float = 0
    miqdor: int = 0
    min_miqdor: int = 5
    birlik: str = "dona"
    izoh: Optional[str] = None

class MahsulotOut(BaseModel):
    id: int
    nomi: str
    kod: Optional[str]
    kategoriya: str
    narx: float
    miqdor: int
    min_miqdor: int
    birlik: str
    izoh: Optional[str]
    yaratilgan: datetime
    class Config:
        from_attributes = True

class KirimCreate(BaseModel):
    miqdor: int
    narx: float
    izoh: Optional[str] = None

class SotuvItemCreate(BaseModel):
    mahsulot_id: int
    miqdor: int
    narx: float

class SotuvCreate(BaseModel):
    mijoz: str = "Mijoz"
    mijoz_tel: Optional[str] = None
    itemlar: List[SotuvItemCreate]
    tolov_turi: str = "naqt"
    izoh: Optional[str] = None

class SotuvItemOut(BaseModel):
    id: int
    mahsulot_id: int
    miqdor: int
    narx: float
    summa: float
    class Config:
        from_attributes = True

class SotuvOut(BaseModel):
    id: int
    mijoz: str
    mijoz_tel: Optional[str]
    jami: float
    tolov_turi: str
    izoh: Optional[str]
    sana: datetime
    itemlar: List[SotuvItemOut]
    class Config:
        from_attributes = True

class QarzdorOut(BaseModel):
    id: int
    mijoz: str
    mijoz_tel: Optional[str]
    qarz: float
    yaratilgan: datetime
    class Config:
        from_attributes = True

class QarzTolovCreate(BaseModel):
    summa: float
    izoh: Optional[str] = None
