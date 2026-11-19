#!/usr/bin/env python3
"""
Radar Musical
-------------
1) Puxa todos os artistas que você já escutou no Last.fm.
2) Confere no Deezer (ou no Spotify) quem lançou álbum / EP / single nos últimos 12 meses.
3) Recomenda artistas parecidos com os seus favoritos que você ainda não ouviu
   (cruzando com o histórico exportado dos apps em historico/ e com seus curti/não curti).
4) Gera a página saida/radar.html e a versão instalável em saida/site/
   (e publica no GitHub Pages, se configurado).

Os catálogos são só consultados: o script não entra na sua conta de nenhum app.

Uso:  python radar_musical.py
Requer: pip install -r requirements.txt
Configuração no arquivo .env (veja .env.exemplo, README.md e docs/).

O progresso fica salvo em cache/, então se cair no meio é só rodar de novo
que ele continua de onde parou.
"""

import json
import math
import os
import random
import re
import sys
import threading
import time
import unicodedata
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote

try:
    import requests
except ImportError:
    sys.exit("Falta a biblioteca 'requests'. Rode:  pip install requests")

# ----------------------------------------------------------------------------
# Configuração
# ----------------------------------------------------------------------------
BASE = Path(__file__).resolve().parent
CACHE = BASE / "cache"          # progresso salvo (pode apagar pra começar do zero)
SAIDA = BASE / "saida"          # radar.html e a versão instalável (site/)
PASTA_GOSTOS = BASE / "gostos"  # arquivos "radar_gostos_*.json" exportados pela página
PASTA_HISTORICO = BASE / "historico"  # dados baixados do Spotify, YouTube Music etc.
for _p in (CACHE, SAIDA, PASTA_GOSTOS, PASTA_HISTORICO):
    _p.mkdir(exist_ok=True)

DIAS_LANCAMENTO = 365        # janela de "lançou recentemente"
SEMENTES_DESCOBERTA = 400    # quantos dos seus top artistas viram base p/ recomendação
SIMILARES_POR_SEMENTE = 50
MAX_DESCOBERTAS = 300        # tamanho da lista final de descobertas
DIAS_EM_BREVE = 60           # lançamentos marcados pra até X dias à frente aparecem como "Em breve"
# gravações novas de compositores (Beethoven, Chopin…) não são lançamentos "do artista"
TAGS_SEM_LANCAMENTO = {"classical", "composer", "composers", "classical music", "baroque",
                       "romantic", "opera", "classic", "classical period", "impressionism"}
LASTFM_INTERVALO = 0.6       # segundos entre pedidos ao Last.fm (doc: nada de "várias por segundo")
SPOTIFY_INTERVALO = (1.0, 1.6)  # pausa aleatória entre pedidos ao Spotify (1 por vez, sem rajadas)
ORCAMENTO_SPOTIFY_DIA = 1200 # máx. de pedidos ao Spotify por dia (a cota do modo dev é oculta, ~1500-2000)
VALIDADE_CACHE_DIAS = 7      # lançamentos de um artista checado há menos que isso não são checados de novo
VALIDADE_ID_DIAS = 60        # por quanto tempo o ID (ou "não achado") de um artista no Spotify vale
PAUSA_MAXIMA = 120           # se o Spotify pedir pausa maior que isso, para e continua outro dia
USER_AGENT = "RadarMusical/1.0 (script pessoal, nao comercial)"


def carregar_env():
    env = BASE / ".env"
    if env.exists():
        for linha in env.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if linha and not linha.startswith("#") and "=" in linha:
                k, v = linha.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


carregar_env()
LASTFM_KEY = os.environ.get("LASTFM_API_KEY", "")
LASTFM_USER = os.environ.get("LASTFM_USER", "")
SP_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")
SP_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")


# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------
def norm(nome: str) -> str:
    """Normaliza nome de artista p/ comparação (sem acento, caixa, pontuação)."""
    s = unicodedata.normalize("NFKD", nome or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).casefold()
    s = s.replace("&", " and ")
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if s.startswith("the "):
        s = s[4:]
    return s


def ler_json(nome, padrao):
    p = CACHE / nome
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return padrao


def salvar_json(nome, dados):
    p = CACHE / nome
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    tmp.replace(p)


def barra(i, total, prefixo=""):
    largura = 30
    feito = int(largura * i / max(total, 1))
    sys.stdout.write(f"\r{prefixo} [{'#' * feito}{'.' * (largura - feito)}] {i}/{total}")
    sys.stdout.flush()
    if i >= total:
        print()


def data_lancamento(d: str, precisao: str) -> date:
    try:
        if precisao == "day":
            return datetime.strptime(d, "%Y-%m-%d").date()
        if precisao == "month":
            return datetime.strptime(d, "%Y-%m").date()
        return date(int(d[:4]), 1, 1)
    except Exception:
        return date(1900, 1, 1)


# ----------------------------------------------------------------------------
# Last.fm
# ----------------------------------------------------------------------------
LFM_URL = "https://ws.audioscrobbler.com/2.0/"
_lfm_lock = threading.Lock()
_lfm_ultimo = [0.0]


LFM_TEMPORARIOS = (8, 11, 16)   # "tente de novo" / fora do ar / indisponível
_lfm_intervalo = [LASTFM_INTERVALO]


def lastfm(metodo, **params):
    params.update(method=metodo, api_key=LASTFM_KEY, format="json")
    for tentativa in range(5):
        with _lfm_lock:
            espera = _lfm_intervalo[0] - (time.time() - _lfm_ultimo[0])
            if espera > 0:
                time.sleep(espera)
            _lfm_ultimo[0] = time.time()
        try:
            r = requests.get(LFM_URL, params=params, timeout=20,
                             headers={"User-Agent": USER_AGENT})
        except requests.RequestException:
            time.sleep(2 * (tentativa + 1))
            continue
        try:
            j = r.json()
        except ValueError:
            j = {}
        erro = j.get("error") if isinstance(j, dict) else None
        if erro == 26:
            sys.exit("✗ O Last.fm suspendeu esta chave de API (erro 26). "
                     "Pare de rodar o script e fale com o Last.fm.")
        if erro == 29 or r.status_code == 429:
            # limite por IP: espera bem mais e desacelera o resto da execução
            _lfm_intervalo[0] = min(_lfm_intervalo[0] * 2, 5.0)
            espera = int(r.headers.get("Retry-After", 0) or 0) or 30 * (2 ** tentativa)
            print(f"\n   (Last.fm pediu calma — aguardando {espera}s…)")
            time.sleep(espera + random.uniform(0, 3))
            continue
        if erro in LFM_TEMPORARIOS or r.status_code >= 500:
            time.sleep(3 * (tentativa + 1))
            continue
        if erro:  # parâmetro inválido, artista inexistente etc.: não adianta repetir
            return None
        if r.status_code == 200:
            return j
        time.sleep(2 * (tentativa + 1))
    return None


