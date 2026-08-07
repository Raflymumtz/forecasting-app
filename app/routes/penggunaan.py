from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import PenggunaanObat, Obat
from datetime import datetime

bp = Blueprint('penggunaan', __name__, url_prefix='/penggunaan')

@bp.route('/')
@login_required
def index():
    data = PenggunaanObat.query.all()
    obats = Obat.query.all()
    return render_template('penggunaan.html', penggunaan=data, obats=obats)

@bp.route('/add', methods=['POST'])
@login_required
def add():
    obat_id = request.form['obat_id']
    tanggal = datetime.strptime(request.form['tanggal'], '%Y-%m-%d')
    jumlah = int(request.form['jumlah'])

    penggunaan = PenggunaanObat(obat_id=obat_id, tanggal=tanggal, jumlah=jumlah)
    db.session.add(penggunaan)
    db.session.commit()
    flash('Data penggunaan obat berhasil ditambahkan.')
    return redirect(url_for('penggunaan.index'))

@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    penggunaan = PenggunaanObat.query.get_or_404(id)
    db.session.delete(penggunaan)
    db.session.commit()
    flash('Data penggunaan obat berhasil dihapus.')
    return redirect(url_for('penggunaan.index'))
