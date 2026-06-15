# AutoParts — Avto Ehtiyot Qismlar Hisob Tizimi

## Imkoniyatlar
- Omborxona boshqaruvi (kirim, chiqim, qoldiq)
- Sotuvlar hisobi (mijoz, mahsulot, narx)
- Qarzdorlar ro'yxati va to'lov qabul qilish
- Dashboard va analitika (haftalik grafik, top mahsulotlar)
- Kam qolgan mahsulotlar uchun ogohlantirish

## Texnologiyalar
- Backend: FastAPI (Python)
- Database: PostgreSQL
- Frontend: HTML/CSS/JS (o'rnatish shart emas)
- Hosting: Railway

---

## Railway'ga deploy qilish

### 1-qadam: GitHub'ga yuklash
```bash
cd avto-hisob
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/avto-hisob.git
git push -u origin main
```

### 2-qadam: Railway.app
1. [railway.app](https://railway.app) ga kiring
2. "New Project" → "Deploy from GitHub repo"
3. `avto-hisob` reponi tanlang
4. "Add Plugin" → PostgreSQL qo'shing
5. Variables bo'limida `DATABASE_URL` avtomatik qo'shiladi

### 3-qadam: Domain
Settings → Networking → Generate Domain

---

## Lokal ishlatish (test uchun)

```bash
pip install -r requirements.txt
DATABASE_URL=sqlite:///./avto.db uvicorn app.main:app --reload
```
Brauzerda: http://localhost:8000
