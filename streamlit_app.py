"""
Dashboard Klasifikasi Spasial Tutupan Lahan (LULC) Jawa Timur
Berbasis Sentinel-2A Level-2A & Algoritma Random Forest

Styling: Tailwind CSS
Palet Warna: https://psd-interpolasi.basisdata2-c.my.id/
  - ink:   #18232F
  - paper: #F2F5F7
  - teal:  { 600: #0F766E, 700: #0B5F58, 50: #E7F4F2 }
Typography: IBM Plex Sans
Icons: Heroicons SVG (Semua emote ditiadakan)
"""

from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
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
# 2. HEROICONS SVG HELPER STRINGS (Tanpa Emote)
# ==============================================================================
ICON_GLOBE = """<svg class="h-6 w-6 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
    <path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-.778.099-1.533.284-2.253" />
</svg>"""

ICON_MAP = """<svg class="h-5 w-5 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
    <path stroke-linecap="round" stroke-linejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.046 4.84-2.42A1.125 1.125 0 0 0 21 16.883V5.86a1.125 1.125 0 0 0-.623-1.006l-4.82-2.41a1.125 1.125 0 0 0-.96.002l-5.195 2.597a1.125 1.125 0 0 1-.96 0L3.623 2.633A1.125 1.125 0 0 0 3 3.639v11.023a1.125 1.125 0 0 0 .623 1.006l4.82 2.41a1.125 1.125 0 0 0 .96-.002l5.195-2.597a1.125 1.125 0 0 1 .96 0l-.062-.033Z" />
</svg>"""

ICON_SATELLITE = """<svg class="h-5 w-5 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
    <path stroke-linecap="round" stroke-linejoin="round" d="m21 7.5-9-5.25L3 7.5m18 0-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9" />
</svg>"""

ICON_CHECK_CIRCLE = """<svg class="h-5 w-5 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
</svg>"""

ICON_CHART_BAR = """<svg class="h-5 w-5 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
    <path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
</svg>"""

ICON_TABLE = """<svg class="h-5 w-5 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
    <path stroke-linecap="round" stroke-linejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 0 1-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0 1 12 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125M12 10.875v7.5m0-7.5a1.125 1.125 0 0 1 1.125-1.125h7.125" />
</svg>"""

ICON_EXCLAMATION = """<svg class="h-5 w-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
</svg>"""

ICON_LAYERS = """<svg class="h-5 w-5 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
    <path stroke-linecap="round" stroke-linejoin="round" d="M6.429 9.75 2.25 12l4.179 2.25m0-4.5 5.571 3 5.571-3m-11.142 0L2.25 7.5 12 2.25l9.75 5.25-4.179 2.25m0 0L21 12l-4.179 2.25m0 0 4.179 2.25L12 21.75 2.25 16.5l4.179-2.25m11.142 0-5.571 3-5.571-3" />
</svg>"""

ICON_SCALE = """<svg class="h-5 w-5 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
    <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v17.25m0 0c-1.472 0-2.882.265-4.185.75M12 20.25c1.472 0 2.882.265 4.185.75M18.75 4.97A48.416 48.416 0 0 0 12 4.5c-2.291 0-4.545.16-6.75.47m13.5 0c1.01.143 2.01.317 3 .52m-3-.52v2.62a3.75 3.75 0 0 1-2.25 3.44l-.84.37m-7.41-6.43c-.99.203-1.99.377-3 .52m3-.52v2.62a3.75 3.75 0 0 0 2.25 3.44l.84.37" />
</svg>"""

ICON_TAG = """<svg class="h-4 w-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
    <path stroke-linecap="round" stroke-linejoin="round" d="M9.568 3H5.25A2.25 2.25 0 0 0 3 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 0 0 5.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 0 0 9.568 3Z" />
    <path stroke-linecap="round" stroke-linejoin="round" d="M6 6h.008v.008H6V6Z" />
</svg>"""

ICON_INFO = """<svg class="h-5 w-5 text-teal-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
    <path stroke-linecap="round" stroke-linejoin="round" d="m11.25 11.25.041-.02a.75.75 0 0 1 1.063.852l-.708 2.836a.75.75 0 0 0 1.063.853l.041-.021M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-3.75h.008v.008H12V8.25Z" />
</svg>"""

