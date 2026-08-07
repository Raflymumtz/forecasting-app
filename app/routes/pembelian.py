from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.models import Pembelian, Resep, Obat
from app.extensions import db
import os

bp = Blueprint("pembelian", __name__, url_prefix="/pembelian")

UPLOAD_FOLDER = "app/static/bukti"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/")
@login_required
def index():
    if current_user.role.name == "pasien":
        pembelian_list = Pembelian.query.filter_by(pasien_id=current_user.id).all()
    else:
        pembelian_list = Pembelian.query.all()
    return render_template("pembelian.html", pembelian_list=pembelian_list)

@bp.route("/upload/<int:id>", methods=["POST"])
@login_required
def upload(id):
    pembelian = Pembelian.query.get_or_404(id)

    # Hanya pasien yang berhak mengunggah bukti untuk dirinya sendiri
    if current_user.role.name != 'pasien' or pembelian.pasien_id != current_user.id:
        flash("Anda tidak memiliki akses untuk melakukan ini.", "danger")
        return redirect(url_for("pembelian.index"))

    file = request.files.get("bukti")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # ✅ Buat folder jika belum ada
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        pembelian.bukti_pembayaran = filename
        db.session.commit()
        flash("Bukti pembayaran berhasil diunggah ✅", "Success ✅")
    else:
        flash("Format file tidak valid (hanya PNG, JPG, JPEG, PDF).", "danger")

    return redirect(url_for("pembelian.index"))

@bp.route("/ubah-status/<int:id>", methods=["POST"])
@login_required
def ubah_status(id):
    if current_user.role.name not in ["admin", "petugas"]:
        flash("Akses ditolak.", "danger")
        return redirect(url_for("pembelian.index"))

    pembelian = Pembelian.query.get_or_404(id)
    new_status = request.form.get("status")

    # Normalisasi untuk validasi
    valid_statuses = ["Belum dibayar", "Sudah dibayar", "Menunggu"]
    if new_status in valid_statuses:
        pembelian.status = new_status
        db.session.commit()
        flash("Status pembayaran diperbarui.", "success")
    else:
        flash("Status tidak valid!", "danger")

    return redirect(url_for("pembelian.index"))

