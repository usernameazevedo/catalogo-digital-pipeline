#!/usr/bin/env python3
"""Gera o catálogo HTML self-contained (uma página, imagens em base64):
capa com logo, índice de marcas, busca instantânea e grid de produtos.

Entrada: config.json, produtos.json, logo, fotos_padrao/ (ou fotos/), logos/<marca>.png
Saída:   index.html
"""
import json, html, base64, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(f"{BASE}/config.json"))
data = json.load(open(f"{BASE}/produtos.json"))
logo = base64.b64encode(open(f"{BASE}/{cfg['logo']}", "rb").read()).decode()
C = cfg['cores']

def foto64(cod):
    for d in ('fotos_padrao', 'fotos'):
        p = f"{BASE}/{d}/{cod}.jpg"
        if os.path.exists(p):
            return base64.b64encode(open(p, "rb").read()).decode()
    return None

def slug(m):
    s = m.lower()
    for a, b in zip('áàãâéêíóôõúüç&', 'aaaaeeiooouuce'):
        s = s.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

marcas = data['marcas']
counts = {m: sum(1 for p in data['prods'] if p['marca'] == m) for m in marcas}
total = len(data['prods'])

def logo64(m):
    if m == cfg['nome']:
        return 'data:image/png;base64,' + logo
    p = f"{BASE}/logos/{slug(m)}.png"
    if os.path.exists(p):
        return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
    return None

idx_cards, sections, logo_css = [], [], []
sem_foto = 0
for m in marcas:
    items = sorted([p for p in data['prods'] if p['marca'] == m], key=lambda x: x['nome'])
    sid = slug(m)
    lg = logo64(m)
    if lg:
        logo_css.append(f'.lg-{sid}{{background-image:url("{lg}")}}')
    lgimg = f'<span class="blogo"><i class="lgbg lg-{sid}"></i></span>' if lg else '<span class="blogo blogo-x">📦</span>'
    idx_cards.append(
        f'<a class="bcard" href="#{sid}">{lgimg}<span class="bname">{html.escape(m)}</span>'
        f'<span class="bcount">{counts[m]} {"item" if counts[m]==1 else "itens"}</span></a>')
    cards = []
    for p in items:
        f = foto64(p['cod'])
        if f:
            img = f'<img src="data:image/jpeg;base64,{f}" loading="lazy" alt="">'
        else:
            sem_foto += 1
            img = ('<div class="nofoto"><svg viewBox="0 0 24 24" width="30" height="30" fill="none" '
                   'stroke="#c6cdb8" stroke-width="1.4"><rect x="3" y="6" width="18" height="14" rx="2"/>'
                   '<path d="M3 10h18M8 6V4h8v2"/></svg></div>')
        cards.append(
            f'<div class="card" data-nome="{html.escape(p["nome"].lower())}" data-cod="{p["cod"]}">'
            f'<div class="ph">{img}</div><div class="info"><span class="cod">COD {p["cod"]}</span>'
            f'<h4>{html.escape(p["nome"])}</h4><span class="um">{html.escape(p["um"] or "CX")}</span></div></div>')
    hlogo = f'<i class="hlogo lgbg lg-{sid}"></i>' if lg else ''
    sections.append(
        f'<section class="bsec" id="{sid}"><header class="bhead">{hlogo}<h2>{html.escape(m)}</h2>'
        f'<span class="count">{counts[m]} itens</span><a class="volta" href="#topo">↑ marcas</a></header>'
        f'<div class="grid">{"".join(cards)}</div></section>')

