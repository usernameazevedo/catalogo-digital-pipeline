# catalogo-digital-pipeline

Pipeline completo para transformar uma lista de produtos em um **catálogo digital profissional**: versão HTML interativa (com busca e índice de marcas), versão PDF compacta para WhatsApp, e publicação em **link limpo** (URL neutra, sem nome de pessoa ou agência) para enviar ao cliente final.

Nasceu de um caso real: catálogo de atacado com 255 produtos e 20+ marcas, entregue como link único que o cliente encaminha aos compradores.

## Como funciona

```
produtos.json + fotos/  →  padronizar_fotos.py  →  fotos_padrao/
                        →  build_catalogo.py    →  index.html   (versão web, self-contained)
                        →  build_pdf.py         →  Catalogo.pdf (versão A4 leve)
index.html              →  publicar-limpo       →  https://<org>.github.io/<slug>/
```

### 1. Dados

`produtos.json` (veja `produtos.exemplo.json`):

- `order`: ordem das categorias
- `marcas`: ordem das marcas no índice
- `prods`: lista de `{cod, nome, um, marca}` (código, nome, unidade de venda, marca)

`config.json` (veja `config.exemplo.json`) define nome do cliente, logo, cores e rodapé — trocar o cliente é trocar esse arquivo.

Fotos entram como `fotos/<COD>.jpg`; logos de marca como `logos/<marca-slug>.png`.

### 2. Padronização das fotos — `padronizar_fotos.py`

Fotos de fornecedor vêm em fundos, tamanhos e enquadramentos diferentes. O script:

- remove o fundo com [rembg](https://github.com/danielgatis/rembg) (u2net) e valida o recorte (área opaca entre 4% e 98% — fora disso mantém a foto original);
- centraliza num canvas quadrado branco de 480px, sem deformar;
- detecta **produtos duplicados** (mesmo produto em embalagens diferentes: "C/12", "FARDO", "CX"...) e reutiliza a melhor foto do grupo para todos.

### 3. Versão HTML — `build_catalogo.py`

Gera um `index.html` **totalmente self-contained** (fotos e logos em base64, zero dependência de servidor): capa com logo, índice de marcas clicável, busca instantânea (acento-insensível, por nome ou código), grid responsivo e botão voltar-ao-topo. Funciona offline e pode ser enviado como arquivo ou publicado em qualquer hosting estático.

### 4. Versão PDF — `build_pdf.py`

Mesmo conteúdo em layout A4 de impressão (6 colunas, fotos reduzidas a 130px/qualidade 55), renderizado via **Chrome headless** (`--print-to-pdf`). Resultado: PDF leve o suficiente para WhatsApp, com índice clicável por marca.

### 5. Link limpo — publicação

O `index.html` é publicado numa URL neutra via GitHub Pages de uma organização com nome genérico, usando o [publicar-limpo](https://github.com/usernameazevedo/publicar-limpo):

```bash
publicar-limpo pasta-do-catalogo/ meu-catalogo "descrição"
# → https://<org>.github.io/meu-catalogo/
```

Republicar o mesmo slug atualiza o mesmo link — o cliente nunca precisa receber URL nova.

## Uso

```bash
pip install -r requirements.txt
cp config.exemplo.json config.json     # edite com os dados do cliente
cp produtos.exemplo.json produtos.json # ou gere a partir da planilha do cliente
python3 padronizar_fotos.py
python3 build_catalogo.py
python3 build_pdf.py
```

## Requisitos

- Python 3.10+ com Pillow e rembg (`requirements.txt`)
- Google Chrome (para o PDF)

## Author

Built by **Luis Azevedo** — available for freelance / consulting work on video, short-form content, and automation.
📬 [username.azevedo@gmail.com](mailto:username.azevedo@gmail.com)

## Licença

MIT
