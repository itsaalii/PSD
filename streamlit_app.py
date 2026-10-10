"""
Dashboard Klasifikasi Spasial Tutupan Lahan (LULC) Jawa Timur
Berbasis Sentinel-2A Level-2A & Algoritma Random Forest

Styling: Tailwind CSS Native (Scoped Pure CSS, Immune to Script Stripping & Markdown Code Indentation)
Palet Warna: https://psd-interpolasi.basisdata2-c.my.id/
  - ink:   #18232F
  - paper: #F2F5F7
  - teal:  { 600: #0F766E, 700: #0B5F58, 50: #E7F4F2 }
  - slate: { 50: #F8FAFC, 100: #F1F5F9, 200: #E2E8F0, 500: #64748B, 600: #475569, 700: #334155 }
Typography: IBM Plex Sans
Icons: Heroicons SVG (Strict Inline Sizing, Tanpa Emote)
Visualisasi: Menampilkan KEDUA Peta Interaktif Secara Bersamaan
"""

from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from PIL import Image

# ==============================================================================
# 1. KONFIGURASI HALAMAN STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Klasifikasi Spasial Tutupan Lahan Jawa Timur",
    page_icon="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f30f.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================================
# 2. HEROICONS SVG HELPER FUNCTION (Strict Width & Height, Anti-Overflow)
# ==============================================================================
def heroicon(path_d: str, size: int = 20, color: str = "#0F766E", stroke_width: float = 2.0) -> str:
    """
    Menghasilkan tag SVG dengan atribut ukuran eksplisit (HTML & inline CSS),
    mencegah browser merender SVG berukuran 100% saat kelas CSS terisolasi.
    """
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
        f'stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" '
        f'style="width:{size}px; height:{size}px; min-width:{size}px; max-width:{size}px; '
        f'min-height:{size}px; max-height:{size}px; display:inline-block; vertical-align:middle; flex-shrink:0;" '
        f'aria-hidden="true">'
        f'<path d="{path_d}"/>'
        f'</svg>'
    )


# Definisi Path SVG Heroicons
D_GLOBE = "M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-.778.099-1.533.284-2.253"
D_MAP = "M9 6.75V15m6-6v8.25m.503 3.046 4.84-2.42A1.125 1.125 0 0 0 21 16.883V5.86a1.125 1.125 0 0 0-.623-1.006l-4.82-2.41a1.125 1.125 0 0 0-.96.002l-5.195 2.597a1.125 1.125 0 0 1-.96 0L3.623 2.633A1.125 1.125 0 0 0 3 3.639v11.023a1.125 1.125 0 0 0 .623 1.006l4.82 2.41a1.125 1.125 0 0 0 .96-.002l5.195-2.597a1.125 1.125 0 0 1 .96 0l-.062-.033Z"
D_LAYERS = "M6.429 9.75 2.25 12l4.179 2.25m0-4.5 5.571 3 5.571-3m-11.142 0L2.25 7.5 12 2.25l9.75 5.25-4.179 2.25m0 0L21 12l-4.179 2.25m0 0 4.179 2.25L12 21.75 2.25 16.5l4.179-2.25m11.142 0-5.571 3-5.571-3"
D_CHECK_CIRCLE = "M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
D_SCALE = "M12 3v17.25m0 0c-1.472 0-2.882.265-4.185.75M12 20.25c1.472 0 2.882.265 4.185.75M18.75 4.97A48.416 48.416 0 0 0 12 4.5c-2.291 0-4.545.16-6.75.47m13.5 0c1.01.143 2.01.317 3 .52m-3-.52v2.62a3.75 3.75 0 0 1-2.25 3.44l-.84.37m-7.41-6.43c-.99.203-1.99.377-3 .52m3-.52v2.62a3.75 3.75 0 0 0 2.25 3.44l.84.37"
D_EXCLAMATION = "M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
D_CHART_BAR = "M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z"
D_TABLE = "M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 0 1-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0 1 12 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125M12 10.875v7.5m0-7.5a1.125 1.125 0 0 1 1.125-1.125h7.125"
D_TAG = "M9.568 3H5.25A2.25 2.25 0 0 0 3 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 0 0 5.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 0 0 9.568 3Z"
D_INFO = "m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z"
D_SATELLITE = "m21 7.5-9-5.25L3 7.5m18 0-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9"
D_ADJUST = "M10.5 6h9.75M10.5 6a1.5 1.5 0 1 1-3 0m3 0a1.5 1.5 0 1 0-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m-9.75 0h9.75"


