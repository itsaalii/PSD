import pandas as pd
import json

# 1. Read the TSFEL CSV for NO2 to get actual values
df = pd.read_csv("data/polutan-baron/NO2_Baron_TSFEL.csv")
vals = df.iloc[0].to_dict()

# 2. Define the 68 features
features_meta = {
    # STATISTICAL
    "calc_max": ("Statistical", "Nilai maksimum dari deret waktu", r"$\max(x)$"),
    "calc_min": ("Statistical", "Nilai minimum dari deret waktu", r"$\min(x)$"),
    "calc_mean": ("Statistical", "Rata-rata (mean) dari deret waktu", r"$\mu = \frac{1}{N} \sum_{i=1}^N x_i$"),
    "calc_median": ("Statistical", "Nilai tengah (median) dari deret waktu", r"$\text{median}(x)$"),
    "calc_std": ("Statistical", "Standar deviasi, mengukur tingkat penyebaran data", r"$\sigma = \sqrt{\frac{1}{N} \sum_{i=1}^N (x_i - \mu)^2}$"),
    "calc_var": ("Statistical", "Varians, kuadrat dari standar deviasi", r"$\sigma^2 = \frac{1}{N} \sum_{i=1}^N (x_i - \mu)^2$"),
    "ecdf": ("Statistical", "Fungsi distribusi kumulatif empiris", r"$\hat{F}(t) = \frac{1}{N} \sum_{i=1}^N \mathbf{1}_{x_i \le t}$"),
    "ecdf_percentile": ("Statistical", "Nilai ECDF pada persentil tertentu", r"$P_{perc}(\hat{F})$"),
    "ecdf_percentile_count": ("Statistical", "Jumlah data yang berada di bawah persentil ECDF", r"$\sum \mathbf{1}_{x_i \le P_{perc}}$"),
    "ecdf_slope": ("Statistical", "Kemiringan dari kurva ECDF", r"$\frac{\Delta y}{\Delta x} \text{ pada } \hat{F}(t)$"),
    "hist_mode": ("Statistical", "Modus (nilai paling sering muncul) berdasarkan histogram", r"$\arg\max_j (\text{count}(bin_j))$"),
    "interq_range": ("Statistical", "Jangkauan interkuartil (IQR), selisih Q3 dan Q1", r"$IQR = Q_3 - Q_1$"),
    "kurtosis": ("Statistical", "Keruncingan (peakedness) dari distribusi data", r"$K = \frac{\frac{1}{N} \sum_{i=1}^N (x_i - \mu)^4}{\sigma^4} - 3$"),
    "skewness": ("Statistical", "Kemiringan (asimetri) dari distribusi data", r"$S = \frac{\frac{1}{N} \sum_{i=1}^N (x_i - \mu)^3}{\sigma^3}$"),
    "mean_abs_deviation": ("Statistical", "Rata-rata simpangan absolut dari mean", r"$MAD = \frac{1}{N} \sum_{i=1}^N |x_i - \mu|$"),
    "median_abs_deviation": ("Statistical", "Median dari simpangan absolut dari median", r"$\text{Median}(|x_i - \text{median}(x)|)$"),
    "rms": ("Statistical", "Root Mean Square (energi kuadrat rata-rata)", r"$RMS = \sqrt{\frac{1}{N} \sum_{i=1}^N x_i^2}$"),

    # TEMPORAL
    "abs_energy": ("Temporal", "Total energi absolut dari deret waktu", r"$E = \sum_{i=1}^N x_i^2$"),
    "auc": ("Temporal", "Area di bawah kurva sinyal (Area Under Curve)", r"$AUC = \sum_{i=1}^{N-1} \frac{x_i + x_{i+1}}{2}$"),
    "autocorr": ("Temporal", "Autokorelasi sinyal, kesamaan sinyal dengan versi tertundanya", r"$R(\tau) = \sum_{i=1}^{N-\tau} x_i x_{i+\tau}$"),
    "average_power": ("Temporal", "Daya rata-rata dari sinyal waktu", r"$P = \frac{1}{N} \sum_{i=1}^N x_i^2$"),
    "calc_centroid": ("Temporal", "Titik pusat dari urutan waktu (Time Centroid)", r"$C_t = \frac{\sum t_i \cdot x_i}{\sum x_i}$"),
    "dfa": ("Temporal", "Detrended Fluctuation Analysis, untuk mengukur dependensi fraktal", r"$F(n) \propto n^\alpha$"),
    "distance": ("Temporal", "Total jarak (panjang lintasan) antar titik-titik berturutan", r"$D = \sum_{i=1}^{N-1} \sqrt{1 + (x_{i+1} - x_i)^2}$"),
    "entropy": ("Temporal", "Shannon Entropy, mengukur ketidakpastian sinyal", r"$H = -\sum p(x) \log p(x)$"),
    "higuchi_fractal_dimension": ("Temporal", "Dimensi Fraktal Higuchi, mengukur kompleksitas bentuk", r"$L(k) \propto k^{-D}$"),
    "hurst_exponent": ("Temporal", "Eksponen Hurst, indikasi memori jangka panjang waktu", r"$E[\frac{R(n)}{S(n)}] = C n^H$"),
    "lempel_ziv": ("Temporal", "Kompleksitas Lempel-Ziv, mengukur tingkat kompresibilitas sinyal", r"$LZ = \frac{c(N)}{\frac{N}{\log N}}$"),
    "maximum_fractal_length": ("Temporal", "Panjang maksimal fraktal di berbagai skala pengukuran", r"$L_{max} = \max_k (L(k))$"),
    "mean_abs_diff": ("Temporal", "Rata-rata dari perbedaan absolut titik berurutan", r"$\mu_{\Delta} = \frac{1}{N-1} \sum_{i=1}^{N-1} |x_{i+1} - x_i|$"),
    "mean_diff": ("Temporal", "Rata-rata perbedaan antara titik berurutan", r"$\mu_{d} = \frac{1}{N-1} \sum_{i=1}^{N-1} (x_{i+1} - x_i)$"),
    "median_abs_diff": ("Temporal", "Median perbedaan absolut berurutan", r"$\text{Median}(|x_{i+1} - x_i|)$"),
    "median_diff": ("Temporal", "Median dari selisih titik berurutan", r"$\text{Median}(x_{i+1} - x_i)$"),
    "mse": ("Temporal", "Mean Squared Error dari sinyal terhadap rata-ratanya", r"$MSE = \frac{1}{N} \sum_{i=1}^N (x_i - \mu)^2$"),
    "negative_turning": ("Temporal", "Jumlah titik belok bergradien negatif (puncak yang turun)", r"$\sum \mathbf{1}_{x_{i-1} < x_i > x_{i+1}}$"),
    "neighbourhood_peaks": ("Temporal", "Jumlah puncak pada area bertetangga yang ditentukan", r"$\sum \text{Peaks}(x, \text{window})$"),
    "petrosian_fractal_dimension": ("Temporal", "Dimensi Fraktal Petrosian", r"$D = \frac{\log_{10}(N)}{\log_{10}(N) + \log_{10}(\frac{N}{N + 0.4 N_{\Delta}})}$"),
    "pk_pk_distance": ("Temporal", "Jarak dari puncak tertinggi ke lembah terendah (Peak-to-Peak)", r"$P2P = \max(x) - \min(x)$"),
    "positive_turning": ("Temporal", "Jumlah titik belok bergradien positif (lembah yang naik)", r"$\sum \mathbf{1}_{x_{i-1} > x_i < x_{i+1}}$"),
    "slope": ("Temporal", "Kemiringan tren regresi linier secara keseluruhan", r"$m = \frac{\sum (t_i - \bar{t})(x_i - \mu)}{\sum (t_i - \bar{t})^2}$"),
    "sum_abs_diff": ("Temporal", "Total akumulasi perbedaan absolut titik berurutan", r"$SAD = \sum_{i=1}^{N-1} |x_{i+1} - x_i|$"),
    "zero_cross": ("Temporal", "Jumlah titik perpotongan nol (zero-crossing)", r"$\sum \mathbf{1}_{x_i \cdot x_{i+1} < 0}$"),

    # SPECTRAL
    "fundamental_frequency": ("Spectral", "Frekuensi dasar yang paling kuat pada spektrum", r"$f_0 = \arg\max_f (|X(f)|^2)$"),
    "max_frequency": ("Spectral", "Frekuensi tertinggi pada analisis spektrum daya", r"$f_{max} = \max(f)$"),
    "median_frequency": ("Spectral", "Frekuensi yang membagi spektrum daya (energi) menjadi dua bagian sama", r"$\int_0^{f_{med}} |X(f)|^2 df = \frac{1}{2} \int_0^\infty |X(f)|^2 df$"),
    "human_range_energy": ("Spectral", "Energi sinyal pada jangkauan pendengaran manusia", r"$E_h = \sum_{f \in H} |X(f)|^2$"),
    "lpcc": ("Spectral", "Koefisien Linear Prediction Cepstral (LPCC)", r"$C_n = -a_n - \sum_{k=1}^{n-1} \frac{k}{n} C_k a_{n-k}$"),
    "mfcc": ("Spectral", "Koefisien Mel-Frequency Cepstral (MFCC)", r"$c_n = \sum_{k=1}^K (\log S_k) \cos\left[n(k-\frac{1}{2})\frac{\pi}{K}\right]$"),
    "max_power_spectrum": ("Spectral", "Daya tertinggi dari seluruh rentang spektrum frekuensi", r"$\max_f (|X(f)|^2)$"),
    "power_bandwidth": ("Spectral", "Lebar pita tempat akumulasi mayoritas kekuatan sinyal (daya)", r"$BW = f_{upper} - f_{lower}$"),
    "spectral_centroid": ("Spectral", "Pusat massa spektral (frekuensi rata-rata berbobot energi)", r"$C_s = \frac{\sum f_k |X(f_k)|}{\sum |X(f_k)|}$"),
    "spectral_decrease": ("Spectral", "Tingkat penurunan kekuatan spektral pada frekuensi yang meninggi", r"$D_s = \frac{\sum_{k=2}^K \frac{|X(f_k)| - |X(f_1)|}{k-1}}{\sum_{k=2}^K |X(f_k)|}$"),
    "spectral_distance": ("Spectral", "Jarak spektral, selisih antar kurva densitas spektrum", r"$D(X, Y) = \sqrt{\sum (X(f) - Y(f))^2}$"),
    "spectral_entropy": ("Spectral", "Entropi spektral, seberapa menyebar distribusi energi spektrum", r"$H_s = -\sum p_f \log p_f$"),
    "spectral_kurtosis": ("Spectral", "Kurtosis dari kepadatan daya spektrum", r"$K_s = \frac{\sum (f - C_s)^4 |X(f)|^2}{(\sum (f - C_s)^2 |X(f)|^2)^2}$"),
    "spectral_positive_turning": ("Spectral", "Titik belok positif pada kurva spektrum", r"$\sum \mathbf{1}_{|X(f_{i-1})| > |X(f_i)| < |X(f_{i+1})|}$"),
    "spectral_roll_off": ("Spectral", "Frekuensi roll-off di mana sebagian besar energi spektral terkonsentrasi", r"$f_c \text{ dimana } \sum_{f=0}^{f_c} |X(f)|^2 = 0.95 \sum_{f} |X(f)|^2$"),
    "spectral_roll_on": ("Spectral", "Frekuensi roll-on tempat sebagian kecil energi (misal 5%) terakumulasi", r"$f_c \text{ dimana } \sum_{f=0}^{f_c} |X(f)|^2 = 0.05 \sum_{f} |X(f)|^2$"),
    "spectral_skewness": ("Spectral", "Skewness (kemiringan) dari kepadatan daya spektrum", r"$S_s = \frac{\sum (f - C_s)^3 |X(f)|^2}{(\sum (f - C_s)^2 |X(f)|^2)^{3/2}}$"),
    "spectral_slope": ("Spectral", "Kemiringan dari spektrum daya yang dihitung menggunakan regresi linier", r"$m_s = \frac{\sum (f_i - \bar{f})(|X(f_i)| - \overline{|X(f)|})}{\sum (f_i - \bar{f})^2}$"),
    "spectral_spread": ("Spectral", "Sebaran spektrum atau varians frekuensi di sekeliling pusat massa", r"$V_s = \sqrt{\frac{\sum (f_k - C_s)^2 |X(f_k)|}{\sum |X(f_k)|}}$"),
    "spectral_variation": ("Spectral", "Variasi atau jarak perubahan spektrum pada titik yang berdekatan", r"$V = 1 - \frac{\sum X_{t-1}(f) X_t(f)}{\sqrt{\sum X_{t-1}^2 \sum X_t^2}}$"),
    "spectrogram_mean_coeff": ("Spectral", "Koefisien magnitudo rata-rata dari matriks spektrogram", r"$\frac{1}{T F} \sum_t \sum_f |S(t, f)|$"),
    "wavelet_abs_mean": ("Spectral", "Rata-rata magnitudo absolut dari koefisien transformasi wavelet", r"$\mu_w = \frac{1}{N} \sum |W(a,b)|$"),
    "wavelet_energy": ("Spectral", "Energi total yang terkandung di dalam koefisien wavelet", r"$E_w = \sum |W(a,b)|^2$"),
    "wavelet_entropy": ("Spectral", "Entropi wavelet, ukuran distribusi sebaran energi di ruang waktu-frekuensi", r"$H_w = -\sum p_j \log p_j, p_j = \frac{E_j}{E_{tot}}$"),
    "wavelet_std": ("Spectral", "Standar deviasi dari sebaran koefisien wavelet", r"$\sigma_w = \sqrt{\frac{1}{N} \sum (|W(a,b)| - \mu_w)^2}$"),
    "wavelet_var": ("Spectral", "Varians dari koefisien dispersi wavelet", r"$\sigma_w^2$"),
}

