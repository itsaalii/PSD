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

# Data Preprocessing dan Ekstraksi Fitur (Interpolasi Linear)

## Preprocessing: Penanganan Outliers dan Interpolasi Linear

Pada tahap _Data Understanding_, kita telah mengidentifikasi adanya kemungkinan nilai _outliers_ pada deret waktu. Untuk menangani permasalahan ini dan mempersiapkan data agar bisa diekstrak fiturnya secara mulus, kita menerapkan pembersihan data secara **iteratif** menggunakan metode Rentang Interkuartil (IQR) dan mengisi (imputasi) kekosongan data menggunakan **interpolasi linier**. 

**Mengapa Interpolasi Linier?**
Interpolasi linier sangat cocok untuk data deret waktu polutan udara karena metode ini bekerja dengan menarik "garis lurus" matematis untuk memperkirakan nilai yang hilang berdasarkan dua titik observasi terdekat yang valid (titik data sebelum dan titik sesudahnya). Melalui fungsi bawaan pandas (seperti `interpolate(method='linear')` maupun `method='time'`), kekosongan data akibat penghapusan _outlier_ dapat diisi secara proporsional dengan mengasumsikan perubahan konstan pada jarak waktu yang kosong. Hal ini efektif untuk menjaga keberlanjutan (_continuity_) tren temporal tanpa menghasilkan anomali baru pada sebaran data harian.

Proses deteksi outlier dan imputasi linier ini dijalankan secara berulang (dalam blok _loop_) hingga distribusi benar-benar bersih. Langkah iteratif ini diperlukan karena nilai baru dari hasil interpolasi terkadang dapat sedikit menggeser batas atas/bawah perhitungan IQR, sehingga deteksi tambahan dipastikan berjalan tuntas.

Di akhir proses imputasi, teknik _backward fill_ (`bfill`) serta _forward fill_ (`ffill`) dimanfaatkan guna mengatasi nilai kosong pada bagian pinggir atau awalan dan akhiran rangkaian data yang tidak bisa diinterpolasi secara linier karena tidak diapit oleh dua titik.

Berikut adalah tahapan deteksi outlier, imputasi, dan penyimpanan dataset untuk masing-masing polutan udara:

### 1. Karbon Monoksida (CO)

```{code-cell}
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("../../data/polutan-baron/CO.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)
df['CO'] = pd.to_numeric(df['CO'], errors='coerce')

# Hitung IQR
Q1 = df['CO'].quantile(0.25)
Q3 = df['CO'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Filter outlier
outliers_iqr = df[(df['CO'] < lower_bound) | (df['CO'] > upper_bound)]

print("Jumlah Outlier CO (IQR):", len(outliers_iqr))
```

Visualisasi batas ambang IQR terhadap distribusi data CO:

```{code-cell}
plt.figure(figsize=(15,5))
plt.plot(df['date'], df['CO'], label="CO", linewidth=1)

plt.scatter(outliers_iqr['date'], outliers_iqr['CO'],
            color='red', marker='o', label="Outliers")

plt.axhline(upper_bound, color='orange', linestyle='dashed', label="Upper Bound (IQR)")
plt.axhline(lower_bound, color='blue',   linestyle='dashed', label="Lower Bound (IQR)")

plt.title("Deteksi Outlier Data CO (Metode IQR)")
plt.xlabel("Tanggal")
plt.ylabel("Kadar CO")
plt.legend()
plt.tight_layout()
plt.xticks(
    ticks=[df['date'].iloc[0], df['date'].iloc[-1]],
    labels=[df['date'].iloc[0].strftime('%Y-%m-%d'),
            df['date'].iloc[-1].strftime('%Y-%m-%d')]
)
plt.show()
```

Penanganan outlier dan pengisian nilai yang hilang untuk **CO**:

```python
df['CO_filled'] = df['CO'].copy()

# Looping iteratif untuk membersihkan outlier sampai benar-benar habis
while True:
    # 1. Hitung ulang kuartil dan batas IQR berdasarkan data saat ini
    Q1 = df['CO_filled'].quantile(0.25)
    Q3 = df['CO_filled'].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # 2. Deteksi lokasi outlier
    outliers = (df['CO_filled'] < lower_bound) | (df['CO_filled'] > upper_bound)
    
    # Jika sudah tidak ada outlier yang terdeteksi, hentikan perulangan
    if not outliers.any():
        break
    
    # 3. Mask nilai outlier menjadi NaN, lalu isi dengan interpolasi linier + bfill + ffill
    df['CO_filled'] = df['CO_filled'].mask(outliers)
    df['CO_filled'] = df['CO_filled'].interpolate(method='linear').bfill().ffill()

# 4. Simpan hasil akhir ke DataFrame baru dan ekspor ke CSV
df_co = pd.DataFrame({"date": df['date'], "CO": df['CO_filled']})
df_co.to_csv("../../data/polutan-baron/CO_filed.csv", index=False)
print("Data CO berhasil diproses dan disimpan ke CO_filed.csv")
```

Visualisasi data CO setelah proses interpolasi (memastikan sudah tidak ada outlier):

```{code-cell}
df_co_final = pd.read_csv("../../data/polutan-baron/CO_filed.csv")
df_co_final['date'] = pd.to_datetime(df_co_final['date'])

Q1 = df_co_final['CO'].quantile(0.25)
Q3 = df_co_final['CO'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers_iqr = df_co_final[(df_co_final['CO'] < lower_bound) | (df_co_final['CO'] > upper_bound)]

plt.figure(figsize=(15,5))
plt.plot(df_co_final['date'], df_co_final['CO'], label="CO", linewidth=1)

plt.scatter(outliers_iqr['date'], outliers_iqr['CO'],
            color='red', marker='o', label="Outliers")

plt.axhline(upper_bound, color='orange', linestyle='dashed', label="Upper Bound (IQR)")
plt.axhline(lower_bound, color='blue',   linestyle='dashed', label="Lower Bound (IQR)")

plt.title("Visualisasi Data CO Setelah Interpolasi")
plt.xlabel("Tanggal")
plt.ylabel("Kadar CO")
plt.legend()
plt.tight_layout()
plt.xticks(
    ticks=[df_co_final['date'].iloc[0], df_co_final['date'].iloc[-1]],
    labels=[df_co_final['date'].iloc[0].strftime('%Y-%m-%d'),
            df_co_final['date'].iloc[-1].strftime('%Y-%m-%d')]
)
plt.show()
```

