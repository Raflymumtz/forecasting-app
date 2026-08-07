import pandas as pd
from datetime import datetime
from app import create_app, db
from app.models import Obat, PenggunaanObat

# Inisialisasi Flask app
app = create_app()

# Baca file CSV
df = pd.read_csv('Obat_Keluar_Per_Minggu_2023_2024_Smoothed.csv')

# Ubah kolom 'Minggu' ke format datetime
df['Minggu'] = pd.to_datetime(df['Minggu'], format='%m/%d/%Y')

with app.app_context():
    inserted = 0
    created_obat = 0
    skipped = 0

    for _, row in df.iterrows():
        tanggal = row['Minggu'].date()

        for nama_obat in df.columns[1:]:  # Lewati kolom 'Minggu'
            jumlah = row[nama_obat]
            if pd.isna(jumlah) or int(jumlah) == 0:
                continue

            # Cari atau buat obat
            obat = Obat.query.filter_by(nama=nama_obat.strip()).first()
            if not obat:
                # Tambahkan obat baru dengan default
                obat = Obat(
                    nama=nama_obat.strip(),
                    kategori='Unknown',
                    satuan='PCS',
                    harga=0,
                    stok=0,
                    tanggal_kadaluarsa=datetime(2030, 1, 1)
                )
                db.session.add(obat)
                db.session.flush()  # Perlu untuk mendapatkan id sebelum commit
                created_obat += 1

            # Tambahkan data penggunaan
            penggunaan = PenggunaanObat(
                obat_id=obat.id,
                tanggal=tanggal,
                jumlah=int(jumlah)
            )
            db.session.add(penggunaan)
            inserted += 1

    db.session.commit()
    print(f"[SELESAI] Tambah {inserted} penggunaan obat.")
    print(f"Obat baru ditambahkan: {created_obat}")