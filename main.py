from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
import os

from database import engine, get_db, Base
from models import Mahsulot, Sotuv, Qarzdor, SotuvItem, KirimTarix, QarzTolov
from schemas import (
    MahsulotCreate, MahsulotOut,
    SotuvCreate, SotuvOut,
    QarzdorOut, QarzTolovCreate,
    KirimCreate
)

Base.metadata.create_all(bind=engine)
app = FastAPI(title="AutoParts Pro")

@app.get("/", response_class=HTMLResponse)
def root():
    with open("index.html", encoding="utf-8") as f:
        return f.read()

# MAHSULOTLAR
@app.get("/api/mahsulotlar", response_model=List[MahsulotOut])
def mahsulotlar_royxat(search: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Mahsulot)
    if search:
        q = q.filter(Mahsulot.nomi.ilike(f"%{search}%"))
    return q.order_by(Mahsulot.nomi).all()

@app.post("/api/mahsulotlar", response_model=MahsulotOut)
def mahsulot_qosh(data: MahsulotCreate, db: Session = Depends(get_db)):
    m = Mahsulot(**data.dict())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

@app.put("/api/mahsulotlar/{mid}", response_model=MahsulotOut)
def mahsulot_tahrir(mid: int, data: MahsulotCreate, db: Session = Depends(get_db)):
    m = db.query(Mahsulot).filter(Mahsulot.id == mid).first()
    if not m:
        raise HTTPException(404, "Mahsulot topilmadi")
    for k, v in data.dict().items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return m

@app.delete("/api/mahsulotlar/{mid}")
def mahsulot_ochir(mid: int, db: Session = Depends(get_db)):
    m = db.query(Mahsulot).filter(Mahsulot.id == mid).first()
    if not m:
        raise HTTPException(404, "Topilmadi")
    db.delete(m)
    db.commit()
    return {"ok": True}

@app.post("/api/mahsulotlar/{mid}/kirim")
def kirim_qosh(mid: int, data: KirimCreate, db: Session = Depends(get_db)):
    m = db.query(Mahsulot).filter(Mahsulot.id == mid).first()
    if not m:
        raise HTTPException(404, "Topilmadi")
    m.miqdor += data.miqdor
    m.narx = data.narx
    tarix = KirimTarix(mahsulot_id=mid, miqdor=data.miqdor, narx=data.narx, izoh=data.izoh)
    db.add(tarix)
    db.commit()
    db.refresh(m)
    return m

@app.get("/api/mahsulotlar/{mid}/tarix")
def kirim_tarix(mid: int, db: Session = Depends(get_db)):
    return db.query(KirimTarix).filter(KirimTarix.mahsulot_id == mid).order_by(KirimTarix.sana.desc()).all()

