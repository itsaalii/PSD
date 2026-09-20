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

Pada proyek ini, proses pengumpulan data dilakukan dengan metode yang sama seperti pada proyek [Polutan di Kabupaten Nganjuk](../polutan/data-understanding.md). Perbedaannya hanya terletak pada titik koordinat wilayah (Area of Interest) yang digunakan. Hasil dari pengumpulan data tersebut berupa dataset deret waktu (Time Series) sebagai berikut:

### Hasil CSV
Berikut adalah cuplikan data tersebut:

1. CO

```{code-cell}
:tags: [hide-input]
import pandas as pd
import numpy as np
df = pd.read_csv("../../data/polutan-baron/CO.csv")
df.head(5)
```

2. SO2

```{code-cell}
:tags: [hide-input]
df = pd.read_csv("../../data/polutan-baron/SO2.csv")
df.head(5)
```

3. NO₂

```{code-cell}
:tags: [hide-input]
df = pd.read_csv("../../data/polutan-baron/NO2.csv")
df.head(5)
```

## Eksplorasi Data
### Missing Values

_Missing values_ (nilai yang hilang) adalah kondisi di mana terdapat informasi yang kosong atau tidak terekam dalam dataset. Seperti halnya pada data satelit, kekosongan data dapat diidentifikasi dalam dua bentuk: **Tanggal yang Hilang** dan **Data yang Hilang (NaN)**.

#### Tanggal Yang Hilang

1. CO

```{code-cell}
import pandas as pd

df = pd.read_csv("../../data/polutan-baron/CO.csv")
df['date'] = pd.to_datetime(df['date'])

# Menentukan rentang tanggal berdasarkan data awal dan akhir
start_date = df['date'].min()
end_date = df['date'].max()
full_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Cek tanggal yang hilang
missing_dates = full_range.difference(df['date'])

print(f"Jumlah hari missing: {len(missing_dates)}")
print("Daftar tanggal missing:")
print(missing_dates)
```

2. SO₂

```{code-cell}
import pandas as pd

df = pd.read_csv("../../data/polutan-baron/SO2.csv")
df['date'] = pd.to_datetime(df['date'])

start_date = df['date'].min()
end_date = df['date'].max()
full_range = pd.date_range(start=start_date, end=end_date, freq='D')

missing_dates = full_range.difference(df['date'])

print(f"Jumlah hari missing: {len(missing_dates)}")
print("Daftar tanggal missing:")
print(missing_dates)
```

3. NO₂

```{code-cell}
import pandas as pd

df = pd.read_csv("../../data/polutan-baron/NO2.csv")
df['date'] = pd.to_datetime(df['date'])

start_date = df['date'].min()
end_date = df['date'].max()
full_range = pd.date_range(start=start_date, end=end_date, freq='D')

missing_dates = full_range.difference(df['date'])

print(f"Jumlah hari missing: {len(missing_dates)}")
print("Daftar tanggal missing:")
print(missing_dates)
```

#### Data Yang Hilang

Selain urutan tanggal, kita juga perlu mengecek jumlah baris data yang memiliki nilai konsentrasi polutan kosong (`NaN`).

1. CO

```{code-cell}
df = pd.read_csv("../../data/polutan-baron/CO.csv")
missing_value = df['CO'].isna().sum()
print(f"Jumlah missing value pada kolom CO: {missing_value}")
```

2. SO₂

```{code-cell}
df = pd.read_csv("../../data/polutan-baron/SO2.csv")
missing_value = df['SO2'].isna().sum()
print(f"Jumlah missing value pada kolom SO2: {missing_value}")
```

3. NO₂

```{code-cell}
df = pd.read_csv("../../data/polutan-baron/NO2.csv")
missing_value = df['NO2'].isna().sum()
print(f"Jumlah missing value pada kolom NO2: {missing_value}")
```

### Outliers

_Outliers_ (pencilan) adalah titik data yang nilainya menyimpang secara drastis dari mayoritas distribusi data. Eksplorasi _outliers_ ini menggunakan algoritma **Isolation Forest** dari pustaka `scikit-learn` dengan parameter estimasi kontaminasi sebesar 5%. Hasil prediksi yang bernilai `-1` menandakan bahwa observasi tersebut terdeteksi sebagai _outlier_.

1. CO

```{code-cell}
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../../data/polutan-baron/CO.csv")
df_clean = df.dropna(subset=['CO']).copy()

df_clean['date'] = pd.to_datetime(df_clean['date'])
df_clean = df_clean.sort_values('date').reset_index(drop=True)

model = IsolationForest(contamination=0.05, random_state=42)
pred = model.fit_predict(df_clean[['CO']])

df_clean['anomaly'] = pred

outliers_if = df_clean[df_clean['anomaly'] == -1]
print("Jumlah outlier:", len(outliers_if))
print(outliers_if[['date', 'CO']].head())
```

```{code-cell}
# Visualisasi Outlier CO
plt.figure(figsize=(15, 5))
plt.plot(df_clean['date'], df_clean['CO'], label="CO", linewidth=1)
plt.scatter(outliers_if['date'], outliers_if['CO'],
            color='red', marker='o', label="Outliers (Isolation Forest)")
plt.title("Deteksi Outlier Data CO (Metode Isolation Forest)")
plt.xlabel("Tanggal")
plt.ylabel("Kadar CO")
plt.legend()
plt.tight_layout()
if not df_clean.empty:
    plt.xticks(
        ticks=[df_clean['date'].iloc[0], df_clean['date'].iloc[-1]],
        labels=[df_clean['date'].iloc[0].strftime('%Y-%m-%d'),
                df_clean['date'].iloc[-1].strftime('%Y-%m-%d')]
    )
plt.show()
```

