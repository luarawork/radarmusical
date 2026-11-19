# Ter o radar como app no celular

O celular só transforma em atalho (ícone na tela inicial) uma página que esteja **na internet**,
num endereço `https://`. O `radar.html` fica no seu computador, então ele precisa ser publicado
primeiro.

O radar publica sozinho no **GitHub Pages**, que é grátis. Você só precisa configurar uma vez.

> **Antes de começar:** a página publicada é **pública**. Ela não aparece no Google e ninguém acha
> sem o link, mas quem tiver o link vê seus artistas, lançamentos e marcações. Se não quiser isso,
> pule este guia: o radar continua funcionando normalmente no computador.

## Parte 1: configurar (uma vez só, uns 10 minutos)

### 1. Crie uma conta no GitHub

Se ainda não tiver, crie em https://github.com/signup. É grátis.

### 2. Crie um repositório pra página

O repositório é a "pasta" do GitHub onde a página vai ficar.

1. Entre em https://github.com/new.
2. Em **Repository name**, escreva um nome, por exemplo `meu-radar`.
3. Marque **Public**. No plano grátis, o GitHub Pages só funciona em repositório público.
4. Marque **Add a README file**, pra o repositório já começar com um arquivo.
5. Clique em **Create repository**.

### 3. Crie uma chave de acesso (token)

O token é uma senha só pra esse repositório. Com ele, o radar consegue enviar a página sem usar a sua senha.

1. Entre em https://github.com/settings/personal-access-tokens e clique em **Generate new token**.
2. **Token name:** `Radar Musical`.
3. **Expiration:** escolha a validade. Quando vencer, é só gerar outro.
4. **Repository access:** escolha **Only select repositories** e marque o `meu-radar`.
5. **Permissions:** clique em **Add permissions** e coloque **Contents** e **Pages** como **Read and write**.
6. Clique em **Generate token** e **copie o código** (começa com `github_pat_`). Ele só aparece uma vez.

### 4. Coloque no `.env`

Abra o arquivo `.env` do radar e preencha, trocando pelo seu usuário do GitHub e pelo token copiado:

```
GITHUB_REPO=seu-usuario/meu-radar
GITHUB_TOKEN=github_pat_...
```

**Nunca publique o `.env`**: o token dá acesso ao seu repositório. Ele já fica fora do Git pelo `.gitignore`.

### 5. Rode o radar

```
python radar_musical.py
```

No fim, ele publica a página e mostra o endereço, algo como:

```
✓ Publicado: https://seu-usuario.github.io/meu-radar/
```

Na primeira vez, o endereço pode levar 1 ou 2 minutos pra começar a funcionar.

## Parte 2: criar o atalho no celular

Abra o endereço no celular.

**iPhone:**
1. Abra no **Safari**, não em outro navegador.
2. Toque no botão **Compartilhar** (o quadrado com a seta pra cima).
3. Role e toque em **Adicionar à Tela de Início** → **Adicionar**.

**Android:**
1. Abra no **Chrome**.
2. Toque em **Instalar app**, no topo da página. Se não aparecer, use o menu **⋮** → **Instalar app**
   ou **Adicionar à tela inicial**.

Pronto: o ícone do radar aparece junto com os seus apps e abre em tela cheia, como um app.

## Atualizações

Cada vez que você roda o radar no computador, a página publicada é atualizada. O atalho no celular
mostra a versão nova na próxima vez que você abrir com internet. Sem internet, abre a última
versão que ficou guardada.

## Por dentro

Toda rodada gera a pasta `saida/site/` com a página (`index.html`), o ícone, o `manifest.webmanifest`
e o `sw.js`. Os dois últimos permitem instalar e abrir sem internet. É essa pasta que vai pro
repositório.

## Problemas comuns

| O que aparece | O que fazer |
|---|---|
| "Não achei o repositório" | confira `GITHUB_REPO` (no formato `usuario/nome`) e se o token tem acesso a esse repositório |
| "Falhou ao enviar index.html (404)" ou "Branch not found" | o repositório foi criado vazio: crie um README nele pelo site do GitHub e rode de novo |
| "não consegui ativar o GitHub Pages" | ative à mão: no repositório, **Settings → Pages**, em "Branch" escolha `main` e `/ (root)`, e salve |
| "O repositório é privado" | em **Settings → General → Danger Zone → Change visibility**, deixe público, ou use outro repositório |
| o endereço abre "404" | espere 1 ou 2 minutos depois da primeira publicação |
| o botão "Instalar app" não aparece | ele só aparece no endereço `https://`, não no arquivo do computador; no iPhone, use Compartilhar → Adicionar à Tela de Início |