def baixar_biblioteca():
    cache = ler_json("biblioteca.json", None)
    if cache and cache.get("user") == LASTFM_USER and cache.get("dia") == str(date.today()):
        print(f"✓ Biblioteca do Last.fm (cache): {len(cache['artistas'])} artistas")
        return cache["artistas"]

    print(f"→ Baixando todos os artistas de '{LASTFM_USER}' no Last.fm…")
    artistas, pagina, total_pag = [], 1, 1
    while pagina <= total_pag:
        j = lastfm("user.gettopartists", user=LASTFM_USER, period="overall",
                   limit=1000, page=pagina)
        if not j:
            if pagina == 1:
                sys.exit("✗ Não consegui ler o Last.fm. Confira LASTFM_API_KEY e se o perfil é público.")
            break
        bloco = j.get("topartists", {})
        total_pag = int(bloco.get("@attr", {}).get("totalPages", 1))
        for a in bloco.get("artist", []):
            artistas.append({"nome": a["name"], "plays": int(a.get("playcount", 0)),
                             "mbid": a.get("mbid", "")})
        barra(pagina, total_pag, "   páginas")
        pagina += 1
    salvar_json("biblioteca.json", {"user": LASTFM_USER, "dia": str(date.today()),
                                    "artistas": artistas})
    print(f"✓ {len(artistas)} artistas no seu histórico")
    return artistas


# ----------------------------------------------------------------------------
# O que você já ouviu (álbuns e músicas do Last.fm), pra marcar lançamentos já escutados
# ----------------------------------------------------------------------------
# sufixos que mudam o título mas não o disco: "(Deluxe)", "[Ao Vivo]", "- Single", "(feat. X)"…
_SUFIXOS_TITULO = re.compile(
    r"\s*[\(\[][^\)\]]*(deluxe|edition|edição|edicao|remaster|version|versão|versao|live|ao vivo|"
    r"feat|ft\.|with|com |explicit|clean|bonus|expanded|anniversary|mono|stereo|single|ep)[^\)\]]*[\)\]]"
    r"|\s+-\s+(single|ep|deluxe.*|remaster.*|ao vivo.*|live.*)$",
    re.IGNORECASE)


def norm_titulo(titulo):
    t = titulo or ""
    for _ in range(3):   # pode ter mais de um sufixo
        t = _SUFIXOS_TITULO.sub("", t).strip()
    return norm(t)


def baixar_ouvidos():
    """Todos os álbuns e músicas que você já ouviu no Last.fm, com o número de plays.
    Vem 1.000 por página, então é rápido mesmo com históricos grandes. Guardado por 1 dia."""
    cache = ler_json("ouvidos.json", None)
    if cache and cache.get("user") == LASTFM_USER and cache.get("dia") == str(date.today()):
        print(f"✓ Já ouvidos (cache): {len(cache['albuns'])} álbuns e {len(cache['musicas'])} músicas")
        return cache
    resultado = {"user": LASTFM_USER, "dia": str(date.today()), "albuns": {}, "musicas": {}}
    for metodo, raiz, item, chave in (("user.gettopalbums", "topalbums", "album", "albuns"),
                                      ("user.gettoptracks", "toptracks", "track", "musicas")):
        print(f"→ Baixando {'álbuns' if chave == 'albuns' else 'músicas'} que você já ouviu…")
        pagina, total_pag = 1, 1
        while pagina <= total_pag:
            j = lastfm(metodo, user=LASTFM_USER, period="overall", limit=1000, page=pagina)
            if not j:
                break
            bloco = j.get(raiz, {})
            total_pag = int(bloco.get("@attr", {}).get("totalPages", 1))
            for x in bloco.get(item, []):
                artista = (x.get("artist") or {}).get("name", "")
                k = f"{norm(artista)}|{norm_titulo(x.get('name', ''))}"
                resultado[chave][k] = resultado[chave].get(k, 0) + int(x.get("playcount", 0) or 0)
            barra(pagina, total_pag, "   páginas")
            pagina += 1
    salvar_json("ouvidos.json", resultado)
    print(f"✓ Você já ouviu {len(resultado['albuns'])} álbuns e {len(resultado['musicas'])} músicas")
    return resultado


def marcar_ouvidos(lanc, ouvidos):
    """Põe em cada lançamento quantas vezes você já ouviu (0 = nunca).
    Álbum/EP: compara com seus álbuns; single: com suas músicas (e álbuns, pra singles
    que o app registrou como álbum). Compara artista + título sem acento e sem sufixos."""
    albuns, musicas = ouvidos.get("albuns", {}), ouvidos.get("musicas", {})
    n = 0
    for r in lanc:
        artistas = {norm(r.get("artista_lfm", "")), norm(r.get("artista", ""))}
        titulo = norm_titulo(r["titulo"])
        fontes = (musicas, albuns) if r["tipo"] == "single" else (albuns,)
        plays = max((f.get(f"{a}|{titulo}", 0) for f in fontes for a in artistas), default=0)
        r["ouvido"] = plays
        n += bool(plays)
    print(f"✓ {n} lançamentos você já ouviu (marcados na página)")
    return lanc


# ----------------------------------------------------------------------------
# Spotify (client credentials: só lê o catálogo público, nunca acessa sua conta)
# ----------------------------------------------------------------------------
_sp_token = {"valor": None, "expira": 0}
_sp_lock = threading.Lock()
_sp_pausa_ate = [0.0]
_sp_ritmo_lock = threading.Lock()
_sp_ultimo = [0.0]


