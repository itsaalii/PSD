# Business Understanding

## Latar Belakang

Polusi udara merupakan salah satu masalah lingkungan utama yang berdampak pada kesehatan manusia dan ekosistem. Pemantauan kualitas udara, khususnya tingkat konsentrasi gas polutan seperti Karbon Monoksida (CO), Sulfur Dioksida (SO₂), dan Nitrogen Dioksida (NO₂), sangat penting dilakukan untuk mengetahui kondisi lingkungan di suatu wilayah. Pada proyek ini, wilayah yang menjadi titik pengamatan (Area of Interest) difokuskan pada Kecamatan Baron, Kabupaten Nganjuk.

Seiring berjalannya waktu, data deret waktu (time series) dari konsentrasi polutan udara seringkali menunjukkan pola fluktuasi tertentu yang dipengaruhi oleh berbagai aktivitas, seperti transportasi, industri, atau faktor cuaca/alam. Namun, data mentah satelit seringkali memiliki kualitas yang kurang baik akibat adanya nilai yang hilang (missing values) atau pencilan (outliers). Oleh karena itu, diperlukan tahapan pemrosesan data yang tepat agar informasi yang tersimpan dapat digali secara maksimal.

## Tujuan Proyek

1. **Eksplorasi dan Pembersihan Data**: Mengidentifikasi dan menangani *missing values* serta nilai anomali (*outliers*) pada data konsentrasi polutan (CO, SO₂, dan NO₂) agar menghasilkan data deret waktu yang konsisten dan siap dianalisis.
2. **Ekstraksi Fitur Deret Waktu**: Menerapkan ekstraksi fitur komprehensif menggunakan modul `tsfel` untuk menghasilkan representasi fitur statistik, temporal, dan spektral dari pergerakan polutan udara.
3. **Pengelompokan (Klasterisasi) Profil Polutan**: Menggunakan algoritma *machine learning* tak berpandu (*unsupervised learning*), yaitu K-Means Clustering, untuk mengelompokkan pola polusi.
4. **Analisis Reduksi Dimensi**: Menguji efektivitas metode reduksi dimensi *Principal Component Analysis* (PCA) dalam mengatasi kompleksitas data berdimensi tinggi tanpa menghilangkan karakteristik penting dari data asli polutan udara.

## Manfaat Analisis (Business Value)

Melalui pemahaman karakteristik dan pengelompokan (*clustering*) fitur dari ketiga jenis polutan ini, pemangku kepentingan (*stakeholders*) maupun peneliti dapat:
- Mengidentifikasi profil atau tingkat keparahan polusi udara di Kecamatan Baron dari waktu ke waktu.
- Membantu pemerintah atau instansi lingkungan hidup setempat dalam memantau tren anomali serta merumuskan kebijakan yang tepat guna meminimalisir dampak polusi.
- Memberikan kerangka kerja (*framework*) berbasis *data science* yang utuh—mulai dari ekstraksi fitur deret waktu hingga klasterisasi—yang dapat direplikasi untuk analisis wilayah atau jenis polutan yang lain.
