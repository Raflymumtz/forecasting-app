"""
Mengisi menu-menu yang tidak punya sumber data di skripsi: User, detail Obat
(kategori/harga/kadaluarsa), Permintaan, Resep dan Pembelian.

    PERHATIAN
    Data pada script ini adalah DATA CONTOH (fiktif) yang dibuat agar seluruh
    halaman aplikasi tidak kosong. Data ini TIDAK berasal dari file
    "Data Lengkap Hasil Peramalan Persediaan Obat (Bab IV).xlsx".

    Yang berasal dari skripsi hanyalah data penggunaan obat mingguan
    (seed_obat.py) dan hasil peramalannya (seed_forecast.py). Script ini tidak
    menambah/mengubah satu pun baris penggunaan obat, sehingga hasil peramalan
    tetap sama persis dengan Bab IV.

Script ini idempoten: menjalankannya berulang kali tidak menggandakan data.

Jalankan:  python seed_demo.py
"""

import random
from datetime import date, timedelta

from app import create_app, db
from app.models import (
    Obat,
    Pembelian,
    PenggunaanObat,
    PermintaanObat,
    Resep,
    ResepItem,
    Role,
    User,
)
from werkzeug.security import generate_password_hash

PASSWORD_DEMO = "user123"

# --- Detail obat (kategori, satuan, harga satuan, kadaluarsa dalam hari) -----
# Kolom terakhir = jarak tanggal kadaluarsa dari HARI INI, dalam hari. Dibuat
# relatif agar data contoh tidak basi kapan pun script dijalankan. Dua obat
# sengaja diberi nilai negatif (sudah kadaluarsa) supaya peringatan kadaluarsa
# di halaman Dashboard ada isinya.
DETAIL_OBAT = {
    "Afolat":                  ("Vitamin & Suplemen", "TABLET", 1_500,   540),
    "Asam Mefenamat":          ("Analgesik",          "TABLET", 2_000,   400),
    "Amoxicillin":             ("Antibiotik",         "KAPSUL", 2_500,   270),
    "Naturoksi":               ("Vitamin & Suplemen", "TABLET", 3_500,   630),
    "Gentamicin Injeksi":      ("Antibiotik",         "AMPUL",  12_000,  150),
    "Tramadol Injeksi":        ("Analgesik",          "AMPUL",  18_000,  330),
    "Nazovel Suppositoria":    ("Analgesik",          "SUPP",   15_000,  210),
    "Ceftriaxone":             ("Antibiotik",         "VIAL",   22_000,  480),
    "Ringer Lactat":           ("Cairan Infus",       "KOLF",   14_000,  900),
    "Aquabidest":              ("Cairan Infus",       "BOTOL",  5_000,   1_080),
    "Tranexamat Acid Injeksi": ("Hemostatik",         "AMPUL",  16_000,  120),
    "Ondansetron Injeksi":     ("Antiemetik",         "AMPUL",  20_000,  600),
    "Sanmol Syrup":            ("Analgesik",          "BOTOL",  17_000,  -20),
    "Natavit":                 ("Vitamin & Suplemen", "TABLET", 2_500,   720),
    "Epexol Syrup":            ("Obat Batuk",         "BOTOL",  26_000,  -45),
    "Apialys Syrup":           ("Vitamin & Suplemen", "BOTOL",  32_000,  810),
}

# --- User contoh -------------------------------------------------------------
USERS = [
    ("petugas_farmasi", "petugas"),
    ("dr_andi",         "dokter"),
    ("dr_sinta",        "dokter"),
    ("ny_rahma",        "pasien"),
    ("ny_dewi",         "pasien"),
    ("ny_lestari",      "pasien"),
    ("ny_maya",         "pasien"),
    ("ny_fitri",        "pasien"),
]

# --- Unit peminta obat -------------------------------------------------------
UNIT_PEMINTA = [
    "Poli Kandungan",
    "Ruang Melati",
    "Ruang Anggrek",
    "IGD",
    "Kamar Bersalin",
    "Ruang Perinatologi",
    "Poli Anak",
    "Kamar Operasi",
]

KETERANGAN_RESEP = [
    "Kontrol kehamilan rutin",
    "Pasca persalinan normal",
    "Demam dan nyeri pasca operasi",
    "Infeksi saluran kemih",
    "Batuk pilek pada anak",
    "Suplemen kehamilan trimester II",
    "Mual muntah kehamilan",
    "Kontrol pasca sectio caesarea",
]

BUKTI_TERSEDIA = ["download.png", "images.jpeg", "IMG-20201118-WA0002.jpg"]


def lengkapi_obat():
    hari_ini = date.today()
    diubah = 0
    for nama, (kategori, satuan, harga, selisih_hari) in DETAIL_OBAT.items():
        obat = Obat.query.filter_by(nama=nama).first()
        if not obat:
            continue
        obat.kategori = kategori
        obat.satuan = satuan
        obat.harga = harga
        obat.tanggal_kadaluarsa = hari_ini + timedelta(days=selisih_hari)
        diubah += 1
    return diubah


