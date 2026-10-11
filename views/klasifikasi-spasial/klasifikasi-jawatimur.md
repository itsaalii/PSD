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

# Klasifikasi Spasial Tutupan Lahan Jawa Timur (K-Nearest Neighbors & Sentinel-2A)

Dokumentasi ini menyajikan alur lengkap (*end-to-end pipeline*) klasifikasi spasial tutupan lahan (*Land Use / Land Cover* - LULC) skala regional di **Provinsi Jawa Timur** berbasis citra satelit optik multispektral **Sentinel-2A Level-2A (Bottom-of-Atmosphere / BOA Surface Reflectance)** dan algoritma **K-Nearest Neighbors (KNN)**, mengacu pada eksperimen dalam notebook `klasifikasi-spasisal-fiksss.ipynb`.

> [!TIP]
> **Aplikasi Web Interaktif (Streamlit Cloud)**:  
> Seluruh visualisasi spasial, kedua peta interaktif, dan evaluasi performa model telah dideploy dan dapat diakses langsung secara publik di:  
> 🌐 **[https://klasifikasi-spasial-tutupan-lahan-jawatimur.streamlit.app/](https://klasifikasi-spasial-tutupan-lahan-jawatimur.streamlit.app/)**

Siklus proyek disusun secara sistematis berdasarkan metodologi standar **CRISP-DM (Cross-Industry Standard Process for Data Mining)**:
1. **Business Understanding**: Identifikasi latar belakang, urgensi pemetaan ruang, dan perumusan tujuan klasifikasi 6 kelas tutupan lahan.
2. **Data Understanding**: Karakteristik spektral band Sentinel-2A, rekayasa indeks vegetasi dan air, eksplorasi data (EDA), dan akuisisi komposit citra via openEO CDSE.
3. **Data Preprocessing**: Seleksi fitur spektral, pemisahan data uji dan latih (*Stratified Train-Test Split* 80:20), serta standarisasi fitur (*StandardScaler*).
4. **Modeling**: Pelatihan model *Machine Learning* K-Nearest Neighbors (KNN, $k=5$) dan pertimbangan teoritis Naive Bayes.
5. **Evaluation**: Pengujian menyeluruh tingkat piksel (64.430 sampel uji) dan tingkat poligon (*Convex Hull* 268 poligon), matriks konfusi, serta pemetaan spasial kesalahan klasifikasi interaktif.
6. **Deployment**: Penerbitan dashboard pemantauan geospasial interaktif berbasis Streamlit.

---

## Instalasi Library & Kebutuhan Lingkungan

Untuk menjalankan seluruh pipeline klasifikasi, ekstraksi citra, pemodelan, hingga visualisasi peta interaktif, instal dependensi Python berikut:

```bash
pip install openeo geopandas rasterio shapely scikit-learn pandas numpy folium matplotlib seaborn pillow
```

---

## 1. Business Understanding (Pemahaman Bisnis)

### 1.1. Latar Belakang
Pemetaan tutupan lahan (*Land Cover*) sangat krusial untuk berbagai kepentingan analisis ruang, konservasi lingkungan hidup, perencanaan tata kota, hingga ketahanan pangan regional di Provinsi Jawa Timur. Provinsi ini memiliki keragaman bentang alam yang sangat tinggi, mulai dari sentra persawahan intensif di lembah Sungai Brantas dan Bengawan Solo, kawasan terbangun megapolitan Surabaya Raya, gugusan hutan pegunungan, perairan danau alami/waduk, hingga ekosistem hutan bakau (*mangrove*) di sepanjang pesisir utara dan selatan.

Proses digitasi dan interpretasi citra satelit secara manual (*visual interpretation*) memakan waktu dan biaya yang sangat besar serta rentan terhadap subjektivitas surveyor. Oleh karena itu, penerapan algoritma *Machine Learning* yang dipadukan dengan citra satelit multispektral menjadi solusi otomatisasi yang cepat, akurat, dan dapat direplikasi secara berkala.

### 1.2. Tujuan Proyek
1. **Membangun Model Machine Learning Otomatis**: Mengklasifikasikan piksel dan wilayah spasial ke dalam 6 kelas tutupan lahan utama: **Sawah**, **Bangunan**, **Hutan (Lahan Hijau)**, **Danau**, **Laut (Perairan Terbuka)**, dan **Mangrove**.
2. **Optimasi Algoritma Klasifikasi**: Menerapkan algoritma berbasis jarak **K-Nearest Neighbors (KNN)** yang terbukti handal dalam memetakan batas keputusan non-linear pada data reflektansi multispektral setelah standarisasi fitur.
3. **Penyajian Peta Spasial Ganda yang Estetik**:
   - **Peta Evaluasi Poligon (Vektor)**: Merekonstruksi poligon sampel ground truth berbasis *Convex Hull*, menandai poligon salah klasifikasi dengan garis putus-putus dan penanda tanda seru (`!`) yang menampilkan detail kelas aktual vs prediksi secara interaktif saat dihover.
   - **Peta Inferensi Regional (Raster)**: Memetakan inferensi tutupan lahan per piksel di seluruh daratan Provinsi Jawa Timur berbasis komposit satelit resolusi 250m dari openEO.
4. **Penyebaran Model Terbuka (*Public Deployment*)**: Mempublikasikan aplikasi web dashboard menggunakan Streamlit agar hasil analisis dapat diakses oleh publik dan pengambil kebijakan secara langsung.

---

## 2. Data Understanding (Pengumpulan & Pemahaman Data)

### 2.1. Definisi 6 Kelas Tutupan Lahan
Wilayah studi dikelompokkan ke dalam 6 kelas tutupan lahan utama:

| No | Nama Kelas | Kode Label | Definisi Objek | Karakteristik Spektral Utama |
| :---: | :--- | :---: | :--- | :--- |
| 1 | **Sawah** | `1` | Lahan pertanian padi berpetak, genangan air sawah, dan fase vegetatif padi. | Reflektansi NIR sedang hingga tinggi saat fase hijau; pantulan SWIR meningkat pada lahan bera kering. |
| 2 | **Bangunan** | `2` | Kawasan terbangun permukiman, gedung, jalan aspal/beton, dan fasilitas industri. | Pantulan tinggi pada SWIR (B11) dan Red (B04); NDBI positif tinggi; NDVI rendah. |
| 3 | **Hutan (Lahan Hijau)** | `3` | Vegetasi alami kanopi pohon lebat, hutan pegunungan, dan perkebunan tahunan rapat. | Pantulan maksimal pada NIR (B08) akibat struktur sel daun; serapan kuat pada Red (B04); NDVI tinggi ($> 0.6$). |
| 4 | **Danau** | `4` | Badan air tawar pedalaman (waduk buatan, telaga, bendungan, dan danau alami). | Penyerapan kuat pada NIR dan SWIR; nilai NDWI dan MNDWI sangat positif; NDVI negatif. |
| 5 | **Laut (Perairan Terbuka)** | `5` | Badan air asin pesisir dan laut terbuka (Selat Madura, Laut Jawa, Samudra Hindia). | Pantulan dominan pada band tampak Blue (B02) dan Green (B03); penyerapan hampir sempurna pada inframerah. |
| 6 | **Mangrove** | `6` | Komunitas hutan bakau pasang surut di muara sungai dan pantai berlumpur pesisir. | Kombinasi sinyal vegetasi hijau lebat (NIR tinggi) dan pengaruh substrat lumpur/air basah (SWIR relatif rendah). |

---

### 2.2. Band Spektral Citra Sentinel-2A Level-2A
Citra satelit bersumber dari sensor **Multispectral Instrument (MSI)** pada wahana **Sentinel-2A Level-2A** (*Copernicus Data Space Ecosystem* - CDSE) dengan koreksi atmosfer *Bottom-of-Atmosphere* (BOA):

* **B02 (Blue - 490 nm)**: Resolusi 10 meter. Berguna untuk mendeteksi badan air jernih dan hamburan partikel atmosfer.
* **B03 (Green - 560 nm)**: Resolusi 10 meter. Puncak pantulan klorofil daun pada spektrum tampak dan deteksi sedimen perairan.
* **B04 (Red - 665 nm)**: Resolusi 10 meter. Pita serapan utama klorofil; pembeda tajam antara vegetasi hidup dan material tanah terbuka/bangunan.
* **B08 (Near Infrared / NIR - 842 nm)**: Resolusi 10 meter. Pantulan sangat tinggi dari struktur sel mesofil daun; diserap hampir total oleh air jernih.
* **B11 (Short-Wave Infrared / SWIR - 1610 nm)**: Resolusi 20 meter (di-resample ke 10 m). Sensitif terhadap kelembapan air pada tanah dan vegetasi, serta reflektansi material atap/beton.

---

### 2.3. Rekayasa Fitur Indeks Spektral
Empat indeks spektral dihitung untuk memperkuat pemisahan matematis antar-kelas (*spectral feature separability*):

#### A. Normalized Difference Vegetation Index (NDVI)
Membedakan kerapatan kanopi vegetasi hijau:
$$\text{NDVI} = \frac{\text{B08} - \text{B04}}{\text{B08} + \text{B04} + \epsilon}$$

#### B. Normalized Difference Water Index (NDWI - McFeeters)
Mengisolasi badan air permukaan terbuka dari daratan:
$$\text{NDWI} = \frac{\text{B03} - \text{B08}}{\text{B03} + \text{B08} + \epsilon}$$

#### C. Modified Normalized Difference Water Index (MNDWI - Xu)
Meredam gangguan pantulan bangunan perkotaan saat mendeteksi air:
$$\text{MNDWI} = \frac{\text{B03} - \text{B11}}{\text{B03} + \text{B11} + \epsilon}$$

#### D. Normalized Difference Built-up Index (NDBI)
Menyoroti konsentrasi kawasan terbangun dan perkerasan semen/aspal:
$$\text{NDBI} = \frac{\text{B11} - \text{B08}}{\text{B11} + \text{B08} + \epsilon}$$

*(Konstanta $\epsilon = 10^{-9}$ digunakan untuk mencegah kesalahan pembagian dengan nol).*

---

### 2.4. Karakteristik Dataset Ground Truth
Dataset hasil ekstraksi disimpan dalam file `dataset.csv`:
* **Total Baris (Piksel)**: **322.146 piksel**
* **Total Kolom (Fitur)**: 19 kolom (metadata koordinat, band spektral asli, dan indeks turunan)
* **Total Poligon Sampel**: **274 poligon** yang didigitasi secara cermat dari berbagai penjuru Jawa Timur.

```python
# Memuat dataset pada notebook
import pandas as pd
df = pd.read_csv('dataset.csv')

print(f"Jumlah baris (piksel): {df.shape[0]}")
print(f"Jumlah kolom (fitur): {df.shape[1]}")
df.head()
```

---

### 2.5. Exploratory Data Analysis (EDA)
Analisis eksplorasi data dilakukan untuk memverifikasi keterpisahan spektral:
1. **Distribusi Jumlah Piksel per Kelas**: Memeriksa volume sampel untuk setiap tutupan lahan.
2. **Distribusi Nilai NDVI**: Membuktikan bahwa kelas **Hutan** dan **Mangrove** memiliki sebaran NDVI tertinggi ($> 0.65$), **Sawah** memiliki variasi NDVI sedang-tinggi ($0.4 - 0.8$), sedangkan **Danau**, **Laut**, dan **Bangunan** memiliki NDVI terendah ($< 0.2$).

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Distribusi Kelas
plt.figure(figsize=(10, 5))
sns.countplot(y='label_teks', data=df, palette='viridis', order=df['label_teks'].value_counts().index)
plt.title('Distribusi Jumlah Piksel per Kelas')
plt.xlabel('Jumlah Piksel')
plt.ylabel('Kelas Tutupan Lahan')
plt.show()

# Boxplot NDVI per Kelas
plt.figure(figsize=(10, 6))
sns.boxplot(x='label_teks', y='NDVI', data=df, palette='Set2')
plt.title('Distribusi Nilai NDVI per Kelas Tutupan Lahan')
plt.xticks(rotation=45)
plt.show()
```

---

### 2.6. Akuisisi Citra Skala Regional via openEO Batch Job
Untuk memetakan klasifikasi skala regional satu provinsi utuh, digunakan platform **openEO CDSE** (`openeo.dataspace.copernicus.eu`). Karena batas geografis Jawa Timur ($110.89^\circ - 114.63^\circ\text{ E}$, $-8.84^\circ - -6.65^\circ\text{ S}$) pada resolusi asli melebihi batas sinkron ($> 20.000 \times 20.000$ piksel), proses unduhan dijalankan menggunakan **Batch Job Asinkron** dengan resolusi agregasi spasial $0.0025^\circ$ (~250 meter):

```python
import openeo

connection = openeo.connect("https://openeo.dataspace.copernicus.eu").authenticate_oidc()
bbox_jatim = {"west": 110.89, "south": -8.84, "east": 114.63, "north": -6.65}

cube = connection.load_collection(
    "SENTINEL2_L2A",
    spatial_extent=bbox_jatim,
    temporal_extent=["2024-08-01", "2024-08-31"],
    bands=['B02', 'B03', 'B04', 'B08', 'B11'],
    max_cloud_cover=30
)
cube = cube.median_time()
cube = cube.resample_spatial(resolution=0.0025, projection=4326)
cube = cube.save_result(format="GTiff")

job = cube.create_job(title="Jatim_Composite_250m")
job.start_and_wait()
job.get_results().download_file("jatim_250m.tif")
```

---

## 3. Data Preprocessing (Pra-pemrosesan Data)

### 3.1. Penentuan Fitur dan Pembersihan Data
Fitur prediktor mencakup 5 band spektral asli dan 4 indeks spektral:
```python
fitur = ['B02', 'B03', 'B04', 'B08', 'B11', 'NDVI', 'NDWI', 'MNDWI', 'NDBI']

df_bersih = df.dropna(subset=fitur + ['label_teks']).copy()
X = df_bersih[fitur]
y = df_bersih['label_teks']
```

### 3.2. Pembagian Data (Stratified Train-Test Split 80:20)
Dataset dibagi menggunakan skema *Stratified Split* dengan rasio 80% data latih dan 20% data uji:
* **Jumlah Data Latih**: **257.716 piksel**
* **Jumlah Data Uji**: **64.430 piksel**

### 3.3. Standarisasi Fitur (StandardScaler)
Karena algoritma KNN sangat bertumpu pada perhitungan jarak Euclidean (L2-norm), fitur dengan skala rentang nilai besar (misal band mentah $0 - 10000$) akan mendominasi fitur dengan skala kecil (indeks ternormalisasi $-1$ s.d. $+1$). Oleh karena itu, standarisasi wajib dilakukan:
$$z = \frac{x - \mu}{\sigma}$$

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

---

## 4. Modeling (Pemodelan Machine Learning)

### 4.1. Algoritma K-Nearest Neighbors (KNN)
Algoritma KNN mengklasifikasikan data baru berdasarkan kedekatan jarak fitur dengan $k$ tetangga terdekat di ruang vektor terstandarisasi. Pada eksperimen ini, digunakan parameter:
* **Jumlah Tetangga ($k$)**: `n_neighbors=5`
* **Metrik Jarak**: Euclidean Distance ($p=2$)
* **Bobot Suara**: *Uniform voting* (setiap tetangga terdekat memiliki bobot suara yang sama)

```python
from sklearn.neighbors import KNeighborsClassifier

knn_model = KNeighborsClassifier(n_neighbors=5)
knn_model.fit(X_train_scaled, y_train)

# Prediksi pada subset data uji
y_pred_knn = knn_model.predict(X_test_scaled)
```

### 4.2. Keunggulan KNN pada Data Spektral
1. **Non-Parametrik**: Tidak mengasumsikan distribusi normal atau independensi antar-fitur (berbeda dengan Naive Bayes yang rentan bias ketika korelasi antar-band spektral tinggi).
2. **Batas Keputusan Fleksibel**: Mampu menangkap pola kompleks pada data spasial, seperti zona transisi air payau mangrove dan petak sawah basah.

---

## 5. Evaluation (Evaluasi Model & Hasil Klasifikasi)

### 5.1. Evaluasi Tingkat Piksel pada Data Uji (64.430 Sampel)
Model KNN mencapai performa klasifikasi yang sangat tinggi pada data uji independen:
* **Akurasi Keseluruhan (Accuracy)**: **98.18%**
* **F1-Score Macro**: **0.944** (94.4%)
* **F1-Score Weighted**: **0.982** (98.2%)

#### Laporan Klasifikasi per Kelas (Classification Report):

| Kelas Tutupan Lahan | Precision | Recall | F1-Score | Support (Jumlah Piksel Uji) |
| :--- | :---: | :---: | :---: | :---: |
| **Bangunan** | 0.873 | 0.822 | 0.847 | 353 |
| **Danau** | 0.979 | 0.960 | 0.969 | 15.269 |
| **Hutan** | 0.963 | 0.982 | 0.972 | 12.058 |
| **Laut** | 0.993 | 0.998 | 0.995 | 27.746 |
| **Mangrove** | 0.982 | 0.978 | 0.980 | 8.753 |
| **Sawah** | 0.918 | 0.888 | 0.903 | 251 |
| **Rata-rata Makro (Macro Avg)** | **0.951** | **0.938** | **0.944** | 64.430 |
| **Rata-rata Tertimbang (Weighted Avg)** | **0.982** | **0.982** | **0.982** | 64.430 |

---

### 5.2. Analisis Confusion Matrix
Matriks konfusi pada data uji menunjukkan separasi yang sangat tegas antar-kelas:

| Aktual \ Prediksi | Bangunan | Danau | Hutan | Laut | Mangrove | Sawah | Total Aktual |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Bangunan** | **290** | 35 | 28 | 0 | 0 | 0 | 353 |
| **Danau** | 35 | **14.663** | 292 | 181 | 96 | 2 | 15.269 |
| **Hutan** | 7 | 128 | **11.845** | 0 | 60 | 18 | 12.058 |
| **Laut** | 0 | 69 | 0 | **27.677** | 0 | 0 | 27.746 |
| **Mangrove** | 0 | 77 | 118 | 1 | **8.557** | 0 | 8.753 |
| **Sawah** | 0 | 8 | 20 | 0 | 0 | **223** | 251 |

**Temuan Utama Evaluasi**:
1. **Perairan Terbuka (Laut)** memiliki akurasi tertinggi ($99.5\%$ F1-Score) karena penyerapan total pada band NIR dan SWIR membedakannya secara sempurna dari daratan.
2. **Kawasan Vegetasi Rapat (Hutan & Mangrove)** memiliki akurasi di atas $97\%$, di mana indeks MNDWI dan NDVI sangat efektif membedakan mangrove pasang-surut dari hutan daratan.
3. **Kekeliruan Minor**: Sebagian kecil piksel danau terprediksi sebagai laut (181 piksel) akibat kemiripan spektral air jernih, dan sebagian kecil piksel bangunan pinggiran kota terprediksi sebagai danau/hutan karena vegetasi pekarangan di sekeliling rumah.

---

### 5.3. Evaluasi Spasial Tingkat Poligon (Convex Hull)
Untuk mengevaluasi kehandalan model pada level entitas geografis, hasil prediksi piksel diagregasikan ke masing-masing poligon sampel menggunakan nilai modus (mayoritas suara piksel):
* **Total Poligon Mengandung Data Uji**: 268 poligon
* **Poligon Benar Klasifikasi**: **259 poligon (96.6%)**
* **Poligon Salah Klasifikasi**: **9 poligon (3.4%)**

#### Rincian 9 Poligon Salah Klasifikasi:

| No | ID Poligon | Kelas Aktual (Asli) | Hasil Prediksi Model | Piksel Uji Benar / Total | Akurasi Poligon |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `Bangunan_0003` | Bangunan | Danau | 0 / 2 | 0.0% |
| 2 | `Bangunan_0007` | Bangunan | Hutan | 2 / 5 | 40.0% |
| 3 | `Bangunan_0027` | Bangunan | Hutan | 1 / 3 | 33.3% |
| 4 | `Danau_0041` | Danau | Laut | 4 / 9 | 44.4% |
| 5 | `Sawah_0004` | Sawah | Hutan | 1 / 5 | 20.0% |
| 6 | `Sawah_0013` | Sawah | Hutan | 3 / 7 | 42.9% |
| 7 | `Sawah_0035` | Sawah | Danau | 1 / 2 | 50.0% |
| 8 | `Sawah_0036` | Sawah | Hutan | 1 / 2 | 50.0% |
| 9 | `Sawah_0047` | Sawah | Hutan | 1 / 3 | 33.3% |

---

### 5.4. Peta Interaktif 1: Evaluasi Poligon Ground Truth (Folium Vektor)
Poligon direkonstruksi dari kumpulan koordinat titik sampel menggunakan algoritma *Convex Hull*. 

Fitur Peta 1:
* **Palet Warna Standar GIS**: Lapisan poligon diwarnai sesuai 6 kelas tutupan lahan.
* **Sorotan Poligon Salah Klasifikasi**: Ditandai dengan garis putus-putus *rose crimson* (`#E11D48`) dan bulatan tanda seru (`!`) di titik centroid poligon.
* **Hint Estetik Saat Hover**: Saat kursor diarahkan ke tanda seru, kotak tooltip modern (*border-free*, tanpa outline, bayangan lembut) muncul secara instan menampilkan ID Poligon, Kelas Aktual, Hasil Prediksi, dan Akurasi Piksel Uji.

```python
# Pembuatan Peta Evaluasi Poligon (Cell 13 pada notebook)
import folium
import geopandas as gpd

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")
polygons = gdf.dissolve(by='poligon_id', aggfunc='first').reset_index()
polygons['geometry'] = polygons['geometry'].convex_hull
polygons = polygons.merge(eval_poligon, on='poligon_id', how='left')

map_center = [df['lat'].mean(), df['lon'].mean()]
m1 = folium.Map(location=map_center, zoom_start=10, tiles=None)
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles &copy; Esri",
    name="Esri World Imagery",
    overlay=False
).add_to(m1)
folium.TileLayer("OpenStreetMap", name="OpenStreetMap", overlay=False).add_to(m1)

# Tambahkan Basemap Esri Satellite & Layer Poligon per Kelas ...
# Tambahkan Layer Khusus 'Salah Klasifikasi' dengan Tanda Seru dan Tooltip Hover ...
folium.LayerControl(collapsed=False).add_to(m1)
m1.save("peta_klasifikasi_rf.html")
```

```{raw} html
<div style="margin: 20px 0; border: 1px solid #d0d7de; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.08);">
    <div style="background: #f6f8fa; padding: 10px 16px; border-bottom: 1px solid #d0d7de; display: flex; justify-content: space-between; align-items: center; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; font-size: 13px;">
        <span><b>Peta Interaktif 1:</b> Evaluasi Poligon Sampel & Sorotan Salah Klasifikasi (Folium Vektor)</span>
        <div>
            <a href="https://klasifikasi-spasial-tutupan-lahan-jawatimur.streamlit.app/" target="_blank" style="color: #0F766E; text-decoration: none; font-weight: 600; padding: 4px 10px; background: #E7F4F2; border: 1px solid #99F6E4; border-radius: 4px; margin-right: 6px;">Buka di Web Streamlit</a>
            <a href="peta_klasifikasi_rf.html" target="_blank" style="color: #0969da; text-decoration: none; font-weight: 600; padding: 4px 10px; background: white; border: 1px solid #d0d7de; border-radius: 4px;">↗ Layar Penuh</a>
        </div>
    </div>
    <iframe src="peta_klasifikasi_rf.html" width="100%" height="620px" style="border: none; display: block;"></iframe>
</div>
```

---

### 5.5. Peta Interaktif 2: Klasifikasi Regional Jawa Timur (Folium ImageOverlay)
Peta kedua memetakan inferensi per piksel skala regional se-Jawa Timur dari citra komposit Sentinel-2A L2A openEO (`jatim_250m.tif`).

Fitur Peta 2:
* **Basemap Satelit Stabil**: Menggunakan **Esri World Imagery** dan **OpenStreetMap** bebas dari kendala pemblokiran URL.
* **Lapisan Klasifikasi Terpisah (*Toggleable*)**: Masing-masing kelas tutupan lahan dijadikan layer `ImageOverlay` tersendiri, sehingga pengguna dapat memfilter sebaran Sawah, Bangunan, atau Hutan secara independen melalui panel kontrol di pojok kanan atas.
* **Opasitas Transparan Semu**: Disetel pada opasitas $65\%$ sehingga bentang relief muka bumi asli tetap terlihat di bawah hasil klasifikasi.

```python
# Pembuatan Peta Regional (Cell 14 pada notebook)
import rasterio
from folium.raster_layers import ImageOverlay

with rasterio.open('jatim_250m.tif') as src:
    b2 = src.read(1).astype(float)
    # ... ekstraksi band dan indeks spektral ...
    bounds = src.bounds
    img_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

# Prediksi seluruh piksel menggunakan KNN
pred_1d = knn_model.predict(features_scaled)
pred_2d = pred_1d.reshape((height, width))

m2 = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles=None)
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles &copy; Esri",
    name="Esri Satellite",
    overlay=False
).add_to(m2)
folium.TileLayer("OpenStreetMap", name="OpenStreetMap", overlay=False).add_to(m2)

# Buat ImageOverlay transparan per kelas tutupan lahan
for label_str, hex_color in colors.items():
    # ... susun array RGBA untuk kelas bersangkutan ...
    ImageOverlay(image=rgba_img, bounds=img_bounds, opacity=0.65, name=f"Sebaran {label_str}").add_to(m2)

folium.LayerControl(collapsed=False).add_to(m2)
m2.save("hasil_klasifikasi_random_forest.html")
```

```{raw} html
<div style="margin: 20px 0; border: 1px solid #d0d7de; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.08);">
    <div style="background: #f6f8fa; padding: 10px 16px; border-bottom: 1px solid #d0d7de; display: flex; justify-content: space-between; align-items: center; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; font-size: 13px;">
        <span><b>Peta Interaktif 2:</b> Klasifikasi Tutupan Lahan Skala Regional Jawa Timur (Folium ImageOverlay)</span>
        <div>
            <a href="https://klasifikasi-spasial-tutupan-lahan-jawatimur.streamlit.app/" target="_blank" style="color: #0F766E; text-decoration: none; font-weight: 600; padding: 4px 10px; background: #E7F4F2; border: 1px solid #99F6E4; border-radius: 4px; margin-right: 6px;">Buka di Web Streamlit</a>
            <a href="hasil_klasifikasi_random_forest.html" target="_blank" style="color: #0969da; text-decoration: none; font-weight: 600; padding: 4px 10px; background: white; border: 1px solid #d0d7de; border-radius: 4px;">↗ Layar Penuh</a>
        </div>
    </div>
    <iframe src="hasil_klasifikasi_random_forest.html" width="100%" height="640px" style="border: none; display: block;"></iframe>
</div>
```

---

## 6. Deployment (Penyebaran Model via Streamlit)

### 6.1. Arsitektur Aplikasi Web Streamlit
Model dan kedua visualisasi peta spasial diintegrasikan ke dalam antarmuka berbasis web interaktif pada file [`streamlit_app.py`](file:///c:/Ali/PSD/streamlit_app.py):
* **Presentation Layer**: Menampilkan 4 kartu ringkasan metrik utama (Akurasi 98.2%, F1-Score 0.944, Poligon Ground Truth 274, dan Salah Klasifikasi 9 poligon).
* **Kontrol Tata Letak**: Pengguna dapat memilih tata letak peta (Tampilkan Kedua Peta Atas-Bawah, Berdampingan 2 Kolom, atau Fokus Peta Tunggal) serta mengatur ketinggian frame peta dinamis (450px s.d. 900px).
* **Eksplorasi Data Tabular**: Tabel interaktif hasil evaluasi 268 poligon uji dilengkapi filter status (Semua Data, Hanya Prediksi Benar, atau Hanya Salah Klasifikasi) dan tombol unduh data CSV (`prediksi_data_uji_knn.csv`).
* **Kinerja Cepat & Ringan**: Aplikasi memuat peta HTML yang telah di-generate sebelumnya sehingga tidak membebani memori CPU/RAM server cloud dengan proses pelatihan berulang.

### 6.2. Akses Publik & URL Deployment
Aplikasi telah dideploy dan dapat diakses publik melalui tautan:  
🌐 **[https://klasifikasi-spasial-tutupan-lahan-jawatimur.streamlit.app/](https://klasifikasi-spasial-tutupan-lahan-jawatimur.streamlit.app/)**

### 6.3. Panduan Menjalankan Aplikasi Secara Lokal
Untuk menjalankan dashboard Streamlit di komputer lokal:
```bash
streamlit run streamlit_app.py
```

---

## 7. Kesimpulan

1. **Efektivitas Model KNN**: Model K-Nearest Neighbors ($k=5$) dengan *StandardScaler* berhasil mengklasifikasikan 6 tutupan lahan di Jawa Timur dengan **akurasi data uji 98.18%** (pada 64.430 piksel) dan **akurasi 96.6%** pada tingkat poligon (259 dari 268 poligon terprediksi tepat).
2. **Kombinasi 9 Fitur Spektral**: Integrasi 5 band optik Sentinel-2A dan 4 indeks spektral (NDVI, NDWI, MNDWI, NDBI) memberikan kemampuan separasi yang kokoh dalam membedakan entitas perairan, vegetasi lebat, dan material binaan perkotaan.
3. **Analisis Kesalahan Terpetakan**: Dari 268 poligon uji, hanya terdapat 9 poligon yang salah klasifikasi mayoritas (3.4% error), yang seluruhnya dapat ditelusuri dan diinspeksi secara detail pada Peta 1 interaktif melalui penanda tanda seru (`!`) dan hover tooltip.
4. **Sistem Terpadu & Terbuka**: Seluruh kode analisis, dokumentasi ilmiah, dan aplikasi web interaktif telah terintegrasi penuh dan dapat diakses secara publik via Streamlit Cloud.
