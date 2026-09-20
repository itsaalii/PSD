# Polutan di Kecamatan Baron - Nganjuk

Pada studi kasus ini, kita akan membahas secara komprehensif mengenai analisis data deret waktu (*time series*) untuk konsentrasi polutan udara di wilayah **Kecamatan Baron, Kabupaten Nganjuk**. Fokus utama analisis ini adalah pada tiga jenis gas polutan utama, yaitu:
- **Karbon Monoksida (CO)**
- **Sulfur Dioksida (SO₂)**
- **Nitrogen Dioksida (NO₂)**

Proyek ini bertujuan untuk mengidentifikasi pola, melakukan ekstraksi fitur yang mendalam dari data mentah satelit, dan mengelompokkan karakteristik polutan menggunakan pendekatan *Machine Learning*. 

Berikut adalah alur tahapan analisis yang dilakukan dalam studi kasus ini:

1. **[Business Understanding](bussiness-understanding.md)**
   Membahas latar belakang permasalahan, tujuan analisis, serta manfaat bisnis (business value) dari pemantauan dan pengelompokan data polutan di wilayah ini.

2. **[Data Understanding](data-understanding.md)**
   Meliputi proses pengumpulan data deret waktu untuk ketiga polutan, serta eksplorasi awal untuk mendeteksi *missing values* (baik dari segi urutan tanggal maupun observasi yang kosong) dan mendeteksi titik-titik *outliers* secara visual menggunakan algoritma *Isolation Forest*.

3. **[Data Preprocessing dan Ekstraksi Fitur](preprocessing.md)**
   Menjelaskan tahapan pembersihan data dan penanganan outlier dengan metode *Interquartile Range* (IQR), imputasi kekosongan data menggunakan interpolasi linier, serta ekstraksi 68 ragam fitur *time series* komprehensif (domain Statistik, Temporal, dan Spektral) dengan menggunakan pustaka `tsfel`.

4. **[K-Means Clustering](kmeans-clustering.md)**
   Menyajikan rancangan eksperimen klasterisasi (*clustering*) baik berbasis visual dengan *workflow* KNIME maupun berbasis skrip Python, untuk membandingkan performa algoritma **K-Means**. Eksperimen ini membandingkan skenario pengelompokan pada data fitur asli melawan data fitur yang telah direduksi dimensinya menggunakan teknik **Principal Component Analysis (PCA)**.