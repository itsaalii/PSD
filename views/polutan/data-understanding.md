# Data Understanding
## Collecting Data
Dataset bertipe _Time Series_ diambil dari [https://dataspace.copernicus.eu/](https://dataspace.copernicus.eu/)

Buat akun terlebih dahulu di website Copernicus agar bisa melakukan crawling data menggunakan library openEO

## Install Library

```bash
pip install openeo
pip install netCDF4
```

### Autentikasi dan Pengambilan Data

```python
import openeo

connection = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()
```

Saat menjalankan baris di atas, akan muncul permintaan autentikasi:

```
Visit (link authentikasi) 📋 to authenticate.
✅ Authorized successfully
Authenticated using device code flow.
```

Klik link autentikasi lalu login menggunakan akun Copernicus.

### Definisi Area dan Pengambilan Data NO₂, CO dan SO₂ dari geojson

Koordinat area Nganjuk diperoleh dari [https://geojson.io](https://geojson.io) dengan menggambar kotak di atas wilayah yang diinginkan kemudian copy kordinatnya

![Grafik Data](../../img/polutan/geojson.png)

```python
aoi = {
    "type": "Polygon",
    "coordinates": [
        [
            [111.80, -7.40],
            [112.10, -7.40],
            [112.10, -7.70],
            [111.80, -7.70],
            [111.80, -7.40],
        ]
    ]
}

s5post = connection.load_collection(
    "SENTINEL_5P_L2",
    temporal_extent=["2023-10-01", "2026-06-01"],
    spatial_extent={
        "west": 111.80,
        "south": -7.70,
        "east": 112.10,
        "north": -7.40
    },
    bands=["NO2"],
)

# Agregasi harian agar tidak ada lebih dari satu data per hari
s5p_no2_daily = s5post.aggregate_temporal_period(reducer="mean", period="day")

# Agregasi spasial untuk menghasilkan rata-rata time series per AOI
s5p_no2_aoi = s5p_no2_daily.aggregate_spatial(reducer="mean", geometries=aoi)
```
