# Histórico de outros apps

O Last.fm só sabe o que você ouviu **desde que criou a conta**, e só pelos apps conectados a ele.
Por isso o radar pode recomendar um artista que você ouvia anos atrás.

Pra evitar isso, baixe seus dados nos apps e coloque os arquivos na pasta **`historico/`**.
O `.zip` pode ir do jeito que chegou, sem descompactar. Na próxima rodada, todo artista que
aparecer nesses dados deixa de ser recomendado.

## Como pedir os dados

| App | Onde pedir | Quanto demora | O que o radar lê |
|---|---|---|---|
| **Spotify** (mais completo) | spotify.com/account/privacy → **"Histórico de streaming estendido"** | até 30 dias | `Streaming_History_Audio_*.json` (a vida toda) |
| **Spotify** (mais rápido) | spotify.com/account/privacy → **"Dados da conta"** | uns 5 dias | `StreamingHistory*.json` (último ano) e `YourLibrary.json` (músicas curtidas) |
| **YouTube Music** | takeout.google.com → desmarque tudo → **"YouTube e YouTube Music"** → histórico, formato **JSON** | minutos a horas | `watch-history.json` (só os itens do YouTube Music) |
| **Apple Music** | privacy.apple.com → **"Obter uma cópia dos seus dados"** → Apple Media Services | até 7 dias | arquivos `.csv` com coluna de artista (*ainda não testado com um arquivo real*) |

Dá pra pedir os dois do Spotify. Os "Dados da conta" chegam antes e já ajudam.

## Regras

- Reproduções com **menos de 30 segundos** não contam, pra uma música pulada não marcar o
  artista como "já ouvido".
- Podcasts e vídeos comuns do YouTube são ignorados.
- Os nomes são comparados sem acento, maiúsculas nem pontuação. "The Beatles", "beatles" e
  "Beatles" contam como o mesmo artista.
- No fim de cada rodada, o terminal mostra quantos artistas vieram de cada app e quantos deixaram
  de ser recomendados.

## Outras pastas

Se os arquivos estão em outro lugar, por exemplo numa pasta do Google Drive, aponte no `.env`:

```
HISTORICO_PASTA=C:\Users\voce\Google Drive\Dados Spotify
```

Separe várias pastas com `;`.

## Outro formato

Se você tem um arquivo de outro app (Deezer, Tidal, Amazon Music…), qualquer `.csv` com uma
coluna chamada `Artist Name`, `Artist`, `artistName` ou `Artista` já funciona. Se o seu não
funcionar, abra uma *issue* com o nome das colunas, sem dados pessoais.