def buat_user():
    dibuat = 0
    for username, nama_role in USERS:
        if User.query.filter_by(username=username).first():
            continue
        role = Role.query.filter_by(name=nama_role).first()
        if not role:
            role = Role(name=nama_role)
            db.session.add(role)
            db.session.flush()
        db.session.add(
            User(
                username=username,
                password=generate_password_hash(PASSWORD_DEMO),
                role_id=role.id,
            )
        )
        dibuat += 1
    return dibuat


def buat_permintaan(rng, obats):
    """Permintaan obat dari berbagai unit dengan status campuran.

    Catatan: permintaan berstatus 'disetujui' hanya mengurangi stok, TIDAK
    menambah baris penggunaan obat, agar deret data peramalan tetap sama
    dengan Bab IV.
    """
    if PermintaanObat.query.count():
        return 0

    hari_ini = date.today()
    dibuat = 0
    for i in range(24):
        obat = rng.choice(obats)
        jumlah = rng.randint(5, 40)
        status = rng.choices(
            ["menunggu", "disetujui", "ditolak"], weights=[4, 5, 1]
        )[0]

        if status == "disetujui":
            if obat.stok < jumlah:
                status = "menunggu"
            else:
                obat.stok -= jumlah

        db.session.add(
            PermintaanObat(
                nama_peminta=rng.choice(UNIT_PEMINTA),
                obat_id=obat.id,
                jumlah=jumlah,
                tanggal=hari_ini - timedelta(days=rng.randint(1, 60)),
                status=status,
                is_processed=(status != "menunggu"),
            )
        )
        dibuat += 1
    return dibuat


def buat_resep_dan_pembelian(rng):
    """Resep beserta pembeliannya.

    ResepItem ditautkan ke baris penggunaan obat yang SUDAH ADA (persis seperti
    alur pada halaman Resep), bukan membuat baris penggunaan baru.
    """
    if Resep.query.count():
        return 0, 0

    dokter = User.query.filter(User.role.has(name="dokter")).all()
    pasien = User.query.filter(User.role.has(name="pasien")).all()
    if not dokter or not pasien:
        return 0, 0

    # Ambil baris penggunaan terbaru yang belum tertaut ke resep mana pun
    kandidat = (
        PenggunaanObat.query.filter(~PenggunaanObat.resep_items.any())
        .order_by(PenggunaanObat.tanggal.desc())
        .limit(120)
        .all()
    )
    rng.shuffle(kandidat)

    resep_dibuat = 0
    pembelian_dibuat = 0
    urut = 0

    for i in range(10):
        if urut >= len(kandidat):
            break

        resep = Resep(
            dokter_id=rng.choice(dokter).id,
            pasien_id=rng.choice(pasien).id,
            tanggal=date.today() - timedelta(days=rng.randint(1, 45)),
            keterangan=KETERANGAN_RESEP[i % len(KETERANGAN_RESEP)],
        )
        db.session.add(resep)
        db.session.flush()

        for _ in range(rng.randint(1, 3)):
            if urut >= len(kandidat):
                break
            penggunaan = kandidat[urut]
            urut += 1
            db.session.add(
                ResepItem(
                    resep_id=resep.id,
                    penggunaan_id=penggunaan.id,
                    jumlah=rng.randint(1, 10),
                )
            )

        status = rng.choices(
            ["Belum dibayar", "Menunggu", "Sudah dibayar"], weights=[3, 2, 5]
        )[0]
        db.session.add(
            Pembelian(
                pasien_id=resep.pasien_id,
                resep_id=resep.id,
                bukti_pembayaran=(
                    rng.choice(BUKTI_TERSEDIA)
                    if status in ("Menunggu", "Sudah dibayar")
                    else None
                ),
                status=status,
            )
        )
        resep_dibuat += 1
        pembelian_dibuat += 1

    return resep_dibuat, pembelian_dibuat


def main():
    rng = random.Random(2024)  # dikunci agar hasilnya selalu sama

    app = create_app()
    with app.app_context():
        penggunaan_sebelum = PenggunaanObat.query.count()

        print("[1/4] Melengkapi kategori, satuan, harga dan kadaluarsa obat")
        n_obat = lengkapi_obat()

        print("[2/4] Membuat user contoh (petugas, dokter, pasien)")
        n_user = buat_user()
        db.session.flush()

        print("[3/4] Membuat data permintaan obat")
        obats = Obat.query.order_by(Obat.id).all()
        n_permintaan = buat_permintaan(rng, obats)

        print("[4/4] Membuat data resep dan pembelian")
        n_resep, n_pembelian = buat_resep_dan_pembelian(rng)

        db.session.commit()

        penggunaan_sesudah = PenggunaanObat.query.count()

    print("\n[SELESAI]")
    print(f"  Obat dilengkapi   : {n_obat}")
    print(f"  User dibuat       : {n_user}")
    print(f"  Permintaan dibuat : {n_permintaan}")
    print(f"  Resep dibuat      : {n_resep}")
    print(f"  Pembelian dibuat  : {n_pembelian}")
    print(
        f"  Penggunaan obat   : {penggunaan_sebelum} -> {penggunaan_sesudah} "
        f"({'TIDAK BERUBAH, hasil peramalan aman' if penggunaan_sebelum == penggunaan_sesudah else 'BERUBAH!'})"
    )
    if n_user:
        print(f"\n  Password semua user contoh: {PASSWORD_DEMO}")


if __name__ == "__main__":
    main()
