# Business Understanding

## 1. Latar Belakang
Kualitas udara merupakan salah satu indikator terpenting bagi kesehatan masyarakat dan kelestarian lingkungan. Seiring dengan peningkatan aktivitas manusia, mobilitas transportasi, dan kegiatan industri, potensi peningkatan konsentrasi gas polutan berbahaya di udara juga semakin besar. Kabupaten Nganjuk, sebagai salah satu wilayah yang terus berkembang di Jawa Timur, tidak luput dari potensi fluktuasi kualitas udara ini. 

Empat jenis gas polutan utama yang menjadi fokus pemantauan global adalah:
- **Nitrogen Dioksida (NO₂):** Sering dihasilkan oleh emisi kendaraan bermotor dan aktivitas industri.
- **Karbon Monoksida (CO):** Gas beracun hasil dari pembakaran yang tidak sempurna.
- **Belerang Dioksida (SO₂):** Polutan yang umumnya berasal dari aktivitas vulkanik atau pembakaran bahan bakar fosil yang mengandung sulfur.
- **Ozon (O₃):** Polutan sekunder yang terbentuk dari reaksi fotokimia antara oksida nitrogen (NOx) dan senyawa organik volatil (VOC) dengan bantuan sinar matahari.

Pemantauan polutan secara berkelanjutan sangat diperlukan untuk memahami pola polusi di suatu wilayah. Pada proyek ini, kita memanfaatkan teknologi satelit mutakhir, yaitu **Sentinel-5P** melalui _Copernicus Data Space Ecosystem_, untuk mengobservasi kadar polutan tersebut di udara Kabupaten Nganjuk dalam bentuk deret waktu (_Time Series_) selama periode **Agustus 2025 hingga Agustus 2026**.

## 2. Rumusan Masalah
Beberapa permasalahan utama yang ingin dijawab melalui analisis data ini adalah:
- Bagaimana tren konsentrasi harian gas polutan (NO₂, CO, SO₂, dan O₃) di wilayah Kabupaten Nganjuk?
- Apakah terdapat pola musiman, tren peningkatan jangka panjang, atau lonjakan (anomali) mendadak pada tingkat polusi udara di wilayah tersebut?

## 3. Tujuan Proyek
Tujuan dari eksplorasi sains data ini adalah:
- Mengotomatisasi pengumpulan data satelit spasial secara langsung ke dalam format tabular (CSV) yang siap dianalisis.
- Melakukan analisis data eksploratif (EDA) untuk mengidentifikasi perilaku dan tren perubahan gas polutan udara secara temporal.
- Menyediakan dasar data historis yang kuat untuk keperluan analisis prediktif (_forecasting_) kualitas udara di masa mendatang.

## 4. Manfaat Proyek
Hasil dari pengolahan data dan pemahaman ini diharapkan dapat memberikan dampak positif, antara lain:
- **Pemerintah / Pembuat Kebijakan:** Memberikan wawasan (_insight_) berbasis data sebagai landasan pengambilan keputusan terkait kebijakan lingkungan, pembatasan lalu lintas, atau pengawasan emisi.
- **Masyarakat:** Menjadi sumber informasi yang transparan untuk meningkatkan kesadaran warga mengenai fluktuasi kualitas udara harian di daerahnya.
- **Akademisi / Data Scientist:** Menyediakan referensi nyata (*use case*) penerapan metodologi pengolahan data spasial beresolusi tinggi ke dalam pemodelan _Time Series_.