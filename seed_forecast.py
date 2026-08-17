"""
Menghitung peramalan DES untuk seluruh obat dan menyimpannya ke tabel
``forecast_result``.

Hasilnya sama persis dengan Tabel 4.6, 4.7 dan 4.8 Bab IV, dan bisa dilihat di
halaman /peramalan/rekap bagian "Hasil Peramalan yang Tersimpan di Database".

Jalankan setelah seed_obat.py:  python seed_forecast.py
"""

from app import create_app
from app.models import ForecastResult
from app.routes.peramalan import simpan_hasil_peramalan


def main():
    app = create_app()
    with app.app_context():
        print("[1/2] Menghitung peramalan seluruh obat (81 kombinasi alpha x beta)")
        jumlah = simpan_hasil_peramalan()

        print("[2/2] Menyimpan ke tabel forecast_result")
        hasil = ForecastResult.query.join(
            ForecastResult.obat
        ).order_by(ForecastResult.obat_id).all()

        print(f"\n[SELESAI] {jumlah} hasil peramalan tersimpan.\n")
        print(f"{'Nama Obat':24s} {'a':>4s} {'b':>4s} {'MAPE (%)':>9s}  "
              f"{'Ramalan':>10s}  Kategori")
        print("-" * 70)
        for h in hasil:
            print(
                f"{h.obat.nama:24s} {h.alpha:4.1f} {h.beta:4.1f} {h.mape:9.4f}  "
                f"{h.hasil:10.4f}  {h.kategori}"
            )


if __name__ == "__main__":
    main()