class SpotifyBloqueado(Exception):
    """O Spotify pediu uma pausa longa demais pra valer a pena esperar."""


class OrcamentoEsgotado(Exception):
    """Já usamos o orçamento de pedidos ao Spotify de hoje."""


def sp_uso_hoje():
    uso = ler_json("spotify_uso.json", {})
    return uso.get("pedidos", 0) if uso.get("dia") == str(date.today()) else 0


def sp_contar_pedido():
    with _sp_ritmo_lock:
        n = sp_uso_hoje() + 1
        salvar_json("spotify_uso.json", {"dia": str(date.today()), "pedidos": n})
        return n


def sp_bloqueado_ate():
    return ler_json("spotify_bloqueio.json", {}).get("ate", 0)


def sp_bloquear(segundos):
    ate = time.time() + segundos
    salvar_json("spotify_bloqueio.json", {"ate": ate})
    return ate


def sp_token():
    with _sp_lock:
        if _sp_token["valor"] and time.time() < _sp_token["expira"] - 60:
            return _sp_token["valor"]
        r = requests.post("https://accounts.spotify.com/api/token",
                          data={"grant_type": "client_credentials"},
                          auth=(SP_ID, SP_SECRET), timeout=20)
        if r.status_code != 200:
            sys.exit(f"✗ Spotify recusou as chaves ({r.status_code}). Confira CLIENT_ID e SECRET.")
        j = r.json()
        _sp_token.update(valor=j["access_token"], expira=time.time() + j.get("expires_in", 3600))
        return _sp_token["valor"]


def spotify(caminho, **params):
    url = caminho if caminho.startswith("http") else "https://api.spotify.com/v1/" + caminho
    for tentativa in range(6):
        if time.time() < sp_bloqueado_ate():
            raise SpotifyBloqueado()
        if sp_uso_hoje() >= ORCAMENTO_SPOTIFY_DIA:
            raise OrcamentoEsgotado()
        pausa = _sp_pausa_ate[0] - time.time()
        if pausa > 0:
            time.sleep(pausa)
        with _sp_ritmo_lock:
            espera = random.uniform(*SPOTIFY_INTERVALO) - (time.time() - _sp_ultimo[0])
            if espera > 0:
                time.sleep(espera)
            _sp_ultimo[0] = time.time()
        token = sp_token()
        sp_contar_pedido()
        try:
            r = requests.get(url, params=params or None, timeout=20,
                             headers={"Authorization": f"Bearer {token}",
                                      "User-Agent": USER_AGENT})
        except requests.RequestException:
            time.sleep(2 * (tentativa + 1))
            continue
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429:
            espera = int(r.headers.get("Retry-After", "5") or 5) + 1
            try:
                motivo = r.json().get("error", {}).get("reason", "")
            except ValueError:
                motivo = ""
            if motivo == "QUOTA_EXCEEDED" or espera > PAUSA_MAXIMA:
                # cota do modo dev estourada: não insistir (pode alongar o bloqueio)
                sp_bloquear(max(espera, 3600))
                raise SpotifyBloqueado()
            _sp_pausa_ate[0] = max(_sp_pausa_ate[0], time.time() + espera)
            if espera > 30:
                print(f"\n   (Spotify pediu pausa de {espera}s — aguardando…)")
            continue
        if r.status_code == 401:
            _sp_token["valor"] = None
            continue
        if r.status_code in (400, 404):
            return None
        time.sleep(2 * (tentativa + 1))
    return None


def achar_artista_spotify(nome):
    alvo = norm(nome)
    if not alvo:
        return None
    j = spotify("search", q=nome, type="artist", limit=10, market="BR")
    if not j:
        return None
    for a in j.get("artists", {}).get("items", []):
        if norm(a.get("name", "")) == alvo:
            return {"id": a["id"], "nome": a["name"],
                    "url": a.get("external_urls", {}).get("spotify", ""),
                    "generos": a.get("genres", [])[:3]}
    return None


def lancamentos_do_artista(sp_id, corte: date):
    achados = []
    for grupo in ("album", "single"):
        url, paginas = f"artists/{sp_id}/albums", 0
        params = {"include_groups": grupo, "limit": 10, "market": "BR"}
        while url and paginas < 3:
            j = spotify(url, **params) if paginas == 0 else spotify(url)
            if not j:
                break
            itens = j.get("items", [])
            algum_recente = False
            for al in itens:
                d = data_lancamento(al.get("release_date", ""), al.get("release_date_precision", "year"))
                if d >= corte:
                    algum_recente = True
                    tipo = al.get("album_type", grupo)
                    faixas = al.get("total_tracks", 0)
                    if tipo == "single" and faixas >= 4:
                        tipo = "ep"
                    achados.append({
                        "titulo": al.get("name", ""),
                        "tipo": tipo,
                        "faixas": faixas,
                        "data": d.isoformat(),
                        "url": al.get("external_urls", {}).get("spotify", ""),
                        # imagens vêm da maior pra menor; a do meio (~300px) fica nítida no card
                        "capa": (al.get("images") or [{}])[min(1, len(al.get("images") or [{}]) - 1)].get("url", ""),
                    })
            if not algum_recente:
                break
            url, paginas = j.get("next"), paginas + 1
    return achados


# ----------------------------------------------------------------------------
# Deezer (catálogo público, sem chave e sem cota diária; uso pessoal e não comercial)
# ----------------------------------------------------------------------------
DEEZER_INTERVALO = 0.15      # ~6-7 pedidos/s; o limite relatado é 50 pedidos a cada 5 s
_dz_lock = threading.Lock()
_dz_ultimo = [0.0]


