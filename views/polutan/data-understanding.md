---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Data Understanding
## Data Collection
Langkah pertama dalam proyek ini adalah mengumpulkan data polutan udara (seperti NO₂, CO, SO₂, dan O₃) yang bertipe deret waktu (_Time Series_). Dataset ini diambil dari platform satelit [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/).

Buat akun terlebih dahulu di website Copernicus agar bisa melakukan crawling data menggunakan library openEO.

### Install Library

Untuk melakukan proses crawling data, kita membutuhkan pustaka Python pendukung yaitu `openeo` untuk berkomunikasi dengan API Copernicus, dan `netCDF4` untuk membaca format data cuaca spasial (`.nc`).

```bash
pip install openeo
pip install netCDF4
```

### Autentikasi dan Pengambilan Data

Skrip di bawah ini melakukan proses autentikasi untuk menghubungkan sistem lokal kita dengan server Copernicus menggunakan _device code flow_.

```python
import openeo

connection = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()
```

Saat menjalankan baris di atas, akan muncul permintaan autentikasi:

```
Visit (link authentikasi) 📋 to authenticate.
✅ Authorized successfully
Authenticated using device code flow.
```

Klik link autentikasi lalu login menggunakan akun Copernicus.

### Definisi Area dan Pengambilan Data NO₂, SO₂, O₃ dan CO dari geojson

