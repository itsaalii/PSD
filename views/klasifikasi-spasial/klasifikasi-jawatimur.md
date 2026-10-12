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
2. **Data Understanding**: Karakteristik spektral band Sentinel-2A, rekayasa indeks vegetasi dan air, *Data Collection / Crawling* citra via openEO CDSE (partisi grid, masking awan SCL, ekstraksi piksel), eksplorasi data (EDA), dan komposit regional Jawa Timur.
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

```python
def tambah_indeks_spektral(df: pd.DataFrame) -> pd.DataFrame:
    eps = 1e-9
    # NDVI: Kerapatan vegetasi hijau
    df["NDVI"] = (df["B08"] - df["B04"]) / (df["B08"] + df["B04"] + eps)
    # NDWI (McFeeters): Deteksi badan air permukaan
    df["NDWI"] = (df["B03"] - df["B08"]) / (df["B03"] + df["B08"] + eps)
    # MNDWI (Xu): Deteksi air dengan meredam pantulan bangunan
    df["MNDWI"] = (df["B03"] - df["B11"]) / (df["B03"] + df["B11"] + eps)
    # NDBI: Identifikasi kawasan perkerasan & permukiman
    df["NDBI"] = (df["B11"] - df["B08"]) / (df["B11"] + df["B08"] + eps)
    return df
```

---

### 2.4. Data Collection (Proses Crawling & Ekstraksi Piksel via openEO)

Proses pengumpulan data (*Data Collection / Crawling*) dilakukan secara terotomatisasi menggunakan platform komputasi awan **Copernicus Data Space Ecosystem (CDSE) openEO** (`openeo.dataspace.copernicus.eu`). Alur ini mengunduh citra satelit multispektral **Sentinel-2A Level-2A (Bottom-of-Atmosphere / BOA Surface Reflectance)** berdasarkan batas poligon sampel ground truth, membersihkan gangguan awan tingkat piksel menggunakan pita **Scene Classification Layer (SCL)**, serta mengekstrak nilai reflektansi spektral dan indeks turunan per piksel ke dalam file `dataset.csv`.

#### 2.4.1. Tahapan Utama Alur Crawling
1. **Pemuatan Sampel Ground Truth (Shapefile Vektor)**:
   * Memuat data batas poligon dari 6 kelas tutupan lahan: Sawah (`sawah.zip`), Bangunan (`bangunan.zip`), Hutan (`Hutan.zip`), Danau (`Danau.zip`), Laut (`laut2.zip`), dan Mangrove (`Mangrove.zip`).
   * Mengonversi koordinat ke **WGS84 (EPSG:4326)**, memvalidasi topologi dengan `shapely.validation.make_valid`, dan memberi identifier unik `poligon_id` (misalnya `Sawah_0012`).
2. **Partisi Spasial Grid Tiling**:
   * Membagi wilayah sebaran poligon sampel ke dalam kisi-kisi ubin (*grid tiles*) berukuran $0.20^\circ \times 0.20^\circ$ (~22 km $\times$ 22 km atau $\sim 2.200 \times 2.200$ piksel @10m) dengan margin penyangga $0.005^\circ$ (~500 m).
   * Hal ini bertujuan agar ukuran unduhan per request tetap optimal dan tidak melampaui batas kompleksitas openEO (*ProcessGraphComplexity Limit*).
3. **Eksekusi Asinkron Batch Job openEO & Masking Awan SCL**:
   * Mengunduh koleksi `SENTINEL2_L2A` periode September 2026 pada 5 band spektral optik (`B02`, `B03`, `B04`, `B08`, `B11`) dan pita `SCL`.
   * Melakukan masking awan per-piksel: piksel bernilai SCL 1 (cacat/jenuh), 3 (bayangan awan), 8/9 (awan probabilitas sedang/tinggi), dan 10 (cirrus) disaring menjadi *NoData*:
     $$\text{Mask Awan} = (\text{SCL} \in \{1, 3, 8, 9, 10\})$$
   * Mengompositkan citra menggunakan nilai median temporal (`cube.median_time()`) untuk menghasilkan reflektansi permukaan tanah bebas awan.
   * Menjalankan unduhan secara paralel menggunakan `MultiBackendJobManager` (2 job paralel simultan) dengan pelacakan database CSV `daftar_job.csv`.
