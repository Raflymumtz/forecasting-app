# Sistem Peramalan Persediaan Obat (RSIA)

Aplikasi web Flask untuk manajemen persediaan obat rumah sakit, dilengkapi modul
peramalan kebutuhan obat dengan metode **Double Exponential Smoothing (DES)**
atau *Holt's linear method*.

Seluruh perhitungan peramalan pada aplikasi ini **identik dengan hasil Bab IV**
pada file `Data Lengkap Hasil Peramalan Persediaan Obat (Bab IV).xlsx` — mulai
dari statistik deskriptif, pembagian data latih/uji, 81 kombinasi α × β, nilai
MAD/MSE/MAPE, sampai prediksi periode ke-106.

---

## Daftar Isi

1. [Yang Perlu Disiapkan](#1-yang-perlu-disiapkan)
2. [Menjalankan Project dari 0 di Laptop Baru](#2-menjalankan-project-dari-0-di-laptop-baru)
3. [Akun untuk Login](#3-akun-untuk-login)
4. [Cara Memakai Menu Peramalan](#4-cara-memakai-menu-peramalan)
5. [Metode Peramalan yang Dipakai](#5-metode-peramalan-yang-dipakai)
6. [Struktur Folder](#6-struktur-folder)
7. [Perintah yang Sering Dipakai](#7-perintah-yang-sering-dipakai)
8. [Mengganti / Menambah Data](#8-mengganti--menambah-data)
9. [Data Asli vs Data Contoh](#9-data-asli-vs-data-contoh)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Yang Perlu Disiapkan

Hanya dua hal:

| Kebutuhan | Versi | Cara dapat |
|---|---|---|
| **Python** | 3.10 atau lebih baru (diuji pada 3.14) | <https://www.python.org/downloads/> |
| **Git** *(opsional)* | terbaru | <https://git-scm.com/downloads> |

> **PENTING saat instal Python di Windows:** centang kotak
> **“Add Python to PATH”** pada layar pertama installer. Kalau lupa, jalankan
> ulang installer → *Modify* → aktifkan opsi tersebut.

Cek instalasi berhasil (buka **Command Prompt** / **PowerShell**):

```bash
python --version
```

Harus muncul misalnya `Python 3.14.6`. Kalau muncul pesan
*"'python' is not recognized"*, PATH belum aktif — tutup terminal, buka lagi,
atau ulangi instalasi.

**Tidak perlu** menginstal database server (MySQL/PostgreSQL). Aplikasi memakai
SQLite yang otomatis dibuat sebagai satu file.

---

## 2. Menjalankan Project dari 0 di Laptop Baru

Ikuti **berurutan**. Semua perintah dijalankan dari dalam folder project.

### Langkah 1 — Ambil kode project

Kalau memakai Git:

```bash
git clone <url-repository> forecasting-app
cd forecasting-app
```

Kalau memakai file ZIP: ekstrak ZIP-nya, lalu buka terminal di folder hasil
ekstrak (di Windows: klik kanan di dalam folder → *Open in Terminal*).

Pastikan sudah berada di folder yang benar — perintah berikut harus menampilkan
`run.py`, `requirements.txt`, dan folder `app`:

```bash
dir        # Windows
ls         # macOS / Linux
```

### Langkah 2 — Buat virtual environment

Virtual environment membuat semua library terpasang khusus untuk project ini,
tidak mengotori Python sistem.

```bash
python -m venv venv
```

Akan muncul folder baru bernama `venv`.

### Langkah 3 — Aktifkan virtual environment

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt / cmd):**

```cmd
venv\Scripts\activate.bat
```

**macOS / Linux:**

```bash
source venv/bin/activate
```

Kalau berhasil, prompt terminal akan diawali `(venv)`, contoh:

```
(venv) D:\Code\forecasting-app>
```

> **Windows PowerShell menolak dengan pesan *"running scripts is disabled on
> this system"*?** Jalankan sekali perintah ini, lalu ulangi aktivasi:
>
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```
>
> Alternatif tanpa mengubah policy: pakai Command Prompt (`cmd`) dan
> `venv\Scripts\activate.bat`.

**Ingat:** setiap kali membuka terminal baru untuk project ini, langkah aktivasi
ini harus diulang.

### Langkah 4 — Instal semua library

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Tunggu sampai selesai (± 1–2 menit). Library yang dipasang: Flask,
Flask-SQLAlchemy, Flask-Login, Flask-Migrate, Werkzeug, dan openpyxl.

> ### Pintasan: database sudah ikut disertakan
>
> File `instance/db.sqlite3` **ikut di dalam repository** dan sudah berisi
> seluruh data (16 obat, 1.696 baris penggunaan, hasil peramalan, serta data
> contoh untuk menu Permintaan/Resep/Pembelian/User).
>
> Jadi kalau file itu ada setelah Langkah 1, Anda boleh **melompat langsung ke
> Langkah 8** (`python run.py`). Langkah 5–7 hanya diperlukan bila database
> hilang, rusak, atau ingin dibuat ulang dari nol.

### Langkah 5 — Buat struktur database

```bash
# Windows (PowerShell)
$env:FLASK_APP = "run.py"
flask db upgrade

# Windows (cmd)
set FLASK_APP=run.py
flask db upgrade

# macOS / Linux
export FLASK_APP=run.py
flask db upgrade
```

Perintah ini membuat file database `instance/db.sqlite3` beserta seluruh
tabelnya. Output terakhir kira-kira:

```
INFO  [alembic.runtime.migration] Running upgrade 3d2f9a04fdb3 -> e034cc8d3a23, add jumlah to resep_item
```

### Langkah 6 — Buat user admin

```bash
python seed_admin.py
```

Output:

```
[SELESAI] User admin berhasil dibuat.
  Username: admin
  Password: admin123
```

### Langkah 7 — Isi data obat & penggunaan mingguan

```bash
python seed_obat.py
```

Script ini membaca sheet **"Data Mentah"** dari file
`Data Lengkap Hasil Peramalan Persediaan Obat (Bab IV).xlsx` dan memasukkan
**16 obat × 106 periode mingguan** ke database.

Output:

```
[1/3] Membaca sheet "Data Mentah" dari Data Lengkap Hasil Peramalan Persediaan Obat (Bab IV).xlsx
      106 periode mingguan x 16 obat
[2/3] Menyiapkan data obat
[3/3] Menulis ulang data penggunaan obat

[SELESAI]
  Obat baru dibuat       : 16
  Penggunaan lama dihapus: 0
  Penggunaan dimasukkan  : 1696
```

> Script ini aman dijalankan berulang kali — data penggunaan lama ditulis ulang,
> tidak digandakan.

### Langkah 7b — Simpan hasil peramalan ke database

```bash
python seed_forecast.py
```

Menghitung peramalan seluruh obat (81 kombinasi α × β per obat) lalu menyimpan
hasilnya ke tabel `forecast_result`, sehingga hasil Bab IV tersimpan permanen —
bukan hanya dihitung saat halaman dibuka.

### Langkah 7c — Isi data contoh untuk menu lain

```bash
python seed_demo.py
```

Melengkapi kategori/satuan/harga/kadaluarsa obat, serta membuat user contoh,
Permintaan, Resep, dan Pembelian supaya seluruh halaman tidak kosong.

> **Data pada langkah ini fiktif**, bukan dari skripsi. Baca
> [bagian 9](#9-data-asli-vs-data-contoh). Script ini **tidak** mengubah satu pun
> baris penggunaan obat, jadi hasil peramalan tetap sama dengan Bab IV.

### Langkah 8 — Jalankan aplikasi

```bash
python run.py
```

Output:

```
 * Running on http://127.0.0.1:5000
 * Debugger is active!
```

Buka browser ke **<http://127.0.0.1:5000>**.

Untuk menghentikan server: tekan **Ctrl + C** di terminal.

---

### Ringkasan (salin-tempel sekaligus)

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:FLASK_APP = "run.py"
flask db upgrade
python seed_admin.py
python seed_obat.py
python seed_forecast.py
python seed_demo.py
python run.py
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
export FLASK_APP=run.py
flask db upgrade
python seed_admin.py
python seed_obat.py
python seed_forecast.py
python seed_demo.py
python run.py
```

---

## 3. Akun untuk Login

| Username | Password | Role | Bisa mengakses |
|---|---|---|---|
| `admin` | `admin123` | admin | semua menu |
| `petugas_farmasi` | `user123` | petugas | Obat, Permintaan, Penggunaan, Resep, Pembelian, **Peramalan** |
| `dr_andi` | `user123` | dokter | Resep, Permintaan, Penggunaan |
| `dr_sinta` | `user123` | dokter | Resep, Permintaan, Penggunaan |
| `ny_rahma`, `ny_dewi`, `ny_lestari`, `ny_maya`, `ny_fitri` | `user123` | pasien | Resep & Pembelian miliknya sendiri |

> Ganti semua password ini lewat menu **User** sebelum dipakai di lingkungan nyata.

Role yang tersedia: `admin`, `petugas`, `dokter`, `pasien`.
Menu **Peramalan** hanya bisa diakses role `admin` dan `petugas` — role lain akan
mendapat halaman 403 (Forbidden).

---

## 4. Cara Memakai Menu Peramalan

### a. Peramalan per obat — `/peramalan`

1. Klik menu **Peramalan** di sidebar.
2. Pilih obat pada dropdown (misal **Afolat**).
3. Pilih horizon proyeksi (1 / 4 / 8 / 12 / 24 / 52 minggu ke depan).
4. Klik **Proses Peramalan**.

Halaman akan menampilkan:

- **Ringkasan** — α dan β terbaik, MAD, MSE, MAPE, kategori MAPE (Tabel 2.1),
  prediksi periode berikutnya, dan rata-rata historis.
- **Grafik** — data aktual, ramalan satu langkah, dan garis proyeksi ke depan.
- **Tabel 4.1** — statistik deskriptif obat tersebut.
- **Tabel 4.3** — pembagian data latih (80%) dan data uji (20%).
- **Tabel proyeksi** — ramalan tiap periode ke depan beserta pembulatannya.
- **Tabel perhitungan DES lengkap** — Level, Tren, Ramalan, Error, |Error|,
  Error², dan APE per periode. Baris kuning = data uji, baris biru = periode
  awal (L0/T0).
- **Tabel 81 kombinasi α × β** — baris hijau adalah kombinasi terpilih.

Bila obat yang dipilih punya data identik dengan obat lain, muncul pemberitahuan
di bagian atas.

### b. Rekap seluruh obat — `/peramalan/rekap`

Klik **Rekap Semua Obat** pada sidebar untuk melihat seluruh tabel Bab IV
sekaligus: Tabel 4.1, 4.2, 4.3, 4.6, 4.7, 4.8, dan acuan kategori MAPE
(Tabel 2.1).

Di bagian bawah halaman ada **"Hasil Peramalan yang Tersimpan di Database"**
beserta tombol **Hitung Ulang & Simpan ke Database**. Perbedaannya:

| | Tabel 4.1–4.8 di atas | Tabel "Tersimpan di Database" |
|---|---|---|
| Sumber | dihitung ulang setiap halaman dibuka | tabel `forecast_result` |
| Berubah otomatis kalau data penggunaan berubah | ya | tidak, sampai tombol simpan ditekan |
| Kegunaan | melihat kondisi terkini | arsip hasil, bisa dilampirkan di skripsi |

Tombol tersebut melakukan hal yang sama dengan `python seed_forecast.py`.

### Contoh hasil (harus sama persis dengan Excel)

| Nama Obat | α | β | MAD | MSE | MAPE (%) | Prediksi ke-106 |
|---|---|---|---|---|---|---|
| Afolat | 0,9 | 0,1 | 5,7940 | 55,5120 | 4,9200 | 109,9136 |
| Amoxicillin | 0,1 | 0,3 | 6,3515 | 61,2027 | 5,6328 | 114,0778 |
| Apialys Syrup | 0,9 | 0,5 | 6,9111 | 77,5972 | 5,8222 | 109,1515 |
| Asam Mefenamat | 0,4 | 0,1 | 7,3738 | 90,0984 | 6,3587 | 113,7053 |
| Epexol Syrup | 0,8 | 0,1 | 5,2816 | 77,1184 | 4,3473 | 119,1470 |
| Gentamicin Injeksi | 0,1 | 0,2 | 5,0520 | 53,6479 | 4,5555 | 111,5163 |
| Naturoksi | 0,9 | 0,1 | 6,3352 | 97,2919 | 5,4497 | 93,2111 |
| Nazovel Suppositoria | 0,9 | 0,1 | 6,6742 | 71,5205 | 5,5075 | 115,7889 |
| Tramadol Injeksi | 0,9 | 0,9 | 5,3232 | 41,9208 | 4,6344 | 77,9401 |

Tujuh obat lain (Ceftriaxone, Ringer Lactat, Aquabidest, Tranexamat Acid
Injeksi, Ondansetron Injeksi, Sanmol Syrup, Natavit) memiliki data mingguan
identik dengan pasangannya, sehingga hasilnya sama persis (Tabel 4.7).

---

## 5. Metode Peramalan yang Dipakai

Implementasi ada di [`app/forecasting.py`](app/forecasting.py).

### Rumus

```
Level_t   = α · Aktual_t + (1 − α) · (Level_(t−1) + Tren_(t−1))
Tren_t    = β · (Level_t − Level_(t−1)) + (1 − β) · Tren_(t−1)
Ramalan_t = Level_(t−1) + Tren_(t−1)                    (ramalan 1 langkah)
Ramalan_(n+m) = Level_n + m · Tren_n                    (proyeksi m periode)
```

### Ketentuan yang mengikuti Bab IV

| Aspek | Ketentuan |
|---|---|
| Inisialisasi | Baris pertama deret dipakai sebagai **L0**; **T0 = 0** |
| Periode | Baris pertama = periode 0, sisanya periode 1..n |
| Pembagian data | 80% latih : 20% uji (105 minggu → 84 latih / 21 uji) |
| Grid parameter | α dan β dari 0,1 s.d. 0,9 → **81 kombinasi** |
| Kriteria pemilihan | **MAPE terkecil pada data uji** |
| Evaluasi | MAD, MSE, MAPE dihitung **hanya pada data uji** |

### Kategori MAPE (Tabel 2.1)

| Rentang MAPE | Kategori |
|---|---|
| < 10% | Sangat Baik |
| 10% – 20% | Baik |
| 20% – 50% | Cukup |
| > 50% | Buruk |

---

## 6. Struktur Folder

```
forecasting-app/
├── app/
│   ├── __init__.py            # factory create_app(), registrasi blueprint & filter
│   ├── extensions.py          # objek db, login_manager, migrate
│   ├── models.py              # model tabel database
│   ├── decorators.py          # decorator role_required
│   ├── forecasting.py         # >> MESIN PERAMALAN DES (rumus Bab IV) <<
│   ├── services.py            # jembatan database <-> mesin peramalan
│   ├── routes/                # halaman: auth, dashboard, obat, peramalan, dll
│   ├── templates/             # tampilan HTML
│   └── static/                # gambar, icon, Chart.js lokal
├── data/
│   ├── penggunaan_obat_mingguan.csv   # hasil ekspor sheet "Data Mentah"
│   └── legacy/                        # CSV lama (tidak dipakai, datanya berbeda)
├── migrations/                # migrasi database (Alembic)
├── instance/db.sqlite3        # database, IKUT di dalam repository
├── Data Lengkap Hasil Peramalan Persediaan Obat (Bab IV).xlsx   # sumber data
├── export_data_mentah.py      # Excel -> CSV
├── seed_admin.py              # buat role + user admin
├── seed_obat.py               # isi data obat & penggunaan  (DATA SKRIPSI)
├── seed_forecast.py           # hitung & simpan hasil peramalan (DATA SKRIPSI)
├── seed_demo.py               # isi menu lain                (DATA CONTOH)
├── requirements.txt
└── run.py                     # titik masuk aplikasi
```

---

## 7. Perintah yang Sering Dipakai

Jalankan setelah virtual environment aktif.

| Tujuan | Perintah |
|---|---|
| Menjalankan aplikasi | `python run.py` |
| Membuat / memperbarui tabel database | `flask db upgrade` |
| Membuat file migrasi baru setelah mengubah `models.py` | `flask db migrate -m "pesan"` |
| Reset password admin | `python seed_admin.py` |
| Muat ulang data dari Excel | `python seed_obat.py` |
| Hitung & simpan hasil peramalan | `python seed_forecast.py` |
| Isi ulang data contoh menu lain | `python seed_demo.py` |
| Ekspor sheet "Data Mentah" ke CSV | `python export_data_mentah.py` |
| Menonaktifkan virtual environment | `deactivate` |

**Reset database total** (semua data hilang):

```bash
# Windows
del instance\db.sqlite3
# macOS / Linux
rm instance/db.sqlite3

flask db upgrade
python seed_admin.py
python seed_obat.py
python seed_forecast.py
python seed_demo.py
```

---

## 8. Mengganti / Menambah Data

### Lewat aplikasi

Menu **Penggunaan Obat** → pilih obat, isi tanggal dan jumlah → **Tambah**.
Hasil peramalan langsung ikut berubah karena dihitung ulang setiap kali tombol
*Proses Peramalan* ditekan.

### Lewat file Excel

1. Ubah nilai pada sheet **"Data Mentah"** di file
   `Data Lengkap Hasil Peramalan Persediaan Obat (Bab IV).xlsx`.
   Formatnya: kolom `No.`, `Minggu` (dd/mm/yyyy), lalu satu kolom per obat.
   Baris pertama (No. 0) adalah nilai awal **L0**.
2. Jalankan ulang:

   ```bash
   python seed_obat.py
   ```

> ### ⚠ Hati-hati: menyetujui Permintaan mengubah hasil peramalan
>
> Pada menu **Permintaan**, mengubah status sebuah permintaan menjadi
> **"disetujui"** akan **menambah satu baris baru di Penggunaan Obat** (perilaku
> bawaan aplikasi). Baris baru itu ikut masuk ke deret data peramalan, sehingga
> α/β terbaik dan nilai MAPE bisa **berbeda dari Bab IV**.
>
> Kalau angka di web harus tetap sama persis dengan skripsi, jangan menyetujui
> permintaan — atau kembalikan datanya dengan `python seed_obat.py` sesudahnya.

---

## 9. Data Asli vs Data Contoh

Tidak semua isi aplikasi berasal dari skripsi. Rinciannya:

### Berasal dari file Excel Bab IV (data penelitian)

| Bagian | Script | Keterangan |
|---|---|---|
| Nama 16 obat | `seed_obat.py` | kolom sheet "Data Mentah" |
| Penggunaan obat mingguan (1.696 baris) | `seed_obat.py` | 106 periode × 16 obat, nilainya persis |
| Seluruh hasil peramalan (α, β, MAD, MSE, MAPE, prediksi) | `seed_forecast.py` | dihitung dari data di atas, cocok dengan Tabel 4.6/4.7/4.8 |

### Data contoh (fiktif, dibuat agar halaman tidak kosong)

| Bagian | Script | Keterangan |
|---|---|---|
| **Stok awal** obat | `seed_obat.py` | ± kebutuhan 4 minggu (4 × rata-rata penggunaan) |
| Kategori, satuan, harga, tanggal kadaluarsa obat | `seed_demo.py` | tidak tersedia di data sumber |
| User `petugas_farmasi`, `dr_*`, `ny_*` | `seed_demo.py` | nama fiktif |
| 24 data Permintaan | `seed_demo.py` | unit peminta fiktif (IGD, Poli Anak, dll) |
| 10 data Resep + 20 item | `seed_demo.py` | ditautkan ke baris penggunaan yang **sudah ada**, tidak membuat baris baru |
| 10 data Pembelian | `seed_demo.py` | status & bukti bayar fiktif |

`seed_demo.py` sengaja dirancang **tidak menambah atau mengubah satu pun baris
penggunaan obat** — di akhir eksekusinya ada baris verifikasi:

```
Penggunaan obat   : 1696 -> 1696 (TIDAK BERUBAH, hasil peramalan aman)
```

### Lain-lain

- File `data/legacy/Obat_Keluar_Per_Minggu_2023_2024_Smoothed.csv` adalah data
  lama yang **berbeda** dari sheet "Data Mentah" (hanya 15 obat, nilainya tidak
  sama). File itu disimpan sebagai arsip dan **tidak lagi dipakai**.

---

## 10. Troubleshooting

| Masalah | Penyebab & Solusi |
|---|---|
| `'python' is not recognized` | Python belum masuk PATH. Instal ulang dan centang *Add Python to PATH*, lalu buka terminal baru. |
| `running scripts is disabled on this system` | Jalankan `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, atau pakai `cmd` + `venv\Scripts\activate.bat`. |
| `ModuleNotFoundError: No module named 'flask'` | Virtual environment belum aktif (`(venv)` tidak terlihat di prompt), atau langkah 4 dilewati. |
| `Error: Could not locate a Flask application` | Variabel `FLASK_APP` belum diatur. Lihat Langkah 5. |
| `no such table: user` | `flask db upgrade` belum dijalankan. |
| Dropdown obat kosong / *"Belum ada obat dengan data penggunaan yang cukup"* | `python seed_obat.py` belum dijalankan. |
| Menu Permintaan/Resep/Pembelian kosong | `python seed_demo.py` belum dijalankan. |
| Bagian "Hasil Peramalan yang Tersimpan" kosong | Tekan tombol **Hitung Ulang & Simpan ke Database**, atau jalankan `python seed_forecast.py`. |
| Login sebagai dokter/pasien, menu Peramalan hilang | Memang begitu — hanya role `admin` dan `petugas` yang boleh mengaksesnya. |
| `Sumber data tidak ditemukan` saat `seed_obat.py` | File `.xlsx` tidak ada di folder project. Pastikan file Excel ikut tersalin, atau gunakan `data/penggunaan_obat_mingguan.csv`. |
| Port 5000 sudah dipakai | Jalankan dengan port lain: `flask run --port 5001` (setelah `FLASK_APP` diatur). |
| Grafik tidak muncul | File `app/static/vendor/chart.umd.min.js` hilang. Pastikan folder `app/static` ikut tersalin — grafik memakai Chart.js lokal, tidak butuh internet. |
| Hasil peramalan berbeda dari Excel | Database berisi data lain. Jalankan ulang `python seed_obat.py`. |

---

## Lisensi

Project ini dibuat untuk keperluan penelitian/skripsi.