Setelah berhasil masuk, langkah selanjutnya adalah menentukan wilayah spesifik. Titik koordinat batas wilayah Nganjuk (Poligon) didapatkan menggunakan alat bantu pemetaan [geojson.io](https://geojson.io) dengan menggambar kotak di atas wilayah yang diinginkan kemudian menyalin koordinatnya.

![Grafik Data](../../img/polutan/geojson.png)

Koordinat yang didapatkan dimasukkan ke dalam variabel `aoi` (Area of Interest). Satelit Sentinel-5P kemudian diminta untuk mengambil data polutan berdasarkan _bounding box_ wilayah tersebut dengan menyesuaikan variabel `s5post` atribut `bands`. 

Karena satelit mungkin merekam area yang sama beberapa kali, dilakukan **agregasi temporal harian** agar hanya terdapat rata-rata satu data per hari. Dilanjutkan dengan **agregasi spasial** agar seluruh _grid_ pada wilayah Nganjuk dirata-rata menjadi satu nilai tunggal.

```python
aoi = {
    "type": "Polygon",
    # Paste koordinat yang didapat 
    "coordinates": [
        [
            [111.80, -7.40],
            [112.10, -7.40],
            [112.10, -7.70],
            [111.80, -7.70],
            [111.80, -7.40],
        ]
    ]
}

s5post = connection.load_collection(
    "SENTINEL_5P_L2",
    temporal_extent=["2025-08-25", "2026-08-25"],
    spatial_extent={
        "west": 111.80,
        "south": -7.70,
        "east": 112.10,
        "north": -7.40
    },
    # Disesuaikan dengan data yang dibutuhkan
    bands=["NO2"],
)

# Agregasi harian agar tidak ada lebih dari satu data per hari
s5p_no2_daily = s5post.aggregate_temporal_period(reducer="mean", period="day")

# Agregasi spasial untuk menghasilkan rata-rata time series per AOI
s5p_no2_aoi = s5p_no2_daily.aggregate_spatial(reducer="mean", geometries=aoi)

# Simpan hasil sebagai CSV
result = s5p_no2_aoi.save_result(format="CSV")

# Jalankan job
job = result.create_job(title="s5p_no2_timeseries")
job.start_and_wait()

# Download
job.get_results().download_files("output_no2")
```

Tunggu proses selesai. Status dan progres eksekusi bisa dipantau di [openEO editor](https://editor.openeo.org/?server=https%3A%2F%2Fopeneo.dataspace.copernicus.eu%2Fopeneo%2F1.2). Setelah diproses oleh server, output akan otomatis diunduh berupa file NetCDF **`NO2DiNganjuk.nc`**.

![Grafik Data](../../img/polutan/editor.png)

```
0:00:00 Job 'j-2608250945264132925ebef4140e0037': send 'start'
0:00:03 Job 'j-2608250945264132925ebef4140e0037': queued (progress 0%)
0:00:08 Job 'j-2608250945264132925ebef4140e0037': queued (progress 0%)
0:00:15 Job 'j-2608250945264132925ebef4140e0037': queued (progress 0%)
0:00:23 Job 'j-2608250945264132925ebef4140e0037': queued (progress 0%)
0:00:33 Job 'j-2608250945264132925ebef4140e0037': queued (progress 0%)
0:00:46 Job 'j-2608250945264132925ebef4140e0037': running (progress N/A)
0:01:02 Job 'j-2608250945264132925ebef4140e0037': running (progress N/A)
0:01:21 Job 'j-2608250945264132925ebef4140e0037': running (progress N/A)
0:01:45 Job 'j-2608250945264132925ebef4140e0037': running (progress N/A)
0:02:16 Job 'j-2608250945264132925ebef4140e0037': running (progress N/A)
0:02:53 Job 'j-2608250945264132925ebef4140e0037': running (progress N/A)
0:03:40 Job 'j-2608250945264132925ebef4140e0037': finished (progress 100%)
```

### Hasil CSV
Pada tahap terakhir, kita memuat file CSV (O₃, SO₂, CO dan NO₂) yang telah dirapikan menggunakan pustaka Pandas. Data ini sekarang sudah terstruktur sebagai dataset _Time Series_ dan siap digunakan untuk analisis lanjutan. Berikut adalah cuplikan data tersebut:

1. CO

```{code-cell}
:tags: [hide-input]
import pandas as pd
import numpy as np
df = pd.read_csv("../../data/polutan/CO.csv")
df.head(5)
```

2. SO2

```{code-cell}
:tags: [hide-input]
df = pd.read_csv("../../data/polutan/SO2.csv")
df.head(5)
```

3. NO 2

```{code-cell}
:tags: [hide-input]
df = pd.read_csv("../../data/polutan/NO2.csv")
df.head(5)
```

4. O₃

```{code-cell}
:tags: [hide-input]
df = pd.read_csv("../../data/polutan/O3.csv")
df.head(5)
```

### Normalisasi Tanggal

Data waktu (tanggal) yang diperoleh dari Copernicus menyertakan zona waktu yang tidak diperlukan. Oleh karena itu, kita perlu menormalisasinya menjadi format standar yang seragam yaitu `YYYY-MM-DD` agar lebih mudah diolah. Berikut adalah kode yang digunakan untuk menyeragamkan format tanggal:
```python
import pandas as pd

df = pd.read_csv("SO2.csv")

# pastikan kolom tanggal valid
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# ambil hanya bulan dan tahun
df["date"] = df["date"].dt.strftime("%Y-%m-%d")

new_df = pd.DataFrame({
    "date": df['date'],
    "SO2": df['SO2']
})

new_df.to_csv("SO2_Timeseries.csv", index=False)
```
Setelah proses normalisasi dilakukan pada seluruh dataset polutan, format waktu pada dataset menjadi lebih rapi dan konsisten. Berikut adalah cuplikan dataset setelah tanggal dinormalisasi:


1. CO

```{code-cell}
:tags: [hide-input]
import pandas as pd
import numpy as np
df = pd.read_csv("../../data/polutan/CO_Timeseries.csv")
df.head(5)
```

2. SO2

```{code-cell}
:tags: [hide-input]
df = pd.read_csv("../../data/polutan/SO2_Timeseries.csv")
df.head(5)
```

3. NO 2

```{code-cell}
:tags: [hide-input]
df = pd.read_csv("../../data/polutan/NO2_Timeseries.csv")
df.head(5)
```

4. O₃

```{code-cell}
:tags: [hide-input]
df = pd.read_csv("../../data/polutan/O3_Timeseries.csv")
df.head(5)
```
## Missing Values

_Missing values_ (nilai yang hilang) adalah kondisi di mana terdapat informasi yang kosong atau tidak terekam dalam dataset. Pada kasus data deret waktu yang diambil menggunakan satelit, kekosongan data ini wajar terjadi, biasanya akibat faktor cuaca (area tertutup awan tebal sehingga sensor tidak dapat membaca permukaan bumi) atau karena orbit satelit yang tidak merekam area tersebut pada hari tertentu. Mengidentifikasi keberadaan _missing values_ sangat penting sebelum melakukan analisis lebih lanjut.

Pada proyek ini, kita mengecek dua bentuk _missing values_:
1. **Tanggal yang Hilang**: Memastikan apakah ada urutan hari yang terlewat (bolong) dari rentang waktu awal hingga akhir (25 Agustus 2025 - 25 Agustus 2026).
2. **Data yang Hilang**: Memeriksa jumlah nilai polutan yang kosong (`NaN`) pada record tanggal yang sudah terekam.

### Tanggal Yang Hilang
1. CO

```{code-cell}
import pandas as pd

df = pd.read_csv("../../data/polutan/CO_Timeseries.csv")
df['date'] = pd.to_datetime(df['date'])

# Buat rentang tanggal lengkap
start_date = "2025-08-25"
end_date   = "2026-08-25"
full_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Cek tanggal yang hilang
missing_dates = full_range.difference(df['date'])

print(f"Jumlah hari missing: {len(missing_dates)}")
print("Daftar tanggal missing:")
print(missing_dates)
```

2. SO2

```{code-cell}
import pandas as pd

df = pd.read_csv("../../data/polutan/SO2_Timeseries.csv")
df['date'] = pd.to_datetime(df['date'])

# Buat rentang tanggal lengkap
start_date = "2025-08-25"
end_date   = "2026-08-25"
full_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Cek tanggal yang hilang
missing_dates = full_range.difference(df['date'])

print(f"Jumlah hari missing: {len(missing_dates)}")
print("Daftar tanggal missing:")
print(missing_dates)
```

3. NO₂

```{code-cell}
import pandas as pd

df = pd.read_csv("../../data/polutan/NO2_Timeseries.csv")
df['date'] = pd.to_datetime(df['date'])

# Buat rentang tanggal lengkap
start_date = "2025-08-25"
end_date   = "2026-08-25"
full_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Cek tanggal yang hilang
missing_dates = full_range.difference(df['date'])

print(f"Jumlah hari missing: {len(missing_dates)}")
print("Daftar tanggal missing:")
print(missing_dates)
```

4. O₃

```{code-cell}
import pandas as pd

df = pd.read_csv("../../data/polutan/O3_Timeseries.csv")
df['date'] = pd.to_datetime(df['date'])

# Buat rentang tanggal lengkap
start_date = "2025-08-25"
end_date   = "2026-08-25"
full_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Cek tanggal yang hilang
missing_dates = full_range.difference(df['date'])

print(f"Jumlah hari missing: {len(missing_dates)}")
print("Daftar tanggal missing:")
print(missing_dates)
```

### Data Yang Hilang

Selain urutan tanggal, kita juga mengecek jumlah baris data yang memiliki nilai konsentrasi polutan kosong (`NaN`).

1. CO

```{code-cell}
df = pd.read_csv("../../data/polutan/CO_Timeseries.csv")
missing_value = df['CO'].isna().sum()
print(missing_value)
```

Implementasi pada tools `Orange Data Mining`
```{image} ../../img/polutan/co_missing.png
:alt: Grafik Data
:width: 100%
:align: center
```

2. SO₂

```{code-cell}
df = pd.read_csv("../../data/polutan/SO2_Timeseries.csv")
missing_value = df['SO2'].isna().sum()
print(missing_value)
```

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/polutan/so2_missing.png
:alt: Grafik Data
:width: 100%
:align: center
```

3. NO₂

```{code-cell}
df = pd.read_csv("../../data/polutan/NO2_Timeseries.csv")
missing_value = df['NO2'].isna().sum()
print(missing_value)
```

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/polutan/no2_missing.png
:alt: Grafik Data
:width: 100%
:align: center
```

4. O₃

```{code-cell}
df = pd.read_csv("../../data/polutan/O3_Timeseries.csv")
missing_value = df['O3'].isna().sum()
print(missing_value)
```

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/polutan/o3_missing.png
:alt: Grafik Data
:width: 100%
:align: center
```

## Outliers

_Outliers_ (pencilan) adalah titik data yang nilainya menyimpang secara drastis atau ekstrem dari mayoritas distribusi data lainnya. Pada data deret waktu kualitas udara, _outlier_ bisa jadi merupakan lonjakan polusi nyata yang terjadi akibat peristiwa tertentu (misalnya kebakaran hutan atau peningkatan aktivitas industri mendadak), atau bisa juga sekadar _noise_ / _error_ pada pembacaan sensor satelit.

Pada tahap _data understanding_ ini, kita mengeksplorasi _outliers_ menggunakan algoritma **Isolation Forest** dari pustaka `scikit-learn`. Algoritma deteksi anomali ini bekerja dengan cara "mengisolasi" observasi melalui pemisahan data secara acak, di mana anomali akan lebih cepat/mudah diisolasi. Kita mengatur parameter _contamination_ (estimasi persentase _outlier_ di dalam dataset) sebesar 5%. Hasil prediksi dari model yang bernilai `-1` menandakan bahwa baris tersebut terdeteksi sebagai _outlier_.

1. CO

```{code-cell}
import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../../data/polutan/CO_Timeseries.csv")
df_clean = df.dropna(subset=['CO']).copy()

model = IsolationForest(contamination=0.05, random_state=42) # contamination 0.05 = 5%
pred = model.fit_predict(df_clean[['CO']])

# Nilai -1 merepresentasikan outlier
jumlah_outlier = (pred == -1).sum()
print("Jumlah outlier:", jumlah_outlier)
```

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/polutan/co_outliers.png
:alt: Grafik Data
:width: 100%
:align: center
```

2. SO₂

```{code-cell}
import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../../data/polutan/SO2_Timeseries.csv")
df_clean = df.dropna(subset=['SO2']).copy()

model = IsolationForest(contamination=0.05, random_state=42) # contamination 0.05 = 5%
pred = model.fit_predict(df_clean[['SO2']])

# Nilai -1 merepresentasikan outlier
jumlah_outlier = (pred == -1).sum()
print("Jumlah outlier:", jumlah_outlier)
```

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/polutan/so2_outliers.png
:alt: Grafik Data
:width: 100%
:align: center
```

3. NO₂

```{code-cell}
import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../../data/polutan/NO2_Timeseries.csv")
df_clean = df.dropna(subset=['NO2']).copy()

model = IsolationForest(contamination=0.05, random_state=42) # contamination 0.05 = 5%
pred = model.fit_predict(df_clean[['NO2']])

# Nilai -1 merepresentasikan outlier
jumlah_outlier = (pred == -1).sum()
print("Jumlah outlier:", jumlah_outlier)
```

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/polutan/no2_outliers.png
:alt: Grafik Data
:width: 100%
:align: center
```

4. O₃

```{code-cell}
import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../../data/polutan/O3_Timeseries.csv")
df_clean = df.dropna(subset=['O3']).copy()

model = IsolationForest(contamination=0.05, random_state=42) # contamination 0.05 = 5%
pred = model.fit_predict(df_clean[['O3']])

# Nilai -1 merepresentasikan outlier
jumlah_outlier = (pred == -1).sum()
print("Jumlah outlier:", jumlah_outlier)
```

Implementasi pada tools `Orange Data Mining`

```{image} ../../img/polutan/o3_outliers.png
:alt: Grafik Data
:width: 100%
:align: center
```
