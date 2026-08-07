from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import PermintaanObat, Obat, PenggunaanObat
from datetime import datetime

bp = Blueprint('permintaan', __name__, url_prefix='/permintaan')

@bp.route('/')
@login_required
def index():
    permintaans = PermintaanObat.query.all()
    obats = Obat.query.all()
    return render_template('permintaan.html', permintaans=permintaans, obats=obats)

@bp.route('/add', methods=['POST'])
@login_required
def add():
    nama_peminta = request.form['nama_peminta']
    obat_id = int(request.form['obat_id'])
    jumlah = int(request.form['jumlah'])
    tanggal = request.form['tanggal']

    obat = Obat.query.get(obat_id)
    if not obat:
        flash('Obat tidak ditemukan.')
        return redirect(url_for('permintaan.index'))

    if jumlah > obat.stok:
        flash(f'Permintaan melebihi stok tersedia. Stok saat ini: {obat.stok}')
        return redirect(url_for('permintaan.index'))

    p = PermintaanObat(
        nama_peminta=nama_peminta,
        obat_id=obat_id,
        jumlah=jumlah,
        tanggal=datetime.strptime(tanggal, '%Y-%m-%d')
    )
    db.session.add(p)
    db.session.commit()
    flash('Permintaan berhasil ditambahkan.')
    return redirect(url_for('permintaan.index'))

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    permintaan = PermintaanObat.query.get_or_404(id)
    obats = Obat.query.all()

    if request.method == 'POST':
        permintaan.nama_peminta = request.form['nama_peminta']
        permintaan.obat_id = request.form['obat_id']
        permintaan.jumlah = int(request.form['jumlah'])
        permintaan.tanggal = datetime.strptime(request.form['tanggal'], '%Y-%m-%d')
        permintaan.status = request.form['status']

        # Logika: jika disetujui dan belum pernah disetujui sebelumnya
        if permintaan.status == 'disetujui':
            obat = Obat.query.get(permintaan.obat_id)
            if obat.stok >= permintaan.jumlah:
                obat.stok -= permintaan.jumlah

                # Tambahkan ke tabel penggunaan obat
                penggunaan = PenggunaanObat(
                    obat_id=permintaan.obat_id,
                    jumlah=permintaan.jumlah,
                    tanggal=permintaan.tanggal
                )
                db.session.add(penggunaan)
            else:
                flash("Stok tidak mencukupi untuk menyetujui permintaan ini.")
                return redirect(url_for('permintaan.edit', id=id))

        db.session.commit()
        flash('Permintaan berhasil diperbarui.')
        return redirect(url_for('permintaan.index'))

    return render_template('edit_permintaan.html', permintaan=permintaan, obats=obats)

@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    permintaan = PermintaanObat.query.get_or_404(id)
    db.session.delete(permintaan)
    db.session.commit()
    flash('Permintaan berhasil dihapus.')
    return redirect(url_for('permintaan.index'))