page = f'''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(cfg['titulo'])} · {html.escape(cfg['nome'])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root{{--verde:{C['primaria']};--verde-esc:{C['primaria_escura']};--laranja:{C['destaque']};--txt:{C['texto']};--cinza:{C['cinza']};--borda:{C['borda']};--bg:{C['fundo']};--bg2:{C['fundo2']}}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--txt);font-family:'Montserrat',sans-serif}}
.hero{{text-align:center;padding:56px 20px 34px;scroll-margin-top:90px}}
.hero img{{width:min(400px,78vw)}}
.hero h1{{margin-top:26px;font-weight:900;font-size:clamp(1.5rem,4.2vw,2.5rem)}}
.hero h1 em{{font-style:normal;color:var(--laranja)}}
.hero p{{margin-top:8px;color:var(--cinza);font-size:.92rem}}
.rule{{width:76px;height:5px;border-radius:3px;margin:20px auto 0;background:linear-gradient(90deg,var(--verde),var(--laranja))}}
.bindex{{max-width:1150px;margin:26px auto 8px;padding:0 min(4vw,26px);display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:11px}}
.bcard{{display:flex;flex-direction:column;align-items:stretch;gap:7px;background:var(--bg2);border:1.5px solid var(--borda);border-radius:14px;padding:16px 17px;text-decoration:none;color:var(--txt);transition:.2s}}
.bcard:hover{{border-color:var(--verde);transform:translateY(-2px)}}
.blogo{{width:100%;height:64px;display:flex;align-items:center;justify-content:center;background:#fff;border:1px solid var(--borda);border-radius:10px;overflow:hidden}}
.lgbg{{display:block;background-position:center;background-repeat:no-repeat;background-size:contain}}
.blogo .lgbg{{width:86%;height:52px}}
.blogo-x{{font-size:1.5rem}}
.bname{{font-weight:800;font-size:.92rem}}
.bcount{{font-size:.72rem;font-weight:600;color:var(--cinza)}}
.toolbar{{position:sticky;top:0;z-index:50;background:var(--bg);border-bottom:1px solid var(--borda);padding:12px min(4vw,26px)}}
.search{{display:flex;align-items:center;gap:10px;background:var(--bg2);border:1.5px solid var(--borda);border-radius:12px;padding:11px 16px;max-width:660px;margin:0 auto}}
.search:focus-within{{border-color:var(--verde)}}
.search input{{flex:1;background:none;border:0;outline:0;color:var(--txt);font-family:inherit;font-size:1rem}}
.search svg{{color:var(--verde-esc);flex:none}}
main{{max-width:1150px;margin:0 auto;padding:8px min(4vw,26px) 60px}}
.bsec{{margin-top:54px;scroll-margin-top:92px}}
.bhead{{display:flex;align-items:baseline;gap:14px;border-bottom:3px solid var(--verde);padding-bottom:10px;margin-bottom:20px;flex-wrap:wrap}}
.bhead h2{{font-size:clamp(1.25rem,3vw,1.8rem);font-weight:900;letter-spacing:.01em}}
.hlogo{{height:44px;width:130px;align-self:center}}
.bhead .count{{color:var(--cinza);font-size:.8rem;font-weight:700}}
.volta{{margin-left:auto;font-size:.75rem;font-weight:700;color:var(--laranja);text-decoration:none}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(205px,1fr));gap:14px}}
.card{{background:#fff;border:1.5px solid var(--borda);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;transition:.22s}}
.card:hover{{transform:translateY(-4px);border-color:var(--verde)}}
.ph{{aspect-ratio:1/1;background:#fff;display:flex;align-items:center;justify-content:center;border-bottom:1px solid var(--borda)}}
.ph img{{width:100%;height:100%;object-fit:contain;padding:12px}}
.nofoto{{display:flex;align-items:center;justify-content:center;width:100%;height:100%;background:var(--bg2)}}
.info{{padding:12px 14px 14px;display:flex;flex-direction:column;gap:6px;flex:1}}
.cod{{font-size:.65rem;font-weight:800;letter-spacing:.12em;color:var(--laranja)}}
.info h4{{font-size:.78rem;font-weight:600;line-height:1.45}}
.um{{margin-top:auto;align-self:flex-start;font-size:.62rem;font-weight:800;letter-spacing:.1em;color:var(--verde-esc);background:var(--bg2);border-radius:6px;padding:3px 9px}}
.noresults{{display:none;text-align:center;color:var(--cinza);padding:70px 0}}
.top{{position:fixed;right:22px;bottom:22px;z-index:60;width:46px;height:46px;border-radius:50%;border:0;background:var(--verde);color:#fff;font-size:1.2rem;cursor:pointer;opacity:0;pointer-events:none;transition:.3s}}
.top.show{{opacity:1;pointer-events:auto}}
footer{{border-top:1px solid var(--borda);padding:34px 20px;text-align:center;color:var(--cinza);font-size:.8rem}}
footer img{{width:170px;margin-bottom:10px}}
@media (max-width:640px){{
.grid{{grid-template-columns:repeat(2,1fr);gap:10px}}
.ph img{{padding:8px}}
.info{{padding:10px 11px 12px;gap:5px}}
.info h4{{font-size:.72rem}}
.bindex{{grid-template-columns:repeat(2,1fr);gap:9px}}
}}
@media print{{.toolbar,.top,.volta{{display:none}}.bsec{{break-inside:avoid-page}}}}
{''.join(logo_css)}
</style></head><body id="topo">
<div class="hero">
 <img src="data:image/png;base64,{logo}" alt="{html.escape(cfg['nome'])}">
 <h1>{html.escape(cfg['titulo']).replace('Produtos', '<em>Produtos</em>')}</h1>
 <p>{total} produtos · {len(marcas)} marcas · Atualizado em {cfg['atualizado']}</p>
 <div class="rule"></div>
</div>
<div class="bindex">{''.join(idx_cards)}</div>
<div class="toolbar">
 <div class="search"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
 <input id="q" type="search" placeholder="Buscar produto, marca ou código..." autocomplete="off"></div>
</div>
<main>
{''.join(sections)}
<div class="noresults" id="nores">Nenhum produto encontrado. Tente outro termo.</div>
</main>
<footer><img src="data:image/png;base64,{logo}" alt=""><br>{html.escape(cfg['rodape'])}</footer>
<button class="top" id="top" title="Voltar ao topo">↑</button>
<script>
const q=document.getElementById('q'),cards=[...document.querySelectorAll('.card')],secs=[...document.querySelectorAll('.bsec')],nores=document.getElementById('nores');
const norm=s=>s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();
q.addEventListener('input',()=>{{
 const t=norm(q.value.trim());let any=false;
 cards.forEach(c=>{{const hit=!t||norm(c.dataset.nome).includes(t)||c.dataset.cod.includes(t);c.style.display=hit?'':'none';if(hit)any=true}});
 secs.forEach(s=>{{const vis=[...s.querySelectorAll('.card')].some(c=>c.style.display!=='none');s.style.display=vis?'':'none'}});
 nores.style.display=any?'none':'block';
}});
const top=document.getElementById('top');
addEventListener('scroll',()=>top.classList.toggle('show',scrollY>600));
top.onclick=()=>scrollTo({{top:0,behavior:'smooth'}});
</script></body></html>'''

open(f"{BASE}/index.html", "w").write(page)
print("bytes:", len(page), "| sem foto:", sem_foto, "de", total)
