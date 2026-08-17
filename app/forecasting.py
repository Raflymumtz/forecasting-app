"""
Mesin peramalan Double Exponential Smoothing (Holt's linear method).

Seluruh rumus di modul ini dibuat identik dengan perhitungan pada file
"Data Lengkap Hasil Peramalan Persediaan Obat (Bab IV).xlsx", sheet
DES_<nama obat>, sehingga hasil aplikasi persis sama dengan hasil Bab IV:

    Level_t   = alpha * Aktual_t + (1 - alpha) * (Level_(t-1) + Tren_(t-1))
    Tren_t    = beta  * (Level_t - Level_(t-1)) + (1 - beta) * Tren_(t-1)
    Ramalan_t = Level_(t-1) + Tren_(t-1)

Inisialisasi mengikuti Excel: baris pertama deret (periode 0) dipakai sebagai
nilai awal L0, dan T0 = 0. Periode 1..n adalah periode yang diramalkan.

Evaluasi (MAD, MSE, MAPE) dihitung HANYA pada data uji, yaitu 20% periode
terakhir (Tabel 4.3: 84 minggu latih / 21 minggu uji dari 105 minggu).

Pencarian parameter memakai grid alpha x beta = 0,1 s.d. 0,9 (81 kombinasi),
dan kombinasi terbaik adalah yang menghasilkan MAPE terkecil pada data uji.
"""

from statistics import mean, stdev

# --- Konstanta yang mengikuti skripsi -------------------------------------

EXCEL_FILENAME = "Data Lengkap Hasil Peramalan Persediaan Obat (Bab IV).xlsx"
SHEET_DATA_MENTAH = "Data Mentah"

#: Nilai alpha/beta yang diuji (0,1 s.d. 0,9 -> 9 x 9 = 81 kombinasi)
GRID_VALUES = [round(i / 10, 1) for i in range(1, 10)]

#: Proporsi data uji (Tabel 4.3 - pembagian 80% latih : 20% uji)
TEST_RATIO = 0.2

#: Minimal jumlah periode agar peramalan layak dihitung
MIN_PERIODE = 5

#: Tabel 2.1 - kategori nilai MAPE (Lewis, 1982)
KATEGORI_MAPE = [
    (10, "Sangat Baik"),
    (20, "Baik"),
    (50, "Cukup"),
    (float("inf"), "Buruk"),
]


def kategori_mape(mape):
    """Mengembalikan kategori MAPE sesuai Tabel 2.1."""
    if mape is None:
        return "-"
    for batas, label in KATEGORI_MAPE:
        if mape < batas:
            return label
    return "Buruk"


# --- Perhitungan inti ------------------------------------------------------


def hitung_des(nilai, alpha, beta):
    """Menghitung tabel DES lengkap untuk satu deret nilai.

    ``nilai[0]`` diperlakukan sebagai periode 0 (nilai awal L0), sama seperti
    baris 26/12/2022 pada sheet "Data Mentah".

    Mengembalikan ``(baris, level_akhir, tren_akhir)`` dengan ``baris`` berisi
    satu dict per periode (termasuk periode 0).
    """
    level = float(nilai[0])
    tren = 0.0

    baris = [
        {
            "periode": 0,
            "aktual": nilai[0],
            "level": level,
            "tren": tren,
            "ramalan": None,
            "error": None,
            "abs_error": None,
            "sq_error": None,
            "ape": None,
        }
    ]

    for t in range(1, len(nilai)):
        aktual = float(nilai[t])
        ramalan = level + tren

        level_sebelumnya = level
        level = alpha * aktual + (1 - alpha) * (level + tren)
        tren = beta * (level - level_sebelumnya) + (1 - beta) * tren

        error = aktual - ramalan
        baris.append(
            {
                "periode": t,
                "aktual": nilai[t],
                "level": level,
                "tren": tren,
                "ramalan": ramalan,
                "error": error,
                "abs_error": abs(error),
                "sq_error": error ** 2,
                "ape": abs(error / aktual) * 100 if aktual else None,
            }
        )

    return baris, level, tren


def jumlah_data_uji(jumlah_periode):
    """Banyaknya periode yang masuk data uji (20% terakhir, minimal 1)."""
    n_uji = int(round(jumlah_periode * TEST_RATIO))
    n_uji = max(1, min(n_uji, jumlah_periode - 1))
    return n_uji


def evaluasi(baris, n_uji):
    """MAD, MSE dan MAPE dihitung pada ``n_uji`` periode terakhir."""
    uji = [b for b in baris if b["ramalan"] is not None][-n_uji:]
    if not uji:
        return None, None, None

    mad = sum(b["abs_error"] for b in uji) / len(uji)
    mse = sum(b["sq_error"] for b in uji) / len(uji)
    ape = [b["ape"] for b in uji if b["ape"] is not None]
    mape = sum(ape) / len(ape) if ape else None
    return mad, mse, mape


def grid_search(nilai, n_uji=None):
    """Menguji seluruh 81 kombinasi alpha x beta.

    Mengembalikan ``(kombinasi, terbaik)``; ``kombinasi`` adalah daftar dict
    berisi alpha, beta, MAD, MSE dan MAPE untuk setiap kombinasi, dan
    ``terbaik`` adalah kombinasi dengan MAPE terkecil.
    """
    n_periode = len(nilai) - 1
    if n_uji is None:
        n_uji = jumlah_data_uji(n_periode)

    kombinasi = []
    terbaik = None

    for alpha in GRID_VALUES:
        for beta in GRID_VALUES:
            baris, level, tren = hitung_des(nilai, alpha, beta)
            mad, mse, mape = evaluasi(baris, n_uji)
            if mape is None:
                continue

            item = {
                "alpha": alpha,
                "beta": beta,
                "mad": mad,
                "mse": mse,
                "mape": mape,
                "terbaik": False,
            }
            kombinasi.append(item)

            if terbaik is None or mape < terbaik["mape"] - 1e-12:
                terbaik = item

    if terbaik is not None:
        terbaik["terbaik"] = True

    return kombinasi, terbaik


