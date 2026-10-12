import re, base64, io
import numpy as np
from PIL import Image

files = [
    'hasil_klasifikasi_knn.html',
    'hasil_klasifikasi_random_forest.html',
    'views/klasifikasi-spasial/hasil_klasifikasi_knn.html',
    'views/klasifikasi-spasial/hasil_klasifikasi_random_forest.html',
    '_static/hasil_klasifikasi_knn.html',
    '_static/hasil_klasifikasi_random_forest.html'
]

for fname in files:
    with open(fname, 'r', encoding='utf-8') as f:
        text = f.read()
    opacities = re.findall(r'"opacity":\s*([0-9.]+)', text)
    legend_match = re.search(r'Opasitas Layer:\s*([0-9%]+)', text)
    legend_str = legend_match.group(0) if legend_match else 'None'
    matches = re.findall(r'data:image/png;base64,([A-Za-z0-9+/=]+)', text)
    alphas = []
    for b64 in matches:
        arr = np.array(Image.open(io.BytesIO(base64.b64decode(b64))))
        alphas.append(list(np.unique(arr[:, :, 3])))
    print(f"{fname}:")
    print(f"  Leaflet opacities: {opacities}")
    print(f"  Legend: {legend_str}")
    print(f"  Images alpha unique sets: {alphas}")