4. **Ekstraksi Piksel Berlabel & De-duplikasi**:
   * Membaca GeoTIFF hasil unduhan per ubin dengan `rasterio`.
   * Memotong piksel di dalam poligon sampel ground truth (`rasterio.mask.mask`).
   * Membatasi maksimal **2.000 piksel per poligon** (`MAKS_PIKSEL_PER_POLIGON = 2000`) dengan sampling acak terstandarisasi (`np.random.default_rng(seed=42)`) guna mencegah ketimpangan kelas yang ekstrim.
   * Membuang piksel bertabrakan/ambigu antar-kelas pada koordinat yang sama dan menghilangkan duplikasi piksel sekelas.
   * Menghitung nilai indeks spektral (NDVI, NDWI, MNDWI, NDBI) per piksel dan mengekspor hasilnya ke `dataset.csv`.

---

#### 2.4.2. Kode Lengkap Pipeline Crawling
Berikut adalah implementasi kode lengkap (*full python script*) untuk seluruh proses crawling data satelit Sentinel-2 L2A via openEO hingga ekstraksi piksel berlabel:

```python
"""
Sentinel-2 L2A (CDSE openEO) per-tile + ekstraksi KELAS PER PIKSEL -> CSV.

Setiap baris CSV = satu piksel, dengan penanda poligon asalnya:
  - poligon_id : ID stabil poligon, mis. "Sawah_0012" (nama kelas + nomor fitur di file sumbernya)
  - poligon_no : nomor fitur (urutan baris) di shapefile sumber, mulai dari 0
  - sampel_id  : indeks poligon pada GeoDataFrame gabungan (internal)

Poligon sampel masuk ke SEMUA tile yang dilewatinya. Piksel di zona overlap antar-tile
hanya diambil sekali (dimiliki sel grid-nya).

Pakai (script):   python sentinel2_piksel.py
Pakai (notebook): from sentinel2_piksel import main; main()
"""

import threading
import time
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import numpy as np
import openeo
import pandas as pd
import rasterio
from openeo.extra.job_management import CsvJobDatabase, MultiBackendJobManager
from rasterio.features import rasterize
from rasterio.mask import mask as rio_mask
from rasterio.warp import transform as warp_transform
from rasterio.windows import Window
from shapely.geometry import box
from shapely.validation import make_valid

# ==============================================================================
# KONFIGURASI
# ==============================================================================
SUMBER = {  # nama kelas: (file, kode label)
    "Sawah": ("/content/drive/MyDrive/PSD/sawah.zip", 1),
    "Bangunan": ("/content/drive/MyDrive/PSD/bangunan.zip", 2),
    "Hutan": ("/content/drive/MyDrive/PSD/Hutan.zip", 3),
    "Danau": ("/content/drive/MyDrive/PSD/Danau.zip", 4),
    "Laut": ("/content/drive/MyDrive/PSD/laut2.zip", 5),
    "Mangrove": ("/content/drive/MyDrive/PSD/Mangrove.zip", 6),
}

TILE_DEG = 0.20      # ukuran tile ~22 km (~2200 x 2200 piksel @10 m)
BUFFER_DEG = 0.005   # margin ~500 m di sekeliling sampel

TANGGAL = ["2026-09-01", "2026-09-30"]
BANDS = ["B02", "B03", "B04", "B08", "B11"]  # Blue, Green, Red, NIR, SWIR
PAKAI_MASK_SCL = True  # mask awan/bayangan per piksel pakai band SCL
MAX_CLOUD = 30         # filter awan level scene (kalau PAKAI_MASK_SCL=False, pakai ~10)

PARALEL = 2            # job bersamaan (akun gratis CDSE biasanya max 2)

# Ekstraksi piksel
MAKS_PIKSEL_PER_POLIGON = 2000  # None = ambil SEMUA piksel (hati-hati: poligon laut/hutan bisa jutaan -> CSV sangat besar)
SEED = 42
BUAT_RASTER_LABEL = True        # buat label_<tile>.tif di samping citra tiap tile

OUT_DIR = Path("hasil_s2_piksel")
JOB_DB_PATH = OUT_DIR / "daftar_job.csv"
PETA_CSV = OUT_DIR / "peta_sampel_tile.csv"
PIKSEL_OUT = OUT_DIR / "dataset.csv"


# ==============================================================================
# 1. BACA & GABUNGKAN SAMPEL
# ==============================================================================
def baca_semua() -> gpd.GeoDataFrame:
    bagian = []
    for nama, (file, label) in SUMBER.items():
        g = gpd.read_file(file).to_crs("EPSG:4326")
        # nomor fitur asli di file sumber (dicatat SEBELUM filter agar tetap stabil)
        g["poligon_no"] = np.arange(len(g))
        g = g[g.geometry.notna() & ~g.geometry.is_empty].copy()
        g["geometry"] = g.geometry.apply(lambda x: x if x.is_valid else make_valid(x))
        g["label_teks"] = nama
        g["label"] = label
        g["poligon_id"] = [f"{nama}_{n:04d}" for n in g["poligon_no"]]
        g = g[["poligon_id", "poligon_no", "label", "label_teks", "geometry"]]
        print(f"Jumlah sampel {nama:<9}: {len(g)}  bounds={[round(v, 3) for v in g.total_bounds]}")
        bagian.append(g)

    gdf = gpd.GeoDataFrame(pd.concat(bagian, ignore_index=True), crs="EPSG:4326")
    print(f"Total sampel gabungan   : {len(gdf)}")
    return gdf


# ==============================================================================
# 2. BAGI JADI TILE (poligon masuk ke semua sel yang dilewatinya)
# ==============================================================================
def buat_tile(gdf: gpd.GeoDataFrame):
    T, B = TILE_DEG, BUFFER_DEG
    peta, batas, sel_xy = [], {}, {}

    for idx, geom in gdf.geometry.items():
        minx, miny, maxx, maxy = geom.bounds
        for gx in range(int(np.floor(minx / T)), int(np.floor(maxx / T)) + 1):
            for gy in range(int(np.floor(miny / T)), int(np.floor(maxy / T)) + 1):
                sel = box(gx * T, gy * T, (gx + 1) * T, (gy + 1) * T)
                if not geom.intersects(sel):
                    continue
                bagian = geom.intersection(sel)
                if bagian.is_empty:
                    continue
                b = bagian.bounds
                tid = f"x{gx}_y{gy}"
                peta.append({"tile_id": tid, "sampel_id": idx, "poligon_id": gdf.at[idx, "poligon_id"]})
                sel_xy[tid] = (gx, gy)
                if tid in batas:
                    o = batas[tid]
                    batas[tid] = (min(o[0], b[0]), min(o[1], b[1]), max(o[2], b[2]), max(o[3], b[3]))
                else:
                    batas[tid] = b

    tiles = pd.DataFrame(
        [
            {
                "tile_id": tid,
                "gx": sel_xy[tid][0],
                "gy": sel_xy[tid][1],
                "west": b[0] - B,
                "south": b[1] - B,
                "east": b[2] + B,
                "north": b[3] + B,
            }
            for tid, b in batas.items()
        ]
    )
    peta = pd.DataFrame(peta)
    tiles["n_sampel"] = tiles["tile_id"].map(peta.groupby("tile_id")["sampel_id"].nunique())

    lebar_km = (tiles.east - tiles.west) * 111.32 * np.cos(np.radians((tiles.north + tiles.south) / 2))
    tinggi_km = (tiles.north - tiles.south) * 110.57
    print(f"\nJumlah tile (job)       : {len(tiles)}")
    print(f"Ukuran tile terbesar    : {lebar_km.max():.1f} km x {tinggi_km.max():.1f} km")
    print(f"Total area diunduh      : {(lebar_km * tinggi_km).sum():,.0f} km2")
    return tiles, peta


# ==============================================================================
# 3. JALANKAN BATCH JOB PER TILE
# ==============================================================================
def _jam() -> str:
    return datetime.now().strftime("%H:%M:%S")


def start_job(row, connection, **kwargs):
    print(f"[{_jam()}] >> Mengirim job tile {row['tile_id']} ({row.get('n_sampel', '?')} poligon)...", flush=True)
    bbox = {
        "west": float(row["west"]),
        "south": float(row["south"]),
        "east": float(row["east"]),
        "north": float(row["north"]),
    }
    bands = BANDS + ["SCL"] if PAKAI_MASK_SCL else BANDS
    cube = connection.load_collection(
        "SENTINEL2_L2A",
        spatial_extent=bbox,
        temporal_extent=TANGGAL,
        bands=bands,
        max_cloud_cover=MAX_CLOUD,
    )

    if PAKAI_MASK_SCL:
        scl = cube.band("SCL")
        # 1=jenuh, 3=bayangan awan, 8/9=awan sedang/tinggi, 10=cirrus
        mask_awan = (scl == 1) | (scl == 3) | (scl == 8) | (scl == 9) | (scl == 10)
        cube = cube.filter_bands(BANDS).mask(mask_awan)

    komposit = cube.median_time()
    return komposit.create_job(title=f"s2_{row['tile_id']}", out_format="GTiff")


INTERVAL_LAPOR = 30  # detik antar laporan progres di terminal


class ManagerBerlapor(MultiBackendJobManager):
    """Manager job yang mencetak pesan saat job selesai / gagal."""

    def on_job_done(self, job, row):
        print(f"[{_jam()}] [OK]    Tile {row['tile_id']} selesai (job {job.job_id}), mengunduh hasil...", flush=True)
        super().on_job_done(job, row)
        print(f"[{_jam()}] [OK]    Tile {row['tile_id']} terunduh.", flush=True)

    def on_job_error(self, job, row):
        print(f"[{_jam()}] [ERROR] Tile {row['tile_id']} gagal (job {job.job_id}). Log disimpan di folder job.", flush=True)
        super().on_job_error(job, row)


def _lapor_berkala(job_db, berhenti: threading.Event):
    mulai = time.time()
    while not berhenti.wait(INTERVAL_LAPOR):
        try:
            df = job_db.read()
        except Exception:  # file sedang ditulis manager; lewati satu siklus
            continue
        n = len(df)
        hitung = df["status"].value_counts().to_dict()
        selesai = hitung.get("finished", 0)
        gagal = sum(hitung.get(s, 0) for s in ("error", "start_failed", "skipped"))
        jalan = hitung.get("running", 0) + hitung.get("queued", 0) + hitung.get("created", 0)
        belum = hitung.get("not_started", 0)
        persen = 100 * selesai / n if n else 0
        menit = (time.time() - mulai) / 60
        print(
            f"[{_jam()}] Progres job: {selesai}/{n} selesai ({persen:.0f}%) | "
            f"berjalan/antre {jalan} | belum mulai {belum} | gagal {gagal} | {menit:.1f} menit",
            flush=True,
        )


def jalankan_job(tiles: pd.DataFrame, ulangi_error: bool = True):
    OUT_DIR.mkdir(exist_ok=True)

    conn = openeo.connect("openeo.dataspace.copernicus.eu")
    conn.authenticate_oidc()

    manager = ManagerBerlapor(root_dir=OUT_DIR, poll_sleep=30)
    manager.add_backend("cdse", connection=conn, parallel_jobs=PARALEL)

    job_db = CsvJobDatabase(JOB_DB_PATH)
    if not job_db.exists():
        job_db.initialize_from_df(tiles)
    elif ulangi_error:
        df = job_db.read()
        gagal = df["status"].isin(["error", "start_failed", "skipped"])
        if gagal.any():
            print(f"Mengulang {int(gagal.sum())} job yang sebelumnya gagal.")
            df.loc[gagal, "status"] = "not_started"
            job_db.persist(df)

    # thread pemantau: cetak ringkasan status job tiap INTERVAL_LAPOR detik
    berhenti = threading.Event()
    pemantau = threading.Thread(target=_lapor_berkala, args=(job_db, berhenti), daemon=True)
    pemantau.start()
    try:
        manager.run_jobs(start_job=start_job, job_db=job_db)
    finally:
        berhenti.set()
        pemantau.join(timeout=5)

    df = job_db.read()
    print("\nRingkasan status job:")
    print(df["status"].value_counts().to_string())
    return df


# ==============================================================================
# 4. EKSTRAK KELAS PER PIKSEL -> CSV
# ==============================================================================
def _nama_band(src) -> list:
    desc = list(src.descriptions or [])
    if len(desc) == src.count and all(desc) and set(BANDS) <= set(desc):
        return desc
    return BANDS  # asumsi urutan band sama dengan permintaan


def _valid_mask(data, nodata, masked=None):
    """data: (band, H, W). Piksel valid = semua band terbatas, > 0, bukan nodata."""
    ok = np.isfinite(data).all(axis=0) & (data > 0).all(axis=0)
    if nodata is not None and not np.isnan(nodata):
        ok &= ~(data == nodata).any(axis=0)
    if masked is not None:
        ok &= ~masked
    return ok


def _piksel_geom(src, geom):
    """Semua piksel valid yang pusatnya di dalam geometri.
    Return (nilai[band, n], baris_raster, kolom_raster, x, y) dalam CRS raster, atau None."""
    nodata = src.nodata

    if geom.geom_type == "Point":
        rr, cc = src.index(geom.x, geom.y)
        if not (0 <= rr < src.height and 0 <= cc < src.width):
            return None
        data = src.read(window=Window(cc, rr, 1, 1)).astype("float64")  # (band,1,1)
        ok = _valid_mask(data, nodata)
        row0, col0 = rr, cc
    else:
        ok = None
        for all_touched in (False, True):  # poligon sangat kecil: coba lagi dengan all_touched
            try:
                arr, tr = rio_mask(src, [geom], crop=True, all_touched=all_touched, filled=False)
            except ValueError:  # tidak beririsan dengan raster
                return None
            data = np.ma.getdata(arr).astype("float64")
            ok = _valid_mask(data, nodata, np.ma.getmaskarray(arr).any(axis=0))
            row0 = int(round((tr.f - src.transform.f) / src.transform.e))
            col0 = int(round((tr.c - src.transform.c) / src.transform.a))
            if ok.any():
                break
        if ok is None or not ok.any():
            return None

    r_idx, c_idx = np.nonzero(ok)
    if len(r_idx) == 0:
        return None
    nilai = data[:, r_idx, c_idx]
    px_row, px_col = row0 + r_idx, col0 + c_idx
    xs, ys = rasterio.transform.xy(src.transform, px_row, px_col)
    return nilai, px_row, px_col, np.asarray(xs), np.asarray(ys)


def tambah_indeks(df: pd.DataFrame) -> pd.DataFrame:
    e = 1e-9
    df["NDVI"] = (df["B08"] - df["B04"]) / (df["B08"] + df["B04"] + e)
    df["NDWI"] = (df["B03"] - df["B08"]) / (df["B03"] + df["B08"] + e)
    df["MNDWI"] = (df["B03"] - df["B11"]) / (df["B03"] + df["B11"] + e)
    df["NDBI"] = (df["B11"] - df["B08"]) / (df["B11"] + df["B08"] + e)
    return df


def _tif_tile(r):
    tifs = sorted(p for p in OUT_DIR.glob(f"job_{r['id']}/*.tif") if not p.name.startswith("label_"))
    return tifs[0] if tifs else None


def ekstrak_piksel(gdf, db, peta) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    T = TILE_DEG
    potongan = []
    selesai = db[db["status"] == "finished"]
    print(f"\nEkstraksi piksel dari {len(selesai)} tile yang selesai...")

    total_tile = len(selesai)
    total_piksel = 0
    t0 = time.time()

    for no_tile, (_, r) in enumerate(selesai.iterrows(), start=1):
        tif = _tif_tile(r)
        if tif is None:
            print(f"  [!] File .tif tidak ditemukan untuk tile {r['tile_id']} (job {r['id']})")
            continue

        cx0, cy0 = int(r["gx"]) * T, int(r["gy"]) * T
        ids = peta.loc[peta["tile_id"] == r["tile_id"], "sampel_id"].unique()
        n_poli = len(ids)
        piksel_tile = 0
        print(f"[{_jam()}] Tile {no_tile}/{total_tile} ({r['tile_id']}): {n_poli} poligon", flush=True)

        with rasterio.open(tif) as src:
            nama_band = _nama_band(src)
            sub_r = gdf.loc[ids].to_crs(src.crs)

            for no_poli, (idx, row) in enumerate(sub_r.iterrows(), start=1):
                if no_poli % 25 == 0 or no_poli == n_poli:
                    print(
                        f"    poligon {no_poli}/{n_poli} | piksel tile ini: {piksel_tile:,} | "
                        f"total: {total_piksel:,} | {(time.time() - t0) / 60:.1f} menit",
                        end="\r", flush=True,
                    )
                hasil = _piksel_geom(src, row.geometry)
                if hasil is None:
                    continue
                nilai, px_row, px_col, xs, ys = hasil

                lon, lat = warp_transform(src.crs, "EPSG:4326", xs.tolist(), ys.tolist())
                lon, lat = np.asarray(lon), np.asarray(lat)

                # hanya piksel yang pusatnya di dalam sel grid tile ini -> tidak ada duplikat antar-tile
                pilih = np.flatnonzero((lon >= cx0) & (lon < cx0 + T) & (lat >= cy0) & (lat < cy0 + T))
                if len(pilih) == 0:
                    continue
                if MAKS_PIKSEL_PER_POLIGON and len(pilih) > MAKS_PIKSEL_PER_POLIGON:
                    pilih = rng.choice(pilih, MAKS_PIKSEL_PER_POLIGON, replace=False)

                d = {
                    "poligon_id": row["poligon_id"],   # penanda poligon asal
                    "poligon_no": row["poligon_no"],
                    "sampel_id": idx,
                    "tile_id": r["tile_id"],
                    "label": row["label"],
                    "label_teks": row["label_teks"],
                    "px_row": px_row[pilih],
                    "px_col": px_col[pilih],
                    "lon": lon[pilih],
                    "lat": lat[pilih],
                }
                for i, nb in enumerate(nama_band):
                    d[nb] = nilai[i, pilih]
                potongan.append(pd.DataFrame(d))
                piksel_tile += len(pilih)
                total_piksel += len(pilih)

        print(f"\n    -> tile {r['tile_id']} selesai: {piksel_tile:,} piksel", flush=True)

    if not potongan:
        print("Tidak ada piksel yang berhasil diekstrak.")
        return pd.DataFrame()

    df = pd.concat(potongan, ignore_index=True)

    # piksel yang sama dimiliki poligon kelas berbeda = label ambigu -> dibuang
    kunci = ["tile_id", "px_row", "px_col"]
    ganda = df.duplicated(kunci, keep=False)
    konflik = ganda & (df.groupby(kunci)["label"].transform("nunique") > 1)
    if konflik.any():
        print(f"Membuang {int(konflik.sum())} piksel dengan label bertabrakan antar-kelas.")
    df = df[~konflik]

    # piksel yang sama dimiliki >1 poligon dari kelas yang sama: simpan satu baris saja
    # (poligon_id = poligon yang pertama memprosesnya)
    n_sebelum = len(df)
    df = df.drop_duplicates(kunci).reset_index(drop=True)
    if n_sebelum != len(df):
        print(f"Menghapus {n_sebelum - len(df)} piksel ganda (poligon sekelas yang saling tumpang tindih).")

    df = tambah_indeks(df)

    OUT_DIR.mkdir(exist_ok=True)
    df.to_csv(PIKSEL_OUT, index=False)
    print(f"\nTersimpan: {PIKSEL_OUT}")
    print(f"Total piksel berlabel: {len(df):,}")
    print(df.groupby("label_teks").size().to_string())
    print(f"Jumlah poligon yang menghasilkan piksel: {df['poligon_id'].nunique()}")
    return df


# ==============================================================================
# 5. (OPSIONAL) RASTER LABEL GeoTIFF SEJAJAR DENGAN CITRA TILE
# ==============================================================================
def buat_raster_label(gdf, db, peta):
    """Tulis label_<tile>.tif (uint8, 0 = tanpa label) pada grid yang sama dengan citra tile."""
    selesai = db[db["status"] == "finished"]
    total = len(selesai)
    for no, (_, r) in enumerate(selesai.iterrows(), start=1):
        tif = _tif_tile(r)
        if tif is None:
            continue
        print(f"[{_jam()}] Raster label {no}/{total}: tile {r['tile_id']}", flush=True)
        ids = peta.loc[peta["tile_id"] == r["tile_id"], "sampel_id"].unique()
        with rasterio.open(tif) as src:
            sub_r = gdf.loc[ids].to_crs(src.crs)
            shapes = [(g, int(l)) for g, l in zip(sub_r.geometry, sub_r["label"])]
            lab = rasterize(
                shapes, out_shape=(src.height, src.width), transform=src.transform,
                fill=0, dtype="uint8",
            )
            profil = dict(
                driver="GTiff", height=src.height, width=src.width, count=1, dtype="uint8",
                crs=src.crs, transform=src.transform, nodata=0, compress="deflate",
            )
            keluar = tif.with_name(f"label_{r['tile_id']}.tif")
            with rasterio.open(keluar, "w", **profil) as dst:
                dst.write(lab, 1)
    print("Raster label selesai (label_<tile>.tif di folder tiap job).")


# ==============================================================================
# MAIN
# ==============================================================================
def main(jalankan: bool = True, ekstrak: bool = True, ulangi_error: bool = True):
    gdf = baca_semua()
    tiles, peta = buat_tile(gdf)

    OUT_DIR.mkdir(exist_ok=True)
    tiles.to_csv(OUT_DIR / "rencana_tile.csv", index=False)
    peta.to_csv(PETA_CSV, index=False)
    # tabel referensi poligon (tanpa geometri) untuk join dengan CSV piksel
    gdf.drop(columns="geometry").assign(
        luas_derajat2=gdf.geometry.area
    ).to_csv(OUT_DIR / "daftar_poligon.csv", index_label="sampel_id")

    if jalankan:
        db = jalankan_job(tiles, ulangi_error=ulangi_error)
    else:
        db = CsvJobDatabase(JOB_DB_PATH).read()

    hasil = None
    if ekstrak:
        hasil = ekstrak_piksel(gdf, db, peta)
    if BUAT_RASTER_LABEL:
        buat_raster_label(gdf, db, peta)
    return hasil if hasil is not None else db


if __name__ == "__main__":
    main()
```

