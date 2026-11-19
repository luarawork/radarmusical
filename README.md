# Radar Musical 🎧

**Descubra o que saiu de novo dos artistas que você ouve, e artistas novos parecidos com o seu gosto.**

O Radar Musical lê o seu histórico no [Last.fm](https://www.last.fm) e monta uma página só sua com:

- **Lançamentos:** álbuns, EPs e singles que saíram nos últimos 12 meses dos artistas que você ouve,
  e os que saem nos próximos dias ("Em breve").
- **Descobertas:** 300 artistas parecidos com os que você mais ouve, mas que você **nunca ouviu**,
  dizendo por que cada um foi recomendado ("porque você ouve X, Y e Z").
- **Curtidos:** tudo o que você marcou que curtiu, num lugar só.

Na página você pode:

- filtrar por **período** (7 dias, 30 dias, 3 meses, 1 ano, em breve), **tipo**, **gênero** e artistas preferidos;
- **ordenar** de vários jeitos e **buscar**;
- tocar em **Ouvir** e abrir direto no seu app: Spotify, Apple Music, YouTube Music, Deezer, Tidal ou Amazon Music;
- marcar **Curti / Não curti / Conheço**, que melhoram as recomendações da próxima vez;
- escolher o **tema claro ou escuro**;
- se quiser, ter o radar como **app no celular**, com ícone na tela inicial.

**Grátis, sem anúncios e sem entrar em nenhuma conta sua:** o programa só consulta dados públicos.

---

## Por que eu criei: furar a bolha do algoritmo

Os apps de música decidem o que chega até você. As playlists de descoberta e os radares de
lançamentos são montados por algoritmos que priorizam o que mantém você ouvindo: mais do mesmo,
o que já é popular, os artistas que você já conhece. Com o tempo, a gente fica numa **bolha**.
Disco novo de um artista que você amava passa batido, e quem é menor quase nunca aparece.

Criei o Radar Musical pra tirar essa decisão do algoritmo e devolver pra você:

- **Todos os lançamentos, não uma seleção.** O radar confere **cada artista** do seu histórico, inclusive
  aquele que você ouviu poucas vezes anos atrás, e mostra tudo o que saiu. Quem decide o que é
  relevante é você, com filtros que você controla.
- **Descobertas que não dependem de engajamento.** As recomendações vêm de dados abertos do Last.fm:
  artistas que **pessoas com gosto parecido com o seu** também ouvem. Nada de "mais tocados" nem de
  quem pagou pra aparecer. Dá pra filtrar só os **menos conhecidos** e ir atrás do underground de propósito.
- **Transparente.** Cada descoberta mostra **por que** foi recomendada ("porque você ouve X, Y e Z").
  Nada de caixa-preta.
- **Sem ficar preso a um app.** O seu histórico vem do Last.fm, que funciona com vários apps, e o botão
  Ouvir abre onde você quiser.
- **Você ensina, e ninguém mais usa isso.** Curti, não curti e conheço ficam no seu computador e
  servem só pra melhorar o seu radar.

É uma ferramentinha pessoal, feita pra quem sente que o algoritmo anda escolhendo demais o que
você ouve. Se ela te ajudar a achar um disco ou um artista que você não teria encontrado, já valeu.

---

## Sumário

> 📖 Por que este projeto existe: [furar a bolha do algoritmo](#por-que-eu-criei-furar-a-bolha-do-algoritmo).
>
> 💡 **Não quer mexer no terminal?** Uma IA pode instalar e rodar tudo por você:
> [Jeito fácil: com o Claude Code ou o Cursor](#jeito-fácil-com-o-claude-code-ou-o-cursor).

1. [Como funciona, em uma frase](#1-como-funciona-em-uma-frase)
2. [O que você precisa](#2-o-que-você-precisa)
3. [Passo 1: ligar o Last.fm ao seu app de música](#3-passo-1-ligar-o-lastfm-ao-seu-app-de-música)
4. [Passo 2: instalar o Python](#4-passo-2-instalar-o-python)
5. [Passo 3: baixar o Radar Musical](#5-passo-3-baixar-o-radar-musical)
6. [Passo 4: pegar a chave do Last.fm](#6-passo-4-pegar-a-chave-do-lastfm)
7. [Passo 5: configurar](#7-passo-5-configurar)
8. [Passo 6: rodar](#8-passo-6-rodar)
9. [Usando a página](#9-usando-a-página)
10. [Uso no dia a dia](#10-uso-no-dia-a-dia)
11. [Extras opcionais](#11-extras-opcionais)
12. [Problemas comuns](#12-problemas-comuns)
13. [Perguntas frequentes](#13-perguntas-frequentes)
14. [Pastas do projeto](#14-pastas-do-projeto)
15. [Privacidade e termos](#15-privacidade-e-termos)

---

## 1. Como funciona, em uma frase

Você ouve música no seu app → o app avisa o **Last.fm** do que você ouviu (isso se chama *scrobble*)
→ o Radar Musical lê seu Last.fm, procura o que seus artistas lançaram e quem é parecido com eles →
gera uma página no seu computador.

| Serviço | Pra que o radar usa |
|---|---|
| **Last.fm** | saber o que você ouve e quais artistas são parecidos |
| **Deezer** | consultar o que cada artista lançou e as capas. Você **não precisa usar o Deezer** nem ter conta: é só um catálogo público de consulta |
| **Seu app de música** | onde o botão **Ouvir** abre as músicas |

---

## 2. O que você precisa

- Um **computador** com Windows, Mac ou Linux. O programa roda no computador; a página depois pode
  ser aberta em qualquer navegador.
- Uma **conta no Last.fm** (grátis), de preferência já com algum tempo de músicas registradas.
- **Python**, um programa gratuito que roda o radar. O passo 2 explica como instalar.
- Uns **20 minutos** pra configurar na primeira vez.

Você **não precisa** saber programar. Dá pra seguir de dois jeitos:

- **Jeito fácil:** uma IA faz a instalação e roda pra você. Veja logo abaixo.
- **Passo a passo manual:** você copia e cola alguns comandos. Siga a partir do [passo 1](#3-passo-1-ligar-o-lastfm-ao-seu-app-de-música).

---

## Jeito fácil: com o Claude Code ou o Cursor

O **Claude Code** e o **Cursor** são programas com uma IA que conversa em português e consegue,
**no seu computador**:
- ler este projeto;
- instalar o que falta;
- criar a configuração;
- rodar o radar;
- resolver erros que aparecerem.

Você só explica o que quer e aprova cada passo.

Mesmo assim, você ainda precisa fazer duas coisas que só você pode fazer:
- ligar o Last.fm ao seu app de música ([passo 1](#3-passo-1-ligar-o-lastfm-ao-seu-app-de-música));
- pegar a sua chave do Last.fm ([passo 4](#6-passo-4-pegar-a-chave-do-lastfm)).

Todo o resto a IA faz.

### Opção A: Claude Code

1. Baixe o app do Claude em https://claude.ai/download e entre com a sua conta.
   O Claude Code precisa de um plano pago do Claude (Pro ou superior).
2. No app, abra a aba **Code**.
3. Escolha uma pasta pro projeto: pode ser uma pasta vazia, como `Documentos\Radar Musical`, ou a
   pasta onde você já descompactou o ZIP.
4. Cole um dos pedidos abaixo na conversa.

> Quem já usa o terminal também pode instalar o Claude Code por lá. Veja as instruções em
> https://claude.com/claude-code.

### Opção B: Cursor

1. Baixe em https://cursor.com e instale. Tem plano gratuito, com limite de uso.
2. Abra o Cursor → **File → Open Folder** e escolha uma pasta pro projeto.
3. Abra o chat da IA (`Ctrl + L` no Windows, `Cmd + L` no Mac) e deixe no modo **Agent**.
4. Cole um dos pedidos abaixo na conversa.

### Pedidos prontos pra copiar e colar

**Instalar do zero, numa pasta vazia:**

```
Quero usar o Radar Musical (https://github.com/luarawork/radarmusical) nesta pasta.
Baixe o projeto aqui e siga o README.md pra instalar: confira se o Python 3.9+ está
instalado (se não estiver, me explique como instalar), instale as dependências do
requirements.txt e crie o arquivo .env a partir do .env.exemplo. Me peça só o meu
usuário do Last.fm e a minha API key. Depois rode o radar_musical.py e me avise quando
a página estiver pronta.
```

**Já baixei o ZIP e abri a pasta do projeto:**

```
Leia o README.md deste projeto e faça a instalação pra mim: instale as dependências,
crie o .env a partir do .env.exemplo (me peça o meu usuário do Last.fm e a API key)
e rode o radar_musical.py. Me avise quando terminar e abra a página.
```

**Rodar de novo (toda semana, por exemplo):**

```
Rode o radar_musical.py de novo e abra a página quando terminar.
```

**Usar os dados que baixei do Spotify / YouTube Music:**

```
Coloquei meus dados exportados na pasta historico. Rode o radar de novo e me diga
quantos artistas do histórico foram reconhecidos.
```

**Ter o radar como app no celular:**

```
Me ajude a publicar o radar no GitHub Pages seguindo o docs/celular.md, um passo de cada vez.
```

**Deu algum erro:**

```
Rodei o radar e apareceu este erro: [cole aqui a mensagem]. Me ajude a resolver.
```

### Cuidados

- **Leia o que a IA pede pra aprovar.** Ela vai pedir permissão pra rodar comandos no seu computador.
  Pra instalar e rodar o radar, os comandos esperados são parecidos com os deste guia:
  `pip install`, `python radar_musical.py`, criar o `.env`.
- **Sua chave do Last.fm** vai pela conversa até o serviço da IA, pra ela poder escrever no `.env`.
  Se preferir não compartilhar, peça pra IA criar o `.env` vazio e cole a chave você mesmo, abrindo
  o arquivo no Bloco de Notas.
- **Não cole senhas** de nenhuma conta na conversa. O radar não precisa de senha de nada; só da
  API key do Last.fm.
- A primeira rodada demora de minutos a horas, conforme o tamanho do seu histórico. Deixe a IA rodando.

---

## 3. Passo 1: ligar o Last.fm ao seu app de música

Se você já usa o Last.fm e ele registra o que você ouve, pule pro [passo 2](#4-passo-2-instalar-o-python).

1. Crie uma conta em https://www.last.fm/join.
2. Ligue o seu app de música ao Last.fm:

| App | Como ligar |
|---|---|
| **Spotify** | em https://www.last.fm/settings/applications, clique em **Connect** ao lado de Spotify |
| **Deezer** e **Tidal** | procure a opção **Last.fm** nas configurações do app (os nomes dos menus mudam de versão pra versão) |
| **YouTube Music** | no computador, instale a extensão gratuita **Web Scrobbler** no navegador e conecte ao Last.fm |
| **Apple Music** | o Apple Music não se liga sozinho; use um app "scrobbler" (procure por *scrobbler* na App Store) |

3. Ouça algumas músicas e confira se elas aparecem no seu perfil: `https://www.last.fm/user/SEU-USUARIO`.

> O Last.fm só sabe o que você ouviu **depois** de ligar. Pra o radar também saber o que você
> ouvia antes, veja [Extras: histórico de outros apps](#11-extras-opcionais).

---

## 4. Passo 2: instalar o Python

Primeiro, veja se você já tem. Abra o **terminal**:

- **Windows:** aperte a tecla Windows, digite `cmd` e tecle Enter.
- **Mac:** abra o **Terminal** (Aplicativos → Utilitários → Terminal).

Digite e tecle Enter:

```
python --version
```

No Mac, use `python3 --version`. Se aparecer `Python 3.9` ou mais novo (3.10, 3.11, 3.12, 3.13…),
pule pro [passo 3](#5-passo-3-baixar-o-radar-musical). Se der erro ou mostrar uma versão menor,
instale:

**Windows**
1. Baixe em https://www.python.org/downloads/ (botão amarelo "Download Python").
2. Abra o instalador e **marque a caixa "Add python.exe to PATH"**, embaixo. Esse passo é importante.
3. Clique em **Install Now**.
4. **Feche e abra o terminal de novo** e teste `python --version`.

**Mac**
1. Baixe em https://www.python.org/downloads/ e instale normalmente.
2. Feche e abra o Terminal e teste `python3 --version`.

> No Mac e no Linux, use sempre `python3` e `pip3` nos comandos deste guia, no lugar de `python` e `pip`.

---

## 5. Passo 3: baixar o Radar Musical

1. Nesta página do GitHub, clique no botão verde **Code** → **Download ZIP**.
2. Descompacte o ZIP numa pasta fácil de achar, por exemplo `Documentos\Radar Musical`.

Agora abra o terminal **dentro dessa pasta**:

- **Windows:** abra a pasta no Explorador de Arquivos, clique na barra de endereço lá em cima,
  apague o que estiver escrito, digite `cmd` e tecle Enter.
- **Mac:** clique com o botão direito na pasta → **Serviços** → **Novo Terminal na Pasta**.
  Se não aparecer, digite `cd ` (com espaço) no Terminal, arraste a pasta pra janela e tecle Enter.

Instale o que o radar precisa:

```
pip install -r requirements.txt
```

Se der "pip não é reconhecido", use `python -m pip install -r requirements.txt`.

> Quem usa Git pode clonar o repositório em vez de baixar o ZIP.

---

## 6. Passo 4: pegar a chave do Last.fm

A chave (API key) é um código que deixa o radar consultar o Last.fm. É grátis e leva 2 minutos.

1. Com a sua conta do Last.fm aberta, entre em https://www.last.fm/api/account/create.
2. Preencha:
   - **Contact email:** seu e-mail;
   - **Application name:** `Radar Musical`;
   - o resto pode ficar em branco.
3. Clique em **Submit**.
4. Na página seguinte, copie o código ao lado de **API key**. É uma sequência de 32 letras e números.
   O "Shared secret" não é necessário.

---

## 7. Passo 5: configurar

As configurações ficam num arquivo chamado `.env`. Ele começa com ponto e não tem extensão.

1. No terminal, ainda dentro da pasta do radar, crie o `.env` a partir do exemplo:

   - **Windows:** `copy .env.exemplo .env`
   - **Mac/Linux:** `cp .env.exemplo .env`

2. Abra o arquivo pra editar:

   - **Windows:** `notepad .env`
   - **Mac:** `open -e .env`

3. Preencha as duas primeiras linhas e **salve**:

   ```
   LASTFM_USER=seu-usuario-do-lastfm
   LASTFM_API_KEY=a-chave-que-voce-copiou
   ```

   Sem espaços e sem aspas. O resto do arquivo é opcional e pode ficar como está.

> **Nunca compartilhe nem publique o seu `.env`.** Ele tem a sua chave.

---

## 8. Passo 6: rodar

No terminal, dentro da pasta do radar:

```
python radar_musical.py
```

(Mac/Linux: `python3 radar_musical.py`)

Você vai ver o progresso, mais ou menos assim:

```
→ Baixando todos os artistas de 'seu-usuario' no Last.fm…
✓ 1234 artistas no seu histórico
→ Buscando artistas semelhantes a partir dos seus 400 mais ouvidos…
✓ 300 artistas novos pra você descobrir
→ Conferindo lançamentos no Deezer: 1234 artistas a checar
   artistas [##########....................] 400/1234
✓ 5210 lançamentos encontrados
→ Buscando gêneros de 900 artistas com lançamentos…
🎧 Pronto em 25 min → ...\saida\radar.html
```

No fim, a página **abre sozinha no navegador**. Ela fica salva em `saida/radar.html`, e dá pra
abrir de novo com dois cliques nesse arquivo.

**Quanto tempo leva?** (aproximado: depende da sua internet)

| Tamanho do seu histórico | Primeira vez | Próximas vezes |
|---|---|---|
| até 500 artistas | ~5 minutos | ~2 minutos |
| ~2.000 artistas | ~30 minutos | ~15 minutos |
| ~5.000 artistas | ~1h30 a 2h | ~45 minutos |

A primeira vez é mais lenta porque busca tudo do zero. Depois, quase tudo vem do que ficou salvo.

- **Pode interromper** quando quiser, apertando `Ctrl + C`. Na próxima vez, ele **continua de onde
  parou**, porque o progresso fica salvo na pasta `cache/`.
- O computador pode ficar sendo usado normalmente enquanto roda.

---

## 9. Usando a página

**No topo**
- **Abas:** Lançamentos, Descobertas e Curtidos. O número em cada aba mostra quantos itens novos ela tem.
- **Ajustes** (canto superior direito): o app em que o botão Ouvir abre, o tema (claro, escuro ou
  automático), o arquivo de marcações e a instalação no celular.

**Barra de busca e filtros**
- **Buscar:** artista, título ou gênero. Atalho: tecla `/`.
- **Período** (em Lançamentos): 7 dias, 30 dias, 3 meses, 1 ano ou Em breve.
- **Ordenar:** mais recentes, dos artistas que você mais ouve, A–Z…
- **Filtros:** tipo (álbum, EP, single), gêneros, "meu top 50 / 200 / 1000", popularidade (em
  Descobertas) e se quer ver o que já descartou.
- Logo abaixo, um **resumo** mostra o que está aparecendo. Cada filtro ativo tem um ✕ pra tirar.

**Cards**
- Toque na **capa** ou em **Ouvir** pra abrir no seu app.
- Toque no **nome do artista** pra ver só os lançamentos dele.
- **"+N deste artista":** pra ninguém tomar a lista, aparecem no máximo 3 lançamentos por artista.
  Clique pra ver todos.
- **♥ Curti / ✕ Não curti** (lançamentos) e **Curti / Conheço / Não curti** (descobertas):
  - "Não curti" e "Conheço" tiram o card da lista, com a opção de **Desfazer**;
  - o que você curte vai pra aba **Curtidos**.

**Levar suas marcações pra próxima vez**

As marcações ficam salvas **no navegador**. Pra o radar usá-las na próxima geração:
**Ajustes → Baixar arquivo de marcações**, e coloque o arquivo na pasta `gostos/` ou deixe em Downloads.

Na próxima vez que você rodar:
- quem você marcou como **não curti** ou **conheço** some das descobertas;
- artistas parecidos com quem você não curtiu perdem pontos;
- quem você **curtiu** passa a servir de referência pra novas recomendações.

Detalhes, inclusive como juntar marcações de vários aparelhos: [docs/gostos.md](docs/gostos.md).

---

## 10. Uso no dia a dia

1. **Uma vez por semana**, por exemplo, abra o terminal na pasta e rode `python radar_musical.py`.
2. A página nova abre com os lançamentos atualizados.
3. Se você marcou coisas, baixe o arquivo de marcações antes de rodar (Ajustes → Baixar).

**Atualizar o Radar Musical pra uma versão nova:** baixe o ZIP novo e copie pra dentro da nova
pasta o seu `.env` e as pastas `cache/`, `gostos/` e `historico/`, pra não perder nada.

**Desinstalar:** apague a pasta. O radar não instala nada fora dela; só o Python fica, se você quiser mantê-lo.

---

## 11. Extras opcionais

| Quero… | Guia |
|---|---|
| que ele **não recomende artistas que eu já ouvia antes** de usar o Last.fm | [docs/historico.md](docs/historico.md): baixe seus dados do Spotify, YouTube Music ou Apple Music e coloque na pasta `historico/` |
| usar **curti / não curti em vários aparelhos** | [docs/gostos.md](docs/gostos.md) |
| ter o radar como **app no celular** (ícone na tela inicial) | [docs/celular.md](docs/celular.md): passo a passo com o GitHub Pages, grátis |
| buscar os lançamentos **no Spotify** em vez do Deezer | [docs/spotify.md](docs/spotify.md): precisa de conta Premium e é bem mais lento |
| entender **como funciona** por dentro, os limites e os ajustes | [docs/como-funciona.md](docs/como-funciona.md) |

---

## 12. Problemas comuns

| O que aparece | O que fazer |
|---|---|
| `'python' não é reconhecido…` / `command not found` | O Python não está instalado ou não está no PATH. Reinstale marcando **"Add python.exe to PATH"** e abra um terminal novo. No Mac, use `python3`. |
| No Windows, digitar `python` abre a **Microsoft Store** | O Python ainda não foi instalado pelo site. Instale pelo [passo 2](#4-passo-2-instalar-o-python) e abra um terminal novo. |
| `'pip' não é reconhecido…` | Use `python -m pip install -r requirements.txt`. |
| `No such file or directory: 'radar_musical.py'` | O terminal não está na pasta do radar. Veja como abrir no [passo 3](#5-passo-3-baixar-o-radar-musical). |
| `Falta a biblioteca 'requests'` | Rode `pip install -r requirements.txt`. |
| `✗ Faltam chaves no arquivo .env: …` | O `.env` não existe, está com outro nome (às vezes o Windows salva como `.env.txt`) ou falta preencher as linhas citadas. Veja o [passo 5](#7-passo-5-configurar). |
| `✗ Não consegui ler o Last.fm…` | Confira o usuário e a chave no `.env`, sem espaços nem aspas. Abra `https://www.last.fm/user/SEU-USUARIO` pra ver se o perfil existe. |
| `✗ O Last.fm suspendeu esta chave (erro 26)` | Pare de rodar e fale com o Last.fm. Não altere os intervalos do programa: eles existem pra isso não acontecer. |
| Recomenda artistas que eu **já conheço** | O Last.fm não sabe o que você ouvia antes de ligá-lo. Marque **Conheço** e/ou siga [docs/historico.md](docs/historico.md). |
| Faltou um lançamento de um artista que eu ouço | O nome do artista no Last.fm e no catálogo precisa ser **idêntico**, pra evitar trazer disco de outro artista com nome parecido. O terminal mostra quantos não foram achados. |
| A página abriu mas está **sem lançamentos** | A conferência foi interrompida antes do fim. Rode de novo: ela continua de onde parou. |
| Caiu a internet / fechei sem querer | Rode de novo. O progresso está salvo. |
| A página está lenta no celular | Com históricos muito grandes, a página fica pesada (mais de 10 MB). A primeira abertura demora mais; depois, os filtros e a rolagem ficam rápidos. |

---

## 13. Perguntas frequentes

**Preciso pagar alguma coisa?**
Não. Last.fm, Deezer (só consulta), Python e GitHub Pages são gratuitos.

**Preciso ter conta no Deezer?**
Não. O radar só consulta o catálogo público do Deezer pra saber o que cada artista lançou. O botão
Ouvir abre no app que você escolher.

**O radar entra na minha conta do Spotify ou de outro app?**
Não. Ele não pede senha de nenhum app e não mexe em playlists nem em nada seu.

**Funciona no celular?**
O programa roda no computador. A página gerada abre em qualquer navegador, inclusive no celular, e
dá pra transformá-la em app com ícone: [docs/celular.md](docs/celular.md).

**Por que demora na primeira vez?**
Porque o radar respeita os limites de uso do Last.fm e do Deezer: faz poucos pedidos por segundo,
pra sua chave não ser bloqueada. Depois, quase tudo vem do que ficou salvo.

**Meus dados vão pra algum lugar?**
Ficam no seu computador. A única exceção é se você publicar a página no GitHub Pages pra usar no
celular, e aí ela fica acessível por quem tiver o link.

**Posso rodar todo dia?**
Pode, mas uma vez por semana já é suficiente pra acompanhar os lançamentos.

---

## 14. Pastas do projeto

```
radar_musical.py   o programa
modelo.html        o visual da página (o programa preenche com os seus dados)
requirements.txt   o que precisa instalar (pip install -r requirements.txt)
.env.exemplo       modelo de configuração. Copie pra .env
.env               SUAS configurações e chaves. Nunca publique!
historico/         coloque aqui os dados baixados dos apps (opcional)
gostos/            coloque aqui os arquivos de marcações baixados da página
saida/             a página gerada (radar.html) e a versão pra celular (site/)
cache/             progresso salvo. Pode apagar pra começar do zero
docs/              guias detalhados
CHANGELOG.md       o que mudou em cada versão
```

`.env`, `historico/`, `gostos/`, `saida/` e `cache/` têm dados pessoais e ficam fora do Git pelo
`.gitignore`. Se você fizer um fork, eles nunca são enviados.

---

## 15. Privacidade e termos

- O programa só **consulta** dados públicos: o seu perfil do Last.fm e os catálogos do Deezer
  (ou do Spotify, se você escolher). Ele **não entra em nenhuma conta sua**.
- Tudo fica no seu computador, a não ser que você publique a página no GitHub Pages
  ([docs/celular.md](docs/celular.md)).
- Os pedidos respeitam os limites de cada serviço: no Last.fm, cerca de 1 pedido a cada 0,6 s;
  no Deezer, menos de 50 a cada 5 s.
- **Uso pessoal e não comercial.** Os termos do Last.fm e do Deezer só permitem esse tipo de uso.
- Dados de [Last.fm](https://www.last.fm) (powered by AudioScrobbler), [Deezer](https://www.deezer.com)
  e [Spotify](https://www.spotify.com). Este projeto não tem ligação com nenhum desses serviços.

---

## Licença

[MIT](LICENSE): pode usar, copiar, modificar e distribuir à vontade, inclusive em outros projetos,
desde que mantenha o aviso de licença. O software é oferecido "como está", sem garantias.