### 2. Sulfur Dioksida (SO2)

```{code-cell}
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("../../data/polutan-baron/SO2.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)
df['SO2'] = pd.to_numeric(df['SO2'], errors='coerce')

# Hitung IQR
Q1 = df['SO2'].quantile(0.25)
Q3 = df['SO2'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Filter outlier
outliers_iqr = df[(df['SO2'] < lower_bound) | (df['SO2'] > upper_bound)]

print("Jumlah Outlier SO2 (IQR):", len(outliers_iqr))
```

Visualisasi batas ambang IQR terhadap distribusi data SO2:

```{code-cell}
plt.figure(figsize=(15,5))
plt.plot(df['date'], df['SO2'], label="SO2", linewidth=1)

plt.scatter(outliers_iqr['date'], outliers_iqr['SO2'],
            color='red', marker='o', label="Outliers")

plt.axhline(upper_bound, color='orange', linestyle='dashed', label="Upper Bound (IQR)")
plt.axhline(lower_bound, color='blue',   linestyle='dashed', label="Lower Bound (IQR)")

plt.title("Deteksi Outlier Data SO2 (Metode IQR)")
plt.xlabel("Tanggal")
plt.ylabel("Kadar SO2")
plt.legend()
plt.tight_layout()
plt.xticks(
    ticks=[df['date'].iloc[0], df['date'].iloc[-1]],
    labels=[df['date'].iloc[0].strftime('%Y-%m-%d'),
            df['date'].iloc[-1].strftime('%Y-%m-%d')]
)
plt.show()
```

Penanganan outlier dan pengisian nilai yang hilang untuk **SO2**:

```python
df['SO2_filled'] = df['SO2'].copy()

# Looping iteratif untuk membersihkan outlier sampai benar-benar habis
while True:
    # 1. Hitung ulang kuartil dan batas IQR berdasarkan data saat ini
    Q1 = df['SO2_filled'].quantile(0.25)
    Q3 = df['SO2_filled'].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # 2. Deteksi lokasi outlier
    outliers = (df['SO2_filled'] < lower_bound) | (df['SO2_filled'] > upper_bound)
    
    # Jika sudah tidak ada outlier yang terdeteksi, hentikan perulangan
    if not outliers.any():
        break
    
    # 3. Mask nilai outlier menjadi NaN, lalu isi dengan interpolasi linier + bfill + ffill
    df['SO2_filled'] = df['SO2_filled'].mask(outliers)
    df['SO2_filled'] = df['SO2_filled'].interpolate(method='linear').bfill().ffill()

# 4. Simpan hasil akhir ke DataFrame baru dan ekspor ke CSV
df_so2 = pd.DataFrame({"date": df['date'], "SO2": df['SO2_filled']})
df_so2.to_csv("../../data/polutan-baron/SO2_filed.csv", index=False)
print("Data SO2 berhasil diproses dan disimpan ke SO2_filed.csv")
```

Visualisasi data SO2 setelah proses interpolasi (memastikan sudah tidak ada outlier):

```{code-cell}
df_so2_final = pd.read_csv("../../data/polutan-baron/SO2_filed.csv")
df_so2_final['date'] = pd.to_datetime(df_so2_final['date'])

Q1 = df_so2_final['SO2'].quantile(0.25)
Q3 = df_so2_final['SO2'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers_iqr = df_so2_final[(df_so2_final['SO2'] < lower_bound) | (df_so2_final['SO2'] > upper_bound)]

plt.figure(figsize=(15,5))
plt.plot(df_so2_final['date'], df_so2_final['SO2'], label="SO2", linewidth=1)

plt.scatter(outliers_iqr['date'], outliers_iqr['SO2'],
            color='red', marker='o', label="Outliers")

plt.axhline(upper_bound, color='orange', linestyle='dashed', label="Upper Bound (IQR)")
plt.axhline(lower_bound, color='blue',   linestyle='dashed', label="Lower Bound (IQR)")

plt.title("Visualisasi Data SO2 Setelah Interpolasi")
plt.xlabel("Tanggal")
plt.ylabel("Kadar SO2")
plt.legend()
plt.tight_layout()
plt.xticks(
    ticks=[df_so2_final['date'].iloc[0], df_so2_final['date'].iloc[-1]],
    labels=[df_so2_final['date'].iloc[0].strftime('%Y-%m-%d'),
            df_so2_final['date'].iloc[-1].strftime('%Y-%m-%d')]
)
plt.show()
```

### 3. Nitrogen Dioksida (NO2)

```{code-cell}
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("../../data/polutan-baron/NO2.csv")
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)
df['NO2'] = pd.to_numeric(df['NO2'], errors='coerce')

# Hitung IQR
Q1 = df['NO2'].quantile(0.25)
Q3 = df['NO2'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Filter outlier
outliers_iqr = df[(df['NO2'] < lower_bound) | (df['NO2'] > upper_bound)]

print("Jumlah Outlier NO2 (IQR):", len(outliers_iqr))
```

Visualisasi batas ambang IQR terhadap distribusi data NO2:

