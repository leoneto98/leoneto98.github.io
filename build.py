#!/usr/bin/env python3
"""Gera o site estatico a partir dos mesmos YAMLs que alimentam o curriculo.

Uso:  .venv/bin/python build.py
Saida: index.html (EN, raiz) e pt/index.html (PT).
"""
import html
import re
import shutil
from pathlib import Path

import yaml

RAIZ = Path(__file__).parent
FONTE_CV = RAIZ.parent / "CVs" / "typst"
SITE_URL = "https://leoneto98.github.io"

# Rotulos que nao vem do YAML do curriculo (o CV nao precisa deles).
UI = {
    "en": {
        "nav": ["Profile", "Skills", "Experience", "Education", "Publications", "Contact"],
        "cv_btn": "Download CV (PDF)",
        "outra_lingua": "Português",
        "outra_href": "/pt/",
        "desc": "Data Scientist with an M.Sc. in Electrical Engineering, working on end-to-end machine learning from business opportunity to production.",
    },
    "pt": {
        "nav": ["Perfil", "Competências", "Experiência", "Formação", "Publicações", "Contato"],
        "cv_btn": "Baixar CV (PDF)",
        "outra_lingua": "English",
        "outra_href": "/",
        "desc": "Cientista de Dados com Mestrado em Engenharia Elétrica, atuando em machine learning de ponta a ponta, da oportunidade de negócio à produção.",
    },
}

CV_PDF = {"en": "Leonardo_Novicki_Neto_CV_EN.pdf", "pt": "Leonardo_Novicki_Neto_CV_PT.pdf"}


def markup(s):
    """Converte o markup leve do YAML (*negrito*, _italico_) em HTML."""
    s = html.escape(s.strip())
    s = re.sub(r"\*(.+?)\*", r"<strong>\1</strong>", s, flags=re.S)
    s = re.sub(r"_(.+?)_", r"<em>\1</em>", s, flags=re.S)
    return re.sub(r"\s+", " ", s)


def secao(id_, titulo, corpo):
    return f'<section id="{id_}"><h2>{html.escape(titulo)}</h2>\n{corpo}\n</section>'


def bloco_experiencia(exp):
    out = []
    for e in exp:
        bullets = "\n".join(f"<li>{markup(b['texto'])}</li>" for b in e["bullets"])
        contexto = (
            f'<p class="contexto">{markup(e["contexto"])}</p>' if e["contexto"].strip() else ""
        )
        out.append(f"""<article class="item">
  <header class="item-head">
    <div><h3>{html.escape(e['empresa'])}</h3><p class="cargo">{html.escape(e['cargo'])}</p></div>
    <div class="meta"><span class="periodo">{html.escape(e['periodo'])}</span><span class="local">{html.escape(e['local'])}</span></div>
  </header>
  {contexto}
  <ul>{bullets}</ul>
</article>""")
    return "\n".join(out)


def bloco_formacao(form):
    out = []
    for f in form:
        det = f'<p class="detalhe">{markup(f["detalhe"])}</p>' if f["detalhe"].strip() else ""
        out.append(f"""<article class="item">
  <header class="item-head">
    <div><h3>{html.escape(f['curso'])}</h3><p class="cargo">{html.escape(f['instituicao'])}</p></div>
    <div class="meta"><span class="periodo">{html.escape(f['periodo'])}</span></div>
  </header>
  {det}
</article>""")
    return "\n".join(out)


def divide_itens(txt):
    """Divide por virgula, mas nao dentro de parenteses: 'AWS (Athena, S3)' fica inteiro."""
    return [x.strip() for x in re.split(r",\s*(?![^()]*\))", txt) if x.strip()]


def bloco_competencias(comp):
    linhas = []
    for c in comp:
        chips = "".join(
            f'<span class="chip">{html.escape(i)}</span>' for i in divide_itens(c["itens"])
        )
        linhas.append(
            f'<div class="skill-row"><dt>{html.escape(c["grupo"])}</dt><dd>{chips}</dd></div>'
        )
    return f'<dl class="skills">{"".join(linhas)}</dl>'


def bloco_publicacoes(pubs):
    itens = "\n".join(
        f'<li>{markup(p["texto"])} <a href="{html.escape(p["url"])}" target="_blank" rel="noopener">{html.escape(p["url_label"])}</a></li>'
        for p in pubs
    )
    return f'<ul class="pubs">{itens}</ul>'


def jsonld(p, data, lang):
    import json

    alma = sorted({f["instituicao"] for f in data["formacao"]})
    obj = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": p["nome"],
        "jobTitle": p["headline"].split("|")[0].strip(),
        "email": f"mailto:{p['email']}",
        "url": SITE_URL + ("/pt/" if lang == "pt" else "/"),
        "image": SITE_URL + "/assets/foto.jpg",
        "address": {"@type": "PostalAddress", "addressLocality": p["local"]},
        "alumniOf": [{"@type": "CollegeOrUniversity", "name": a} for a in alma],
        "sameAs": [p["linkedin_url"], p["github_url"], "https://arxiv.org/abs/2310.03895"],
        "knowsLanguage": [i["nome"] for i in data["idiomas"]],
    }
    return json.dumps(obj, ensure_ascii=False, indent=2)


