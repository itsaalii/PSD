import json

nb_path = 'data/Klasifikasi/land/klasifikasi-spasisal-fiksss.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

c15_src = ''.join(nb['cells'][15]['source'])

old_legenda_1 = """    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px; margin-bottom: 8px;">
        <span style="font-weight: 700; font-size: 12px; color: #0F766E;">Legenda Poligon</span>
        <span style="font-size: 10px; font-weight: 600; color: #64748B; background: #F1F5F9; padding: 2px 6px; border-radius: 4px;">6 Kelas</span>
    </div>"""

new_legenda_1 = """    <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #E2E8F0; padding-bottom: 6px; margin-bottom: 8px;">
        <span style="font-weight: 700; font-size: 12.5px; color: #0F766E; letter-spacing: -0.01em;">Legenda Tutupan Lahan</span>
        <span style="font-size: 10px; font-weight: 600; color: #64748B; background: #F1F5F9; padding: 2px 6px; border-radius: 4px; border: 1px solid #E2E8F0;">Vektor Poligon</span>
    </div>"""

if old_legenda_1 in c15_src:
    c15_src = c15_src.replace(old_legenda_1, new_legenda_1)
    nb['cells'][15]['source'] = [l + '\n' for l in c15_src.splitlines()]
    if nb['cells'][15]['source']:
        nb['cells'][15]['source'][-1] = nb['cells'][15]['source'][-1].rstrip('\n')
    print('Updated Cell 15 in notebook!')
else:
    print('Pattern not matched in cell 15, checking substrings...')
    c15_src = c15_src.replace('Legenda Poligon', 'Legenda Tutupan Lahan').replace('6 Kelas</span>', 'Vektor Poligon</span>')
    nb['cells'][15]['source'] = [l + '\n' for l in c15_src.splitlines()]
    if nb['cells'][15]['source']:
        nb['cells'][15]['source'][-1] = nb['cells'][15]['source'][-1].rstrip('\n')
    print('Replaced substrings in cell 15!')

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
print('Notebook saved successfully.')
