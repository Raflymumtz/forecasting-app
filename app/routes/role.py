from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Role
from app.decorators import role_required

bp = Blueprint('role', __name__)

@bp.route("/")
@login_required
@role_required('admin')
def index():
    roles = Role.query.all()
    return render_template("role.html", roles=roles)

@bp.route("/add", methods=["POST"])
@login_required
@role_required('admin')
def add():
    name = request.form["name"]
    if name:
        new_role = Role(name=name)
        db.session.add(new_role)
        db.session.commit()
        flash("Role berhasil ditambahkan.")
    return redirect(url_for("role.index"))

@bp.route("/delete/<int:id>")
@login_required
@role_required('admin')
def delete(id):
    role = Role.query.get(id)
    db.session.delete(role)
    db.session.commit()
    flash("Role berhasil dihapus.")
    return redirect(url_for("role.index"))
