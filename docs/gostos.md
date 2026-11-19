# Curti / não curti

Cada card da página tem botões:

- **Lançamentos**: ♥ curti e ✕ não curti. Passe o mouse em cima pra ver o nome do botão.
- **Descobertas**: **Curti**, **Conheço** e **Não curti**.

Tudo o que você curtiu aparece na aba **Curtidos**.

## O que muda

Na página, na hora:

- **Não curti** e **Conheço** tiram o card da lista. Um aviso com **Desfazer** aparece por alguns segundos.
- Pra ver de novo o que você tirou, abra **Filtros** e marque "Incluir o que marquei como não curti ou já conheço".
- Clicar de novo no mesmo botão desmarca.

Na próxima geração do radar:

| Marcação | Efeito |
|---|---|
| **Não curti** | o artista some das descobertas, e artistas **parecidos com ele perdem pontos** |
| **Conheço** | o artista some das descobertas |
| **Curti** | o artista continua na lista e passa a servir de **referência** pra novas recomendações |

## Levar pra próxima geração

As marcações ficam salvas **no navegador** em que você clicou. Pra o script usar:

1. Abra **Ajustes**, no canto de cima, e clique em **"Baixar arquivo de marcações"**. Depois de
   algumas marcações, a página também lembra você com um aviso embaixo.
2. Ele baixa um arquivo `radar_gostos_<data e hora>.json`.
3. Deixe o arquivo em **`gostos/`**, em **Downloads** ou numa pasta configurada em `GOSTOS_PASTA`.

Em Ajustes dá pra ver quantas marcações ainda não foram baixadas. O script lê **todos** os
arquivos que encontrar nesses lugares.

## Vários aparelhos

Cada navegador e cada aparelho guarda as próprias marcações. Pra juntar tudo:

1. Escolha uma pasta que todos os aparelhos enxergam (Google Drive, OneDrive, Dropbox…).
2. No `.env`, aponte pra ela:

   ```
   GOSTOS_PASTA=C:\Users\voce\Google Drive\Radar Musical
   ```

3. Em cada aparelho, baixe o arquivo de marcações e coloque nessa pasta.

O script **junta todos os arquivos**:

- **Cada marcação guarda quando foi feita.** Se você curtiu algo no celular e depois desmarcou
  no computador, vale a mais recente.
- **Desmarcar também conta:** a marcação some nos outros aparelhos.
- **Os nomes dos arquivos têm data e hora**, então dois aparelhos não sobrescrevem um ao outro.

A página gerada já vem com tudo junto, então ao abrir em qualquer aparelho as marcações estão lá.
