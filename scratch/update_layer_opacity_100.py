import os
import re
import base64
import io
from PIL import Image
import numpy as np

def update_html_file(filepath):
    print(f"Processing: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Update Leaflet ImageOverlay opacity option: "opacity": 0.65 -> "opacity": 1.0
    content_updated = re.sub(r'"opacity":\s*0\.65,?', '"opacity": 1.0,', content)
    
    # 2. Update legend text: "Opasitas Layer: 65%" or "Opasitas: 65%" -> "Opasitas Layer: 100%"
    content_updated = re.sub(r'Opasitas Layer:\s*65%', 'Opasitas Layer: 100%', content_updated)
    content_updated = re.sub(r'Opasitas:\s*65%', 'Opasitas: 100%', content_updated)
    
    # 3. Update all embedded base64 RGBA images so that alpha > 0 becomes alpha = 255 (100% opaque)
    def repl_img(match):
        prefix = match.group(1) # "data:image/png;base64,"
        b64_str = match.group(2)
        try:
            raw_data = base64.b64decode(b64_str)
            img = Image.open(io.BytesIO(raw_data)).convert('RGBA')
            arr = np.array(img)
            # If any alpha is between 1 and 254 (e.g. 160)
            if np.any((arr[:, :, 3] > 0) & (arr[:, :, 3] < 255)):
                arr[arr[:, :, 3] > 0, 3] = 255
                new_img = Image.fromarray(arr)
                buf = io.BytesIO()
                new_img.save(buf, format='PNG', optimize=True, compress_level=9)
                new_b64 = base64.b64encode(buf.getvalue()).decode('ascii')
                return prefix + new_b64
            else:
                return match.group(0)
        except Exception as e:
            print(f"Error processing image in {filepath}: {e}")
            return match.group(0)

    pattern = r'(data:image/png;base64,)([A-Za-z0-9+/=]+)'
    content_updated = re.sub(pattern, repl_img, content_updated)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content_updated)
    print(f"Successfully updated: {filepath}")

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    target_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip .git and virtual environments if any
        if '.git' in dirpath:
            continue
        for fn in filenames:
            if fn.startswith('hasil_klasifikasi_') and fn.endswith('.html'):
                target_files.append(os.path.join(dirpath, fn))
    
    print(f"Found {len(target_files)} html files to update.")
    for fp in target_files:
        update_html_file(fp)

if __name__ == '__main__':
    main()