def pagina(lang):
    data = yaml.safe_load((RAIZ / "data" / f"cv-{lang}.yml").read_text(encoding="utf-8"))
    p, t, ui = data["perfil"], data["titulos"], UI[lang]
    nav_ids = ["perfil", "skills", "exp", "edu", "pubs", "contato"]
    nav = "".join(
        f'<a href="#{i}">{html.escape(n)}</a>' for i, n in zip(nav_ids, ui["nav"])
    )
    prefixo = "../" if lang == "pt" else ""

    corpo = "\n".join([
        secao("skills", t["competencias"], bloco_competencias(data["competencias"])),
        secao("exp", t["experiencia"], bloco_experiencia(data["experiencia"])),
        secao("edu", t["formacao"], bloco_formacao(data["formacao"])),
        secao("pubs", t["publicacoes"], bloco_publicacoes(data["publicacoes"])),
        secao("extra", t["complementar"],
              "<ul>" + "".join(f"<li>{markup(c)}</li>" for c in data["complementar"]) + "</ul>"),
        secao("idiomas", t["idiomas"],
              '<dl class="skills">' + "".join(
                  f'<div class="skill-row"><dt>{html.escape(i["nome"])}</dt><dd>{markup(i["nivel"])}</dd></div>'
                  for i in data["idiomas"]) + "</dl>"),
    ])

    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(p['nome'])} | {html.escape(p['headline'])}</title>
<meta name="description" content="{html.escape(ui['desc'])}">
<link rel="canonical" href="{SITE_URL}{'/pt/' if lang == 'pt' else '/'}">
<link rel="alternate" hreflang="en" href="{SITE_URL}/">
<link rel="alternate" hreflang="pt" href="{SITE_URL}/pt/">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/">
<meta property="og:type" content="profile">
<meta property="og:title" content="{html.escape(p['nome'])} | {html.escape(p['headline'])}">
<meta property="og:description" content="{html.escape(ui['desc'])}">
<meta property="og:image" content="{SITE_URL}/assets/foto.jpg">
<meta property="og:url" content="{SITE_URL}{'/pt/' if lang == 'pt' else '/'}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>">
<link rel="stylesheet" href="{prefixo}style.css">
<script type="application/ld+json">
{jsonld(p, data, lang)}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topo">
  <nav class="nav-topo">
    <span class="marca">{html.escape(p['nome'])}</span>
    <div class="nav-links">{nav}</div>
    <a class="lang" href="{ui['outra_href']}">{html.escape(ui['outra_lingua'])}</a>
  </nav>
</header>
<main id="main">
  <section id="perfil" class="hero">
    <img class="foto" src="{prefixo}assets/foto.jpg" alt="{html.escape(p['nome'])}" width="150" height="180">
    <div class="hero-txt">
      <h1>{html.escape(p['nome'])}</h1>
      <p class="headline">{html.escape(p['headline'])}</p>
      <p class="resumo">{markup(p['resumo'])}</p>
      <p class="contatos">
        <a class="btn primario" href="{prefixo}{CV_PDF[lang]}" download>{html.escape(ui['cv_btn'])}</a>
        <a class="btn" href="{html.escape(p['linkedin_url'])}" target="_blank" rel="noopener">LinkedIn</a>
        <a class="btn" href="{html.escape(p['github_url'])}" target="_blank" rel="noopener">GitHub</a>
        <a class="btn" href="mailto:{html.escape(p['email'])}">{html.escape(p['email'])}</a>
      </p>
      <p class="local">{html.escape(p['local'])}</p>
    </div>
  </section>
{corpo}
</main>
<footer id="contato">
  <p><a href="mailto:{html.escape(p['email'])}">{html.escape(p['email'])}</a> ·
     <a href="{html.escape(p['linkedin_url'])}" target="_blank" rel="noopener">LinkedIn</a> ·
     <a href="{html.escape(p['github_url'])}" target="_blank" rel="noopener">GitHub</a></p>
  <p class="fine">© 2026 {html.escape(p['nome'])}</p>
</footer>
</body>
</html>
"""


def main():
    # Sincroniza os YAMLs e o PDF a partir do repositorio do curriculo.
    for lang in ("pt", "en"):
        shutil.copy(FONTE_CV / "data" / f"cv-{lang}.yml", RAIZ / "data" / f"cv-{lang}.yml")
        shutil.copy(FONTE_CV / CV_PDF[lang], RAIZ / CV_PDF[lang])
    shutil.copy(FONTE_CV / "assets" / "foto.jpg", RAIZ / "assets" / "foto.jpg")

    (RAIZ / "index.html").write_text(pagina("en"), encoding="utf-8")
    (RAIZ / "pt").mkdir(exist_ok=True)
    (RAIZ / "pt" / "index.html").write_text(pagina("pt"), encoding="utf-8")
    print("gerado: index.html (en) e pt/index.html (pt)")


if __name__ == "__main__":
    main()
