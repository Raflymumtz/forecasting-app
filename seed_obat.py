"""
Mengisi database dengan data obat dan penggunaan obat mingguan.

Sumber data adalah sheet "Data Mentah" pada file skripsi
"Data Lengkap Hasil Peramalan Persediaan Obat (Bab IV).xlsx".
Bila file Excel tidak ditemukan, script memakai hasil ekspornya di
data/penggunaan_obat_mingguan.csv.

Script ini idempoten: menjalankannya berulang kali tidak menggandakan data
(seluruh data penggunaan lama akan ditulis ulang).

Jalankan:  python seed_obat.py
"""

import csv
import os
from datetime import datetime

from app import create_app, db
from app.forecasting import EXCEL_FILENAME, baca_data_mentah
from app.models import Obat, PenggunaanObat

CSV_FALLBACK = os.path.join("data", "penggunaan_obat_mingguan.csv")

# Stok awal diisi kira-kira kebutuhan 4 minggu (4 x rata-rata penggunaan
# mingguan). Nilai ini TIDAK berasal dari skripsi, hanya agar aplikasi punya
# stok awal yang masuk akal; silakan ubah lewat menu Obat.
MINGGU_STOK_AWAL = 4


def baca_dari_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        nama_obat = header[1:]
        tanggal, series = [], {n: [] for n in nama_obat}
        for row in reader:
            if not row or not row[0]:
                continue
            tanggal.append(datetime.strptime(row[0], "%d/%m/%Y").date())
            for i, n in enumerate(nama_obat):
                series[n].append(int(row[1 + i]))
    return tanggal, series


def muat_data():
    if os.path.exists(EXCEL_FILENAME):
        print(f'[1/3] Membaca sheet "Data Mentah" dari {EXCEL_FILENAME}')
        return baca_data_mentah(EXCEL_FILENAME)
    if os.path.exists(CSV_FALLBACK):
        print(f"[1/3] File Excel tidak ada, membaca {CSV_FALLBACK}")
        return baca_dari_csv(CSV_FALLBACK)
    raise SystemExit(
        f"Sumber data tidak ditemukan. Letakkan '{EXCEL_FILENAME}' atau "
        f"'{CSV_FALLBACK}' di folder proyek."
    )


def main():
    tanggal, series = muat_data()
    print(f"      {len(tanggal)} periode mingguan x {len(series)} obat")

    app = create_app()
    with app.app_context():
        print("[2/3] Menyiapkan data obat")
        obat_map = {}
        dibuat = 0
        for nama in series:
            nama = nama.strip()
            obat = Obat.query.filter_by(nama=nama).first()
            rata = sum(series[nama][1:]) / max(1, len(series[nama][1:]))
            if not obat:
                obat = Obat(
                    nama=nama,
                    kategori="Obat",
                    satuan="PCS",
                    harga=0,
                    stok=int(round(rata * MINGGU_STOK_AWAL)),
                    tanggal_kadaluarsa=datetime(2030, 12, 31).date(),
                )
                db.session.add(obat)
                dibuat += 1
            obat_map[nama] = obat
        db.session.flush()

        print("[3/3] Menulis ulang data penggunaan obat")
        id_obat = [o.id for o in obat_map.values()]
        dihapus = PenggunaanObat.query.filter(
            PenggunaanObat.obat_id.in_(id_obat)
        ).delete(synchronize_session=False)

        dimasukkan = 0
        for nama, obat in obat_map.items():
            for tgl, jumlah in zip(tanggal, series[nama]):
                db.session.add(
                    PenggunaanObat(obat_id=obat.id, tanggal=tgl, jumlah=int(jumlah))
                )
                dimasukkan += 1

        db.session.commit()

    print("\n[SELESAI]")
    print(f"  Obat baru dibuat       : {dibuat}")
    print(f"  Penggunaan lama dihapus: {dihapus}")
    print(f"  Penggunaan dimasukkan  : {dimasukkan}")


if __name__ == "__main__":
    main()
