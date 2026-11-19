# Mudanças

## Novembro de 2026: "já ouvi"

- O radar confere no seu Last.fm se você **já ouviu** cada lançamento. Ele compara artista + título,
  ignorando acentos e sufixos como "(Deluxe)", "(Ao Vivo)" e "- Single".
- Na página, o que você já ouviu fica **oculto por padrão**. O resumo diz quantos ficaram de fora, e
  **Filtros → Incluir o que eu já ouvi** mostra todos com o selo "✓ já ouvi · N×".
- Versões do mesmo título ("Disco" e "Disco (Deluxe)") viram um lançamento só.

## Novembro de 2026: ajustes finos

- O número na aba **Lançamentos** agora é o **total** de lançamentos, e não só os álbuns e EPs dos últimos 30 dias.
- O resumo avisa quando algum tipo está oculto, por exemplo "só álbuns e EPs (singles ocultos em Filtros)".
- **Gêneros juntos:** variações do mesmo gênero viram um nome só, como brazil / brazilian / brasil →
  "brasileira" e baile funk / funk carioca → "funk brasileiro". Tags que não são gênero ("all", "cover"…) saem.
- README: seção **"Por que eu criei: furar a bolha do algoritmo"**.

## Novembro de 2026: página reorganizada

### Organização
- **Três abas**: Lançamentos, Descobertas e **Curtidos**, uma aba nova com tudo o que você curtiu.
- **Período** em destaque: 7 dias, 30 dias (padrão), 3 meses, 1 ano e **Em breve**.
- **Busca, ordenação e Filtros** numa barra só. Tipo, artistas, popularidade, gêneros e
  "mostrar descartados" ficam num painel de Filtros, com um número que mostra quantos estão ativos.
- **Resumo** do que está aparecendo, com cada filtro removível (✕) e "Limpar tudo".
- **Ajustes** num painel lateral: app do botão Ouvir, tema, arquivo de marcações e instalação.
  O topo da página ficou limpo.

### Usabilidade
- **No máximo 3 por artista**, com "+N deste artista": quem lança muitos singles não toma mais a lista.
- Clicar no **nome do artista** mostra só os lançamentos dele.
- **Carrega aos poucos** (60 por vez) ao rolar: a página abre rápido mesmo com milhares de lançamentos.
- Datas relativas, como "há 3 dias" e "ontem".
- A capa inteira é clicável pra ouvir.
- **Não curti / Conheço** tiram o card com um aviso **Desfazer**.
- Botões das descobertas com texto: Curti, Conheço, Não curti.
- Depois de algumas marcações, um aviso lembra de baixar o arquivo de marcações.
- Atalho `/` pra buscar e `Esc` pra fechar painéis. O que você escolheu (aba, período, ordem,
  filtros) fica lembrado.
- Layout de celular revisado: sem rolagem lateral e com 2 colunas de lançamentos.

### Dados
- Lançamentos com data **até 60 dias à frente** aparecem em "Em breve"; datas mais distantes, que
  costumam ser erro do catálogo, ficam de fora.
- **Compositores clássicos** não entram nos lançamentos: o catálogo lista gravações de outros
  músicos como se fossem deles.

## Novembro de 2026

### Recomendações
- Artistas do **histórico exportado** dos apps (Spotify, YouTube Music, CSV como os da Apple Music)
  não são mais recomendados. Basta colocar os arquivos, ou o `.zip`, em `historico/`.
- **Colaborações** ("A & B", "A feat. B") em que você já ouve todos os artistas não são recomendadas.
- **Curti / não curti / já conheço** passaram a influenciar a próxima rodada:
  - curtidos viram referência;
  - não curtidos tiram pontos dos parecidos;
  - os dois tipos de descarte somem da lista.

### Lançamentos
- Agora vêm do **Deezer** por padrão: sem chave, sem conta Premium e sem cota diária.
- O **Spotify** continua como opção (`FONTE_LANCAMENTOS=spotify`), com proteção contra bloqueio:
  - orçamento diário;
  - mais ouvidos primeiro;
  - para sozinho se a cota acabar, sem insistir.
- Os gêneros dos lançamentos vêm das tags do Last.fm.

### Página
- Visual novo em cards, com capas maiores, tema **claro / escuro / automático** e layout pra celular.
- **Filtro por gênero**, várias ordenações e filtro por estado (não avaliados, curtidos, descartados).
- Botão **Ouvir** no app escolhido: Spotify, Apple Music, YouTube Music, Deezer, Tidal ou Amazon Music.
- **Instalável no celular**, com ícone, botão Instalar e funcionamento sem internet, quando publicada
  no **GitHub Pages**. O script publica sozinho se estiver configurado.
- "Salvar meus gostos" exporta as marcações com data. O script **junta os arquivos de vários
  aparelhos**, e vale a marcação mais recente.

### Uso responsável das APIs
- Last.fm: um pedido a cada 0,6 s, User-Agent identificado e tratamento dos erros 8, 26 e 29.
- Deezer: menos de 50 pedidos a cada 5 s; só o ID do artista fica guardado por mais de um dia.

### Projeto
- Pastas organizadas: `saida/`, `historico/`, `gostos/`, `cache/` e `docs/`.
- `README.md` com começo rápido e guias em `docs/`.
- `.gitignore` deixa de fora chaves e dados pessoais.
- O usuário do Last.fm não fica mais fixo no código.