```{code-cell}
plt.figure(figsize=(15,5))
plt.plot(df['date'], df['NO2'], label="NO2", linewidth=1)

plt.scatter(outliers_iqr['date'], outliers_iqr['NO2'],
            color='red', marker='o', label="Outliers")

plt.axhline(upper_bound, color='orange', linestyle='dashed', label="Upper Bound (IQR)")
plt.axhline(lower_bound, color='blue',   linestyle='dashed', label="Lower Bound (IQR)")

plt.title("Deteksi Outlier Data NO2 (Metode IQR)")
plt.xlabel("Tanggal")
plt.ylabel("Kadar NO2")
plt.legend()
plt.tight_layout()
plt.xticks(
    ticks=[df['date'].iloc[0], df['date'].iloc[-1]],
    labels=[df['date'].iloc[0].strftime('%Y-%m-%d'),
            df['date'].iloc[-1].strftime('%Y-%m-%d')]
)
plt.show()
```

Penanganan outlier dan pengisian nilai yang hilang untuk **NO2**:

```python
df['NO2_filled'] = df['NO2'].copy()

# Looping iteratif untuk membersihkan outlier sampai benar-benar habis
while True:
    # 1. Hitung ulang kuartil dan batas IQR berdasarkan data saat ini
    Q1 = df['NO2_filled'].quantile(0.25)
    Q3 = df['NO2_filled'].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # 2. Deteksi lokasi outlier
    outliers = (df['NO2_filled'] < lower_bound) | (df['NO2_filled'] > upper_bound)
    
    # Jika sudah tidak ada outlier yang terdeteksi, hentikan perulangan
    if not outliers.any():
        break
    
    # 3. Mask nilai outlier menjadi NaN, lalu isi dengan interpolasi linier + bfill + ffill
    df['NO2_filled'] = df['NO2_filled'].mask(outliers)
    df['NO2_filled'] = df['NO2_filled'].interpolate(method='linear').bfill().ffill()

# 4. Simpan hasil akhir ke DataFrame baru dan ekspor ke CSV
df_no2 = pd.DataFrame({"date": df['date'], "NO2": df['NO2_filled']})
df_no2.to_csv("../../data/polutan-baron/NO2_filed.csv", index=False)
print("Data NO2 berhasil diproses dan disimpan ke NO2_filed.csv")
```

Visualisasi data NO2 setelah proses interpolasi (memastikan sudah tidak ada outlier):

```{code-cell}
df_no2_final = pd.read_csv("../../data/polutan-baron/NO2_filed.csv")
df_no2_final['date'] = pd.to_datetime(df_no2_final['date'])

Q1 = df_no2_final['NO2'].quantile(0.25)
Q3 = df_no2_final['NO2'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers_iqr = df_no2_final[(df_no2_final['NO2'] < lower_bound) | (df_no2_final['NO2'] > upper_bound)]

plt.figure(figsize=(15,5))
plt.plot(df_no2_final['date'], df_no2_final['NO2'], label="NO2", linewidth=1)

plt.scatter(outliers_iqr['date'], outliers_iqr['NO2'],
            color='red', marker='o', label="Outliers")

plt.axhline(upper_bound, color='orange', linestyle='dashed', label="Upper Bound (IQR)")
plt.axhline(lower_bound, color='blue',   linestyle='dashed', label="Lower Bound (IQR)")

plt.title("Visualisasi Data NO2 Setelah Interpolasi")
plt.xlabel("Tanggal")
plt.ylabel("Kadar NO2")
plt.legend()
plt.tight_layout()
plt.xticks(
    ticks=[df_no2_final['date'].iloc[0], df_no2_final['date'].iloc[-1]],
    labels=[df_no2_final['date'].iloc[0].strftime('%Y-%m-%d'),
            df_no2_final['date'].iloc[-1].strftime('%Y-%m-%d')]
)
plt.show()
```

### 4. Visualisasi Gabungan Setelah Preprocessing

Setelah proses penanganan *outlier* dan interpolasi selesai untuk ketiga polutan, kita dapat melihat visualisasi gabungan dari kadar CO, SO2, dan NO2 yang telah bersih dan utuh. Deret waktu ini telah siap untuk dilanjutkan ke tahap ekstraksi fitur.

```{code-cell}
import pandas as pd
import matplotlib.pyplot as plt

# Memuat data yang telah diproses
df_co = pd.read_csv("../../data/polutan-baron/CO_filed.csv")
df_so2 = pd.read_csv("../../data/polutan-baron/SO2_filed.csv")
df_no2 = pd.read_csv("../../data/polutan-baron/NO2_filed.csv")

df_co['date'] = pd.to_datetime(df_co['date'])
df_so2['date'] = pd.to_datetime(df_so2['date'])
df_no2['date'] = pd.to_datetime(df_no2['date'])

# Membuat subplot untuk ketiga polutan
fig, axes = plt.subplots(3, 1, figsize=(15, 10), sharex=True)

# Plot CO
axes[0].plot(df_co['date'], df_co['CO'], color='blue', linewidth=1)
axes[0].set_title('Kadar CO (Setelah Preprocessing)')
axes[0].set_ylabel('Kadar CO')
axes[0].grid(True, linestyle='--', alpha=0.6)

# Plot SO2
axes[1].plot(df_so2['date'], df_so2['SO2'], color='green', linewidth=1)
axes[1].set_title('Kadar SO2 (Setelah Preprocessing)')
axes[1].set_ylabel('Kadar SO2')
axes[1].grid(True, linestyle='--', alpha=0.6)

# Plot NO2
axes[2].plot(df_no2['date'], df_no2['NO2'], color='red', linewidth=1)
axes[2].set_title('Kadar NO2 (Setelah Preprocessing)')
axes[2].set_xlabel('Tanggal')
axes[2].set_ylabel('Kadar NO2')
axes[2].grid(True, linestyle='--', alpha=0.6)

# Menyesuaikan tampilan sumbu X
plt.xticks(
    ticks=[df_co['date'].iloc[0], df_co['date'].iloc[-1]],
    labels=[df_co['date'].iloc[0].strftime('%Y-%m-%d'),
            df_co['date'].iloc[-1].strftime('%Y-%m-%d')]
)

plt.tight_layout()
plt.show()
```

