from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User, Role
from app.extensions import db, login_manager

bp = Blueprint('auth', __name__)

# Loader user untuk Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# LOGIN
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash('Username atau password salah.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user)
        flash('Berhasil login.', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('login.html')


# LOGOUT
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))


# REGISTER
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username sudah digunakan. Silakan pilih yang lain.', 'warning')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password)

        role_pasien = Role.query.filter_by(name='pasien').first()

        new_user = User(
        username=username,
        password=hashed_password,
        role_id=role_pasien.id if role_pasien else None  # fallback
        )

        db.session.add(new_user)
        db.session.commit()

        # Autologin setelah register (opsional)
        login_user(new_user)
        flash('Registrasi berhasil. Selamat datang!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('register.html')
