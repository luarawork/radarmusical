# Como funciona

## Passo a passo de uma rodada

1. **Biblioteca:** baixa do Last.fm todos os artistas que você já ouviu, com o número de plays.
   Fica guardado por um dia.
2. **Gostos:** junta os arquivos de curti / não curti ([gostos.md](gostos.md)).
3. **Histórico:** lê os dados exportados dos apps ([historico.md](historico.md)).
4. **Descobertas:**
   - pega seus **400 artistas mais ouvidos** e, pra cada um, os 50 mais parecidos segundo o Last.fm;
   - cada candidato soma pontos: parecença × peso da referência, sendo que o peso cresce com os
     seus plays daquele artista;
   - artistas que você **curtiu** também viram referência; os que você **não curtiu** tiram pontos
     dos parecidos com eles;
   - **saem da lista:**
     - quem está no seu Last.fm ou no histórico exportado;
     - quem você marcou como não curti ou já conheço;
     - colaborações ("A & B", "A feat. B") em que você já ouve todos os envolvidos;
   - ficam os **300** com mais pontos. Pra esses, o script busca no Last.fm o número de ouvintes e
     os gêneros.
5. **Lançamentos:** pra cada artista da sua biblioteca, em ordem de plays, procura o artista no
   Deezer (ou no Spotify) e lista o que saiu nos últimos 365 dias.
   - Só vale se o nome bater **exatamente**, pra não trazer disco de outro artista com nome parecido.
   - Se um título saiu como single e depois dentro do álbum, fica só o álbum.
   - Datas até 60 dias à frente aparecem como **Em breve**; mais longe que isso costumam ser erro do catálogo e ficam de fora.
   - Compositores clássicos (tags como "classical" e "composer") ficam de fora: o catálogo lista gravações novas de outros músicos como se fossem deles.
   - O gênero vem das tags do Last.fm.
6. **Página:** gera `saida/radar.html` e a versão instalável `saida/site/`, e publica no GitHub
   Pages se estiver configurado ([celular.md](celular.md)).

## Limites das APIs

O script respeita os limites de cada serviço. **Não diminua os intervalos**: o Last.fm pode
suspender a chave e o Spotify bloqueia por um dia.

| Serviço | Ritmo do script | Por quê |
|---|---|---|
| Last.fm | 1 pedido a cada 0,6 s | a documentação avisa que "várias chamadas por segundo" podem suspender a conta |
| Deezer | ~6 pedidos/s, 3 em paralelo | o limite relatado é 50 pedidos a cada 5 s |
| Spotify | 1 pedido a cada 1–1,6 s, até 1.200/dia | cota diária escondida no modo de desenvolvedor ([spotify.md](spotify.md)) |

Todos os pedidos se identificam com o User-Agent `RadarMusical/1.0`, como o Last.fm pede.
Em erros temporários, o script espera e tenta de novo. Se o Last.fm suspender a chave (erro 26),
ele para na hora.

## Cache

Tudo fica em `cache/`. Apagar a pasta faz o script começar do zero.

| Arquivo | O que guarda | Validade |
|---|---|---|
| `biblioteca.json` | seus artistas do Last.fm | 1 dia |
| `similares.json`, `info_artistas.json`, `tags_artistas.json` | parecidos, ouvintes e gêneros | sem prazo |
| `deezer_artistas.json` | ID de cada artista no Deezer + lançamentos | ID 60 dias, lançamentos 1 dia* |
| `spotify_artistas.json` | o mesmo, no Spotify | ID 60 dias, lançamentos 7 dias |
| `spotify_uso.json`, `spotify_bloqueio.json` | pedidos do dia e bloqueio em vigor | — |

\* Os termos do Deezer pedem pra não manter cópia do catálogo, por isso a lista de lançamentos é
refeita todo dia.

## Ajustes

No `.env`:

| Variável | Padrão | O que faz |
|---|---|---|
| `FONTE_LANCAMENTOS` | `deezer` | `deezer` ou `spotify` |
| `APP_MUSICA` | `spotify` | app padrão do botão Ouvir: `spotify`, `apple`, `ytmusic`, `deezer`, `tidal`, `amazon` |
| `HISTORICO_PASTA` | — | pastas extras com dados exportados |
| `GOSTOS_PASTA` | — | pastas extras com arquivos de gostos |
| `GITHUB_REPO`, `GITHUB_TOKEN`, `GITHUB_BRANCH` | — | publicação no GitHub Pages |

No topo do `radar_musical.py`:

| Ajuste | Padrão | O que faz |
|---|---|---|
| `DIAS_LANCAMENTO` | 365 | janela de lançamentos, em dias |
| `SEMENTES_DESCOBERTA` | 400 | quantos dos seus mais ouvidos servem de referência |
| `SIMILARES_POR_SEMENTE` | 50 | quantos parecidos buscar por referência |
| `MAX_DESCOBERTAS` | 300 | tamanho da lista de descobertas |
| `DIAS_EM_BREVE` | 60 | até quantos dias à frente um lançamento aparece como "Em breve" |
| `TAGS_SEM_LANCAMENTO` | classical, composer… | artistas com essas tags não entram nos lançamentos |
| `PESO_CURTI` / `PESO_NAO_CURTI` | 2,0 / −1,5 | força das suas marcações |
| `ORCAMENTO_SPOTIFY_DIA` | 1200 | máximo de pedidos ao Spotify por dia |

## Visual

O visual da página fica em `modelo.html`: HTML, CSS e JavaScript num arquivo só, sem dependências.
O script troca o marcador `/*__DADOS__*/null` pelos seus dados. Dá pra mudar cores e textos ali
sem mexer no Python.
