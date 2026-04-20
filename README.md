# Smart Tourism Samosir — Backend API 🏝️

Backend **Flask** untuk aplikasi mobile **Smart Tourism Samosir**: Rekomendasi & Itinerary Wisata Berbasis AI di Pulau Samosir, Danau Toba.

---

## 🔑 Akun Default (untuk testing & pengumpulan artefak)

| Role  | Username | Password    |
|-------|----------|-------------|
| Admin | `admin`  | `admin123`  |
| User  | `tester` | `tester123` |

> Tidak ada fitur registrasi — akun hanya bisa dibuat manual oleh admin untuk mencegah pemakaian token AI berlebihan.

---

## 🚀 Setup Lokal

### 1. Clone & masuk folder
```bash
git clone <repo-url>
cd samosir-backend
```

### 2. Buat virtual environment
```bash
python -m venv venv --without-pip
```

### 3. Aktifkan virtual environment
```bash
# Windows CMD
venv\Scripts\activate

# Windows PowerShell
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install pip
python -m ensurepip --upgrade
```

### 4. Install library
```bash
pip install -r requirements.txt
```

### 5. Buat file `.env`
```bash
cp .env.example .env
```
Lalu isi `LLM_TOKEN` dengan token dari [delcom.org](https://delcom.org).

### 6. Jalankan
```bash
python app.py
```

API berjalan di: `http://127.0.0.1:5000`

---

## ☁️ Deploy ke Railway / Render

### Railway
1. Push repo ke GitHub
2. Buat project baru di [railway.app](https://railway.app)
3. Connect ke GitHub repo
4. Set **Environment Variables**:
   ```
   LLM_BASE_URL = https://delcom.org/api
   LLM_TOKEN    = token_kamu
   JWT_SECRET_KEY = string_acak_yang_kuat
   ```
5. Railway otomatis deteksi `Procfile` dan deploy

### Render
1. Buat **Web Service** baru di [render.com](https://render.com)
2. Connect GitHub repo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
5. Set Environment Variables (sama seperti Railway)

---

## 📡 Endpoint API

> Semua endpoint kecuali `/` dan `/auth/login` memerlukan header:
> ```
> Authorization: Bearer <token>
> ```

### 🔐 Auth

| Method | Endpoint      | Auth | Deskripsi              |
|--------|---------------|------|------------------------|
| POST   | `/auth/login` | ❌   | Login, dapat JWT token |
| GET    | `/auth/me`    | ✅   | Info user yang login   |

**Body `/auth/login`:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```
**Response:**
```json
{
  "message": "Login berhasil",
  "token": "eyJ...",
  "user": { "id": 1, "name": "Administrator", "username": "admin", "is_admin": true }
}
```

---

### 🏖️ Tourist Spots

| Method | Endpoint              | Auth | Deskripsi                  |
|--------|-----------------------|------|----------------------------|
| GET    | `/spots`              | ✅   | List semua tempat wisata   |
| GET    | `/spots/categories`   | ✅   | Daftar kategori            |
| GET    | `/spots/<id>`         | ✅   | Detail tempat wisata       |

**Query Params `/spots`:**

| Param      | Default | Contoh             |
|------------|---------|--------------------|
| `page`     | 1       | `?page=1`          |
| `per_page` | 20      | `?per_page=10`     |
| `category` | -       | `?category=Alam`   |
| `search`   | -       | `?search=simanindo`|

**Kategori yang tersedia:** `Alam`, `Budaya`, `Sejarah`, `Kuliner`

---

### 🤖 AI Rekomendasi Wisata

| Method | Endpoint                   | Auth | Deskripsi               |
|--------|----------------------------|------|-------------------------|
| POST   | `/recommendations/generate`| ✅   | Generate rekomendasi AI |
| GET    | `/recommendations`         | ✅   | Riwayat rekomendasi     |
| GET    | `/recommendations/<id>`    | ✅   | Detail rekomendasi      |
| DELETE | `/recommendations/<id>`    | ✅   | Hapus rekomendasi       |

**Body `/recommendations/generate`:**
```json
{
  "interest": "wisata alam dan petualangan outdoor",
  "budget": "medium",
  "duration": 3
}
```

---

### 🗺️ AI Itinerary Perjalanan

| Method | Endpoint                | Auth | Deskripsi             |
|--------|-------------------------|------|-----------------------|
| POST   | `/itineraries/generate` | ✅   | Generate itinerary AI |
| GET    | `/itineraries`          | ✅   | Riwayat itinerary     |
| GET    | `/itineraries/<id>`     | ✅   | Detail itinerary      |
| DELETE | `/itineraries/<id>`     | ✅   | Hapus itinerary       |

**Body `/itineraries/generate`:**
```json
{
  "theme": "budaya dan kuliner Batak",
  "duration_days": 3,
  "budget": "medium",
  "group_type": "family"
}
```

**Nilai valid:**
- `budget`: `low` | `medium` | `high`
- `group_type`: `solo` | `couple` | `family` | `group`
- `duration_days`: `1` – `7`

---

## 🗄️ Database

SQLite (`db/data.db`) dengan tabel:
- `users` — akun pengguna
- `tourist_spots` — data 10 tempat wisata Samosir (auto-seed)
- `recommendations` — riwayat rekomendasi AI per user
- `itineraries` — riwayat itinerary AI per user