def deezer(caminho, **params):
    url = "https://api.deezer.com/" + caminho
    for tentativa in range(6):
        with _dz_lock:
            espera = DEEZER_INTERVALO - (time.time() - _dz_ultimo[0])
            if espera > 0:
                time.sleep(espera)
            _dz_ultimo[0] = time.time()
        try:
            r = requests.get(url, params=params or None, timeout=20,
                             headers={"User-Agent": USER_AGENT})
            j = r.json()
        except (requests.RequestException, ValueError):
            time.sleep(2 * (tentativa + 1))
            continue
        erro = (j.get("error") or {}) if isinstance(j, dict) else {}
        if erro:
            if erro.get("code") == 4:          # "Quota limit exceeded": passou de 50 pedidos em 5 s
                time.sleep(6 + 2 * tentativa)
                continue
            if erro.get("code") == 800:        # "no data": artista/álbum inexistente
                return None
            time.sleep(2 * (tentativa + 1))
            continue
        if r.status_code == 200:
            return j
        time.sleep(2 * (tentativa + 1))
    return None


def achar_artista_deezer(nome):
    alvo = norm(nome)
    if not alvo:
        return None
    j = deezer("search/artist", q=nome, limit=10)
    for a in (j or {}).get("data", []):
        if norm(a.get("name", "")) == alvo:
            return {"id": a["id"], "nome": a["name"], "url": a.get("link", "")}
    return None


def lancamentos_deezer(dz_id, corte: date):
    j = deezer(f"artist/{dz_id}/albums", limit=100)
    achados = []
    for al in (j or {}).get("data", []):
        d = data_lancamento(al.get("release_date", ""), "day")
        if d < corte:
            continue
        tipo = {"compile": "compilation"}.get(al.get("record_type"), al.get("record_type") or "album")
        achados.append({"titulo": al.get("title", ""), "tipo": tipo, "faixas": 0,
                        "data": d.isoformat(), "url": al.get("link", ""),
                        "capa": al.get("cover_big") or al.get("cover_medium") or ""})
    return achados


# ----------------------------------------------------------------------------
# Conferência de lançamentos (Deezer por padrão; Spotify opcional)
# ----------------------------------------------------------------------------
FONTE_LANCAMENTOS = (os.environ.get("FONTE_LANCAMENTOS", "deezer") or "deezer").strip().lower()
FONTES = {
    # Deezer: os termos pedem pra não manter cópia local do catálogo, então só o ID do
    # artista fica guardado por mais tempo; a lista de lançamentos é refeita todo dia.
    "deezer": {"nome": "Deezer", "cache": "deezer_artistas.json", "validade": 1,
               "achar": lambda n: achar_artista_deezer(n), "lancamentos": lambda i, c: lancamentos_deezer(i, c)},
    "spotify": {"nome": "Spotify", "cache": "spotify_artistas.json", "validade": VALIDADE_CACHE_DIAS,
                "achar": lambda n: achar_artista_spotify(n), "lancamentos": lambda i, c: lancamentos_do_artista(i, c)},
}


def checar_lancamentos(biblioteca, fonte=None):
    fonte = fonte or FONTE_LANCAMENTOS
    if fonte not in FONTES:
        sys.exit(f"✗ FONTE_LANCAMENTOS='{fonte}' não existe. Use: {', '.join(FONTES)}.")
    F = FONTES[fonte]
    corte = date.today() - timedelta(days=DIAS_LANCAMENTO)
    cache = ler_json(F["cache"], {})
    hoje = str(date.today())
    validade = str(date.today() - timedelta(days=F["validade"]))
    validade_id = str(date.today() - timedelta(days=VALIDADE_ID_DIAS))
    # mais ouvidos primeiro: se a rodada parar no meio, o que importa já foi checado
    pendentes = sorted((a for a in biblioteca
                        if cache.get(a["nome"], {}).get("checado", "") <= validade),
                       key=lambda a: a["plays"], reverse=True)
    print(f"→ Conferindo lançamentos no {F['nome']}: {len(pendentes)} artistas a checar "
          f"({len(biblioteca) - len(pendentes)} já checados recentemente)")

    if fonte == "spotify":
        bloqueio = sp_bloqueado_ate()
        restante = ORCAMENTO_SPOTIFY_DIA - sp_uso_hoje()
        if pendentes and time.time() < bloqueio:
            quando = datetime.fromtimestamp(bloqueio).strftime("%d/%m às %H:%M")
            print(f"   ⚠ Spotify está bloqueando consultas até {quando}. "
                  "Pulando esta etapa — rode de novo depois disso.")
            pendentes = []
        elif pendentes and restante <= 0:
            print(f"   ⚠ Orçamento de hoje ({ORCAMENTO_SPOTIFY_DIA} pedidos) já usado. "
                  "Pulando esta etapa — rode de novo amanhã.")
            pendentes = []
        elif pendentes:
            print(f"   Orçamento de hoje: {restante} pedidos. O progresso é salvo; "
                  "o que faltar continua na próxima rodada.")
    elif pendentes:
        minutos = max(1, round(len(pendentes) * 0.5 / 60))
        print(f"   Uns {minutos} min. Pode deixar rodando — o progresso é salvo.")

    def checar(a):
        anterior = cache.get(a["nome"], {})
        # reaproveita o ID (ou o "não achado") se foi buscado há pouco tempo
        if "artista" in anterior and anterior.get("id_checado", "") > validade_id:
            info, id_checado = anterior["artista"], anterior["id_checado"]
        else:
            info, id_checado = F["achar"](a["nome"]), hoje
        rel = F["lancamentos"](info["id"], corte) if info else []
        return a["nome"], {"checado": hoje, "id_checado": id_checado, "artista": info, "lancamentos": rel}

    feitos, motivo_parada = 0, None

    def registrar(nome, dado):
        nonlocal feitos
        cache[nome] = dado
        feitos += 1
        if feitos % 25 == 0:
            salvar_json(F["cache"], cache)
        barra(feitos, len(pendentes), "   artistas")

    if fonte == "deezer":
        # 3 em paralelo; o ritmo global continua limitado por DEEZER_INTERVALO
        with ThreadPoolExecutor(max_workers=3) as ex:
            for f in as_completed([ex.submit(checar, a) for a in pendentes]):
                try:
                    registrar(*f.result())
                except Exception:
                    pass
    else:
        # Spotify: um por vez, parando no bloqueio ou no fim do orçamento do dia
        for a in pendentes:
            try:
                registrar(*checar(a))
            except SpotifyBloqueado:
                motivo_parada = "bloqueio"
                break
            except OrcamentoEsgotado:
                motivo_parada = "orcamento"
                break
    salvar_json(F["cache"], cache)
    faltam = len(pendentes) - feitos
    if motivo_parada == "bloqueio":
        quando = datetime.fromtimestamp(sp_bloqueado_ate()).strftime("%d/%m às %H:%M")
        print(f"\n   ⚠ Spotify pediu uma pausa longa (até {quando}). {feitos} artistas "
              f"checados e salvos, {faltam} ficam pra próxima rodada.")
    elif motivo_parada == "orcamento":
        print(f"\n   ⏸ Orçamento de hoje usado. {feitos} artistas checados e salvos, "
              f"{faltam} ficam pra amanhã.")

    plays = {a["nome"]: a["plays"] for a in biblioteca}
    rank = {a["nome"]: i + 1 for i, a in enumerate(biblioteca)}
    limite_futuro = (date.today() + timedelta(days=DIAS_EM_BREVE)).isoformat()
    resultado, vistos = [], set()
    for nome, dado in cache.items():
        info = dado.get("artista") or dado.get("spotify")   # "spotify" = cache de versões antigas
        if nome not in plays or not info:
            continue
        for r in dado.get("lancamentos", []):
            if r["data"] < corte.isoformat():
                continue
            if r["data"] > limite_futuro:   # data muito adiante costuma ser erro do catálogo
                continue
            chave = (nome, norm_titulo(r["titulo"]))   # "Disco" e "Disco (Deluxe)" contam como um
            if chave in vistos:
                continue
            vistos.add(chave)
            resultado.append({**r, "artista": info["nome"], "artista_lfm": nome,
                              "artista_url": info.get("url", ""), "fonte": fonte,
                              "plays": plays[nome], "rank": rank[nome]})
    # se o mesmo título saiu como single e depois dentro do álbum, mantém o maior
    ordem_tipo = {"album": 3, "ep": 2, "single": 1, "compilation": 0}
    melhor = {}
    for r in resultado:
        k = (norm(r["artista"]), norm_titulo(r["titulo"]))
        if k not in melhor or ordem_tipo.get(r["tipo"], 0) > ordem_tipo.get(melhor[k]["tipo"], 0):
            melhor[k] = r
    resultado = sorted(melhor.values(), key=lambda r: r["data"], reverse=True)
    sem_match = sum(1 for n in plays if cache.get(n, {}).get("checado")
                    and not (cache[n].get("artista") or cache[n].get("spotify")))
    print(f"✓ {len(resultado)} lançamentos encontrados "
          f"({sem_match} artistas não achados no {F['nome']} com nome exato)")
    return resultado