Selain divisualisasikan dalam subplot terpisah, kita juga dapat menumpuk (*overlay*) ketiga polutan dalam satu grafik untuk membandingkan fluktuasinya secara langsung. Karena skala kadar polutan mungkin berbeda, perbandingan ini difokuskan pada pengamatan pola tren perubahannya.

```{code-cell}
plt.figure(figsize=(15, 6))

# Plot ketiga polutan dalam satu axis
plt.plot(df_co['date'], df_co['CO'], color='blue', label='CO', linewidth=1, alpha=0.8)
plt.plot(df_so2['date'], df_so2['SO2'], color='green', label='SO2', linewidth=1, alpha=0.8)
plt.plot(df_no2['date'], df_no2['NO2'], color='red', label='NO2', linewidth=1, alpha=0.8)

plt.title('Perbandingan Fluktuasi Kadar CO, SO2, dan NO2 (Overlay)')
plt.xlabel('Tanggal')
plt.ylabel('Kadar Polutan')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()

# Menyesuaikan tampilan sumbu X
plt.xticks(
    ticks=[df_co['date'].iloc[0], df_co['date'].iloc[-1]],
    labels=[df_co['date'].iloc[0].strftime('%Y-%m-%d'),
            df_co['date'].iloc[-1].strftime('%Y-%m-%d')]
)

plt.tight_layout()
plt.show()
```

### 5. Penggabungan Data Polutan

Sebelum melakukan ekstraksi fitur, ada baiknya seluruh data polutan udara digabungkan ke dalam satu file dataset tunggal (`Polutan_Baron_linear.csv`). Hal ini akan memudahkan proses iterasi dan menghindari duplikasi kolom tanggal saat fitur diekstraksi sekaligus.

```{code-cell}
import pandas as pd

# Memuat data yang telah diproses
df_co = pd.read_csv("../../data/polutan-baron/CO_filed.csv")
df_no2 = pd.read_csv("../../data/polutan-baron/NO2_filed.csv")
df_so2 = pd.read_csv("../../data/polutan-baron/SO2_filed.csv")

dataframe_merged = pd.DataFrame({
    "date": df_no2['date'],
    "CO": df_co['CO'],
    "NO2": df_no2['NO2'],
    "SO2": df_so2['SO2']
})

dataframe_merged.to_csv("../../data/polutan-baron/Polutan_Baron_linear.csv", index=False)
print("Data polutan berhasil digabungkan dan disimpan ke Polutan_Baron_linear.csv")
```

## Ekstraksi Fitur Deret Waktu (Time Series)

Dengan data deret waktu polutan udara yang konsisten (tanpa tanggal hilang dan tanpa _outlier_), kita dapat melangkah ke ekstraksi berbagai fitur statistik, temporal, maupun spektral. Fitur-fitur ini sangat berguna sebagai parameter *input* yang merepresentasikan karakteristik *trend* harian polutan ke dalam model _machine learning_ maupun _deep learning_.

Kita akan memanfaatkan modul pustaka Python bernama `tsfel` (_Time Series Feature Extraction Library_) guna mempermudah proses komputasi serta standarisasi ragam tipe fitur. Ekstraksi dilakukan secara *looping* untuk seluruh polutan yang ada di dalam dataset gabungan (`Polutan_Baron_linear.csv`). 

Untuk memastikan hasil ekstraksi bersih dan aman dari error, pada setiap iterasi polutan data akan kembali difilter dari outlier dan diinterpolasi ulang menggunakan metode `time` sebelum dilakukan komputasi fitur. Seluruh fitur dari ketiga polutan (3 × 68 = 204 fitur) kemudian digabung dalam satu baris.

```python
import pandas as pd
import numpy as np
import inspect
import tsfel.feature_extraction.features as tsfel_features

# ---------- 1. Muat 1 file CSV utama yang berisi semua polutan ----------
df = pd.read_csv('../../data/polutan-baron/Polutan_Baron_linear.csv')

df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)

pollutants = ['NO2', 'SO2', 'CO']
fs = 1

# ---------- 2. Daftar 68 Fitur TSFEL ----------
FEATURE_LIST = """abs_energy auc autocorr average_power calc_centroid calc_max calc_mean
calc_median calc_min calc_std calc_var dfa distance ecdf ecdf_percentile ecdf_percentile_count
ecdf_slope entropy fundamental_frequency higuchi_fractal_dimension hist_mode human_range_energy
hurst_exponent interq_range kurtosis lempel_ziv lpcc max_frequency max_power_spectrum
maximum_fractal_length mean_abs_deviation mean_abs_diff mean_diff median_abs_deviation
median_abs_diff median_diff median_frequency mfcc mse negative_turning neighbourhood_peaks
petrosian_fractal_dimension pk_pk_distance positive_turning power_bandwidth rms skewness slope
spectral_centroid spectral_decrease spectral_distance spectral_entropy spectral_kurtosis
spectral_positive_turning spectral_roll_off spectral_roll_on spectral_skewness spectral_slope
spectral_spread spectral_variation spectrogram_mean_coeff sum_abs_diff wavelet_abs_mean
wavelet_energy wavelet_entropy wavelet_std wavelet_var zero_cross""".split()

print(f"Jumlah fitur per polutan: {len(FEATURE_LIST)}")
print(f"Total target fitur keseluruhan: {len(FEATURE_LIST) * len(pollutants)}")

# ---------- 3. Fungsi ekstraksi dan penyeragaman output  ----------
def to_scalar(result):
    if isinstance(result, dict) and "values" in result:
        result = result["values"]
    if isinstance(result, (list, tuple, np.ndarray)):
        arr = np.asarray(result, dtype=float)
        return float(np.nanmean(arr))
    return float(result)

def extract_one(fn_name, signal, fs):
    fn = getattr(tsfel_features, fn_name)
    params = inspect.signature(fn).parameters
    if "fs" in params:
        result = fn(signal, fs)
    else:
        result = fn(signal)
    return to_scalar(result)

# Dictionary untuk menampung seluruh hasil ekstraksi
combined_row = {}

# ---------- 4. Looping untuk membersihkan dan mengekstraksi tiap polutan ----------
for pollutant in pollutants:
    print(f"\n--- Memproses polutan: {pollutant} ---")
    
    df_poly = df[['date', pollutant]].copy()
    df_poly[pollutant] = pd.to_numeric(df_poly[pollutant], errors='coerce')

    # Handling outlier dengan IQR (sebagai safeguard tambahan)
    Q1 = df_poly[pollutant].quantile(0.25)
    Q3 = df_poly[pollutant].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df_poly.loc[(df_poly[pollutant] < lower_bound) | (df_poly[pollutant] > upper_bound), pollutant] = np.nan

    # Interpolasi waktu dan cleaning
    df_clean = df_poly.set_index('date').interpolate(method='time').ffill().bfill()
    signal_1d = df_clean[pollutant].astype(float).values

    # Ekstraksi fitur dan beri prefix nama polutan (misal: NO2_abs_energy)
    for fn_name in FEATURE_LIST:
        feature_key = f"{pollutant}_{fn_name}"
        combined_row[feature_key] = extract_one(fn_name, signal_1d, fs)

# ---------- 5. Simpan ke DataFrame final ----------
extracted_features_final = pd.DataFrame([combined_row])
print(f"\nBerhasil! Total kolom akhir yang dihasilkan: {extracted_features_final.shape[1]}")

output_filename = '../../data/polutan-baron/Baron_Linear.csv'
extracted_features_final.to_csv(output_filename, index=False)
print(f"File berhasil disimpan sebagai: {output_filename}")
```

