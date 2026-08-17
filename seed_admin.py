"""
Membuat role dasar (admin, apoteker, dokter, pasien) dan satu user admin.

Script ini idempoten: bila user admin sudah ada, passwordnya hanya di-reset.

Jalankan:  python seed_admin.py
"""

from app import create_app
from app.extensions import db
from app.models import Role, User
from werkzeug.security import generate_password_hash

ROLES = ["admin", "petugas", "dokter", "pasien"]
USERNAME = "admin"
PASSWORD = "admin123"


def main():
    app = create_app()
    with app.app_context():
        for nama in ROLES:
            if not Role.query.filter_by(name=nama).first():
                db.session.add(Role(name=nama))
        db.session.commit()

        admin_role = Role.query.filter_by(name="admin").first()

        user = User.query.filter_by(username=USERNAME).first()
        if user:
            user.password = generate_password_hash(PASSWORD)
            user.role_id = admin_role.id
            pesan = "Password user admin di-reset."
        else:
            db.session.add(
                User(
                    username=USERNAME,
                    password=generate_password_hash(PASSWORD),
                    role_id=admin_role.id,
                )
            )
            pesan = "User admin berhasil dibuat."
        db.session.commit()

    print(f"[SELESAI] {pesan}")
    print(f"  Username: {USERNAME}")
    print(f"  Password: {PASSWORD}")


if __name__ == "__main__":
    main()