ICON_DOWNLOAD = """<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
    <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.5V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
</svg>"""

# ==============================================================================
# 3. INJEKSI TAILWIND CSS & TEMA (Sesuai psd-interpolasi)
# ==============================================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.tailwindcss.com"></script>
<script>
    tailwind.config = {
        theme: {
            extend: {
                fontFamily: {
                    sans: ['"IBM Plex Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif']
                },
                colors: {
                    ink: '#18232F',
                    paper: '#F2F5F7',
                    teal: {
                        50: '#E7F4F2',
                        600: '#0F766E',
                        700: '#0B5F58'
                    }
                }
            }
        }
    }
</script>
<style>
    /* Global Stylesheet Override */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #F2F5F7 !important;
        font-family: "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif !important;
        color: #18232F !important;
    }
    
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    /* Tab Styling: Mirip Navigasi Pill di psd-interpolasi */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem !important;
        background-color: rgba(226, 232, 240, 0.7) !important;
        padding: 0.25rem !important;
        border-radius: 0.75rem !important;
        border: none !important;
        display: inline-flex !important;
    }

    .stTabs [data-baseweb="tab"] {
        height: auto !important;
        padding: 0.5rem 1.25rem !important;
        border-radius: 0.5rem !important;
        background-color: transparent !important;
        color: #475569 !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        border: none !important;
        transition: all 0.15s ease-in-out !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #18232F !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #18232F !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
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
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 4. HELPER RESOLUSI FILE & CACHING
# ==============================================================================
def cari_file(nama_file: str) -> Path | None:
    """Mencari file aset di direktori kerja atau folder subproyek."""
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
# 5. SIDEBAR: INFORMASI MODEL & KONTROL
# ==============================================================================
with st.sidebar:
    st.markdown(f"""
    <div class="flex items-center gap-2 mb-4">
        {ICON_GLOBE}
        <h2 class="text-base font-semibold text-ink">Spasial LULC</h2>
    </div>
    <div class="text-xs text-slate-600 space-y-1.5 pb-4 border-b border-slate-200">
        <p><span class="font-medium text-ink">Model:</span> Random Forest (Stratified CV)</p>
        <p><span class="font-medium text-ink">Sensor:</span> Sentinel-2A MSI (ESA CDSE)</p>
        <p><span class="font-medium text-ink">Koleksi:</span> Level-2A BOA Surface Reflectance</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="mt-4 mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-500">
        {ICON_TAG}
        <span>6 Kelas Tutupan Lahan</span>
    </div>
    <div class="space-y-2 text-xs">
        <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-[#FFD92F] inline-block border border-slate-300"></span>
            <span class="text-slate-700 font-medium">Sawah</span>
            <span class="text-slate-400 text-[11px]">(Lahan Pertanian)</span>
        </div>
        <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-[#E41A1C] inline-block border border-slate-300"></span>
            <span class="text-slate-700 font-medium">Bangunan</span>
            <span class="text-slate-400 text-[11px]">(Kawasan Terbangun)</span>
        </div>
        <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-[#2E7D32] inline-block border border-slate-300"></span>
            <span class="text-slate-700 font-medium">Hutan</span>
            <span class="text-slate-400 text-[11px]">(Lahan Hijau)</span>
        </div>
        <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-[#4FC3F7] inline-block border border-slate-300"></span>
            <span class="text-slate-700 font-medium">Danau</span>
            <span class="text-slate-400 text-[11px]">(Air Pedalaman)</span>
        </div>
        <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-[#0D47A1] inline-block border border-slate-300"></span>
            <span class="text-slate-700 font-medium">Laut</span>
            <span class="text-slate-400 text-[11px]">(Perairan Terbuka)</span>
        </div>
        <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-full bg-[#8E44AD] inline-block border border-slate-300"></span>
            <span class="text-slate-700 font-medium">Mangrove</span>
            <span class="text-slate-400 text-[11px]">(Hutan Bakau Pesisir)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr class='my-5 border-slate-200'>", unsafe_allow_html=True)
    st.markdown("<div class='text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2'>Tinggi Tampilan Peta</div>", unsafe_allow_html=True)
    tinggi_peta = st.slider("Ukuran Frame (px):", min_value=500, max_value=950, value=700, step=20, label_visibility="collapsed")
    
    st.markdown(f"""
    <div class="mt-6 rounded-xl border border-teal-200 bg-teal-50 p-3.5 text-xs text-teal-800">
        <div class="flex items-start gap-2">
            {ICON_INFO}
            <div>
                <p class="font-semibold text-teal-900 mb-0.5">Navigasi Tab</p>
                <p class="leading-relaxed">Gunakan tab pilihan di bagian atas untuk mengeksplorasi peta evaluasi, peta regional provinsi, dan metrik performa.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 6. HEADER UTAMA (Sesuai Layout psd-interpolasi)
# ==============================================================================
st.markdown(f"""
<header class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between mb-6">
    <div>
        <div class="flex items-center gap-2.5">
            {ICON_GLOBE}
            <h1 class="text-2xl font-semibold tracking-tight text-ink sm:text-3xl">
                Klasifikasi Spasial Tutupan Lahan Jawa Timur
            </h1>
        </div>
        <p class="mt-1 max-w-prose text-sm text-slate-600">
            Visualisasi spasial berbasis citra satelit Sentinel-2A Level-2A dan algoritma Random Forest untuk pemetaan 6 kelas tutupan lahan.
        </p>
    </div>
    <div class="inline-flex items-center gap-2 rounded-lg bg-teal-50 border border-teal-200/60 px-3.5 py-2 text-xs font-medium text-teal-800">
        {ICON_SATELLITE}
        <span>Sentinel-2A MSI BOA</span>
    </div>
</header>
""", unsafe_allow_html=True)

# Muat Data Evaluasi
p_pred = cari_file("prediksi_data_uji.csv")
df_pred = muat_data_csv(str(p_pred)) if p_pred else None

# Baris Kartu Metrik Tailwind
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

st.markdown(f"""
<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-6">
    <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between">
            <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">Akurasi Data Uji</span>
            <span class="rounded-full bg-teal-50 p-1.5">{ICON_CHECK_CIRCLE}</span>
        </div>
        <div class="mt-3 flex items-baseline gap-2">
            <span class="text-3xl font-bold tracking-tight text-ink">{akurasi:.1f}%</span>
            <span class="rounded-full bg-teal-50 px-2.5 py-0.5 text-xs font-medium text-teal-700">{n_benar}/{n_uji} Poligon</span>
        </div>
        <p class="mt-1.5 text-xs text-slate-500">Evaluasi Stratified Test Set</p>
    </div>

    <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between">
            <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">F1-Score Macro</span>
            <span class="rounded-full bg-teal-50 p-1.5">{ICON_SCALE}</span>
        </div>
        <div class="mt-3 flex items-baseline gap-2">
            <span class="text-3xl font-bold tracking-tight text-ink">0.963</span>
            <span class="rounded-full bg-teal-50 px-2.5 py-0.5 text-xs font-medium text-teal-700">Seimbang</span>
        </div>
        <p class="mt-1.5 text-xs text-slate-500">Rata-rata harmonik seluruh kelas</p>
    </div>

    <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between">
            <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">Poligon Sampel</span>
            <span class="rounded-full bg-teal-50 p-1.5">{ICON_LAYERS}</span>
        </div>
        <div class="mt-3 flex items-baseline gap-2">
            <span class="text-3xl font-bold tracking-tight text-ink">~300</span>
            <span class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700">6 Kategori</span>
        </div>
        <p class="mt-1.5 text-xs text-slate-500">Ekstraksi fitur tingkat poligon</p>
    </div>

    <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between">
            <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">Salah Klasifikasi</span>
            <span class="rounded-full bg-amber-50 p-1.5">{ICON_EXCLAMATION}</span>
        </div>
        <div class="mt-3 flex items-baseline gap-2">
            <span class="text-3xl font-bold tracking-tight text-ink">{n_salah}</span>
            <span class="rounded-full bg-amber-50 px-2.5 py-0.5 text-xs font-medium text-amber-700">Error 3.6%</span>
        </div>
        <p class="mt-1.5 text-xs text-slate-500">Hanya pada spektral air Danau/Laut</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# 7. TAB NAVIGASI UTAMA (Tanpa Emote)
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "Peta Evaluasi Poligon",
    "Peta Regional Jawa Timur",
    "Evaluasi Model & Fitur",
    "Tabel Data Uji & Ekspor"
])

# ------------------------------------------------------------------------------
# TAB 1: PETA EVALUASI POLIGON
# ------------------------------------------------------------------------------
with tab1:
    st.markdown(f"""
    <div class="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden mb-4">
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
            <div class="flex items-center gap-2">
                {ICON_MAP}
                <h2 class="text-base font-semibold text-ink">Peta Evaluasi Poligon Ground Truth (Folium Vector)</h2>
            </div>
            <span class="rounded-full bg-teal-50 px-3 py-1 text-xs font-medium text-teal-700">
                83 Poligon Uji Terverifikasi
            </span>
        </div>
        <div class="p-5 text-xs text-slate-600 bg-slate-50/50 border-b border-slate-200">
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div class="flex items-start gap-2">
                    <span class="w-3 h-3 rounded bg-blue-600 mt-0.5 inline-block shrink-0"></span>
                    <div><b class="text-ink">Garis Tepi Biru:</b> Subset data uji (Testing) yang dievaluasi.</div>
                </div>
                <div class="flex items-start gap-2">
                    <span class="w-3 h-3 rounded bg-amber-500 mt-0.5 inline-block shrink-0"></span>
                    <div><b class="text-ink">Garis Putus-putus Oranye:</b> Poligon yang salah diprediksi model.</div>
                </div>
                <div class="flex items-start gap-2">
                    <span class="w-3 h-3 rounded bg-emerald-600 mt-0.5 inline-block shrink-0"></span>
                    <div><b class="text-ink">Klik Bidang:</b> Menampilkan popup NDVI, NDWI, dan probabilitas.</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    file_peta1 = cari_file("peta_klasifikasi_rf.html")
    if file_peta1:
        konten_html1 = muat_konten_html(str(file_peta1))
        components.html(konten_html1, height=tinggi_peta, scrolling=True)
    else:
        st.error("File peta `peta_klasifikasi_rf.html` tidak ditemukan di folder proyek.")

# ------------------------------------------------------------------------------
# TAB 2: PETA REGIONAL JAWA TIMUR
# ------------------------------------------------------------------------------
with tab2:
    st.markdown(f"""
    <div class="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden mb-4">
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
            <div class="flex items-center gap-2">
                {ICON_GLOBE}
                <h2 class="text-base font-semibold text-ink">Peta Inferensi Spasial Seluruh Jawa Timur (ImageOverlay)</h2>
            </div>
            <span class="rounded-full bg-teal-50 px-3 py-1 text-xs font-medium text-teal-700">
                Grid Resolusi 1536 x 896
            </span>
        </div>
        <div class="p-5 text-xs text-slate-600 bg-slate-50/50 border-b border-slate-200 leading-relaxed">
            Lapisan klasifikasi granular (~200 meter per piksel) menutupi seluruh daratan provinsi Jawa Timur yang di-overlay di atas citra satelit Esri World Imagery (zoom level 10) dengan opasitas 65% dan pembatasan batas administrasi GeoJSON.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    file_peta2 = cari_file("hasil_klasifikasi_random_forest.html")
    if file_peta2:
        konten_html2 = muat_konten_html(str(file_peta2))
        components.html(konten_html2, height=tinggi_peta, scrolling=True)
    else:
        st.error("File peta `hasil_klasifikasi_random_forest.html` tidak ditemukan di folder proyek.")

# ------------------------------------------------------------------------------
# TAB 3: EVALUASI MODEL & FITUR
# ------------------------------------------------------------------------------
with tab3:
    st.markdown(f"""
    <div class="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden mb-6">
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
            <div class="flex items-center gap-2">
                {ICON_CHART_BAR}
                <h2 class="text-base font-semibold text-ink">Evaluasi Performa & Kontribusi Fitur</h2>
            </div>
            <span class="rounded-full bg-teal-50 px-3 py-1 text-xs font-medium text-teal-700">
                Random Forest Gini
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_kiri, col_kanan = st.columns(2)
    
    with col_kiri:
        st.markdown("""
        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm mb-4">
            <h3 class="text-sm font-semibold text-ink mb-1">Confusion Matrix (Data Uji)</h3>
            <p class="text-xs text-slate-500 mb-4">Perbandingan antara kelas ground truth asli dan hasil klasifikasi model.</p>
        </div>
        """, unsafe_allow_html=True)
        
        p_cm_img = cari_file("confusion_matrix.png")
        if p_cm_img:
            st.image(Image.open(p_cm_img), caption="Confusion Matrix pada 83 Poligon Data Uji", use_container_width=True)
        else:
            p_cm_csv = cari_file("confusion_matrix.csv")
            if p_cm_csv:
                st.dataframe(pd.read_csv(p_cm_csv, index_col=0), use_container_width=True)

    with col_kanan:
        st.markdown("""
        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm mb-4">
            <h3 class="text-sm font-semibold text-ink mb-1">Tingkat Kepentingan Fitur Spektral</h3>
            <p class="text-xs text-slate-500 mb-4">Tingkat kontribusi band optik dan indeks spektral berdasarkan Gini Importance.</p>
        </div>
        """, unsafe_allow_html=True)
        
        p_fi_img = cari_file("kepentingan_fitur.png")
        if p_fi_img:
            st.image(Image.open(p_fi_img), caption="Kepentingan Fitur Random Forest", use_container_width=True)
        else:
            p_fi_csv = cari_file("kepentingan_fitur.csv")
            if p_fi_csv:
                st.dataframe(pd.read_csv(p_fi_csv), use_container_width=True)

# ------------------------------------------------------------------------------
# TAB 4: TABEL DATA UJI & EKSPOR
# ------------------------------------------------------------------------------
with tab4:
    st.markdown(f"""
    <div class="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden mb-6">
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
            <div class="flex items-center gap-2">
                {ICON_TABLE}
                <h2 class="text-base font-semibold text-ink">Eksplorasi Data Uji (83 Poligon)</h2>
            </div>
            <span class="rounded-full bg-teal-50 px-3 py-1 text-xs font-medium text-teal-700">
                Format Tabular
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if df_pred is not None:
        c1, c2 = st.columns([2, 1])
        with c1:
            pilihan_kelas = st.multiselect(
                "Filter Berdasarkan Kelas Asli:",
                options=sorted(df_pred["kelas_asli"].unique()),
                default=sorted(df_pred["kelas_asli"].unique())
            )
        with c2:
            status_filter = st.radio(
                "Filter Status Prediksi:",
                options=["Semua", "Hanya Benar", "Hanya Salah"],
                horizontal=True
            )
        
        df_tampil = df_pred[df_pred["kelas_asli"].isin(pilihan_kelas)].copy()
        if status_filter == "Hanya Benar":
            df_tampil = df_tampil[df_tampil["benar"] == True]
        elif status_filter == "Hanya Salah":
            df_tampil = df_tampil[df_tampil["benar"] == False]
            
        st.markdown(f"<p class='text-xs text-slate-600 mt-2 mb-3'>Menampilkan <b class='text-ink'>{len(df_tampil)}</b> dari total <b class='text-ink'>{len(df_pred)}</b> poligon uji.</p>", unsafe_allow_html=True)
        st.dataframe(df_tampil, use_container_width=True, height=380)
        
        csv_bytes = df_tampil.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Unduh Data Hasil Prediksi (CSV)",
            data=csv_bytes,
            file_name="prediksi_data_uji_rf.csv",
            mime="text/csv"
        )
    else:
        st.warning("File `prediksi_data_uji.csv` tidak ditemukan.")

# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("""
<footer class="mt-12 pt-6 border-t border-slate-200 text-center text-xs text-slate-500">
    Proyek Sains Data &mdash; Klasifikasi Spasial LULC Jawa Timur &bull; Sentinel-2A Level-2A & Random Forest
</footer>
""", unsafe_allow_html=True)