Contoh cuplikan hasil ekstraksi fitur gabungan (204 kolom):

```{code-cell}
:tags: [hide-input]
df_feat = pd.read_csv("../../data/polutan-baron/Baron_Linear.csv")
df_feat.head()
```

## Penjelasan Domain TSFEL

Pustaka TSFEL membagi 68 fitur deret waktu menjadi tiga domain utama: **Statistik (Statistical)**, **Waktu (Temporal)**, dan **Frekuensi (Spectral)**. Berikut adalah penjabaran lengkap untuk masing-masing fitur beserta rumusnya, serta hasil perhitungannya yang diterapkan pada polutan NO2 (dari `NO2_filed.csv`) yang disajikan pada hasil akhir (`Baron_Linear.csv` pada kolom berawalan `NO2_`).

### 1. Domain Statistical
Domain statistik mengekstrak metrik kuantitatif dan karakteristik sebaran serta bentuk distribusi dari sinyal deret waktu. Domain ini terdiri dari 17 fitur utama yang fokus pada distribusi.

1. **`calc_max`**
   - **Penjelasan**: Nilai maksimum dari deret waktu.
   - **Rumus**: $\max(x)$
   - **Hasil (NO2)**: `5.51000e-05`

2. **`calc_min`**
   - **Penjelasan**: Nilai minimum dari deret waktu.
   - **Rumus**: $\min(x)$
   - **Hasil (NO2)**: `5.12000e-06`

3. **`calc_mean`**
   - **Penjelasan**: Rata-rata (mean) dari deret waktu.
   - **Rumus**: $\mu = \frac{1}{N} \sum_{i=1}^N x_i$
   - **Hasil (NO2)**: `2.84004e-05`

4. **`calc_median`**
   - **Penjelasan**: Nilai tengah (median) dari deret waktu.
   - **Rumus**: $\text{median}(x)$
   - **Hasil (NO2)**: `2.81250e-05`

5. **`calc_std`**
   - **Penjelasan**: Standar deviasi, mengukur tingkat penyebaran data.
   - **Rumus**: $\sigma = \sqrt{\frac{1}{N} \sum_{i=1}^N (x_i - \mu)^2}$
   - **Hasil (NO2)**: `1.01280e-05`

6. **`calc_var`**
   - **Penjelasan**: Varians, kuadrat dari standar deviasi.
   - **Rumus**: $\sigma^2 = \frac{1}{N} \sum_{i=1}^N (x_i - \mu)^2$
   - **Hasil (NO2)**: `1.02577e-10`

7. **`ecdf`**
   - **Penjelasan**: Fungsi distribusi kumulatif empiris.
   - **Rumus**: $\hat{F}(t) = \frac{1}{N} \sum_{i=1}^N \mathbf{1}_{x_i \le t}$
   - **Hasil (NO2)**: `1.50273e-02`

8. **`ecdf_percentile`**
   - **Penjelasan**: Nilai ECDF pada persentil tertentu.
   - **Rumus**: $P_{perc}(\hat{F})$
   - **Hasil (NO2)**: `2.84000e-05`

9. **`ecdf_percentile_count`**
   - **Penjelasan**: Jumlah data yang berada di bawah persentil ECDF.
   - **Rumus**: $\sum \mathbf{1}_{x_i \le P_{perc}}$
   - **Hasil (NO2)**: `1.82500e+02`

10. **`ecdf_slope`**
   - **Penjelasan**: Kemiringan dari kurva ECDF.
   - **Rumus**: $\frac{\Delta y}{\Delta x} \text{ pada } \hat{F}(t)$
   - **Hasil (NO2)**: `3.47222e+04`

11. **`hist_mode`**
   - **Penjelasan**: Modus (nilai paling sering muncul) berdasarkan histogram.
   - **Rumus**: $\arg\max_j (\text{count}(bin_j))$
   - **Hasil (NO2)**: `2.76110e-05`