---

### 2.5. Karakteristik Dataset Ground Truth (`dataset.csv`)
Dataset hasil proses ekstraksi dan crawling di atas tersimpan dalam file `dataset.csv`:
* **Total Baris (Piksel)**: **322.146 piksel**
* **Total Kolom (Fitur)**: 19 kolom (metadata koordinat, band spektral asli, dan indeks turunan)
* **Total Poligon Sampel**: **274 poligon** yang didigitasi secara cermat dari berbagai penjuru Jawa Timur.

```{code-cell}
# Memuat dataset pada notebook
import pandas as pd
df = pd.read_csv('../../data/Klasifikasi/land/dataset.csv')

print(f"Jumlah baris (piksel): {df.shape[0]}")
print(f"Jumlah kolom (fitur): {df.shape[1]}")
df.head()
```

---

### 2.6. Exploratory Data Analysis (EDA)
Analisis eksplorasi data dilakukan untuk memverifikasi keterpisahan spektral:
1. **Distribusi Jumlah Piksel per Kelas**: Memeriksa volume sampel untuk setiap tutupan lahan.
2. **Distribusi Nilai NDVI**: Membuktikan bahwa kelas **Hutan** dan **Mangrove** memiliki sebaran NDVI tertinggi ($> 0.65$), **Sawah** memiliki variasi NDVI sedang-tinggi ($0.4 - 0.8$), sedangkan **Danau**, **Laut**, dan **Bangunan** memiliki NDVI terendah ($< 0.2$).

