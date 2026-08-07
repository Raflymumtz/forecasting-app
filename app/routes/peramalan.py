from flask import Blueprint, render_template, request
from app.models import Obat, PenggunaanObat
from app import db
from sqlalchemy import func
import pandas as pd
from datetime import datetime
import numpy as np

bp = Blueprint("peramalan", __name__, url_prefix="/peramalan")

MIN_DATA_POINTS = 5  # jumlah data minimum agar hasil peramalan cukup diandalkan

@bp.route("/", methods=["GET", "POST"])
def index():
    hasil = None
    hasil_data = []
    hasil_forecast = None
    selected_obat_id = None
    n_weeks = 4

    # Ambil daftar obat yang punya data penggunaan
    obats = (
        db.session.query(Obat)
        .join(PenggunaanObat)
        .group_by(Obat.id)
        .having(func.count(PenggunaanObat.id) > 2)
        .all()
    )

    if request.method == "POST":
        obat_id = request.form["obat_id"]
        selected_obat_id = int(obat_id)
        n_weeks = max(1, min(52, int(request.form.get("n_weeks", 4) or 4)))

        data = PenggunaanObat.query.filter_by(obat_id=obat_id).order_by(PenggunaanObat.tanggal).all()

        if len(data) >= 2:
            df = pd.DataFrame([(d.tanggal, d.jumlah) for d in data], columns=["tanggal", "jumlah"])
            df["tanggal"] = pd.to_datetime(df["tanggal"])
            df.sort_values("tanggal", inplace=True)

            y = df["jumlah"].values
            tanggal = df["tanggal"].dt.strftime('%Y-%m-%d').tolist()

            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            from sklearn.metrics import mean_absolute_error, mean_squared_error

            best_mape = float('inf')
            best_model = None

            # Cari kombinasi alpha dan beta terbaik
            for alpha in np.arange(0.1, 1.1, 0.1):
                for beta in np.arange(0.1, 1.1, 0.1):
                    try:
                        model = ExponentialSmoothing(y, trend='add', seasonal=None)
                        fitted = model.fit(smoothing_level=alpha, smoothing_trend=beta, optimized=False)
                        fits = fitted.fittedvalues
                        mape = np.mean(np.abs((y - fits) / y)) * 100
                        if mape < best_mape:
                            best_model = fitted
                            best_fits = fits
                            best_alpha = alpha
                            best_beta = beta
                            best_mape = mape
                    except:
                        continue

            # Peramalan N minggu ke depan
            forecast_values = np.asarray(best_model.forecast(n_weeks)).flatten()
            forecast_values = np.clip(forecast_values, 0, None)  # stok tidak mungkin negatif
            mad = mean_absolute_error(y, best_fits)
            msd = mean_squared_error(y, best_fits)

            # Perkirakan interval antar data (default mingguan) untuk membuat tanggal masa depan
            last_date = df["tanggal"].max()
            deltas = df["tanggal"].diff().dropna()
            deltas = deltas[deltas > pd.Timedelta(0)]  # abaikan entri dengan tanggal duplikat
            step = deltas.median() if not deltas.empty else pd.Timedelta(weeks=1)
            if pd.isna(step) or step <= pd.Timedelta(0):
                step = pd.Timedelta(weeks=1)

            forecast_dates = [(last_date + step * (i + 1)).strftime('%Y-%m-%d') for i in range(n_weeks)]
            forecast_data = [
                {"tanggal": d, "jumlah": round(float(v), 2)}
                for d, v in zip(forecast_dates, forecast_values)
            ]

            # Susun hasil (urutan kronologis, dipakai untuk grafik & tabel)
            hasil_data = [{
                "tanggal": t,
                "jumlah": int(j),
                "S1": float(s)
            } for t, j, s in zip(tanggal, y, best_fits)]

            hasil = {
                "obat": Obat.query.get(obat_id).nama,
                "forecast": forecast_data[0]["jumlah"],
                "alpha": round(best_alpha, 2),
                "beta": round(best_beta, 2),
                "mape": round(best_mape, 2),
                "mad": round(mad, 2),
                "msd": round(msd, 2),
                "data": hasil_data,
                "forecast_data": forecast_data,
                "n_weeks": n_weeks,
                "low_data": len(data) < MIN_DATA_POINTS
            }

            hasil_forecast = hasil["forecast"]

    return render_template(
        "peramalan.html",
        obats=obats,
        hasil=hasil,
        hasil_data=hasil_data,
        hasil_forecast=hasil_forecast,
        selected_obat_id=selected_obat_id,
        n_weeks=n_weeks
    )