12. **`interq_range`**
   - **Penjelasan**: Jangkauan interkuartil (IQR), selisih Q3 dan Q1.
   - **Rumus**: $IQR = Q_3 - Q_1$
   - **Hasil (NO2)**: `1.45000e-05`

13. **`kurtosis`**
   - **Penjelasan**: Keruncingan (peakedness) dari distribusi data.
   - **Rumus**: $K = \frac{\frac{1}{N} \sum_{i=1}^N (x_i - \mu)^4}{\sigma^4} - 3$
   - **Hasil (NO2)**: `-4.15397e-01`

14. **`skewness`**
   - **Penjelasan**: Kemiringan (asimetri) dari distribusi data.
   - **Rumus**: $S = \frac{\frac{1}{N} \sum_{i=1}^N (x_i - \mu)^3}{\sigma^3}$
   - **Hasil (NO2)**: `1.02776e-01`

15. **`mean_abs_deviation`**
   - **Penjelasan**: Rata-rata simpangan absolut dari mean.
   - **Rumus**: $MAD = \frac{1}{N} \sum_{i=1}^N |x_i - \mu|$
   - **Hasil (NO2)**: `8.22498e-06`

16. **`median_abs_deviation`**
   - **Penjelasan**: Median dari simpangan absolut dari median.
   - **Rumus**: $\text{Median}(|x_i - \text{median}(x)|)$
   - **Hasil (NO2)**: `7.10833e-06`

17. **`rms`**
   - **Penjelasan**: Root Mean Square (energi kuadrat rata-rata).
   - **Rumus**: $RMS = \sqrt{\frac{1}{N} \sum_{i=1}^N x_i^2}$
   - **Hasil (NO2)**: `3.01523e-05`

### 2. Domain Temporal
Domain temporal mengevaluasi sinyal dari segi urutan waktunya. Terdiri dari 25 fitur yang mengukur dependensi, jarak, autokorelasi, dan kompleksitas waktu.

1. **`abs_energy`**
   - **Penjelasan**: Total energi absolut dari deret waktu.
   - **Rumus**: $E = \sum_{i=1}^N x_i^2$
   - **Hasil (NO2)**: `3.32752e-07`

2. **`auc`**
   - **Penjelasan**: Area di bawah kurva sinyal (Area Under Curve).
   - **Rumus**: $AUC = \sum_{i=1}^{N-1} \frac{x_i + x_{i+1}}{2}$
   - **Hasil (NO2)**: `1.03695e-02`

3. **`autocorr`**
   - **Penjelasan**: Autokorelasi sinyal, kesamaan sinyal dengan versi tertundanya.
   - **Rumus**: $R(\tau) = \sum_{i=1}^{N-\tau} x_i x_{i+\tau}$
   - **Hasil (NO2)**: `1.70000e+01`

4. **`average_power`**
   - **Penjelasan**: Daya rata-rata dari sinyal waktu.
   - **Rumus**: $P = \frac{1}{N} \sum_{i=1}^N x_i^2$
   - **Hasil (NO2)**: `9.11650e-10`

5. **`calc_centroid`**
   - **Penjelasan**: Titik pusat dari urutan waktu (Time Centroid).
   - **Rumus**: $C_t = \frac{\sum t_i \cdot x_i}{\sum x_i}$
   - **Hasil (NO2)**: `2.03671e+02`

6. **`dfa`**
   - **Penjelasan**: Detrended Fluctuation Analysis, untuk mengukur dependensi fraktal.
   - **Rumus**: $F(n) \propto n^\alpha$
   - **Hasil (NO2)**: `1.01119e+00`

7. **`distance`**
   - **Penjelasan**: Total jarak (panjang lintasan) antar titik-titik berturutan.
   - **Rumus**: $D = \sum_{i=1}^{N-1} \sqrt{1 + (x_{i+1} - x_i)^2}$
   - **Hasil (NO2)**: `3.65000e+02`

8. **`entropy`**
   - **Penjelasan**: Shannon Entropy, mengukur ketidakpastian sinyal.
   - **Rumus**: $H = -\sum p(x) \log p(x)$
   - **Hasil (NO2)**: `9.27850e-01`

9. **`higuchi_fractal_dimension`**
   - **Penjelasan**: Dimensi Fraktal Higuchi, mengukur kompleksitas bentuk.
   - **Rumus**: $L(k) \propto k^{-D}$
   - **Hasil (NO2)**: `1.84022e+00`

10. **`hurst_exponent`**
   - **Penjelasan**: Eksponen Hurst, indikasi memori jangka panjang waktu.
   - **Rumus**: $E[\frac{R(n)}{S(n)}] = C n^H$
   - **Hasil (NO2)**: `8.03093e-01`

11. **`lempel_ziv`**
   - **Penjelasan**: Kompleksitas Lempel-Ziv, mengukur tingkat kompresibilitas sinyal.
   - **Rumus**: $LZ = \frac{c(N)}{\frac{N}{\log N}}$
   - **Hasil (NO2)**: `1.72131e-01`

12. **`maximum_fractal_length`**
   - **Penjelasan**: Panjang maksimal fraktal di berbagai skala pengukuran.
   - **Rumus**: $L_{max} = \max_k (L(k))$
   - **Hasil (NO2)**: `-2.69521e+00`

13. **`mean_abs_diff`**
   - **Penjelasan**: Rata-rata dari perbedaan absolut titik berurutan.
   - **Rumus**: $\mu_{\Delta} = \frac{1}{N-1} \sum_{i=1}^{N-1} |x_{i+1} - x_i|$
   - **Hasil (NO2)**: `4.56367e-06`

14. **`mean_diff`**
   - **Penjelasan**: Rata-rata perbedaan antara titik berurutan.
   - **Rumus**: $\mu_{d} = \frac{1}{N-1} \sum_{i=1}^{N-1} (x_{i+1} - x_i)$
   - **Hasil (NO2)**: `1.20548e-08`