# ----------------------------------------------------------------------------
# Descobertas (Last.fm similar, filtrando todo o seu histórico)
# ----------------------------------------------------------------------------
TAGS_LIXO = {"seen live", "favorites", "favourite", "favorite", "my favorite",
             "awesome", "love", "beautiful", "cool", "amazing", "best", "under 2000 listeners",
             "albums i own", "spotify", "check out", "fip"}


PESO_CURTI = 2.0       # um artista que você curtiu vale como semente de ~100 plays
PESO_NAO_CURTI = -1.5  # parecidos com quem você não curtiu perdem pontos


def pastas_gostos():
    """Onde procurar arquivos de gostos: a pasta do projeto, Downloads e as pastas
    em GOSTOS_PASTA no .env (separe várias com ';'), ex.: uma pasta do Google Drive
    ou OneDrive que todos os seus aparelhos enxergam."""
    pastas = [PASTA_GOSTOS, BASE, Path.home() / "Downloads"]
    for p in os.environ.get("GOSTOS_PASTA", "").split(";"):
        if p.strip():
            pastas.append(Path(os.path.expandvars(os.path.expanduser(p.strip()))))
    vistas, saida = set(), []
    for p in pastas:
        try:
            r = p.resolve()
        except OSError:
            continue
        if r not in vistas and r.is_dir():
            vistas.add(r)
            saida.append(r)
    return saida


def carregar_gostos():
    """Junta TODOS os arquivos exportados pelo botão 'Salvar meus gostos' (de qualquer
    aparelho). Cada marcação tem data; quando há conflito, vale a mais recente.
    Devolve {"descobertas": {nome: {"v":..., "t":...}}, "lancamentos": {...}}."""
    registro = {"descobertas": {}, "lancamentos": {}}
    arquivos = [a for p in pastas_gostos() for a in p.glob("radar_gostos*.json")]
    for arq in sorted(arquivos, key=lambda a: a.stat().st_mtime):
        try:
            g = json.loads(arq.read_text(encoding="utf-8"))
        except Exception:
            print(f"⚠ Não consegui ler {arq}; ignorando.")
            continue
        # arquivos antigos guardavam só o valor; usam a data do arquivo como referência
        t_arquivo = int(arq.stat().st_mtime * 1000)
        for tipo in registro:
            for nome, x in (g.get(tipo) or {}).items():
                e = ({"v": x.get("v"), "t": int(x.get("t") or 0)} if isinstance(x, dict)
                     else {"v": x or None, "t": t_arquivo})
                atual = registro[tipo].get(nome)
                if not atual or e["t"] >= atual["t"]:
                    registro[tipo][nome] = e
    if arquivos:
        d = [e["v"] for e in registro["descobertas"].values()]
        print(f"✓ Gostos juntados de {len(arquivos)} arquivo(s): {d.count('curti')} curtidos, "
              f"{d.count('nao')} não curtidos, {d.count('conheco')} já conhecidos")
    return registro


def valores_gostos(registro, tipo):
    """{nome: "curti"|"nao"|"conheco"} só com o que está marcado agora."""
    return {n: e["v"] for n, e in registro.get(tipo, {}).items() if e.get("v")}


# ----------------------------------------------------------------------------
# Histórico exportado dos apps (pra saber quem você já ouviu fora do Last.fm)
# ----------------------------------------------------------------------------
MIN_MS_HISTORICO = 30_000   # reprodução com menos de 30 s não conta como "já ouvi"


