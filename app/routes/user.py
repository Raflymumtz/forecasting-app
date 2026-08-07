from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import User, Role
from werkzeug.security import generate_password_hash
from app.decorators import role_required

bp = Blueprint('user', __name__)

@bp.route("/")
@login_required
@role_required('admin')
def index():
    users = User.query.all()
    roles = Role.query.all()
    return render_template("user.html", users=users, roles=roles)

@bp.route("/add", methods=["POST"])
@login_required
@role_required('admin')
def add():
    username = request.form["username"]
    password = request.form["password"]
    role_id = request.form["role_id"]

    # Validasi username unik
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash(f'Username "{username}" sudah digunakan. Silakan pilih username lain.', 'danger')
        return redirect(url_for("user.index"))

    if username and password:
        user = User(
            username=username,
            password=generate_password_hash(password),
            role_id=role_id
        )
        db.session.add(user)
        db.session.commit()
        flash("User berhasil ditambahkan.", 'success')
    else:
        flash("Username dan password wajib diisi.", 'warning')

    return redirect(url_for("user.index"))

@bp.route("/delete/<int:id>")
@login_required
@role_required('admin')
def delete(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash("User berhasil dihapus.", 'success')
    return redirect(url_for("user.index"))