15. **`median_abs_diff`**
   - **Penjelasan**: Median perbedaan absolut berurutan.
   - **Rumus**: $\text{Median}(|x_{i+1} - x_i|)$
   - **Hasil (NO2)**: `2.50000e-06`

16. **`median_diff`**
   - **Penjelasan**: Median dari selisih titik berurutan.
   - **Rumus**: $\text{Median}(x_{i+1} - x_i)$
   - **Hasil (NO2)**: `4.00000e-07`

17. **`mse`**
   - **Penjelasan**: Mean Squared Error dari sinyal terhadap rata-ratanya.
   - **Rumus**: $MSE = \frac{1}{N} \sum_{i=1}^N (x_i - \mu)^2$
   - **Hasil (NO2)**: `1.28358e+00`

18. **`negative_turning`**
   - **Penjelasan**: Jumlah titik belok bergradien negatif (puncak yang turun).
   - **Rumus**: $\sum \mathbf{1}_{x_{i-1} < x_i > x_{i+1}}$
   - **Hasil (NO2)**: `6.70000e+01`

19. **`neighbourhood_peaks`**
   - **Penjelasan**: Jumlah puncak pada area bertetangga yang ditentukan.
   - **Rumus**: $\sum \text{Peaks}(x, \text{window})$
   - **Hasil (NO2)**: `1.60000e+01`

20. **`petrosian_fractal_dimension`**
   - **Penjelasan**: Dimensi Fraktal Petrosian.
   - **Rumus**: $D = \frac{\log_{10}(N)}{\log_{10}(N) + \log_{10}(\frac{N}{N + 0.4 N_{\Delta}})}$
   - **Hasil (NO2)**: `1.02404e+00`

21. **`pk_pk_distance`**
   - **Penjelasan**: Jarak dari puncak tertinggi ke lembah terendah (Peak-to-Peak).
   - **Rumus**: $P2P = \max(x) - \min(x)$
   - **Hasil (NO2)**: `4.99800e-05`

22. **`positive_turning`**
   - **Penjelasan**: Jumlah titik belok bergradien positif (lembah yang naik).
   - **Rumus**: $\sum \mathbf{1}_{x_{i-1} > x_i < x_{i+1}}$
   - **Hasil (NO2)**: `6.80000e+01`

23. **`slope`**
   - **Penjelasan**: Kemiringan tren regresi linier secara keseluruhan.
   - **Rumus**: $m = \frac{\sum (t_i - \bar{t})(x_i - \mu)}{\sum (t_i - \bar{t})^2}$
   - **Hasil (NO2)**: `2.85331e-08`

24. **`sum_abs_diff`**
   - **Penjelasan**: Total akumulasi perbedaan absolut titik berurutan.
   - **Rumus**: $SAD = \sum_{i=1}^{N-1} |x_{i+1} - x_i|$
   - **Hasil (NO2)**: `1.66574e-03`

25. **`zero_cross`**
   - **Penjelasan**: Jumlah titik perpotongan nol (zero-crossing).
   - **Rumus**: $\sum \mathbf{1}_{x_i \cdot x_{i+1} < 0}$
   - **Hasil (NO2)**: `0.00000e+00`

### 3. Domain Spectral
Domain spektral mentransformasi data ke domain frekuensi (melalui Fourier/Wavelet). Terdiri dari 26 fitur untuk mengukur sifat periodik, energi spektrum, dan rentang frekuensi.

1. **`fundamental_frequency`**
   - **Penjelasan**: Frekuensi dasar yang paling kuat pada spektrum.
   - **Rumus**: $f_0 = \arg\max_f (|X(f)|^2)$
   - **Hasil (NO2)**: `2.73224e-03`

2. **`max_frequency`**
   - **Penjelasan**: Frekuensi tertinggi pada analisis spektrum daya.
   - **Rumus**: $f_{max} = \max(f)$
   - **Hasil (NO2)**: `4.34426e-01`

3. **`median_frequency`**
   - **Penjelasan**: Frekuensi yang membagi spektrum daya (energi) menjadi dua bagian sama.
   - **Rumus**: $\int_0^{f_{med}} |X(f)|^2 df = \frac{1}{2} \int_0^\infty |X(f)|^2 df$
   - **Hasil (NO2)**: `4.09836e-02`

4. **`human_range_energy`**
   - **Penjelasan**: Energi sinyal pada jangkauan pendengaran manusia.
   - **Rumus**: $E_h = \sum_{f \in H} |X(f)|^2$
   - **Hasil (NO2)**: `0.00000e+00`

5. **`lpcc`**
   - **Penjelasan**: Koefisien Linear Prediction Cepstral (LPCC).
   - **Rumus**: $C_n = -a_n - \sum_{k=1}^{n-1} \frac{k}{n} C_k a_{n-k}$
   - **Hasil (NO2)**: `7.48200e-01`

6. **`mfcc`**
   - **Penjelasan**: Koefisien Mel-Frequency Cepstral (MFCC).
   - **Rumus**: $c_n = \sum_{k=1}^K (\log S_k) \cos\left[n(k-\frac{1}{2})\frac{\pi}{K}\right]$
   - **Hasil (NO2)**: `2.43670e+01`

7. **`max_power_spectrum`**
   - **Penjelasan**: Daya tertinggi dari seluruh rentang spektrum frekuensi.
   - **Rumus**: $\max_f (|X(f)|^2)$
   - **Hasil (NO2)**: `1.22004e+02`

8. **`power_bandwidth`**
   - **Penjelasan**: Lebar pita tempat akumulasi mayoritas kekuatan sinyal (daya).
   - **Rumus**: $BW = f_{upper} - f_{lower}$
   - **Hasil (NO2)**: `3.22404e-01`