def pastas_historico():
    pastas = [PASTA_HISTORICO]
    for p in os.environ.get("HISTORICO_PASTA", "").split(";"):
        if p.strip():
            pastas.append(Path(os.path.expandvars(os.path.expanduser(p.strip()))))
    return [p for p in pastas if p.is_dir()]


def _artistas_do_arquivo(nome_arq, conteudo):
    """Reconhece o formato pelo nome/estrutura e devolve (app, [nomes de artista]).
    Formatos: Spotify (histórico estendido, dados da conta, biblioteca),
    YouTube Music (Google Takeout) e CSV com coluna de artista (ex.: Apple Music)."""
    base = Path(nome_arq).name.lower()
    if base.endswith(".csv"):
        import csv, io
        texto = conteudo.decode("utf-8-sig", errors="replace")
        leitor = csv.DictReader(io.StringIO(texto))
        col = next((c for c in (leitor.fieldnames or [])
                    if c and c.strip().lower() in ("artist name", "artist", "artistname", "artista", "nome do artista")), None)
        if not col:
            return None, []
        dur = next((c for c in leitor.fieldnames if "duration" in c.lower() and "milli" in c.lower()), None)
        nomes = []
        for linha in leitor:
            if dur and (linha.get(dur) or "").isdigit() and int(linha[dur]) < MIN_MS_HISTORICO:
                continue
            nomes.append(linha.get(col, ""))
        return "csv", nomes
    if not base.endswith(".json"):
        return None, []
    try:
        dados = json.loads(conteudo.decode("utf-8-sig", errors="replace"))
    except ValueError:
        return None, []
    if base.startswith("streaming_history_audio") and isinstance(dados, list):
        return "spotify", [d.get("master_metadata_album_artist_name") for d in dados
                           if (d.get("ms_played") or 0) >= MIN_MS_HISTORICO]
    if base.startswith("streaminghistory") and isinstance(dados, list):
        return "spotify", [d.get("artistName") for d in dados if (d.get("msPlayed") or 0) >= MIN_MS_HISTORICO]
    if base == "yourlibrary.json" and isinstance(dados, dict):
        return "spotify", ([t.get("artist") for t in dados.get("tracks", [])] +
                           [a.get("name") for a in dados.get("artists", []) if isinstance(a, dict)])
    if base.startswith("watch-history") and isinstance(dados, list):
        nomes = []
        for d in dados:
            if d.get("header") == "YouTube Music" and d.get("subtitles"):
                nomes.append(re.sub(r"\s+-\s+Topic$", "", d["subtitles"][0].get("name", "")))
        return "youtube music", nomes
    return None, []


def carregar_historico():
    """Lê tudo em historico/ (e HISTORICO_PASTA), inclusive dentro de .zip.
    Devolve {nome_normalizado: nome} de todo artista que você já ouviu."""
    import zipfile
    artistas, por_app = {}, {}

    def absorver(nome_arq, ler):
        try:
            app, nomes = _artistas_do_arquivo(nome_arq, ler())
        except Exception:
            return
        if not app:
            return
        for n in nomes:
            k = norm(n or "")
            if k:
                artistas.setdefault(k, n)
                por_app.setdefault(app, set()).add(k)

    for pasta in pastas_historico():
        for arq in pasta.rglob("*"):
            if arq.suffix.lower() == ".zip":
                try:
                    with zipfile.ZipFile(arq) as z:
                        for info in z.infolist():
                            if not info.is_dir():
                                absorver(info.filename, lambda i=info: z.read(i))
                except zipfile.BadZipFile:
                    print(f"⚠ {arq.name} não é um zip válido; ignorando.")
            elif arq.is_file():
                absorver(arq.name, arq.read_bytes)
    if artistas:
        resumo = ", ".join(f"{app}: {len(s)}" for app, s in sorted(por_app.items()))
        print(f"✓ Histórico exportado: {len(artistas)} artistas ({resumo})")
    return artistas


_SEPARA_COLAB = re.compile(
    r"\s*(?:,|&|\+|/|\bfeat\.?|\bft\.?|\bfeaturing\b|\bwith\b|\bvs\.?|\bx\b|\be\b|\band\b|\bcom\b)\s*",
    re.IGNORECASE)


def e_colaboracao_conhecida(nome, conhecidos):
    """True se o nome junta 2+ artistas (feat, &, x, vírgula…) e você já conhece TODOS.
    Ex.: 'JAY-Z & Kanye West' sai; 'Mumford & Sons' fica (você não ouve 'Sons')."""
    partes = [norm(p) for p in _SEPARA_COLAB.split(nome or "")]
    partes = [p for p in partes if p]
    return len(partes) >= 2 and all(p in conhecidos for p in partes)


