from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Obat
from app.decorators import role_required
from datetime import datetime

bp = Blueprint('obat', __name__, url_prefix='/obat')

# Fungsi validasi untuk angka 1 hingga 5 digit (1 - 99999)
def is_valid_number(value):
    return value.isdigit() and 1 <= int(value) <= 99999

@bp.route("/")
@login_required
@role_required('admin', 'petugas')
def index():
    obats = Obat.query.all()
    return render_template("obat.html", obats=obats)

@bp.route("/add", methods=["POST"])
@login_required
@role_required('admin', 'petugas')
def add():
    harga = request.form["harga"]
    stok = request.form["stok"]

    if not (is_valid_number(harga) and is_valid_number(stok)):
        flash("Harga dan Stok harus berupa angka 1 hingga 5 digit (1 - 99999).", "error")
        return redirect(url_for("obat.index"))

    o = Obat(
        nama=request.form["nama"],
        kategori=request.form["kategori"],
        satuan=request.form["satuan"],
        harga=int(harga),
        stok=int(stok),
        tanggal_kadaluarsa=datetime.strptime(request.form["tanggal_kadaluarsa"], "%Y-%m-%d")
    )
    db.session.add(o)
    db.session.commit()
    flash("Obat berhasil ditambahkan.")
    return redirect(url_for("obat.index"))

@bp.route("/delete/<int:id>")
@login_required
@role_required('admin', 'petugas')
def delete(id):
    obat = Obat.query.get_or_404(id)
    db.session.delete(obat)
    db.session.commit()
    flash("Obat berhasil dihapus.")
    return redirect(url_for("obat.index"))

@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@role_required('admin', 'petugas')
def edit(id):
    obat = Obat.query.get_or_404(id)
    if request.method == "POST":
        harga = request.form["harga"]
        stok = request.form["stok"]

        if not (is_valid_number(harga) and is_valid_number(stok)):
            flash("Harga dan Stok harus berupa angka 1 hingga 5 digit (1 - 9999999).", "error")
            return redirect(url_for("obat.index"))

        obat.nama = request.form["nama"]
        obat.kategori = request.form["kategori"]
        obat.satuan = request.form["satuan"]
        obat.harga = int(harga)
        obat.stok = int(stok)
        obat.tanggal_kadaluarsa = datetime.strptime(request.form["tanggal_kadaluarsa"], "%Y-%m-%d")
        db.session.commit()
        flash("Obat berhasil diperbarui.")
        return redirect(url_for("obat.index"))
    return render_template("edit_obat.html", obat=obat)
