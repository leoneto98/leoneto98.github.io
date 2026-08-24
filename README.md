# leoneto98.github.io

Site pessoal estático, bilíngue (EN/PT). Publicado pelo GitHub Pages direto da branch `main` — sem build na nuvem, sem GitHub Actions.

## Fonte única com o currículo

O site **não tem conteúdo próprio**. Ele é gerado a partir dos mesmos YAMLs que produzem o currículo em PDF, em `../CVs/typst/data/`.

Atualizar o currículo e o site é uma coisa só:

```sh
# 1. edite o conteudo
vim ../CVs/typst/data/cv-pt.yml

# 2. regenere o PDF
cd ../CVs/typst && typst compile cv-pt.typ Leonardo_Novicki_Neto_CV_PT.pdf

# 3. regenere o site (copia YAMLs, foto e PDFs, e emite o HTML)
cd ../../site-v2 && .venv/bin/python build.py

# 4. publique
git add -A && git commit -m "atualiza conteudo" && git push
```

## Estrutura

| Caminho | O que é |
|---|---|
| `build.py` | Gerador: lê os YAMLs do currículo e emite o HTML |
| `style.css` | Estilos — tema claro/escuro, responsivo, regras de impressão |
| `index.html` | **Gerado** — versão em inglês (raiz) |
| `pt/index.html` | **Gerado** — versão em português |
| `data/` | **Gerado** — cópia dos YAMLs do currículo |
| `assets/foto.jpg` | **Gerado** — cópia da foto |
| `*.pdf` | **Gerado** — cópia dos currículos |

Não edite os arquivos marcados como gerados: o próximo `build.py` sobrescreve. Para mudar **conteúdo**, edite os YAMLs em `../CVs/typst/data/`. Para mudar **aparência**, edite `style.css` ou os templates dentro de `build.py`.

## Setup inicial (só uma vez)

```sh
python3 -m venv .venv && .venv/bin/pip install pyyaml
```

## Ver localmente

```sh
.venv/bin/python -m http.server 8899
# abra http://localhost:8899/ (EN) e http://localhost:8899/pt/ (PT)
```

## SEO

Cada página traz JSON-LD `Person` (com `alumniOf`, `sameAs` para LinkedIn/GitHub/arXiv), Open Graph, canonical e `hreflang` ligando EN ↔ PT. Tudo é gerado a partir do YAML, então não desatualiza.

## Publicação

O GitHub Pages serve os arquivos como estão. Os HTML gerados **precisam ser commitados** — é isso que dispensa qualquer build na nuvem.

Em Settings → Pages: Source = *Deploy from a branch*, Branch = `main`, pasta `/ (root)`.