def descobrir(biblioteca, gostos, historico=None):
    conhecidos = {norm(a["nome"]) for a in biblioteca}
    if historico:
        fora_do_lastfm = set(historico) - conhecidos
        if fora_do_lastfm:
            print(f"   (+{len(fora_do_lastfm)} artistas que você ouviu fora do Last.fm não serão recomendados)")
        conhecidos |= set(historico)
    marcados = valores_gostos(gostos, "descobertas")
    # "não curti" e "já conheço" nunca mais aparecem como descoberta
    escondidos = {norm(n) for n, v in marcados.items() if v in ("nao", "conheco")}
    curtidos = [n for n, v in marcados.items() if v == "curti"]
    nao_curtidos = [n for n, v in marcados.items() if v == "nao"]
    sementes = biblioteca[:SEMENTES_DESCOBERTA]
    cache = ler_json("similares.json", {})
    extras = [{"nome": n} for n in curtidos + nao_curtidos]
    pend = [s for s in sementes + extras if s["nome"] not in cache]
    print(f"→ Buscando artistas semelhantes a partir dos seus {len(sementes)} mais ouvidos"
          + (f" e {len(extras)} que você avaliou" if extras else "") + "…")
    for i, s in enumerate(pend, 1):
        j = lastfm("artist.getsimilar", artist=s["nome"], limit=SIMILARES_POR_SEMENTE, autocorrect=1)
        lista = []
        if j:
            for a in j.get("similarartists", {}).get("artist", []):
                try:
                    lista.append([a["name"], float(a.get("match", 0))])
                except (KeyError, ValueError):
                    pass
        cache[s["nome"]] = lista
        if i % 25 == 0:
            salvar_json("similares.json", cache)
        barra(i, len(pend), "   sementes")
    salvar_json("similares.json", cache)

    pontos, motivos, nomes = {}, {}, {}
    fontes = [(s["nome"], math.log10(1 + s["plays"])) for s in sementes]
    fontes += [(n, PESO_CURTI) for n in curtidos] + [(n, PESO_NAO_CURTI) for n in nao_curtidos]
    for semente, peso in fontes:
        for nome, match in cache.get(semente, []):
            n = norm(nome)
            if not n or n in conhecidos or n in escondidos:
                continue
            if e_colaboracao_conhecida(nome, conhecidos | escondidos):
                continue
            pontos[n] = pontos.get(n, 0) + match * peso
            nomes.setdefault(n, nome)
            if peso > 0:
                motivos.setdefault(n, []).append((match * peso, semente))
    # quem você curtiu continua na lista (marcado), mesmo fora do top
    for nome in curtidos:
        n = norm(nome)
        if n not in conhecidos:
            nomes.setdefault(n, nome)
            pontos.setdefault(n, 0)
    candidatos = [n for n in pontos if motivos.get(n) or n in {norm(c) for c in curtidos}]
    melhores = sorted(candidatos, key=pontos.get, reverse=True)[:MAX_DESCOBERTAS]
    ja = set(melhores)
    melhores += [norm(c) for c in curtidos if norm(c) in pontos and norm(c) not in ja]
    print(f"→ Detalhando as {len(melhores)} melhores descobertas…")
    info_cache = ler_json("info_artistas.json", {})
    saida = []
    for i, n in enumerate(melhores, 1):
        nome = nomes[n]
        if nome not in info_cache:
            j = lastfm("artist.getinfo", artist=nome, autocorrect=1, lang="pt")
            info = {"ouvintes": 0, "tags": []}
            if j and "artist" in j:
                art = j["artist"]
                info["ouvintes"] = int(art.get("stats", {}).get("listeners", 0) or 0)
                tags = [t["name"].lower() for t in art.get("tags", {}).get("tag", [])]
                info["tags"] = [t for t in tags if t not in TAGS_LIXO and norm(t) != n][:3]
            info_cache[nome] = info
            if i % 25 == 0:
                salvar_json("info_artistas.json", info_cache)
        info = info_cache[nome]
        porque = [m[1] for m in sorted(motivos.get(n, []), reverse=True)[:3]]
        saida.append({
            "nome": nome,
            "pontos": round(pontos[n], 2),
            "sementes": len(motivos.get(n, [])),
            "porque": porque,
            "tags": info["tags"],
            "ouvintes": info["ouvintes"],
            "lastfm": f"https://www.last.fm/music/{quote(nome.replace(' ', '+'), safe='+')}",
        })
        barra(i, len(melhores), "   detalhes")
    salvar_json("info_artistas.json", info_cache)
    print(f"✓ {len(saida)} artistas novos pra você descobrir")
    return saida


def generos_lancamentos(lanc):
    """Põe gêneros (tags do Last.fm) nos lançamentos. Só consulta artistas que
    lançaram algo e guarda no cache, então custa pouco."""
    cache = ler_json("tags_artistas.json", {})
    nomes = sorted({r["artista_lfm"] for r in lanc} - set(cache))
    if nomes:
        print(f"→ Buscando gêneros de {len(nomes)} artistas com lançamentos…")
    for i, nome in enumerate(nomes, 1):
        j = lastfm("artist.gettoptags", artist=nome, autocorrect=1)
        tags = [t.get("name", "").lower() for t in (j or {}).get("toptags", {}).get("tag", [])]
        cache[nome] = [t for t in tags if t and t not in TAGS_LIXO and norm(t) != norm(nome)][:3]
        if i % 25 == 0:
            salvar_json("tags_artistas.json", cache)
        barra(i, len(nomes), "   gêneros")
    salvar_json("tags_artistas.json", cache)
    for r in lanc:
        r["tags"] = cache.get(r["artista_lfm"], [])
    # compositores clássicos: o catálogo lista gravações de outros músicos como se fossem deles
    antes = len(lanc)
    lanc = [r for r in lanc if not (set(r["tags"]) & TAGS_SEM_LANCAMENTO)]
    if antes - len(lanc):
        print(f"   ({antes - len(lanc)} lançamentos de compositores clássicos deixados de fora)")
    return lanc


# ----------------------------------------------------------------------------
# Saída
# ----------------------------------------------------------------------------
APP_MUSICA = (os.environ.get("APP_MUSICA", "spotify") or "spotify").strip().lower()
SITE = SAIDA / "site"   # versão instalável (index.html + ícones), pra publicar em https


def _png(tamanho):
    """Ícone do radar (anéis laranja num fundo escuro) como PNG, sem bibliotecas extras."""
    import struct, zlib
    fundo, laranja = (19, 16, 14), (255, 122, 69)
    c, linhas = (tamanho - 1) / 2, []
    for y in range(tamanho):
        linha = bytearray([0])
        for x in range(tamanho):
            dx, dy = (x - c) / c, (y - c) / c
            r = math.hypot(dx, dy)
            ang = (math.degrees(math.atan2(dy, dx)) + 360) % 360
            a = 0.0
            if r < 0.78:
                if abs(r - 0.76) < 0.022 or abs(r - 0.52) < 0.018 or abs(r - 0.28) < 0.018:
                    a = 0.9          # anéis
                elif ang > 270 or ang < 0.5:
                    a = 0.55 * (1 - ((ang - 270) % 360) / 90)   # varredura do radar
                if r < 0.07:
                    a = 1.0          # centro
            linha += bytes(round(f + (l - f) * a) for f, l in zip(fundo, laranja))
        linhas.append(bytes(linha))
    def bloco(tipo, dados):
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + bloco(b"IHDR", struct.pack(">IIBBBBB", tamanho, tamanho, 8, 2, 0, 0, 0))
            + bloco(b"IDAT", zlib.compress(b"".join(linhas), 9)) + bloco(b"IEND", b""))


