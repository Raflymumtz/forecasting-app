from flask import Flask, redirect, url_for
from app.extensions import db, login_manager, migrate

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.models import User  # Masih diperlukan untuk user loader

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes import auth, dashboard, user, role, obat, permintaan, penggunaan, resep, peramalan, pembelian
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(dashboard.bp, url_prefix='/dashboard')
    app.register_blueprint(user.bp, url_prefix='/user')
    app.register_blueprint(role.bp, url_prefix='/role')
    app.register_blueprint(obat.bp, url_prefix='/obat')
    app.register_blueprint(permintaan.bp, url_prefix='/permintaan')
    app.register_blueprint(penggunaan.bp, url_prefix='/penggunaan')
    app.register_blueprint(resep.bp, url_prefix='/resep')
    app.register_blueprint(peramalan.bp, url_prefix="/peramalan")
    app.register_blueprint(pembelian.bp, url_prefix="/pembelian")

    @app.route("/")
    def root():
        from flask_login import current_user
        return redirect(url_for('dashboard.index')) if current_user.is_authenticated else redirect(url_for('auth.login'))

    # ⬇️ Tambahkan ini agar semua model dikenali Alembic
    from app import models

    return app
