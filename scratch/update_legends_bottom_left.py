import re
import os
import shutil

legenda_peta_1 = """<div style="
    position: fixed; 
    bottom: 25px; 
    left: 20px; 
    z-index: 9999; 
    background: rgba(255, 255, 255, 0.95); 
    backdrop-filter: blur(8px); 
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(203, 213, 225, 0.85); 
    border-radius: 12px; 
    padding: 12px 14px; 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.15); 
    min-width: 175px;
    pointer-events: auto;
">
    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px; margin-bottom: 8px;">
        <span style="font-weight: 700; font-size: 12.5px; color: #0F766E; letter-spacing: -0.01em;">Legenda Tutupan Lahan</span>
        <span style="font-size: 10px; font-weight: 600; color: #64748B; background: #F1F5F9; padding: 2px 6px; border-radius: 4px; border: 1px solid #E2E8F0;">Vektor Poligon</span>
    </div>
    <div style="display: flex; flex-direction: column; gap: 5px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 13px; height: 13px; border-radius: 3px; background: #FFD92F; display: inline-block; border: 1px solid rgba(0,0,0,0.15); flex-shrink: 0;"></span>
            <span style="font-weight: 600; color: #334155; font-size: 11.5px;">Sawah</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 13px; height: 13px; border-radius: 3px; background: #E41A1C; display: inline-block; border: 1px solid rgba(0,0,0,0.15); flex-shrink: 0;"></span>
            <span style="font-weight: 600; color: #334155; font-size: 11.5px;">Bangunan</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 13px; height: 13px; border-radius: 3px; background: #2E7D32; display: inline-block; border: 1px solid rgba(0,0,0,0.15); flex-shrink: 0;"></span>
            <span style="font-weight: 600; color: #334155; font-size: 11.5px;">Hutan</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 13px; height: 13px; border-radius: 3px; background: #4FC3F7; display: inline-block; border: 1px solid rgba(0,0,0,0.15); flex-shrink: 0;"></span>
            <span style="font-weight: 600; color: #334155; font-size: 11.5px;">Danau</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 13px; height: 13px; border-radius: 3px; background: #0D47A1; display: inline-block; border: 1px solid rgba(0,0,0,0.15); flex-shrink: 0;"></span>
            <span style="font-weight: 600; color: #334155; font-size: 11.5px;">Laut</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 13px; height: 13px; border-radius: 3px; background: #8E44AD; display: inline-block; border: 1px solid rgba(0,0,0,0.15); flex-shrink: 0;"></span>
            <span style="font-weight: 600; color: #334155; font-size: 11.5px;">Mangrove</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; padding-top: 4px; border-top: 1px dashed #E2E8F0;">
            <span style="width: 14px; height: 14px; border-radius: 50%; background: #E11D48; color: #FFFFFF; display: inline-flex; align-items: center; justify-content: center; font-size: 9px; font-weight: 800; line-height: 1; flex-shrink: 0; box-shadow: 0 1px 3px rgba(225,29,72,0.4);">!</span>
            <span style="font-weight: 600; color: #E11D48; font-size: 11.5px;">Salah Klasifikasi</span>
        </div>
    </div>
    <div style="border-top: 1px solid #E2E8F0; margin-top: 6px; padding-top: 5px; font-size: 10px; color: #64748B;">
        <span>Opasitas Layer: 80%</span>
    </div>
</div>"""

