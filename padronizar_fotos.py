#!/usr/bin/env python3
"""Padroniza as fotos dos produtos: recorta o fundo (rembg), centraliza num canvas
quadrado branco sem deformar, e unifica a foto de produtos duplicados (mesmo produto
em embalagens/quantidades diferentes) usando a melhor foto do grupo para todos.

Entrada:  fotos/<COD>.jpg        Saída: fotos_padrao/<COD>.jpg
"""
import json, os, re
from PIL import Image
from rembg import remove, new_session

BASE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = f"{BASE}/fotos", f"{BASE}/fotos_padrao"
os.makedirs(OUT, exist_ok=True)
data = json.load(open(f"{BASE}/produtos.json"))

CANVAS = 480   # lado do quadrado final, px
MARGIN = 30    # respiro em volta do produto, px

# termos de embalagem ignorados ao detectar duplicados
PACK = re.compile(r'\b(CX|FD|PCT|UN|PC|KG|C/\s?\d+\s?\w*|FARDO( COM)?( C/)?|CAIXA|\d+\s?X\s?\d+\w*|BDJ|EMB\.?)\b', re.I)

def key(nome):
    n = PACK.sub(' ', nome.upper())
    n = re.sub(r'[^A-Z0-9]+', ' ', n)
    return re.sub(r'\s+', ' ', n).strip()

groups = {}
for p in data['prods']:
    groups.setdefault(key(p['nome']), []).append(p['cod'])

# melhor foto do grupo = maior arquivo
best = {}
for k, cods in groups.items():
    if len(cods) < 2:
        continue
    sizes = [(os.path.getsize(f"{SRC}/{c}.jpg") if os.path.exists(f"{SRC}/{c}.jpg") else 0, c) for c in cods]
    b = max(sizes)[1]
    for c in cods:
        best[c] = b

session = new_session("u2net")

def squareize(cod):
    src = f"{SRC}/{best.get(cod, cod)}.jpg"
    if not os.path.exists(src):
        return False
    im = Image.open(src).convert('RGB')
    try:
        cut = remove(im, session=session)
        alpha = cut.split()[3]
        bbox = alpha.getbbox()
        opaque = sum(1 for a in alpha.getdata() if a > 40)
        frac = opaque / (cut.width * cut.height)
        # recorte só é usado quando o rembg encontrou um objeto plausível
        fg = cut.crop(bbox) if bbox and 0.04 < frac < 0.98 else None
    except Exception:
        fg = None
    canvas = Image.new('RGB', (CANVAS, CANVAS), 'white')
    img = fg if fg is not None else im
    w, h = img.size
    scale = min((CANVAS - 2 * MARGIN) / w, (CANVAS - 2 * MARGIN) / h)
    img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    mask = img.split()[3] if fg is not None else None
    canvas.paste(img, ((CANVAS - img.width) // 2, (CANVAS - img.height) // 2), mask)
    canvas.save(f"{OUT}/{cod}.jpg", 'JPEG', quality=72, optimize=True)
    return True

log = open(f"{BASE}/padronizar.log", "w")
log.write(f"grupos duplicados: {sum(1 for v in groups.values() if len(v) > 1)} ({len(best)} itens)\n")
for i, p in enumerate(data['prods']):
    log.write(f"{'OK' if squareize(p['cod']) else 'MISS'} {p['cod']}\n")
    if i % 25 == 0:
        log.flush()
log.write("DONE\n")
log.close()
print("done")