```{code-cell}
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

### 2.7. Akuisisi Citra Skala Regional via openEO Batch Job
Untuk memetakan klasifikasi skala regional satu provinsi utuh, digunakan platform **openEO CDSE** (`openeo.dataspace.copernicus.eu`). Karena batas geografis Jawa Timur ($110.89^\circ - 114.63^\circ\text{ E}$, $-8.84^\circ - -6.65^\circ\text{ S}$) pada resolusi asli melebihi batas sinkron ($> 20.000 \times 20.000$ piksel), proses unduhan dijalankan menggunakan **Batch Job Asinkron** dengan resolusi agregasi spasial $0.0025^\circ$ (~250 meter):

```python
import openeo

connection = openeo.connect("https://openeo.dataspace.copernicus.eu").authenticate_oidc()
bbox_jatim = {"west": 110.89, "south": -8.84, "east": 114.63, "north": -6.65}

cube = connection.load_collection(
    "SENTINEL2_L2A",
    spatial_extent=bbox_jatim,
    temporal_extent=["2026-08-01", "2026-08-31"],
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
```{code-cell}
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

```{code-cell}
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

```{code-cell}
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


```{code-cell}
# Visualisasi Diagram Batang Kinerja per Kelas (Palet Tema Teal)
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report

labels = sorted(y_test.unique())
report_dict = classification_report(y_test, y_pred_knn, labels=labels, output_dict=True)

df_metrics = pd.DataFrame([
    {
        "Kelas": lbl,
        "Precision": report_dict[lbl]["precision"] * 100,
        "Recall": report_dict[lbl]["recall"] * 100,
        "F1-Score": report_dict[lbl]["f1-score"] * 100
    }
    for lbl in labels
])

plt.figure(figsize=(9, 5.5), dpi=150)
y_indices = np.arange(len(labels))
bar_height = 0.25

# Tiga bar bersisian dengan variasi saturasi warna teal
plt.barh(y_indices + bar_height, df_metrics["Precision"], height=bar_height, label="Precision", color="#14B8A6")
plt.barh(y_indices, df_metrics["Recall"], height=bar_height, label="Recall", color="#5EEAD4")
plt.barh(y_indices - bar_height, df_metrics["F1-Score"], height=bar_height, label="F1-Score", color="#0F766E")

for i, row in df_metrics.iterrows():
    plt.text(row["F1-Score"] + 0.8, i - bar_height, f"{row['F1-Score']:.1f}%", va="center", ha="left", fontsize=8.5, fontweight="bold", color="#0F766E")
    plt.text(row["Recall"] + 0.8, i, f"{row['Recall']:.1f}%", va="center", ha="left", fontsize=8, color="#0D9488")
    plt.text(row["Precision"] + 0.8, i + bar_height, f"{row['Precision']:.1f}%", va="center", ha="left", fontsize=8, color="#0F766E")

plt.yticks(y_indices, labels, fontsize=10, fontweight="600", color="#18232F")
plt.xlabel("Skor Performa Evaluasi (%)", fontsize=10.5, fontweight="600", color="#334155", labelpad=8)
plt.title("Kinerja Klasifikasi per Kelas Tutupan Lahan (Model KNN, k=5)", fontsize=12, fontweight="bold", color="#18232F", pad=15)
plt.xlim(0, 115)
plt.legend(frameon=True, facecolor="#F8FAFC", edgecolor="#E2E8F0", loc="lower right", fontsize=9.5)
plt.grid(axis="x", linestyle="--", alpha=0.5, color="#CBD5E1")
plt.gca().set_axisbelow(True)

for spine in ["top", "right"]:
    plt.gca().spines[spine].set_visible(False)
plt.gca().spines["left"].set_color("#CBD5E1")
plt.gca().spines["bottom"].set_color("#CBD5E1")

plt.tight_layout()
plt.savefig("kinerja_kelas.png", dpi=180, bbox_inches="tight")
plt.show()
```

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



```{code-cell}
import matplotlib.colors as mcolors
import seaborn as sns
from sklearn.metrics import confusion_matrix

# Gradien tema kehijauan (Teal) selaras antarmuka Streamlit
cmap_teal = mcolors.LinearSegmentedColormap.from_list(
    "psd_teal_theme",
    ["#F2F5F7", "#CCFBF1", "#2DD4BF", "#0F766E", "#0B5F58", "#042F2E"]
)

cm = confusion_matrix(y_test, y_pred_knn, labels=labels)
cm_df = pd.DataFrame(cm, index=labels, columns=labels)

plt.figure(figsize=(8, 6.2), dpi=150)
sns.heatmap(
    cm_df,
    annot=True,
    fmt='d',
    cmap=cmap_teal,
    cbar=True,
    linewidths=1.2,
    linecolor="#FFFFFF",
    square=True,
    annot_kws={"size": 10.5, "weight": "bold"},
    cbar_kws={"shrink": 0.82, "label": "Jumlah Sampel Piksel"}
)
plt.title("Confusion Matrix - K-Nearest Neighbors (KNN, k=5)\nData Uji 64.430 Piksel", 
          fontsize=12, fontweight="bold", color="#18232F", pad=15)
plt.xlabel("Hasil Prediksi Model", fontsize=10.5, fontweight="600", color="#334155", labelpad=10)
plt.ylabel("Kelas Ground Truth (Aktual)", fontsize=10.5, fontweight="600", color="#334155", labelpad=10)

plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=180, bbox_inches="tight")
plt.show()
```

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
        <div>
            <b style="color: #18232F;">Peta 1: Evaluasi Poligon Sampel & Sorotan Salah Klasifikasi</b>
        </div>
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
    ImageOverlay(image=rgba_img, bounds=img_bounds, opacity=0.8, name=f"Sebaran {label_str}").add_to(m2)

folium.LayerControl(collapsed=False).add_to(m2)
m2.save("hasil_klasifikasi_knn.html")
```

```{raw} html
<div style="margin: 20px 0; border: 1px solid #d0d7de; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.08);">
    <div style="background: #f6f8fa; padding: 10px 16px; border-bottom: 1px solid #d0d7de; display: flex; justify-content: space-between; align-items: center; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; font-size: 13px;">
        <div>
            <b style="color: #18232F;">Peta 2: Klasifikasi Tutupan Lahan Skala Regional Jawa Timur</b>
        </div>
        <div>
            <a href="https://klasifikasi-spasial-tutupan-lahan-jawatimur.streamlit.app/" target="_blank" style="color: #0F766E; text-decoration: none; font-weight: 600; padding: 4px 10px; background: #E7F4F2; border: 1px solid #99F6E4; border-radius: 4px; margin-right: 6px;">Buka di Web Streamlit</a>
            <a href="hasil_klasifikasi_knn.html" target="_blank" style="color: #0969da; text-decoration: none; font-weight: 600; padding: 4px 10px; background: white; border: 1px solid #d0d7de; border-radius: 4px;">↗ Layar Penuh</a>
        </div>
    </div>
    <iframe src="hasil_klasifikasi_knn.html" width="100%" height="640px" style="border: none; display: block;"></iframe>
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