SW_JS = """// Guarda a última versão do radar pra abrir mesmo sem internet.
const CACHE = "radar-v1";
self.addEventListener("install", e => { self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(self.clients.claim()); });
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;
  // rede primeiro (pra pegar o radar novo); sem rede, usa a cópia guardada
  e.respondWith(fetch(e.request).then(r => {
    const copia = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copia)); return r;
  }).catch(() => caches.match(e.request, {ignoreSearch: true})));
});
"""


def gerar_html(lanc, desc, total_artistas, gostos):
    modelo = (BASE / "modelo.html").read_text(encoding="utf-8")
    dados = {"gerado": datetime.now().strftime("%d/%m/%Y %H:%M"), "usuario": LASTFM_USER,
             "total": total_artistas, "dias": DIAS_LANCAMENTO, "app": APP_MUSICA,
             "fonte": FONTE_LANCAMENTOS, "lancamentos": lanc, "descobertas": desc, "gostos": gostos}
    js = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    html = modelo.replace("/*__DADOS__*/null", js)
    saida = SAIDA / "radar.html"
    saida.write_text(html, encoding="utf-8")

    # versão instalável: mesma página + manifest, ícones e service worker
    SITE.mkdir(exist_ok=True)
    (SITE / "index.html").write_text(html, encoding="utf-8")
    (SITE / "manifest.webmanifest").write_text(json.dumps({
        "name": "Radar Musical", "short_name": "Radar", "start_url": "./", "scope": "./",
        "display": "standalone", "background_color": "#13100e", "theme_color": "#13100e",
        "icons": [{"src": f"icone-{t}.png", "sizes": f"{t}x{t}", "type": "image/png", "purpose": "any"}
                  for t in (192, 512)]}, ensure_ascii=False, indent=2), encoding="utf-8")
    (SITE / "sw.js").write_text(SW_JS, encoding="utf-8")
    for t in (180, 192, 512):
        icone = SITE / f"icone-{t}.png"
        if not icone.exists():
            icone.write_bytes(_png(t))
    return saida


# ----------------------------------------------------------------------------
# Publicação no GitHub Pages (opcional): vira um endereço https que dá pra
# instalar no celular. Configure GITHUB_TOKEN e GITHUB_REPO no .env.
# ----------------------------------------------------------------------------
def publicar_github():
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    repo = os.environ.get("GITHUB_REPO", "").strip().strip("/")
    ramo = os.environ.get("GITHUB_BRANCH", "main").strip() or "main"
    if not (token and repo):
        return None
    import base64
    api = f"https://api.github.com/repos/{repo}"
    h = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
         "X-GitHub-Api-Version": "2022-11-28", "User-Agent": USER_AGENT}
    print(f"→ Publicando no GitHub Pages ({repo})…")
    r = requests.get(api, headers=h, timeout=20)
    if r.status_code != 200:
        print(f"   ✗ Não achei o repositório {repo} ({r.status_code}). Crie ele no GitHub (público) "
              "e confira se o token tem acesso a ele. Veja o README.")
        return None
    if r.json().get("private"):
        print("   ⚠ O repositório é privado: no plano grátis o GitHub Pages só funciona com repositório público.")
    for arq in sorted(SITE.iterdir()):
        caminho = arq.name
        atual = requests.get(f"{api}/contents/{caminho}", params={"ref": ramo}, headers=h, timeout=30)
        corpo = {"message": f"Atualiza {caminho}", "branch": ramo,
                 "content": base64.b64encode(arq.read_bytes()).decode()}
        if atual.status_code == 200:
            sha = atual.json().get("sha")
            if caminho.startswith("icone-") or caminho == "sw.js":
                continue   # não muda entre rodadas: não precisa reenviar
            corpo["sha"] = sha
        r = requests.put(f"{api}/contents/{caminho}", json=corpo, headers=h, timeout=60)
        if r.status_code not in (200, 201):
            print(f"   ✗ Falhou ao enviar {caminho} ({r.status_code}): {r.json().get('message', '')}")
            return None
    pages = requests.get(f"{api}/pages", headers=h, timeout=20)
    if pages.status_code == 404:
        r = requests.post(f"{api}/pages", json={"source": {"branch": ramo, "path": "/"}}, headers=h, timeout=20)
        if r.status_code not in (201, 409):
            print(f"   ⚠ Arquivos enviados, mas não consegui ativar o GitHub Pages ({r.status_code}). "
                  "Ative em Settings → Pages do repositório.")
        pages = requests.get(f"{api}/pages", headers=h, timeout=20)
    url = (pages.json().get("html_url") if pages.status_code == 200 else None) or \
          f"https://{repo.split('/')[0]}.github.io/{repo.split('/')[1]}/"
    print(f"✓ Publicado: {url}  (a primeira vez pode levar 1-2 min pra aparecer)")
    return url


def main():
    exigidas = [("LASTFM_USER", LASTFM_USER), ("LASTFM_API_KEY", LASTFM_KEY)]
    if FONTE_LANCAMENTOS == "spotify":   # o Deezer não precisa de chave
        exigidas += [("SPOTIFY_CLIENT_ID", SP_ID), ("SPOTIFY_CLIENT_SECRET", SP_SECRET)]
    faltando = [n for n, v in exigidas if not v]
    if faltando:
        sys.exit("✗ Faltam chaves no arquivo .env: " + ", ".join(faltando) +
                 "\n  Copie .env.exemplo para .env e preencha (veja o README.md).")
    inicio = time.time()
    biblioteca = baixar_biblioteca()
    gostos = carregar_gostos()
    historico = carregar_historico()
    desc = descobrir(biblioteca, gostos, historico)
    lanc = generos_lancamentos(checar_lancamentos(biblioteca))
    lanc = marcar_ouvidos(lanc, baixar_ouvidos())
    saida = gerar_html(lanc, desc, len(biblioteca), gostos)
    url = publicar_github()
    print(f"\n🎧 Pronto em {int((time.time() - inicio) / 60)} min → {saida}")
    if url:
        print(f"   No celular, abra {url} e toque em Instalar (ou Compartilhar → Adicionar à Tela de Início).")
    try:
        webbrowser.open(saida.as_uri())
    except Exception:
        pass


if __name__ == "__main__":
    main()