# SOTUVLAR
@app.get("/api/sotuvlar", response_model=List[SotuvOut])
def sotuvlar_royxat(
    boshlanish: Optional[date] = None,
    tugash: Optional[date] = None,
    tolov_turi: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(Sotuv)
    if boshlanish:
        q = q.filter(Sotuv.sana >= boshlanish)
    if tugash:
        q = q.filter(Sotuv.sana <= tugash)
    if tolov_turi:
        q = q.filter(Sotuv.tolov_turi == tolov_turi)
    return q.order_by(Sotuv.sana.desc()).limit(200).all()

@app.post("/api/sotuvlar", response_model=SotuvOut)
def sotuv_qosh(data: SotuvCreate, db: Session = Depends(get_db)):
    sotuv = Sotuv(mijoz=data.mijoz, mijoz_tel=data.mijoz_tel, tolov_turi=data.tolov_turi, izoh=data.izoh)
    jami = 0
    items = []
    for item in data.itemlar:
        m = db.query(Mahsulot).filter(Mahsulot.id == item.mahsulot_id).first()
        if not m:
            raise HTTPException(404, f"Mahsulot topilmadi")
        if m.miqdor < item.miqdor:
            raise HTTPException(400, f"'{m.nomi}' omborda yetarli emas ({m.miqdor} ta qolgan)")
        m.miqdor -= item.miqdor
        summa = item.narx * item.miqdor
        jami += summa
        items.append(SotuvItem(mahsulot_id=m.id, miqdor=item.miqdor, narx=item.narx, summa=summa))
    sotuv.jami = jami
    sotuv.itemlar = items
    db.add(sotuv)

    if data.tolov_turi == "nasiya":
        q = db.query(Qarzdor).filter(Qarzdor.mijoz == data.mijoz).first()
        if q:
            q.qarz += jami
            if data.mijoz_tel:
                q.mijoz_tel = data.mijoz_tel
        else:
            db.add(Qarzdor(mijoz=data.mijoz, mijoz_tel=data.mijoz_tel, qarz=jami))

    db.commit()
    db.refresh(sotuv)
    return sotuv

# QARZDORLAR
@app.get("/api/qarzdorlar", response_model=List[QarzdorOut])
def qarzdorlar(db: Session = Depends(get_db)):
    return db.query(Qarzdor).filter(Qarzdor.qarz > 0).order_by(Qarzdor.qarz.desc()).all()

@app.post("/api/qarzdorlar/{qid}/tolov")
def tolov_qabul(qid: int, data: QarzTolovCreate, db: Session = Depends(get_db)):
    q = db.query(Qarzdor).filter(Qarzdor.id == qid).first()
    if not q:
        raise HTTPException(404, "Topilmadi")
    q.qarz = max(0, q.qarz - data.summa)
    t = QarzTolov(qarzdor_id=qid, summa=data.summa, izoh=data.izoh)
    db.add(t)
    db.commit()
    return {"qolgan_qarz": q.qarz}

# ANALITIKA
@app.get("/api/analitika/dashboard")
def dashboard(db: Session = Depends(get_db)):
    from sqlalchemy import func
    bugun = date.today()

    bugungi = db.query(func.sum(Sotuv.jami)).filter(func.date(Sotuv.sana) == bugun).scalar() or 0
    oylik = db.query(func.sum(Sotuv.jami)).filter(
        func.extract('month', Sotuv.sana) == bugun.month,
        func.extract('year', Sotuv.sana) == bugun.year
    ).scalar() or 0
    jami_qarz = db.query(func.sum(Qarzdor.qarz)).scalar() or 0
    kam_qolgan = db.query(Mahsulot).filter(Mahsulot.miqdor <= Mahsulot.min_miqdor).count()

    naqt = db.query(func.sum(Sotuv.jami)).filter(
        func.extract('month', Sotuv.sana) == bugun.month,
        Sotuv.tolov_turi == 'naqt'
    ).scalar() or 0
    karta = db.query(func.sum(Sotuv.jami)).filter(
        func.extract('month', Sotuv.sana) == bugun.month,
        Sotuv.tolov_turi == 'karta'
    ).scalar() or 0
    nasiya_oy = db.query(func.sum(Sotuv.jami)).filter(
        func.extract('month', Sotuv.sana) == bugun.month,
        Sotuv.tolov_turi == 'nasiya'
    ).scalar() or 0

    haftalik = []
    for i in range(6, -1, -1):
        d = bugun - timedelta(days=i)
        s = db.query(func.sum(Sotuv.jami)).filter(func.date(Sotuv.sana) == d).scalar() or 0
        haftalik.append({"kun": d.strftime("%d/%m"), "sotuv": float(s)})

    top5 = db.query(
        Mahsulot.nomi,
        func.sum(SotuvItem.miqdor).label("jami")
    ).join(SotuvItem).group_by(Mahsulot.id).order_by(func.sum(SotuvItem.miqdor).desc()).limit(5).all()

    return {
        "bugungi_sotuv": float(bugungi),
        "oylik_sotuv": float(oylik),
        "jami_qarz": float(jami_qarz),
        "kam_qolgan": kam_qolgan,
        "naqt": float(naqt),
        "karta": float(karta),
        "nasiya_oy": float(nasiya_oy),
        "haftalik": haftalik,
        "top5": [{"nomi": r.nomi, "miqdor": r.jami} for r in top5],
    }

@app.get("/api/analitika/hisobot")
def hisobot(yil: int, oy: int, db: Session = Depends(get_db)):
    from sqlalchemy import func
    sotuvlar = db.query(Sotuv).filter(
        func.extract('year', Sotuv.sana) == yil,
        func.extract('month', Sotuv.sana) == oy
    ).all()
    jami = sum(s.jami for s in sotuvlar)
    naqt = sum(s.jami for s in sotuvlar if s.tolov_turi == 'naqt')
    karta = sum(s.jami for s in sotuvlar if s.tolov_turi == 'karta')
    nasiya = sum(s.jami for s in sotuvlar if s.tolov_turi == 'nasiya')
    return {
        "jami_sotuv": jami,
        "naqt": naqt,
        "karta": karta,
        "nasiya": nasiya,
        "sotuv_soni": len(sotuvlar),
    }