def proyeksi(level, tren, n_periode_kedepan):
    """Ramalan m periode ke depan: Ramalan_(n+m) = Level_n + m * Tren_n."""
    return [max(0.0, level + (m + 1) * tren) for m in range(n_periode_kedepan)]


def statistik_deskriptif(nilai_periode):
    """Statistik deskriptif seperti Tabel 4.1 (tanpa baris periode 0)."""
    if not nilai_periode:
        return None
    return {
        "n": len(nilai_periode),
        "min": min(nilai_periode),
        "maks": max(nilai_periode),
        "rata": mean(nilai_periode),
        "std": stdev(nilai_periode) if len(nilai_periode) > 1 else 0.0,
    }


# --- Orkestrasi ------------------------------------------------------------


def jalankan_peramalan(tanggal, nilai, n_periode_kedepan=4):
    """Menjalankan seluruh alur Bab IV untuk satu obat.

    ``tanggal`` dan ``nilai`` harus terurut menaik dan memiliki panjang sama.
    Elemen pertama adalah periode 0 (nilai awal L0).

    Mengembalikan dict berisi statistik deskriptif, pembagian data, hasil grid
    search, tabel DES pada parameter terbaik, evaluasi, dan proyeksi.
    """
    n_periode = len(nilai) - 1
    if n_periode < MIN_PERIODE:
        return None

    n_uji = jumlah_data_uji(n_periode)
    n_latih = n_periode - n_uji

    kombinasi, terbaik = grid_search(nilai, n_uji)
    if terbaik is None:
        return None

    baris, level, tren = hitung_des(nilai, terbaik["alpha"], terbaik["beta"])
    mad, mse, mape = evaluasi(baris, n_uji)

    # Sisipkan tanggal dan penanda latih/uji ke setiap baris tabel DES
    for b in baris:
        b["tanggal"] = tanggal[b["periode"]]
        if b["periode"] == 0:
            b["kelompok"] = "Awal (L0)"
        elif b["periode"] <= n_latih:
            b["kelompok"] = "Latih"
        else:
            b["kelompok"] = "Uji"

    nilai_ramalan = proyeksi(level, tren, n_periode_kedepan)

    # Perkiraan jarak antar periode untuk membuat tanggal masa depan
    selisih = [
        (tanggal[i + 1] - tanggal[i]).days
        for i in range(len(tanggal) - 1)
        if (tanggal[i + 1] - tanggal[i]).days > 0
    ]
    selisih.sort()
    langkah = selisih[len(selisih) // 2] if selisih else 7

    from datetime import timedelta

    proyeksi_data = [
        {
            "periode": n_periode + m + 1,
            "tanggal": tanggal[-1] + timedelta(days=langkah * (m + 1)),
            "ramalan": nilai_ramalan[m],
        }
        for m in range(n_periode_kedepan)
    ]

    nilai_periode = [float(v) for v in nilai[1:]]

    return {
        "deskriptif": statistik_deskriptif(nilai_periode),
        "pembagian": {
            "n_total": n_periode,
            "n_latih": n_latih,
            "n_uji": n_uji,
            "persen_latih": round(n_latih / n_periode * 100),
            "persen_uji": round(n_uji / n_periode * 100),
            "periode_latih": f"1 - {n_latih}",
            "periode_uji": f"{n_latih + 1} - {n_periode}",
            "tanggal_latih": f"{tanggal[1]:%d/%m/%Y} - {tanggal[n_latih]:%d/%m/%Y}",
            "tanggal_uji": f"{tanggal[n_latih + 1]:%d/%m/%Y} - {tanggal[-1]:%d/%m/%Y}",
        },
        "alpha": terbaik["alpha"],
        "beta": terbaik["beta"],
        "mad": mad,
        "mse": mse,
        "mape": mape,
        "kategori": kategori_mape(mape),
        "level_akhir": level,
        "tren_akhir": tren,
        "l0": float(nilai[0]),
        "t0": 0.0,
        "baris": baris,
        "kombinasi": kombinasi,
        "proyeksi": proyeksi_data,
        "prediksi_berikutnya": nilai_ramalan[0] if nilai_ramalan else None,
        "n_periode_kedepan": n_periode_kedepan,
    }


# --- Pembacaan file Excel sumber ------------------------------------------


def baca_data_mentah(path=EXCEL_FILENAME):
    """Membaca sheet "Data Mentah" dari file Excel Bab IV.

    Mengembalikan ``(daftar_tanggal, {nama_obat: [nilai, ...]})``.
    """
    from datetime import datetime

    import openpyxl

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[SHEET_DATA_MENTAH]
    baris = list(ws.iter_rows(values_only=True))

    # Cari baris header (kolom pertama "No.")
    idx_header = next(
        i for i, r in enumerate(baris) if r and str(r[0]).strip() == "No."
    )
    nama_obat = [n for n in baris[idx_header][2:] if n]

    tanggal = []
    series = {n: [] for n in nama_obat}
    for r in baris[idx_header + 1 :]:
        if r[0] is None or r[1] is None:
            continue
        nilai_tanggal = r[1]
        if isinstance(nilai_tanggal, datetime):
            tanggal.append(nilai_tanggal.date())
        else:
            tanggal.append(datetime.strptime(str(nilai_tanggal), "%d/%m/%Y").date())
        for i, n in enumerate(nama_obat):
            series[n].append(int(r[2 + i]))

    wb.close()
    return tanggal, series