9. **`spectral_centroid`**
   - **Penjelasan**: Pusat massa spektral (frekuensi rata-rata berbobot energi).
   - **Rumus**: $C_s = \frac{\sum f_k |X(f_k)|}{\sum |X(f_k)|}$
   - **Hasil (NO2)**: `1.20096e-01`

10. **`spectral_decrease`**
   - **Penjelasan**: Tingkat penurunan kekuatan spektral pada frekuensi yang meninggi.
   - **Rumus**: $D_s = \frac{\sum_{k=2}^K \frac{|X(f_k)| - |X(f_1)|}{k-1}}{\sum_{k=2}^K |X(f_k)|}$
   - **Hasil (NO2)**: `-2.52716e+00`

11. **`spectral_distance`**
   - **Penjelasan**: Jarak spektral, selisih antar kurva densitas spektrum.
   - **Rumus**: $D(X, Y) = \sqrt{\sum (X(f) - Y(f))^2}$
   - **Hasil (NO2)**: `-1.58982e+00`

12. **`spectral_entropy`**
   - **Penjelasan**: Entropi spektral, seberapa menyebar distribusi energi spektrum.
   - **Rumus**: $H_s = -\sum p_f \log p_f$
   - **Hasil (NO2)**: `6.21878e-01`

13. **`spectral_kurtosis`**
   - **Penjelasan**: Kurtosis dari kepadatan daya spektrum.
   - **Rumus**: $K_s = \frac{\sum (f - C_s)^4 |X(f)|^2}{(\sum (f - C_s)^2 |X(f)|^2)^2}$
   - **Hasil (NO2)**: `2.71723e+00`

14. **`spectral_positive_turning`**
   - **Penjelasan**: Titik belok positif pada kurva spektrum.
   - **Rumus**: $\sum \mathbf{1}_{|X(f_{i-1})| > |X(f_i)| < |X(f_{i+1})|}$
   - **Hasil (NO2)**: `6.10000e+01`

15. **`spectral_roll_off`**
   - **Penjelasan**: Frekuensi roll-off di mana sebagian besar energi spektral terkonsentrasi.
   - **Rumus**: $f_c \text{ dimana } \sum_{f=0}^{f_c} |X(f)|^2 = 0.95 \sum_{f} |X(f)|^2$
   - **Hasil (NO2)**: `4.34426e-01`

16. **`spectral_roll_on`**
   - **Penjelasan**: Frekuensi roll-on tempat sebagian kecil energi (misal 5%) terakumulasi.
   - **Rumus**: $f_c \text{ dimana } \sum_{f=0}^{f_c} |X(f)|^2 = 0.05 \sum_{f} |X(f)|^2$
   - **Hasil (NO2)**: `0.00000e+00`

17. **`spectral_skewness`**
   - **Penjelasan**: Skewness (kemiringan) dari kepadatan daya spektrum.
   - **Rumus**: $S_s = \frac{\sum (f - C_s)^3 |X(f)|^2}{(\sum (f - C_s)^2 |X(f)|^2)^{3/2}}$
   - **Hasil (NO2)**: `1.05467e+00`

18. **`spectral_slope`**
   - **Penjelasan**: Kemiringan dari spektrum daya yang dihitung menggunakan regresi linier.
   - **Rumus**: $m_s = \frac{\sum (f_i - \bar{f})(|X(f_i)| - \overline{|X(f)|})}{\sum (f_i - \bar{f})^2}$
   - **Hasil (NO2)**: `-3.35216e-02`

19. **`spectral_spread`**
   - **Penjelasan**: Sebaran spektrum atau varians frekuensi di sekeliling pusat massa.
   - **Rumus**: $V_s = \sqrt{\frac{\sum (f_k - C_s)^2 |X(f_k)|}{\sum |X(f_k)|}}$
   - **Hasil (NO2)**: `1.50384e-01`

20. **`spectral_variation`**
   - **Penjelasan**: Variasi atau jarak perubahan spektrum pada titik yang berdekatan.
   - **Rumus**: $V = 1 - \frac{\sum X_{t-1}(f) X_t(f)}{\sqrt{\sum X_{t-1}^2 \sum X_t^2}}$
   - **Hasil (NO2)**: `2.64122e-01`

21. **`spectrogram_mean_coeff`**
   - **Penjelasan**: Koefisien magnitudo rata-rata dari matriks spektrogram.
   - **Rumus**: $\frac{1}{T F} \sum_t \sum_f |S(t, f)|$
   - **Hasil (NO2)**: `1.21204e-10`

22. **`wavelet_abs_mean`**
   - **Penjelasan**: Rata-rata magnitudo absolut dari koefisien transformasi wavelet.
   - **Rumus**: $\mu_w = \frac{1}{N} \sum |W(a,b)|$
   - **Hasil (NO2)**: `1.83560e-06`

23. **`wavelet_energy`**
   - **Penjelasan**: Energi total yang terkandung di dalam koefisien wavelet.
   - **Rumus**: $E_w = \sum |W(a,b)|^2$
   - **Hasil (NO2)**: `1.42750e-05`

24. **`wavelet_entropy`**
   - **Penjelasan**: Entropi wavelet, ukuran distribusi sebaran energi di ruang waktu-frekuensi.
   - **Rumus**: $H_w = -\sum p_j \log p_j, p_j = \frac{E_j}{E_{tot}}$
   - **Hasil (NO2)**: `2.12394e+00`

25. **`wavelet_std`**
   - **Penjelasan**: Standar deviasi dari sebaran koefisien wavelet.
   - **Rumus**: $\sigma_w = \sqrt{\frac{1}{N} \sum (|W(a,b)| - \mu_w)^2}$
   - **Hasil (NO2)**: `1.41400e-05`

26. **`wavelet_var`**
   - **Penjelasan**: Varians dari koefisien dispersi wavelet.
   - **Rumus**: $\sigma_w^2$
   - **Hasil (NO2)**: `2.24529e-10`
