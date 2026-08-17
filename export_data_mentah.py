"""
Mengekspor sheet "Data Mentah" dari file skripsi

    Data Lengkap Hasil Peramalan Persediaan Obat (Bab IV).xlsx

menjadi CSV yang dipakai oleh seed_obat.py.

Jalankan:  python export_data_mentah.py
Hasil:     data/penggunaan_obat_mingguan.csv
"""

import csv
import os

from app.forecasting import EXCEL_FILENAME, SHEET_DATA_MENTAH, baca_data_mentah

OUTPUT = os.path.join("data", "penggunaan_obat_mingguan.csv")


def main():
    tanggal, series = baca_data_mentah(EXCEL_FILENAME)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Minggu"] + list(series.keys()))
        for i, tgl in enumerate(tanggal):
            writer.writerow([tgl.strftime("%d/%m/%Y")] + [series[n][i] for n in series])

    print(f'[OK] Sheet "{SHEET_DATA_MENTAH}" diekspor ke {OUTPUT}')
    print(f"     {len(tanggal)} baris minggu x {len(series)} obat")


if __name__ == "__main__":
    main()
