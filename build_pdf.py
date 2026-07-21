#!/usr/bin/env python3
"""Gera a versão PDF compacta do catálogo (HTML de impressão A4 → Chrome headless).
Fotos são reduzidas (130px, qualidade 55) para o PDF ficar leve e enviável no WhatsApp.

Entrada: config.json, produtos.json, logo, fotos_padrao/, logos/
Saída:   catalogo_pdf.html + Catalogo.pdf
"""
import json, html, base64, os, io, re, subprocess

from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(f"{BASE}/config.json"))
data = json.load(open(f"{BASE}/produtos.json"))
logo = base64.b64encode(open(f"{BASE}/{cfg['logo']}", "rb").read()).decode()
C = cfg['cores']

def slug(m):
    s = m.lower()
    for a, b in zip('áàãâéêíóôõúüç&', 'aaaaeeiooouuce'):
        s = s.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

def foto_small(cod):
    p = f"{BASE}/fotos_padrao/{cod}.jpg"
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert('RGB')
    im = im.resize((130, 130), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=55, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()

def logo_small(m):
    p = f"{BASE}/{cfg['logo']}" if m == cfg['nome'] else f"{BASE}/logos/{slug(m)}.png"
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert('RGB')
    im.thumbnail((200, 120))
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=70, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()

idx_rows, secs = [], []
for m in data['marcas']:
    items = sorted([p for p in data['prods'] if p['marca'] == m], key=lambda x: x['nome'])
    lg = logo_small(m)
    lgimg = f'<img class="hlogo" src="data:image/jpeg;base64,{lg}">' if lg else ''
    if lg:
        idx_rows.append(f'<a class="icard" href="#{slug(m)}" title="{html.escape(m)}"><img src="data:image/jpeg;base64,{lg}"></a>')
    else:
        idx_rows.append(f'<a class="icard icard-txt" href="#{slug(m)}">{html.escape(m)}</a>')
    cards = []
    for p in items:
        f = foto_small(p['cod'])
        img = f'<img src="data:image/jpeg;base64,{f}">' if f else '<div class="nf"></div>'
        cards.append(
            f'<div class="card">{img}<div class="cod">COD {p["cod"]} · {html.escape(p["um"] or "CX")}</div>'
            f'<div class="nome">{html.escape(p["nome"])}</div></div>')
    secs.append(
        f'<section id="{slug(m)}"><header>{lgimg}<h2>{html.escape(m)}</h2><span>{len(items)} {"item" if len(items)==1 else "itens"}</span>'
        f'<a class="volta" href="#indice">&#8593; índice</a></header>'
        f'<div class="grid">{"".join(cards)}</div></section>')

total = len(data['prods'])
page = f'''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><title>{html.escape(cfg['titulo'])} · {html.escape(cfg['nome'])}</title>
<style>
@page{{size:A4;margin:9mm 9mm 11mm}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Montserrat','Helvetica Neue',Arial,sans-serif;color:{C['texto']}}}
.capa{{display:flex;flex-direction:column;align-items:center;text-align:center;padding:0 0 3mm}}
.capa img{{width:58mm}}
.capa h1{{margin-top:3mm;font-size:16pt;font-weight:900}}
.capa h1 em{{font-style:normal;color:{C['destaque']}}}
.capa p{{margin-top:1.4mm;color:{C['cinza']};font-size:8.5pt}}
.capa .rule{{width:24mm;height:1.4mm;border-radius:1mm;margin-top:2.6mm;background:linear-gradient(90deg,{C['primaria']},{C['destaque']})}}
section{{page-break-inside:auto;margin-bottom:6mm}}
header{{display:flex;align-items:center;gap:4mm;border-bottom:1.2mm solid {C['primaria']};padding-bottom:1.6mm;margin-bottom:2.6mm;page-break-after:avoid;page-break-inside:avoid}}
header .hlogo{{height:15mm;max-width:42mm;object-fit:contain}}
header h2{{font-size:13pt;font-weight:900}}
header span{{margin-left:auto;color:{C['cinza']};font-size:8pt;font-weight:700}}
.grid{{display:grid;grid-template-columns:repeat(6,1fr);gap:1.8mm}}
.card{{border:0.3mm solid {C['borda']};border-radius:2mm;overflow:hidden;page-break-inside:avoid;background:#fff}}
.card img{{width:100%;aspect-ratio:1/1;object-fit:contain;display:block}}
.nf{{width:100%;aspect-ratio:1/1;background:{C['fundo2']}}}
.cod{{font-size:5.4pt;font-weight:800;color:{C['destaque']};letter-spacing:.04em;padding:1mm 1.6mm 0}}
.nome{{font-size:5.8pt;font-weight:600;line-height:1.32;padding:0.4mm 1.6mm 1.6mm}}
header .volta{{margin-left:4mm;font-size:7pt;font-weight:700;color:{C['destaque']};text-decoration:none}}
.indice{{page-break-after:always}}
.isub{{color:{C['cinza']};font-size:8pt;margin:0 0 2.6mm;font-weight:700;text-align:center}}
.icols{{display:grid;grid-template-columns:repeat(5,1fr);gap:1.7mm}}
.icard{{display:flex;align-items:center;justify-content:center;height:18mm;text-decoration:none;color:{C['texto']};border:0.3mm solid {C['borda']};border-radius:2mm;padding:1.6mm;break-inside:avoid;background:#fff}}
.icard img{{max-width:92%;max-height:15mm;object-fit:contain}}
.icard-txt{{font-size:8pt;font-weight:800;text-align:center}}
.rodape{{margin-top:8mm;text-align:center;color:{C['cinza']};font-size:7pt}}
</style></head><body>
<div class="capa">
 <img src="data:image/png;base64,{logo}">
 <h1>{html.escape(cfg['titulo']).replace('Produtos', '<em>Produtos</em>')}</h1>
 <p>{total} produtos · {len(data['marcas'])} marcas · {cfg['atualizado'].capitalize()}</p>
 <div class="rule"></div>
</div>
<div class="indice" id="indice"><p class="isub">Nossas marcas - toque para ir direto à seção</p>
<div class="icols">{''.join(idx_rows)}</div></div>
{''.join(secs)}
<div class="rodape">{html.escape(cfg['rodape'])}</div>
</body></html>'''

htmlpath = f"{BASE}/catalogo_pdf.html"
open(htmlpath, 'w').write(page)
print('html:', len(page) // 1024, 'KB')

pdfpath = f"{BASE}/Catalogo.pdf"
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
subprocess.run([chrome, "--headless", "--disable-gpu", f"--print-to-pdf={pdfpath}",
                "--no-pdf-header-footer", "--virtual-time-budget=20000", f"file://{htmlpath}"],
               check=True, capture_output=True)
print('pdf:', os.path.getsize(pdfpath) // 1024, 'KB')