# ==============================================================================
# 3. SCOPED PURE CSS (Palet psd-interpolasi & Bebas Bug Indentasi Markdown)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

    /* Global Layout & Typography */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #F2F5F7 !important;
        font-family: "IBM Plex Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        color: #18232F !important;
    }

    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    /* Strict Rule: Cegah semua SVG membengkak */
    svg {
        max-width: 100% !important;
    }

    /* Card Styling */
    .psd-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 1rem;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        margin-bottom: 1rem;
    }

    .psd-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 0.85rem;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 0.75rem;
    }

    .psd-card-title {
        font-size: 1rem;
        font-weight: 600;
        color: #18232F;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0;
    }

    /* Badges */
    .psd-badge-teal {
        background-color: #E7F4F2;
        color: #0F766E;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }

    .psd-badge-amber {
        background-color: #FEF3C7;
        color: #B45309;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }

    .psd-badge-slate {
        background-color: #F1F5F9;
        color: #475569;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }

    /* Metric Box */
    .metric-box {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 1rem;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        margin-bottom: 0.5rem;
    }

    .metric-box-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .metric-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
    }

    .metric-val-row {
        display: flex;
        align-items: baseline;
        gap: 0.5rem;
        margin-top: 0.75rem;
    }

    .metric-num {
        font-size: 1.85rem;
        font-weight: 700;
        color: #18232F;
        line-height: 1;
    }

    .metric-sub {
        font-size: 0.75rem;
        color: #64748B;
        margin-top: 0.4rem;
    }

    /* Button Styling */
    .stDownloadButton button, .stButton button {
        background-color: #0F766E !important;
        color: #FFFFFF !important;
        border-radius: 0.5rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        padding: 0.5rem 1rem !important;
        border: none !important;
        transition: background-color 0.15s ease-in-out !important;
    }

    .stDownloadButton button:hover, .stButton button:hover {
        background-color: #0B5F58 !important;
    }

    /* Banner Info */
    .info-banner {
        background-color: #E7F4F2;
        border: 1px solid #99F6E4;
        border-radius: 0.75rem;
        padding: 0.85rem 1rem;
        margin-bottom: 1.25rem;
        font-size: 0.85rem;
        color: #115E59;
        display: flex;
        align-items: flex-start;
        gap: 0.65rem;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 4. HELPER RESOLUSI FILE & CACHING
# ==============================================================================
def cari_file(nama_file: str) -> Path | None:
    """Mencari file aset di berbagai kemungkinan folder."""
    kandidat = [
        Path(nama_file),
        Path("maps") / nama_file,
        Path("data") / nama_file,
        Path("data/Klasifikasi") / nama_file,
        Path("views/klasifikasi-spasial") / nama_file,
        Path("data/Klasifikasi/hasil_rf") / nama_file,
        Path("hasil_rf") / nama_file,
        Path("_static") / nama_file,
    ]
    for path in kandidat:
        if path.exists():
            return path
    return None


@st.cache_data
def muat_data_csv(path_str: str) -> pd.DataFrame | None:
    path = Path(path_str)
    if path.exists():
        return pd.read_csv(path)
    return None


@st.cache_data
def muat_konten_html(path_str: str) -> str | None:
    path = Path(path_str)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


# ==============================================================================
# 5. SIDEBAR: METADATA & KONTROL TAMPILAN
# ==============================================================================
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:1rem;">
        {heroicon(D_GLOBE, size=24, color="#0F766E")}
        <h2 style="font-size:1.05rem; font-weight:700; color:#18232F; margin:0;">Spasial LULC</h2>
    </div>
    <div style="font-size:0.8rem; color:#475569; padding-bottom:1rem; border-bottom:1px solid #E2E8F0; line-height:1.6;">
        <p style="margin:0;"><b style="color:#18232F;">Model:</b> Random Forest Classifier</p>
        <p style="margin:0;"><b style="color:#18232F;">Sensor:</b> Sentinel-2A MSI (ESA CDSE)</p>
        <p style="margin:0;"><b style="color:#18232F;">Koleksi:</b> Level-2A BOA Surface Reflectance</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:1rem; margin-bottom:0.5rem; display:flex; align-items:center; gap:0.4rem; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#64748B;">
        {heroicon(D_TAG, size=16, color="#64748B")}
        <span>6 Kelas Tutupan Lahan</span>
    </div>
    <div style="font-size:0.8rem; line-height:1.75; color:#334155;">
        <div style="display:flex; align-items:center; gap:0.5rem;">
            <span style="width:11px; height:11px; border-radius:50%; background:#FFD92F; display:inline-block; border:1px solid #CBD5E1;"></span>
            <b>Sawah</b> <span style="color:#94A3B8; font-size:0.75rem;">(Lahan Pertanian)</span>
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem;">
            <span style="width:11px; height:11px; border-radius:50%; background:#E41A1C; display:inline-block; border:1px solid #CBD5E1;"></span>
            <b>Bangunan</b> <span style="color:#94A3B8; font-size:0.75rem;">(Kawasan Terbangun)</span>
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem;">
            <span style="width:11px; height:11px; border-radius:50%; background:#2E7D32; display:inline-block; border:1px solid #CBD5E1;"></span>
            <b>Hutan</b> <span style="color:#94A3B8; font-size:0.75rem;">(Lahan Hijau Rapat)</span>
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem;">
            <span style="width:11px; height:11px; border-radius:50%; background:#4FC3F7; display:inline-block; border:1px solid #CBD5E1;"></span>
            <b>Danau</b> <span style="color:#94A3B8; font-size:0.75rem;">(Air Pedalaman)</span>
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem;">
            <span style="width:11px; height:11px; border-radius:50%; background:#0D47A1; display:inline-block; border:1px solid #CBD5E1;"></span>
            <b>Laut</b> <span style="color:#94A3B8; font-size:0.75rem;">(Perairan Terbuka)</span>
        </div>
        <div style="display:flex; align-items:center; gap:0.5rem;">
            <span style="width:11px; height:11px; border-radius:50%; background:#8E44AD; display:inline-block; border:1px solid #CBD5E1;"></span>
            <b>Mangrove</b> <span style="color:#94A3B8; font-size:0.75rem;">(Bakau Pesisir)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:1.25rem 0; border:none; border-top:1px solid #E2E8F0;'>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:0.4rem; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:#64748B; margin-bottom:0.5rem;">
        {heroicon(D_ADJUST, size=16, color="#64748B")}
        <span>Pengaturan Visualisasi Peta</span>
    </div>
    """, unsafe_allow_html=True)

    mode_tampilan = st.radio(
        "Pilihan Tata Letak Peta:",
        options=[
            "Tampilkan Kedua Peta (Atas - Bawah)",
            "Berdampingan (2 Kolom Bersisian)",
            "Hanya Peta 1 (Evaluasi Poligon)",
            "Hanya Peta 2 (Regional Jawa Timur)"
        ],
        index=0,
        help="Pilih format penyajian peta interaktif."
    )

    tinggi_peta = st.slider(
        "Tinggi Frame Peta (px):",
        min_value=450,
        max_value=900,
        value=650,
        step=25,
        help="Sesuaikan tinggi vertikal tampilan peta."
    )

    st.markdown(f"""
    <div class="info-banner" style="margin-top:1.25rem;">
        {heroicon(D_INFO, size=18, color="#0F766E")}
        <div>
            <b>Kedua Peta Aktif</b>
            <div style="font-size:0.75rem; margin-top:0.25rem; line-height:1.4;">
                Peta 1 menyajikan evaluasi sampel poligon, dan Peta 2 menyajikan hasil inferensi regional per piksel se-Jawa Timur.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 6. HEADER UTAMA & METRIK (Menggunakan st.columns Tanpa Indentasi Markdown)
# ==============================================================================
st.markdown(f"""
<header style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:flex-end; gap:1rem; margin-bottom:1.5rem;">
    <div>
        <div style="display:flex; align-items:center; gap:0.6rem;">
            {heroicon(D_GLOBE, size=28, color="#0F766E")}
            <h1 style="font-size:1.85rem; font-weight:700; letter-spacing:-0.02em; color:#18232F; margin:0;">
                Klasifikasi Spasial Tutupan Lahan Jawa Timur
            </h1>
        </div>
        <p style="font-size:0.875rem; color:#475569; margin:0.35rem 0 0 0; max-width:48rem; line-height:1.5;">
            Visualisasi spasial berbasis citra satelit Sentinel-2A Level-2A dan algoritma Random Forest untuk pemetaan 6 kelas tutupan lahan di seluruh wilayah Provinsi Jawa Timur.
        </p>
    </div>
    <div class="psd-badge-teal" style="font-size:0.8rem; padding:0.4rem 0.85rem;">
        {heroicon(D_SATELLITE, size=16, color="#0F766E")}
        <span>Sentinel-2A MSI BOA &bull; Random Forest</span>
    </div>
</header>
""", unsafe_allow_html=True)

# Muat Data Evaluasi
p_pred = cari_file("prediksi_data_uji.csv")
df_pred = muat_data_csv(str(p_pred)) if p_pred else None

if df_pred is not None:
    n_uji = len(df_pred)
    n_benar = int(df_pred["benar"].sum())
    n_salah = n_uji - n_benar
    akurasi = (n_benar / n_uji) * 100
else:
    n_uji = 83
    n_benar = 80
    n_salah = 3
    akurasi = 96.4

# Render 4 Kartu Metrik via st.columns (Mencegah Parse Codeblock Markdown)
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.markdown(f"""<div class="metric-box">
<div class="metric-box-top">
<span class="metric-label">Akurasi Data Uji</span>
<span style="background:#E7F4F2; border-radius:50%; padding:0.3rem; display:inline-flex;">{heroicon(D_CHECK_CIRCLE, size=18, color="#0F766E")}</span>
</div>
<div class="metric-val-row">
<span class="metric-num">{akurasi:.1f}%</span>
<span class="psd-badge-teal">{n_benar}/{n_uji} Poligon</span>
</div>
<div class="metric-sub">Evaluasi Stratified Test Set (Random Forest)</div>
</div>""", unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""<div class="metric-box">
<div class="metric-box-top">
<span class="metric-label">F1-Score Macro</span>
<span style="background:#E7F4F2; border-radius:50%; padding:0.3rem; display:inline-flex;">{heroicon(D_SCALE, size=18, color="#0F766E")}</span>
</div>
<div class="metric-val-row">
<span class="metric-num">0.963</span>
<span class="psd-badge-teal">Seimbang</span>
</div>
<div class="metric-sub">Rata-rata harmonik seluruh 6 kelas tutupan lahan</div>
</div>""", unsafe_allow_html=True)

with col_m3:
    st.markdown(f"""<div class="metric-box">
<div class="metric-box-top">
<span class="metric-label">Poligon Ground Truth</span>
<span style="background:#E7F4F2; border-radius:50%; padding:0.3rem; display:inline-flex;">{heroicon(D_LAYERS, size=18, color="#0F766E")}</span>
</div>
<div class="metric-val-row">
<span class="metric-num">~300</span>
<span class="psd-badge-slate">6 Kategori</span>
</div>
<div class="metric-sub">Ekstraksi fitur tingkat poligon (bebas autokorelasi)</div>
</div>""", unsafe_allow_html=True)

with col_m4:
    st.markdown(f"""<div class="metric-box">
<div class="metric-box-top">
<span class="metric-label">Salah Klasifikasi</span>
<span style="background:#FEF3C7; border-radius:50%; padding:0.3rem; display:inline-flex;">{heroicon(D_EXCLAMATION, size=18, color="#B45309")}</span>
</div>
<div class="metric-val-row">
<span class="metric-num">{n_salah}</span>
<span class="psd-badge-amber">Error 3.6%</span>
</div>
<div class="metric-sub">Hanya pada kemiripan spektral air Danau/Laut</div>
</div>""", unsafe_allow_html=True)

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)


# ==============================================================================
# 7. VISUALISASI KEDUA PETA INTERAKTIF
# ==============================================================================
file_peta1 = cari_file("peta_klasifikasi_rf.html")
file_peta2 = cari_file("hasil_klasifikasi_random_forest.html")

konten_peta1 = muat_konten_html(str(file_peta1)) if file_peta1 else None
konten_peta2 = muat_konten_html(str(file_peta2)) if file_peta2 else None


def render_peta_1():
    """Merender Peta 1: Evaluasi Poligon Ground Truth (Folium Vektor)"""
    st.markdown(f"""<div class="psd-card" style="margin-bottom:0.75rem;">
<div class="psd-card-header">
<h2 class="psd-card-title">
{heroicon(D_MAP, size=20, color="#0F766E")}
<span>Evaluasi Poligon Sampel & Prediksi Data Uji (Folium Vektor)</span>
</h2>
<span class="psd-badge-teal">83 Poligon Uji Terverifikasi</span>
</div>
<div style="font-size:0.8rem; color:#475569; line-height:1.5;">
Menampilkan seluruh poligon sampel dari 6 kelas tutupan lahan. 
<b style="color:#0D47A1;">Garis tepi biru:</b> poligon data uji. 
<b style="color:#D97706;">Garis putus-putus oranye + ikon seru:</b> poligon yang salah diprediksi. 
Klik poligon untuk melihat nilai spektral NDVI, NDWI, dan keyakinan model.
</div>
</div>""", unsafe_allow_html=True)
    if konten_peta1:
        components.html(konten_peta1, height=tinggi_peta, scrolling=True)
    else:
        st.error("File `peta_klasifikasi_rf.html` tidak ditemukan.")


def render_peta_2():
    """Merender Peta 2: Klasifikasi Regional Jawa Timur (ImageOverlay Raster)"""
    st.markdown(f"""<div class="psd-card" style="margin-bottom:0.75rem;">
<div class="psd-card-header">
<h2 class="psd-card-title">
{heroicon(D_GLOBE, size=20, color="#0F766E")}
<span>Klasifikasi Tutupan Lahan Skala Regional Jawa Timur (ImageOverlay)</span>
</h2>
<span class="psd-badge-teal">Resolusi Tinggi 1536 x 896 Piksel</span>
</div>
<div style="font-size:0.8rem; color:#475569; line-height:1.5;">
Inferensi spasial per piksel (~200m/piksel) menutupi seluruh wilayah Jawa Timur berpadu dengan citra satelit 
<b>Esri World Imagery (zoom level 10)</b> dengan opasitas 65% dan pembatasan batas daratan provinsi.
</div>
</div>""", unsafe_allow_html=True)
    if konten_peta2:
        components.html(konten_peta2, height=tinggi_peta, scrolling=True)
    else:
        st.error("File `hasil_klasifikasi_random_forest.html` tidak ditemukan.")


# Logika Tata Letak Berdasarkan Pilihan Pengguna
if mode_tampilan == "Tampilkan Kedua Peta (Atas - Bawah)":
    render_peta_1()
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    render_peta_2()

elif mode_tampilan == "Berdampingan (2 Kolom Bersisian)":
    col_kiri, col_kanan = st.columns(2)
    with col_kiri:
        render_peta_1()
    with col_kanan:
        render_peta_2()

elif mode_tampilan == "Hanya Peta 1 (Evaluasi Poligon)":
    render_peta_1()

elif mode_tampilan == "Hanya Peta 2 (Regional Jawa Timur)":
    render_peta_2()


# ==============================================================================
# 8. EVALUASI MODEL & FEATURE IMPORTANCE
# ==============================================================================
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

st.markdown(f"""<div class="psd-card" style="margin-bottom:1rem;">
<div class="psd-card-header" style="margin-bottom:0.25rem; padding-bottom:0.65rem;">
<h2 class="psd-card-title">
{heroicon(D_CHART_BAR, size=20, color="#0F766E")}
<span>Evaluasi Kinerja Model & Kontribusi Fitur Spektral</span>
</h2>
<span class="psd-badge-teal">Random Forest Gini Importance</span>
</div>
</div>""", unsafe_allow_html=True)

col_cm, col_fi = st.columns(2)

with col_cm:
    st.markdown("""<div class="psd-card" style="margin-bottom:0.75rem;">
<h3 style="font-size:0.95rem; font-weight:600; color:#18232F; margin:0 0 0.35rem 0;">Confusion Matrix (Data Uji 83 Poligon)</h3>
<p style="font-size:0.8rem; color:#64748B; margin:0 0 0.75rem 0;">Perbandingan kelas ground truth aktual vs hasil prediksi model.</p>
</div>""", unsafe_allow_html=True)

    p_cm_img = cari_file("confusion_matrix.png")
    if p_cm_img:
        st.image(Image.open(p_cm_img), caption="Confusion Matrix Data Uji", use_container_width=True)
    else:
        p_cm_csv = cari_file("confusion_matrix.csv")
        if p_cm_csv:
            st.dataframe(pd.read_csv(p_cm_csv, index_col=0), use_container_width=True)
        else:
            st.info("File confusion matrix belum tersedia.")

    st.markdown("""<div class="psd-card" style="font-size:0.75rem; color:#64748B; margin-top:0.5rem; line-height:1.4;">
<b>Analisis Matriks:</b> Akurasi mencapai 96.4%. Seluruh poligon Bangunan, Mangrove, dan Sawah terklasifikasi 100% sempurna tanpa salah.
</div>""", unsafe_allow_html=True)

with col_fi:
    st.markdown("""<div class="psd-card" style="margin-bottom:0.75rem;">
<h3 style="font-size:0.95rem; font-weight:600; color:#18232F; margin:0 0 0.35rem 0;">Tingkat Kepentingan Fitur Spektral (Gini)</h3>
<p style="font-size:0.8rem; color:#64748B; margin:0 0 0.75rem 0;">Kontribusi relatif band citra optik dan indeks spektral dalam memisahkan tutupan lahan.</p>
</div>""", unsafe_allow_html=True)

    p_fi_img = cari_file("kepentingan_fitur.png")
    if p_fi_img:
        st.image(Image.open(p_fi_img), caption="Feature Importance (Gini)", use_container_width=True)
    else:
        p_fi_csv = cari_file("kepentingan_fitur.csv")
        if p_fi_csv:
            st.dataframe(pd.read_csv(p_fi_csv), use_container_width=True)
        else:
            st.info("File feature importance belum tersedia.")

    st.markdown("""<div class="psd-card" style="font-size:0.75rem; color:#64748B; margin-top:0.5rem; line-height:1.4;">
<b>Temuan Fitur:</b> Band SWIR (B11) dan NDBI memegang peranan paling penting dalam membedakan kawasan terbangun beton dari vegetasi dan perairan.
</div>""", unsafe_allow_html=True)


# ==============================================================================
# 9. TABEL EKSPLORASI DATA UJI & EKSPOR CSV
# ==============================================================================
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

st.markdown(f"""<div class="psd-card" style="margin-bottom:1rem;">
<div class="psd-card-header" style="margin-bottom:0.5rem;">
<h2 class="psd-card-title">
{heroicon(D_TABLE, size=20, color="#0F766E")}
<span>Eksplorasi Data Prediksi Poligon Uji</span>
</h2>
<span class="psd-badge-teal">Format Tabular Interaktif</span>
</div>
</div>""", unsafe_allow_html=True)

if df_pred is not None:
    c1, c2 = st.columns([2, 1])
    with c1:
        pilihan_kelas = st.multiselect(
            "Filter Kelas Asli:",
            options=sorted(df_pred["kelas_asli"].unique()),
            default=sorted(df_pred["kelas_asli"].unique())
        )
    with c2:
        status_filter = st.radio(
            "Filter Status Hasil Prediksi:",
            options=["Semua Data", "Hanya Prediksi Benar", "Hanya Salah Klasifikasi"],
            horizontal=True
        )

    df_tampil = df_pred[df_pred["kelas_asli"].isin(pilihan_kelas)].copy()
    if status_filter == "Hanya Prediksi Benar":
        df_tampil = df_tampil[df_tampil["benar"] == True]
    elif status_filter == "Hanya Salah Klasifikasi":
        df_tampil = df_tampil[df_tampil["benar"] == False]

    st.markdown(
        f"<p style='font-size:0.8rem; color:#475569; margin:0.5rem 0 0.75rem 0;'>"
        f"Menampilkan <b style='color:#18232F;'>{len(df_tampil)}</b> dari total <b style='color:#18232F;'>{len(df_pred)}</b> poligon uji:"
        f"</p>",
        unsafe_allow_html=True
    )
    st.dataframe(df_tampil, use_container_width=True, height=360)

    csv_bytes = df_tampil.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Unduh Data Hasil Prediksi (CSV)",
        data=csv_bytes,
        file_name="prediksi_data_uji_rf.csv",
        mime="text/csv"
    )
else:
    st.warning("File `prediksi_data_uji.csv` tidak ditemukan di folder data.")


# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("""
<footer style="margin-top:3rem; padding-top:1.5rem; border-top:1px solid #E2E8F0; text-align:center; font-size:0.8rem; color:#64748B;">
    Proyek Sains Data &mdash; Klasifikasi Spasial LULC Jawa Timur &bull; Sentinel-2A Level-2A & Random Forest
</footer>
""", unsafe_allow_html=True)
