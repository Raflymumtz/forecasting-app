from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Resep, Obat, ResepItem, User, PenggunaanObat, Pembelian
from datetime import datetime

bp = Blueprint('resep', __name__, url_prefix='/resep')

@bp.route("/")
@login_required
def index():
    if current_user.role.name == 'pasien':
        resep_list = Resep.query.filter_by(pasien_id=current_user.id).all()
        pasien_list = []
        penggunaan_list = []
    else:
        resep_list = Resep.query.all()
        pasien_list = User.query.filter(User.role.has(name='pasien')).all()
        penggunaan_list = PenggunaanObat.query.filter(
            ~PenggunaanObat.resep_items.any()
        ).all()

    return render_template(
        "resep.html",
        reseps=resep_list,
        pasien_list=pasien_list,
        penggunaan_list=penggunaan_list
    )

@bp.route("/add", methods=["POST"])  # ✅ Ini penting agar url_for('resep.add') bisa dikenali
@login_required
def add():
    if current_user.role.name not in ['dokter', 'admin']:
        flash("Hanya dokter atau admin yang dapat menambahkan resep.", "danger")
        return redirect(url_for("resep.index"))

    dokter_id = current_user.id
    pasien_id = request.form["pasien_id"]
    tanggal = datetime.strptime(request.form["tanggal"], "%Y-%m-%d").date()
    keterangan = request.form["keterangan"]
    penggunaan_ids = request.form.getlist("penggunaan_ids")

    if not penggunaan_ids:
        flash("Silakan pilih minimal satu penggunaan obat.", "danger")
        return redirect(url_for("resep.index"))

    resep = Resep(
        dokter_id=dokter_id,
        pasien_id=pasien_id,
        tanggal=tanggal,
        keterangan=keterangan
    )
    db.session.add(resep)
    db.session.commit()

    for pid in penggunaan_ids:
        penggunaan = PenggunaanObat.query.get(int(pid))
        if penggunaan:  # Safety check
            item = ResepItem(
                resep_id=resep.id,
                penggunaan_id=penggunaan.id,
                jumlah=penggunaan.jumlah  # Gunakan jumlah dari penggunaan
            )
            db.session.add(item)

    pembelian = Pembelian(
        pasien_id=pasien_id,
        resep_id=resep.id,
        bukti_pembayaran=None,
        status="Belum dibayar"
    )
    db.session.add(pembelian)
    db.session.commit()

    flash("Resep dan pembelian berhasil ditambahkan.", "success")
    return redirect(url_for("resep.index"))

@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    resep = Resep.query.get_or_404(id)

    for item in resep.items:
        db.session.delete(item)

    pembelian = Pembelian.query.filter_by(resep_id=resep.id).first()
    if pembelian:
        db.session.delete(pembelian)

    db.session.delete(resep)
    db.session.commit()
    flash("Resep berhasil dihapus.", "success")
    return redirect(url_for('resep.index'))
