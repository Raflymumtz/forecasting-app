from flask import Blueprint, render_template
from flask_login import login_required
from datetime import date
from sqlalchemy import func
from app.models import db, Obat, Pembelian, User, PenggunaanObat

bp = Blueprint('dashboard', __name__)

@bp.route("/")
@login_required
def index():
    # Total obat dan statistik umum
    total_obat = Obat.query.count()
    obat_kadaluarsa = Obat.query.filter(Obat.tanggal_kadaluarsa < date.today()).count()
    obat_habis = Obat.query.filter(Obat.stok == 0).count()
    total_transaksi = Pembelian.query.count()
    total_user = User.query.count()

    # Data pie chart
    pie_labels = ['Kadaluarsa', 'Habis', 'Tersedia']
    pie_values = [
        obat_kadaluarsa,
        obat_habis,
        total_obat - (obat_kadaluarsa + obat_habis)
    ]

    # Bar chart: 5 obat paling banyak dipakai
    top_penggunaan = (
        db.session.query(Obat.nama, func.sum(PenggunaanObat.jumlah).label("jumlah_pakai"))
        .join(Obat, Obat.id == PenggunaanObat.obat_id)
        .group_by(Obat.id, Obat.nama)
        .order_by(func.sum(PenggunaanObat.jumlah).desc())
        .limit(5)
        .all()
    )
    bar_labels = [item[0] for item in top_penggunaan]
    bar_values = [item[1] for item in top_penggunaan]

    # List obat habis dan kadaluarsa untuk tabel
    obat_habis_list = Obat.query.filter(Obat.stok == 0).all()
    obat_kadaluarsa_list = Obat.query.filter(Obat.tanggal_kadaluarsa < date.today()).all()

    # Render template dengan semua data
    return render_template(
        "dashboard.html",
        total_obat=total_obat,
        obat_kadaluarsa=obat_kadaluarsa,
        obat_habis=obat_habis,
        total_transaksi=total_transaksi,
        total_user=total_user,
        pie_labels=pie_labels,
        pie_values=pie_values,
        bar_labels=bar_labels,
        bar_values=bar_values,
        obat_habis_list=obat_habis_list,
        obat_kadaluarsa_list=obat_kadaluarsa_list
    )
