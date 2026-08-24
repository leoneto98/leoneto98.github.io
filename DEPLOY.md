# Publicação

Dois passos independentes: colocar o site novo na raiz, e fazer o endereço antigo apontar para ele.

---

## Passo 1 — Publicar o site novo em `leoneto98.github.io`

### 1.1 Criar o repositório

Em <https://github.com/new>:

- **Repository name:** `leoneto98.github.io` — o nome exato importa: é ele que faz o Pages servir na raiz do domínio
- **Public**
- **Não** marque "Add a README", ".gitignore" nem "license" — o repositório precisa nascer vazio

### 1.2 Enviar o conteúdo

```sh
cd ~/professional/site-v2
git remote add origin git@github.com:leoneto98/leoneto98.github.io.git
git push -u origin main
```

Se o `git push` reclamar que a branch é `master`, rode antes `git branch -M main`.

### 1.3 Ligar o GitHub Pages

No repositório → **Settings** → **Pages**:

- **Source:** Deploy from a branch
- **Branch:** `main` · pasta `/ (root)` → **Save**

Em um a dois minutos o site fica em <https://leoneto98.github.io>. A versão em português fica em `/pt/`.

---

## Passo 2 — Redirecionar o endereço antigo

O repositório `leoneto98/site` serve hoje em `leoneto98.github.io/site` com o conteúdo antigo. Substitua o conteúdo dele pelo redirecionamento pronto em `~/professional/site-legacy-redirect/`.

```sh
cd ~/professional/site

# guarde o estado atual numa branch, por segurança
git checkout -b conteudo-antigo && git push -u origin conteudo-antigo
git checkout main

# remove o conteudo antigo mantendo o historico do git
git rm -rq . --ignore-unmatch

# coloca o redirecionamento no lugar
cp ~/professional/site-legacy-redirect/index.html .
cp ~/professional/site-legacy-redirect/404.html .
touch .nojekyll

git add -A
git commit -m "Redireciona para leoneto98.github.io"
git push
```

Depois disso, `leoneto98.github.io/site` e qualquer subpágina antiga (`/site/bio.html`, `/site/master.html`, …) levam ao site novo. O `404.html` cobre as subpáginas porque o GitHub Pages o usa para toda rota inexistente.

> O repositório `twicedataset/site` é separado e **não** é afetado por nada disso — o site do TWICE Dataset continua no ar normalmente.

---

## Passo 3 — Depois de publicar

- [ ] Abrir <https://leoneto98.github.io> **no celular** — o Chrome headless não renderiza abaixo de 500px, então esta é a única checagem mobile que faltou
- [ ] Conferir se o botão de download entrega o PDF
- [ ] Rodar o Lighthouse (DevTools → Lighthouse) — a meta é 95+ nas quatro categorias
- [ ] Validar o JSON-LD em <https://search.google.com/test/rich-results>
- [ ] Colar a URL no <https://www.linkedin.com/post-inspector/> para conferir o card de preview
- [ ] Atualizar a URL do site no LinkedIn e nos PDFs do currículo
- [ ] Submeter <https://leoneto98.github.io/sitemap.xml> ao Google Search Console *(o sitemap ainda não existe — peça se quiser)*

---

## Reverter

Se algo der errado no passo 2, o conteúdo antigo está na branch `conteudo-antigo`:

```sh
cd ~/professional/site
git checkout main
git reset --hard origin/conteudo-antigo
git push --force-with-lease
```