legenda_peta_2 = """<div style="
    position: fixed; 
    bottom: 25px; 
    left: 20px; 
    z-index: 9999; 
    background: rgba(255, 255, 255, 0.95); 
    backdrop-filter: blur(8px); 
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(203, 213, 225, 0.85); 
    border-radius: 12px; 
    padding: 12px 14px; 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.15); 
    min-width: 175px;
    pointer-events: auto;
">
    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px; margin-bottom: 8px;">
        <span style="font-weight: 700; font-size: 12.5px; color: #0F766E; letter-spacing: -0.01em;">Legenda Tutupan Lahan</span>
        <span style="font-size: 10px; font-weight: 600; color: #64748B; background: #F1F5F9; padding: 2px 6px; border-radius: 4px; border: 1px solid #E2E8F0;">Raster 250m</span>
    </div>
    <div style="display: flex; flex-direction: column; gap: 5px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 13px; height: 13px; border-radius: 3px; background: #FFD92F; display: inline-block; border: 1px solid rgba(0,0,0,0.15); flex-shrink: 0;"></span>
            <span style="font-weight: 600; color: #334155; font-size: 11.5px;">Sawah</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 13px; height: 13px; border-radius: 3px; background: #E41A1C; display: inline-block; border: 1px solid rgba(0,0,0,0.15); flex-shrink: 0;"></span>
            <span style="font-weight: 600; color: #334155; font-size: 11.5px;">Bangunan</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 13px; height: 13px; border-radius: 3px; background: #2E7D32; display: inline-block; border: 1px solid rgba(0,0,0,0.15); flex-shrink: 0;"></span>
            <span style="font-weight: 600; color: #334155; font-size: 11.5px;">Hutan</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 13px; height: 13px; border-radius: 3px; background: #4FC3F7; display: inline-block; border: 1px solid rgba(0,0,0,0.15); flex-shrink: 0;"></span>
            <span style="font-weight: 600; color: #334155; font-size: 11.5px;">Danau</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 13px; height: 13px; border-radius: 3px; background: #0D47A1; display: inline-block; border: 1px solid rgba(0,0,0,0.15); flex-shrink: 0;"></span>
            <span style="font-weight: 600; color: #334155; font-size: 11.5px;">Laut</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="width: 13px; height: 13px; border-radius: 3px; background: #8E44AD; display: inline-block; border: 1px solid rgba(0,0,0,0.15); flex-shrink: 0;"></span>
            <span style="font-weight: 600; color: #334155; font-size: 11.5px;">Mangrove</span>
        </div>
    </div>
    <div style="border-top: 1px solid #E2E8F0; margin-top: 6px; padding-top: 5px; font-size: 10px; color: #64748B;">
        <span>Opasitas Layer: 100%</span>
    </div>
</div>"""

def update_map_html(filepath, new_legend_html):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if there is an existing floating legend div
    pattern = r'<div style="[^"]*position:\s*fixed;[^"]*bottom:\s*25px;[^"]*">.*?</div>\s*</div>'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + new_legend_html + content[match.end():]
        print(f"Replaced existing legend in {filepath}")
    else:
        body_idx = content.find('<body>')
        if body_idx != -1:
            insert_pos = body_idx + len('<body>\n')
            content = content[:insert_pos] + '\n' + new_legend_html + '\n' + content[insert_pos:]
            print(f"Inserted legend after <body> in {filepath}")
        else:
            content = new_legend_html + '\n' + content
            print(f"Prepended legend to {filepath}")
            
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

# Update root files
update_map_html('peta_klasifikasi_rf.html', legenda_peta_1)
update_map_html('hasil_klasifikasi_knn.html', legenda_peta_2)
update_map_html('hasil_klasifikasi_random_forest.html', legenda_peta_2)

# Distribute to all directories
dest_dirs = [
    'data/Klasifikasi',
    'data/Klasifikasi/land',
    'views/klasifikasi-spasial',
    '_static',
    '_build/html',
    '_build/html/views/klasifikasi-spasial',
    '_build/html/_static',
    'extra_assets',
    'extra_assets/views/klasifikasi-spasial',
]

for d in dest_dirs:
    os.makedirs(d, exist_ok=True)
    shutil.copy2('peta_klasifikasi_rf.html', os.path.join(d, 'peta_klasifikasi_rf.html'))
    shutil.copy2('hasil_klasifikasi_knn.html', os.path.join(d, 'hasil_klasifikasi_knn.html'))
    shutil.copy2('hasil_klasifikasi_random_forest.html', os.path.join(d, 'hasil_klasifikasi_random_forest.html'))
    print(f"Synced to {d}")

print("Completed updating all HTML map files!")