# Add any missing features from `vals` to Spectral (or other domain if obvious) just to be safe
for f in vals:
    if f not in features_meta:
        features_meta[f] = ("Spectral", "Fitur spektral", r"")

# 3. Generate Markdown content
md_lines = []
md_lines.append("## Penjelasan Domain TSFEL\n")
md_lines.append("Pustaka TSFEL membagi 68 fitur deret waktu menjadi tiga domain utama: **Statistik (Statistical)**, **Waktu (Temporal)**, dan **Frekuensi (Spectral)**. Berikut adalah penjabaran lengkap untuk masing-masing fitur beserta rumusnya, serta hasil perhitungannya yang diterapkan pada polutan NO2 (dari `NO2_filed.csv`) yang disajikan pada hasil akhir (`NO2_Baron_TSFEL.csv`).\n")

domains = ["Statistical", "Temporal", "Spectral"]
domain_desc = {
    "Statistical": "Domain statistik mengekstrak metrik kuantitatif dan karakteristik sebaran serta bentuk distribusi dari sinyal deret waktu. Domain ini terdiri dari 17 fitur utama yang fokus pada distribusi.",
    "Temporal": "Domain temporal mengevaluasi sinyal dari segi urutan waktunya. Terdiri dari 25 fitur yang mengukur dependensi, jarak, autokorelasi, dan kompleksitas waktu.",
    "Spectral": "Domain spektral mentransformasi data ke domain frekuensi (melalui Fourier/Wavelet). Terdiri dari 26 fitur untuk mengukur sifat periodik, energi spektrum, dan rentang frekuensi."
}

