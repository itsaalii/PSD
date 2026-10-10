# Panduan Ringkas Deployment Streamlit

File dokumentasi lengkap dengan format Jupyter Book telah dibuat di:
👉 [views/klasifikasi-spasial/panduan-deploy-streamlit.md](file:///e:/Kuliah/Akademik/Matkul/Semester%205/Proyek%20Sain%20Data/notes/views/klasifikasi-spasial/panduan-deploy-streamlit.md)

Aplikasi siap dijalankan di file:
👉 [streamlit_app.py](file:///e:/Kuliah/Akademik/Matkul/Semester%205/Proyek%20Sain%20Data/notes/streamlit_app.py)

---

## Cara Cepat Menjalankan di Komputer Lokal

1. Buka terminal di folder ini:
   ```bash
   streamlit run streamlit_app.py
   ```
2. Aplikasi akan otomatis terbuka di browser: `http://localhost:8501`.

---

## Fitur Dashboard Streamlit yang Telah Disiapkan

1. **🗺️ Tab 1: Peta Evaluasi Poligon (Vector & Prediksi)**:
   - Menampilkan `peta_klasifikasi_rf.html` (Cell 5 notebook).
   - Memvisualisasikan 6 kelas tutupan lahan poligon ground truth.
   - Outline biru untuk 83 poligon data uji dan outline oranye + ikon peringatan untuk poligon yang salah diprediksi.
   - Popup interaktif nilai spektral (NDVI, NDWI, jumlah piksel, probabilitas).
2. **🌏 Tab 2: Peta Regional Seluruh Jawa Timur (High-Res Raster)**:
   - Menampilkan `hasil_klasifikasi_random_forest.html` (Cell 7 notebook).
   - Resolusi tinggi ~1536 x 896 piksel (~200m per piksel) menutupi seluruh provinsi Jawa Timur.
   - Citra satelit Esri World Imagery (z=10) tertanam dengan layer klasifikasi semi-transparan (opasitas 65%).
3. **📊 Tab 3: Evaluasi Model & Feature Importance**:
   - Menampilkan gambar & tabel Confusion Matrix (akurasi 96.4%).
   - Menampilkan gambar & tabel Gini Feature Importance (dominansi band SWIR B11 dan NDBI).
4. **📋 Tab 4: Eksplorasi Data Uji & Ekspor CSV**:
   - Filter interaktif per kelas tutupan lahan dan per status kebenaran prediksi.
   - Tombol download data uji ke format CSV.

---

## Langkah Deploy ke Streamlit Community Cloud (Gratis)

1. Push repository Anda ke GitHub.
2. Buka [https://share.streamlit.io/](https://share.streamlit.io/) dan login dengan akun GitHub.
3. Klik **"New app"**, pilih repository dan branch Anda, serta tentukan `Main file path` ke `streamlit_app.py`.
4. Klik **"Deploy!"**.
