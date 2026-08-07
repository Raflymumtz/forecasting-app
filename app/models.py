from app.extensions import db
from flask_login import UserMixin
from datetime import datetime

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    users = db.relationship('User', backref='role', lazy=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))
    role_id = db.Column(
        db.Integer,
        db.ForeignKey('role.id', name='fk_user_role'),
        nullable=True
    )

    def has_role(self, role_name):
        return self.role and self.role.name == role_name

class Obat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(50), nullable=False)
    satuan = db.Column(db.String(20), nullable=False)
    harga = db.Column(db.Integer, nullable=False)
    stok = db.Column(db.Integer, nullable=False)
    tanggal_kadaluarsa = db.Column(db.Date, nullable=False)

class PermintaanObat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_peminta = db.Column(db.String(100), nullable=False)
    obat_id = db.Column(db.Integer, db.ForeignKey('obat.id'), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)
    tanggal = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), default='menunggu', nullable=False)  # 'menunggu', 'disetujui', 'ditolak'
    is_processed = db.Column(db.Boolean, default=False, nullable=False)

    obat = db.relationship('Obat', backref=db.backref('permintaan_obat', lazy=True))

class PenggunaanObat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    obat_id = db.Column(db.Integer, db.ForeignKey('obat.id'), nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)

    # relasi ke obat
    obat = db.relationship('Obat', backref='penggunaan')

    # relasi ke ResepItem
    resep_items = db.relationship('ResepItem', back_populates='penggunaan', cascade='all, delete-orphan')


class Resep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dokter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pasien_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tanggal = db.Column(db.Date, nullable=False)
    keterangan = db.Column(db.String(255))

    dokter = db.relationship('User', foreign_keys=[dokter_id])
    pasien = db.relationship('User', foreign_keys=[pasien_id])

    # relasi ke ResepItem
    items = db.relationship('ResepItem', back_populates='resep', cascade='all, delete-orphan')


class ResepItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resep_id = db.Column(db.Integer, db.ForeignKey('resep.id'), nullable=False)
    penggunaan_id = db.Column(db.Integer, db.ForeignKey('penggunaan_obat.id'), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False, default=1)  # Tambahan

    # hubungan dua arah dengan Resep dan PenggunaanObat
    resep = db.relationship('Resep', back_populates='items')
    penggunaan = db.relationship('PenggunaanObat', back_populates='resep_items')

class ForecastResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    obat_id = db.Column(db.Integer, db.ForeignKey('obat.id'), nullable=False)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    hasil = db.Column(db.Float, nullable=False)

    obat = db.relationship('Obat', backref='forecast_results')

class Pembelian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pasien_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    resep_id = db.Column(db.Integer, db.ForeignKey('resep.id'))
    bukti_pembayaran = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='belum dibayar')

    pasien = db.relationship('User', backref='pembelian')
    resep = db.relationship('Resep', backref='pembelian')