domain_num = 1
for d in domains:
    md_lines.append(f"### {domain_num}. Domain {d}")
    md_lines.append(f"{domain_desc[d]}\n")
    
    # Filter features for this domain
    domain_features = {k: v for k, v in features_meta.items() if v[0] == d}
    
    item_num = 1
    for f_name, f_info in domain_features.items():
        desc = f_info[1]
        latex = f_info[2]
        # format value
        val = vals[f_name]
        val_str = f"{val:.5e}" if isinstance(val, float) else str(val)
        
        md_lines.append(f"{item_num}. **`{f_name}`**")
        md_lines.append(f"   - **Penjelasan**: {desc}.")
        md_lines.append(f"   - **Rumus**: {latex}")
        md_lines.append(f"   - **Hasil (NO2)**: `{val_str}`\n")
        
        item_num += 1
    domain_num += 1

new_content = "\n".join(md_lines)

# 4. Read the markdown file and replace the old section
with open("views/polutan-baron/preprocessing.md", "r", encoding="utf-8") as f:
    content = f.read()

# Find the start of the old section
idx = content.find("## Penjelasan Domain TSFEL")
if idx != -1:
    content = content[:idx] + new_content
else:
    content = content + "\n\n" + new_content

with open("views/polutan-baron/preprocessing.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Berhasil mengupdate preprocessing.md!")
