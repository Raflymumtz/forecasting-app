"""
Layanan peramalan tingkat aplikasi: menjembatani database dengan mesin DES
pada app/forecasting.py.

Dipakai bersama oleh halaman /peramalan/rekap dan script seed_forecast.py agar
angka yang tampil di web dan yang tersimpan di tabel forecast_result selalu
dihitung dengan cara yang sama.
"""

from sqlalchemy import func

from app.extensions import db
from app.forecasting import MIN_PERIODE, jalankan_peramalan, statistik_deskriptif
from app.models import Obat, PenggunaanObat


def deret_obat(obat_id):
    """Deret penggunaan satu obat, terurut menaik: (daftar_tanggal, daftar_nilai)."""
    data = (
        PenggunaanObat.query.filter_by(obat_id=obat_id)
        .order_by(PenggunaanObat.tanggal, PenggunaanObat.id)
        .all()
    )
    return [d.tanggal for d in data], [d.jumlah for d in data]


def obat_layak(urut_nama=True):
    """Obat yang punya cukup data penggunaan untuk diramalkan.

    ``urut_nama=False`` mengurutkan berdasarkan id, yaitu urutan kolom asli pada
    sheet "Data Mentah". Urutan itu dipakai saat menentukan obat acuan untuk
    pasangan data identik agar hasilnya sama dengan Tabel 4.2 / 4.7.
    """
    return (
        db.session.query(Obat)
        .join(PenggunaanObat)
        .group_by(Obat.id)
        .having(func.count(PenggunaanObat.id) > MIN_PERIODE)
        .order_by(Obat.nama if urut_nama else Obat.id)
        .all()
    )


def hitung_semua_obat(n_periode_kedepan=1):
    """Menghitung peramalan untuk seluruh obat sekaligus.

    Obat dengan deret penggunaan identik dikelompokkan; hanya obat pertama pada
    tiap kelompok (menurut urutan data asli) yang dihitung, sisanya memakai
    hasil yang sama persis karena DES bersifat deterministik.

    Mengembalikan dict:
        obats   : daftar Obat (urutan data asli)
        deret   : {id obat: (tanggal, nilai)}
        acuan   : {id obat: id obat acuan}
        hasil   : {id obat acuan: hasil jalankan_peramalan()}
        stat    : {id obat: statistik deskriptif}
        nama    : {id obat: nama obat}
    """
    obats = obat_layak(urut_nama=False)

    deret = {o.id: deret_obat(o.id) for o in obats}

    acuan = {}
    kunci_ke_acuan = {}
    for o in obats:
        kunci = tuple(deret[o.id][1])
        if kunci in kunci_ke_acuan:
            acuan[o.id] = kunci_ke_acuan[kunci]
        else:
            kunci_ke_acuan[kunci] = o.id
            acuan[o.id] = o.id

    hasil = {}
    for o in obats:
        if acuan[o.id] == o.id:
            tanggal, nilai = deret[o.id]
            hasil[o.id] = jalankan_peramalan(tanggal, nilai, n_periode_kedepan)

    stat = {
        o.id: statistik_deskriptif([float(v) for v in deret[o.id][1][1:]]) for o in obats
    }

    return {
        "obats": obats,
        "deret": deret,
        "acuan": acuan,
        "hasil": hasil,
        "stat": stat,
        "nama": {o.id: o.nama for o in obats},
    }
