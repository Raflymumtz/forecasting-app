"""
Halaman peramalan persediaan obat dengan metode Double Exponential Smoothing.

Seluruh perhitungan mengikuti Bab IV skripsi (lihat app/forecasting.py) sehingga
angka yang tampil di web identik dengan file
"Data Lengkap Hasil Peramalan Persediaan Obat (Bab IV).xlsx".
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app import db
from app.decorators import role_required
from app.forecasting import GRID_VALUES, MIN_PERIODE, jalankan_peramalan, kategori_mape
from app.models import ForecastResult, Obat
from app.services import deret_obat, hitung_semua_obat, obat_layak

bp = Blueprint("peramalan", __name__, url_prefix="/peramalan")

PILIHAN_MINGGU = [1, 4, 8, 12, 24, 52]


@bp.route("/", methods=["GET", "POST"])
@login_required
@role_required("admin", "petugas")
def index():
    obats = obat_layak()
    hasil = None
    pesan = None
    selected_obat_id = None
    n_weeks = 4

    if request.method == "POST" and request.form.get("obat_id"):
        selected_obat_id = int(request.form["obat_id"])
        try:
            n_weeks = int(request.form.get("n_weeks") or 4)
        except ValueError:
            n_weeks = 4
        n_weeks = max(1, min(52, n_weeks))

        obat = Obat.query.get(selected_obat_id)
        tanggal, nilai = deret_obat(selected_obat_id)

        if obat is None:
            pesan = "Obat tidak ditemukan."
        elif len(nilai) - 1 < MIN_PERIODE:
            pesan = (
                f"Data penggunaan obat ini hanya {max(0, len(nilai) - 1)} periode. "
                f"Dibutuhkan minimal {MIN_PERIODE} periode agar peramalan dapat "
                "dihitung."
            )
        else:
            hasil = jalankan_peramalan(tanggal, nilai, n_weeks)
            if hasil is None:
                pesan = "Peramalan tidak dapat dihitung untuk data ini."
            else:
                hasil["obat"] = obat
                hasil["kembar"] = _cari_kembar(obat, nilai)

    return render_template(
        "peramalan.html",
        obats=obats,
        hasil=hasil,
        pesan=pesan,
        selected_obat_id=selected_obat_id,
        n_weeks=n_weeks,
        pilihan_minggu=PILIHAN_MINGGU,
        grid_values=GRID_VALUES,
    )


def _cari_kembar(obat, nilai):
    """Obat lain yang deret penggunaannya identik (Tabel 4.2 / 4.7)."""
    kembar = []
    for lain in obat_layak():
        if lain.id == obat.id:
            continue
        if deret_obat(lain.id)[1] == nilai:
            kembar.append(lain.nama)
    return kembar


@bp.route("/rekap")
@login_required
@role_required("admin", "petugas")
def rekap():
    """Rekap seluruh obat: Tabel 4.1, 4.2, 4.3, 4.6, 4.7 dan 4.8."""
    data = hitung_semua_obat(n_periode_kedepan=1)
    nama = data["nama"]
    acuan = data["acuan"]

    tabel_41, tabel_46, tabel_47, tabel_48 = [], [], [], []
    pembagian = None

    for o in data["obats"]:
        h = data["hasil"][acuan[o.id]]
        if h is None:
            continue
        if pembagian is None:
            pembagian = h["pembagian"]

        stat = data["stat"][o.id]
        identik = acuan[o.id] != o.id

        tabel_41.append(
            {
                "nama": o.nama,
                "stat": stat,
                "keterangan": (
                    f"Data identik dengan {nama[acuan[o.id]]}" if identik else "Data unik"
                ),
            }
        )

        baris = {
            "nama": o.nama,
            "acuan": nama[acuan[o.id]],
            "alpha": h["alpha"],
            "beta": h["beta"],
            "mad": h["mad"],
            "mse": h["mse"],
            "mape": h["mape"],
            "kategori": kategori_mape(h["mape"]),
        }
        (tabel_47 if identik else tabel_46).append(baris)

        if not identik:
            tabel_48.append(
                {
                    "nama": o.nama,
                    "rata": stat["rata"],
                    "prediksi": h["prediksi_berikutnya"],
                    "selisih": h["prediksi_berikutnya"] - stat["rata"],
                    "kategori": kategori_mape(h["mape"]),
                    "periode": h["pembagian"]["n_total"] + 1,
                    "stok": o.stok,
                }
            )

    tabel_42 = [
        {"nama": nama[oid], "sama_dengan": nama[ref]}
        for oid, ref in acuan.items()
        if ref != oid
    ]

    for tabel in (tabel_41, tabel_42, tabel_46, tabel_47, tabel_48):
        tabel.sort(key=lambda r: r["nama"])

    # Hasil peramalan yang sudah tersimpan permanen di database
    tersimpan = (
        ForecastResult.query.order_by(
            ForecastResult.tanggal.desc(), ForecastResult.id.desc()
        ).all()
    )
    waktu_simpan = tersimpan[0].tanggal if tersimpan else None
    if waktu_simpan is not None:
        tersimpan = [t for t in tersimpan if t.tanggal == waktu_simpan]
        tersimpan.sort(key=lambda t: t.obat.nama)

    return render_template(
        "peramalan_rekap.html",
        pembagian=pembagian,
        tabel_41=tabel_41,
        tabel_42=tabel_42,
        tabel_46=tabel_46,
        tabel_47=tabel_47,
        tabel_48=tabel_48,
        tersimpan=tersimpan,
        waktu_simpan=waktu_simpan,
    )


@bp.route("/simpan", methods=["POST"])
@login_required
@role_required("admin", "petugas")
def simpan():
    """Menghitung ulang seluruh obat lalu menyimpannya ke tabel forecast_result."""
    jumlah = simpan_hasil_peramalan()
    flash(f"{jumlah} hasil peramalan berhasil disimpan ke database.", "success")
    return redirect(url_for("peramalan.rekap"))


def simpan_hasil_peramalan(hapus_lama=True):
    """Hitung peramalan seluruh obat dan simpan ke tabel forecast_result.

    Dipakai oleh tombol "Simpan ke Database" dan oleh script seed_forecast.py.
    Mengembalikan jumlah baris yang tersimpan.
    """
    from datetime import datetime

    data = hitung_semua_obat(n_periode_kedepan=1)
    acuan = data["acuan"]

    if hapus_lama:
        ForecastResult.query.delete()

    waktu = datetime.utcnow()
    jumlah = 0

    for o in data["obats"]:
        h = data["hasil"][acuan[o.id]]
        if h is None:
            continue
        stat = data["stat"][o.id]
        proyeksi = h["proyeksi"][0] if h["proyeksi"] else None

        db.session.add(
            ForecastResult(
                obat_id=o.id,
                tanggal=waktu,
                hasil=h["prediksi_berikutnya"],
                periode=h["pembagian"]["n_total"] + 1,
                tanggal_ramalan=proyeksi["tanggal"] if proyeksi else None,
                alpha=h["alpha"],
                beta=h["beta"],
                mad=h["mad"],
                mse=h["mse"],
                mape=h["mape"],
                kategori=kategori_mape(h["mape"]),
                rata_historis=stat["rata"],
                n_latih=h["pembagian"]["n_latih"],
                n_uji=h["pembagian"]["n_uji"],
                obat_acuan_id=acuan[o.id] if acuan[o.id] != o.id else None,
            )
        )
        jumlah += 1

    db.session.commit()
    return jumlah
