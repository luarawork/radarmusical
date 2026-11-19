# Lançamentos pelo Spotify

Por padrão os lançamentos vêm do **Deezer**: sem chave, sem conta e sem cota diária. O Spotify é
opcional e tem duas desvantagens:

- precisa de conta **Premium** pra criar o app de desenvolvedor, uma exigência do Spotify desde 2026;
- tem uma **cota diária** escondida, então históricos grandes levam vários dias pra conferir.

O botão **Ouvir** abre no Spotify mesmo com o Deezer como fonte. Isso se escolhe na própria página.

## Configurar

1. Acesse https://developer.spotify.com/dashboard e entre com a sua conta.
2. **Create app**:
   - nome `Radar Musical` e qualquer descrição;
   - Redirect URI `http://127.0.0.1:8888/callback`. É obrigatória, mas não é usada.
3. Marque **Web API** e salve.
4. Em **Settings**, copie o **Client ID** e, em "View client secret", o **Client secret**.
5. No `.env`:

   ```
   FONTE_LANCAMENTOS=spotify
   SPOTIFY_CLIENT_ID=...
   SPOTIFY_CLIENT_SECRET=...
   ```

## Cota e bloqueios

O Spotify não publica os números. Pelos relatos, apps pessoais são bloqueados por cerca de
**24 h** depois de algo entre 1.500 e 2.000 pedidos num dia. Por isso o script:

- usa no máximo `ORCAMENTO_SPOTIFY_DIA = 1200` pedidos por dia e para sozinho quando chega lá;
- confere primeiro os artistas que você **mais ouve**;
- guarda o ID de cada artista por 60 dias e os lançamentos por 7 dias;
- faz uma consulta por vez, com intervalo de 1 a 1,6 s;
- se levar um bloqueio, **não insiste**: anota até quando dura, gera a página com o que já tem e
  avisa quando dá pra rodar de novo. Insistir pode alongar o bloqueio.

Com ~5 mil artistas no histórico, a primeira conferência completa leva de **8 a 10 dias**,
rodando uma vez por dia.