2. SO₂

```{code-cell}
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../../data/polutan-baron/SO2.csv")
df_clean = df.dropna(subset=['SO2']).copy()

df_clean['date'] = pd.to_datetime(df_clean['date'])
df_clean = df_clean.sort_values('date').reset_index(drop=True)

model = IsolationForest(contamination=0.05, random_state=42)
pred = model.fit_predict(df_clean[['SO2']])

df_clean['anomaly'] = pred

outliers_if = df_clean[df_clean['anomaly'] == -1]
print("Jumlah outlier:", len(outliers_if))
print(outliers_if[['date', 'SO2']].head())
```

```{code-cell}
# Visualisasi Outlier SO2
plt.figure(figsize=(15, 5))
plt.plot(df_clean['date'], df_clean['SO2'], label="SO2", linewidth=1)
plt.scatter(outliers_if['date'], outliers_if['SO2'],
            color='red', marker='o', label="Outliers (Isolation Forest)")
plt.title("Deteksi Outlier Data SO2 (Metode Isolation Forest)")
plt.xlabel("Tanggal")
plt.ylabel("Kadar SO2")
plt.legend()
plt.tight_layout()
if not df_clean.empty:
    plt.xticks(
        ticks=[df_clean['date'].iloc[0], df_clean['date'].iloc[-1]],
        labels=[df_clean['date'].iloc[0].strftime('%Y-%m-%d'),
                df_clean['date'].iloc[-1].strftime('%Y-%m-%d')]
    )
plt.show()
```

3. NO₂

```{code-cell}
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

df = pd.read_csv("../../data/polutan-baron/NO2.csv")
df_clean = df.dropna(subset=['NO2']).copy()

df_clean['date'] = pd.to_datetime(df_clean['date'])
df_clean = df_clean.sort_values('date').reset_index(drop=True)

model = IsolationForest(contamination=0.05, random_state=42)
pred = model.fit_predict(df_clean[['NO2']])

df_clean['anomaly'] = pred

outliers_if = df_clean[df_clean['anomaly'] == -1]
print("Jumlah outlier:", len(outliers_if))
print(outliers_if[['date', 'NO2']].head())
```

```{code-cell}
# Visualisasi Outlier NO2
plt.figure(figsize=(15, 5))
plt.plot(df_clean['date'], df_clean['NO2'], label="NO2", linewidth=1)
plt.scatter(outliers_if['date'], outliers_if['NO2'],
            color='red', marker='o', label="Outliers (Isolation Forest)")
plt.title("Deteksi Outlier Data NO2 (Metode Isolation Forest)")
plt.xlabel("Tanggal")
plt.ylabel("Kadar NO2")
plt.legend()
plt.tight_layout()
if not df_clean.empty:
    plt.xticks(
        ticks=[df_clean['date'].iloc[0], df_clean['date'].iloc[-1]],
        labels=[df_clean['date'].iloc[0].strftime('%Y-%m-%d'),
                df_clean['date'].iloc[-1].strftime('%Y-%m-%d')]
    )
plt.show()
```

## Visualisasi Gabungan (CO, SO₂, NO₂)

Berikut adalah grafik yang menampilkan fluktuasi ketiga polutan udara secara bersamaan untuk melihat pola dan perbandingan di antara ketiganya. Karena besaran numerik CO jauh lebih besar dibanding SO₂ dan NO₂, nilai-nilainya akan disesuaikan skalanya menjadi *Min-Max Normalization* (0 hingga 1) agar seluruh fluktuasinya dapat terlihat jelas secara berdampingan.

```{code-cell}
:tags: [hide-input]
import pandas as pd
import matplotlib.pyplot as plt

df_co = pd.read_csv("../../data/polutan-baron/CO.csv")
df_so2 = pd.read_csv("../../data/polutan-baron/SO2.csv")
df_no2 = pd.read_csv("../../data/polutan-baron/NO2.csv")

df_co['date'] = pd.to_datetime(df_co['date'])
df_so2['date'] = pd.to_datetime(df_so2['date'])
df_no2['date'] = pd.to_datetime(df_no2['date'])

# Normalisasi menggunakan metode Min-Max agar ada di skala 0-1
df_co['CO_scaled'] = (df_co['CO'] - df_co['CO'].min()) / (df_co['CO'].max() - df_co['CO'].min())
df_so2['SO2_scaled'] = (df_so2['SO2'] - df_so2['SO2'].min()) / (df_so2['SO2'].max() - df_so2['SO2'].min())
df_no2['NO2_scaled'] = (df_no2['NO2'] - df_no2['NO2'].min()) / (df_no2['NO2'].max() - df_no2['NO2'].min())

plt.figure(figsize=(15, 6))

plt.plot(df_co['date'], df_co['CO_scaled'], label="CO", linewidth=1.5, color='blue')
plt.plot(df_so2['date'], df_so2['SO2_scaled'], label="SO2", linewidth=1.5, color='green')
plt.plot(df_no2['date'], df_no2['NO2_scaled'], label="NO2", linewidth=1.5, color='purple')

plt.title("Fluktuasi Kadar Polutan CO, SO2, dan NO2 (Skala Ternormalisasi 0-1)")
plt.xlabel("Tanggal")
plt.ylabel("Kadar Polutan (Min-Max Scaled)")
plt.legend()
plt.tight_layout()
plt.xticks(
    ticks=[df_co['date'].min(), df_co['date'].max()],
    labels=[df_co['date'].min().strftime('%Y-%m-%d'),
            df_co['date'].max().strftime('%Y-%m-%d')]
)
plt.show()
```