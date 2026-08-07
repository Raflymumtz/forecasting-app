from app import create_app
from app.extensions import db
from app.models import User, Role
from werkzeug.security import generate_password_hash

app = create_app()
app.app_context().push()

# Pastikan role admin sudah ada
admin_role = Role.query.filter_by(name="admin").first()
if not admin_role:
    admin_role = Role(name="admin")
    db.session.add(admin_role)
    db.session.commit()

# Buat user admin
admin_user = User(
    username="admin",
    password=generate_password_hash("admin123"),  # Ganti password sesuai kebutuhan
    role_id=admin_role.id
)

db.session.add(admin_user)
db.session.commit()
print("✅ Admin berhasil ditambahkan!")