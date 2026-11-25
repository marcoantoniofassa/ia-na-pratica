"""PDF Falado: leitura integral de documento em audio natural (Gemini TTS), conferida por Whisper.

Metodo e regras do roteiro: skills/pdf-falado/SKILL.md do repositorio ia-na-pratica.

Por que paragrafo a paragrafo: em trecho longo o TTS pula frase e sequencia de digitos, e o
whisper "perde" frase que esta no audio. Por isso o atestado do arquivo final recorta o mp3 nos
limites de cada paragrafo (janela fixa de 60 s corta frase no meio e gera falso "nao ouvido").

Precisa: python3, ffmpeg, whisper-cli (brew install whisper-cpp) e o modelo ggml-large-v3-turbo.bin
(https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin), apontado em
WHISPER_MODEL. Motor gemini (padrao): chave em GEMINI_API_KEY (gratis em aistudio.google.com/apikey).
Motor kokoro (local, gratis, Apple Silicon): brew install espeak-ng e rodar com
  uv run --python 3.11 --with mlx-audio --with "misaki[en]" --with phonemizer-fork --with espeakng-loader \
    python pdf-falado.py roteiro.txt saida --motor kokoro
Motor voxcpm2 (local, voz mais natural, Apache): mesmo "uv run --with mlx-audio ..." do kokoro, com
    --motor voxcpm2 --ref voz.wav   (wav de 3 a 10 s; texto falado nela em voz.txt, opcional)
  ou --instruct "voz feminina jovem, calma e clara, sotaque brasileiro" pra criar a voz por descricao
  (criada uma vez e travada como referencia, senao a voz muda de paragrafo pra paragrafo).

uso: python3 pdf-falado.py <roteiro.txt> <saida-sem-extensao> [--motor gemini|kokoro|voxcpm2] [--idioma pt-BR] [--voz ...] [--tempo ...] [--paralelo 4]
     python3 pdf-falado.py --check      autoteste do comparador (casos reais de 24/11)
Roteiro: paragrafos separados por linha em branco; '===' separa secoes (pausa maior).
Saida: <saida>.mp3, <saida>.ogg (opus, pra mandar como audio nativo do WhatsApp) e <saida>.json
(inicio e fim de cada paragrafo no arquivo final).
Chave gratuita tem limite por minuto e por dia: use --paralelo 1; em 429 o script espera e tenta de novo.
"""
import argparse, base64, difflib, io, json, os, re, subprocess, sys, threading, time, unicodedata, urllib.error, urllib.request, wave
from concurrent.futures import ThreadPoolExecutor

# US$ por 1M tokens de audio de saida ate 31/12/2026 (dobra em 2027): conferir na pagina de precos
PRECO = {"gemini-3.8-flash-tts": 9.00, "gemini-3.8-flash-lite-tts": 6.00}
# --idioma: (nome pro estilo da voz, idioma do whisper). Fora da lista, o whisper detecta sozinho.
IDIOMAS = {"pt-BR": ("Brazilian Portuguese", "pt"), "pt-PT": ("European Portuguese", "pt"),
           "en": ("English", "en"), "es": ("Spanish", "es"), "fr": ("French", "fr"), "it": ("Italian", "it"), "de": ("German", "de")}
ESTILO = ("calm, clear, professional narrator reading a document aloud in full in {nome}, steady natural pace; "
          "words from other languages, brand names and technical terms keep their native pronunciation")
STYLE, LANG_WHISPER = ESTILO.format(nome="Brazilian Portuguese"), "pt"  # trocados por --idioma no main
# Kokoro (local): idioma -> (lang_code, voz padrao). pf_dora e voz feminina em pt-BR.
KOKORO = {"pt-BR": ("p", "pm_alex"), "pt-PT": ("p", "pm_alex"), "en": ("a", "am_michael"),
          "es": ("e", "em_alex"), "fr": ("f", "ff_siwis"), "it": ("i", "im_nicola")}
KOKORO_MODELO, _kokoro, _kokoro_lock = "mlx-community/Kokoro-82M-bf16", None, threading.Lock()
VOXCPM_MODELO, _vox, _vox_lock = "mlx-community/VoxCPM2-8bit", None, threading.Lock()
REF_FRASE = "Oi, tudo bem? Acabei de terminar a análise e tenho uma notícia boa pra te dar. Deu certo, e foi mais rápido do que eu esperava."
WHISPER = os.environ.get("WHISPER_MODEL") or os.path.expanduser(
    "~/Library/Application Support/github.com.thewh1teagle.vibe/ggml-large-v3-turbo.bin")
PAUSA_PAR, PAUSA_SEC, TENTATIVAS = 0.6, 1.4, 3
# Cada whisper large-v3-turbo come ~1,5 GB: 12 simultaneos (3 copias do script x 4) travaram um Mac de 16 GB
# em 24/11/2026. Teto fixo por processo; nao rode varias copias do script ao mesmo tempo.
OUVIR = threading.Semaphore(int(os.environ.get("WHISPER_SIMULTANEOS", "2")))

UN = {"zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6,
      "sete": 7, "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12, "treze": 13, "quatorze": 14,
      "catorze": 14, "quinze": 15, "dezesseis": 16, "dezessete": 17, "dezoito": 18, "dezenove": 19,
      "vinte": 20, "trinta": 30, "quarenta": 40, "cinquenta": 50, "sessenta": 60, "setenta": 70,
      "oitenta": 80, "noventa": 90, "cem": 100, "cento": 100, "duzentos": 200, "duzentas": 200,
      "trezentos": 300, "trezentas": 300, "quatrocentos": 400, "quatrocentas": 400, "quinhentos": 500,
      "quinhentas": 500, "seiscentos": 600, "setecentos": 700, "oitocentos": 800, "novecentos": 900}
MULT = {"mil": 1000, "milhao": 10**6, "milhoes": 10**6, "bilhao": 10**9, "bilhoes": 10**9}


def toks(t):
    """Normaliza roteiro e transcricao pro mesmo alfabeto: numero por extenso e em digito viram o
    mesmo digito, sigla soletrada ("O.B.D.", "A, B, C") e colada ("OBD2", "ABC") viram a mesma."""
    t = re.sub(r"\[[a-z-]+\]", " ", t)  # [laughter], [sigh]: marca de som, nao palavra
    t = unicodedata.normalize("NFKD", t.lower().replace("%", " por cento "))
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"\b((?:[a-z]\.){2,})", lambda m: m.group(1).replace(".", "") + " ", t)  # "c.a.c." = "cac"
    t = re.sub(r"(?<=\d)\.(?=\d{3}\b)", "", t)  # 1.200.000 -> 1200000
    t = re.sub(r"(\d+),(\d+) ?(milhao|milhoes|bilhao|bilhoes|mil)\b",  # "1,2 milhao" -> 1200000
               lambda m: str(round(float(f"{m.group(1)}.{m.group(2)}") * MULT[m.group(3)])), t)
    t = re.sub(r"r\$ ?([\d.,]+(?: ?(?:milhao|milhoes|mil))?)", r"\1 reais", t)  # "r$ 150" = "150 reais"
    t = re.sub(r"(?<=[a-z])(?=\d)|(?<=\d)(?=[a-z])", " ", t)
    raw = [w for w in re.findall(r"\w+|[,.;:]", t) if w != "traco"]
    out, i = [], 0
    while i < len(raw):  # "dois mil e vinte e seis" -> 2026; "vinte e quatro e trinta" -> 24 e 30
        if raw[i] in UN or raw[i] in MULT:
            total, cur, last, j = 0, 0, None, i
            while j < len(raw):
                w = raw[j]
                if w in UN and (last is None or UN[w] < last):
                    cur, last, j = cur + UN[w], UN[w], j + 1
                elif w in MULT and (last is None or MULT[w] > (last or 0)):  # "um milhao e duzentos mil"
                    total, cur, last, j = total + (cur or 1) * MULT[w], 0, MULT[w], j + 1
                elif w == "e" and last and j + 1 < len(raw) and raw[j + 1] in UN and UN[raw[j + 1]] < last:
                    j += 1
                else:
                    break
            out.append(str(total + cur))
            i = j
        else:
            out.append(raw[i])
            i += 1
    out = [w for w in out if w not in ",.;:"]
    junta = []  # digitos e letras soltas em sequencia viram um token so: "3 8 4" = "384", "o b d" = "obd"
    for w in out:
        # "a", "e", "o" sao palavras: colar "e a garantia" escondia frase faltando (caso real)
        tipo = "d" if w.isdigit() else "l" if len(w) == 1 and w.isalpha() and w not in "aeo" else None
        if tipo and junta and junta[-1][0] == tipo:
            junta[-1] = (tipo, junta[-1][1] + w)
        else:
            junta.append((tipo, w))
    return [w for _, w in junta]


def atesta(texto, ouvido):
    """(ok, cobertura, trechos do roteiro com 3+ tokens seguidos que o whisper nao ouviu)."""
    want, got = toks(texto), toks(ouvido)
    sm = difflib.SequenceMatcher(None, want, got, autojunk=False)
    falta = [" ".join(want[a:b]) for op, a, b, c, d in sm.get_opcodes()
             if (op == "delete" and b - a >= 3) or (op == "replace" and (b - a) - (d - c) >= 3)]
    casou = sum(m.size for m in sm.get_matching_blocks())
    cob = casou / max(1, len(want))
    # paragrafo curto: 1 sigla divergente ("e in" x "ein") derrubava 5 tokens pra 60%
    return not falta and (cob >= 0.85 or len(want) - casou <= 2), cob, falta


def key():
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    if os.path.exists(".env"):
        for line in open(".env"):
            if line.startswith(("GEMINI_API_KEY=", "GOOGLE_API_KEY=")):
                return line.split("=", 1)[1].strip().strip('"')
    sys.exit("falta GEMINI_API_KEY (crie gratis em aistudio.google.com/apikey)")


def gen(texto, voz, k, destino, modelo):
    """Gera um paragrafo; devolve os tokens de audio cobrados (usageMetadata)."""
    body = {"contents": [{"parts": [{"text": texto, "speech_metadata": {"style": STYLE}}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voz}}}}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": k})
    for espera in (20, 40, 80, 160, 0):  # 429 (limite da chave gratis) e 5xx: espera e tenta de novo
        try:
            resp = json.load(urllib.request.urlopen(req, timeout=300))
            break
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 503) or not espera:
                raise
            time.sleep(espera)
    cand = resp["candidates"][0]
    if cand.get("finishReason") == "MAX_TOKENS":
        raise RuntimeError("paragrafo passou do limite de saida: quebrar em dois no roteiro")
    part = cand["content"]["parts"][0]["inlineData"]
    audio = base64.b64decode(part["data"])
    if audio[:4] == b"RIFF":
        with wave.open(io.BytesIO(audio)) as w:
            pcm, rate = w.readframes(w.getnframes()), w.getframerate()
    else:
        pcm, rate = audio, int((re.search(r"rate=(\d+)", part.get("mimeType", "")) or [0, 24000])[1])
    with wave.open(destino, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm)
    return resp.get("usageMetadata", {}).get("candidatesTokenCount", 0)


def gen_kokoro(texto, voz, destino, lang_code):
    """Motor local: Kokoro no Apple Silicon via mlx-audio. Uma geracao por vez (MLX nao e thread-safe)."""
    global _kokoro
    import numpy as np
    from mlx_audio.tts.utils import load_model
    # Kokoro corta texto longo sem aviso: uma frase por linha (split_pattern do mlx-audio e "\n+")
    frases = re.sub(r"(?<=[.!?;:])\s+", "\n", texto.strip())
    with _kokoro_lock:
        if _kokoro is None:
            _kokoro = load_model(KOKORO_MODELO)
        partes = [np.array(r.audio, dtype=np.float32) for r in _kokoro.generate(text=frases, voice=voz, speed=1.0, lang_code=lang_code)]
    pcm = (np.clip(np.concatenate(partes), -1, 1) * 32767).astype("<i2").tobytes()
    with wave.open(destino, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm)
    return 0


def _voxcpm(texto, **kw):
    """VoxCPM2 no Apple Silicon via mlx-audio; devolve (amostras float32, sample rate). Uma geracao por vez."""
    global _vox
    import numpy as np
    from mlx_audio.tts.utils import load_model
    with _vox_lock:
        if _vox is None:
            _vox = load_model(VOXCPM_MODELO)
        partes = [np.array(r.audio, dtype=np.float32) for r in _vox.generate(text=texto, **kw)]
        return np.concatenate(partes), getattr(_vox, "sample_rate", 48000)


def _grava(destino, amostras, sr):
    import numpy as np
    pcm = (np.clip(np.asarray(amostras, dtype=np.float32), -1, 1) * 32767).astype("<i2").tobytes()
    with wave.open(destino, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm)


def gen_voxcpm(texto, destino, ref, ref_texto):
    """Clona SEMPRE a mesma referencia, senao a voz muda de paragrafo pra paragrafo."""
    _grava(destino, *_voxcpm(texto, ref_audio=ref, ref_text=ref_texto or None))
    return 0


def cria_voz(instruct, destino):
    """Voz por descricao vira referencia travada (uma vez), usada pra clonar todos os paragrafos."""
    _grava(destino, *_voxcpm(REF_FRASE, instruct=instruct))
    return destino, REF_FRASE


def ff(*a):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *a], check=True)


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)


def ouvir(wav_in):
    wav = wav_in + ".16k.wav"
    ff("-i", wav_in, "-ar", "16000", "-ac", "1", wav)
    # -mc 0: sem contexto entre segmentos; com contexto o whisper.cpp pula frase inteira.
    # Sem -nt: sem marcacao de tempo ele pula texto na emenda das janelas de 30 s (paragrafo de 42 s, 25/11/2026).
    with OUVIR:
        o = subprocess.run(["whisper-cli", "-m", WHISPER, "-l", LANG_WHISPER, "-mc", "0", "-np", "-f", wav],
                           capture_output=True, text=True).stdout
    o = " ".join(re.sub(r"^\s*\[[^\]]*\]\s*", "", linha).strip() for linha in o.splitlines() if linha.strip())
    os.remove(wav)
    return o


def unidade(n, texto, voz, k, raw, modelo, motor="gemini", lang_code="p", ref=None):
    base, tokens = f"{raw}/u{n:03d}", 0
    melhor = None
    for t in range(TENTATIVAS):
        if motor == "kokoro":
            tokens += gen_kokoro(texto, voz, f"{base}.try.wav", lang_code)
        elif motor == "voxcpm2":
            tokens += gen_voxcpm(texto, f"{base}.try.wav", *ref)
        else:
            tokens += gen(texto, voz, k, f"{base}.try.wav", modelo)
        ok, cob, falta = atesta(texto, ouvir(f"{base}.try.wav"))
        if melhor is None or cob > melhor[1]:
            os.replace(f"{base}.try.wav", f"{base}.wav")
            melhor = (ok, cob, falta)
        if ok:
            break
    return n, melhor, t + 1, tokens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro"); ap.add_argument("saida")
    ap.add_argument("--motor", default="gemini", choices=["gemini", "kokoro", "voxcpm2"],
                    help="kokoro = local e rapido; voxcpm2 = local e mais natural (Apple Silicon)")
    ap.add_argument("--ref", help="voxcpm2: wav de 3 a 10 s da voz a clonar (texto dela em .txt de mesmo nome, opcional)")
    ap.add_argument("--instruct", help='voxcpm2 sem --ref: descricao da voz, ex. "voz feminina jovem, calma e clara"')
    ap.add_argument("--voz", help="padrao: Charon (gemini), pm_alex (kokoro pt-BR)")
    ap.add_argument("--tempo", type=float, help="padrao: 1.08 (gemini), 1.0 (kokoro)")
    ap.add_argument("--modelo", default="gemini-3.8-flash-tts", choices=list(PRECO))
    ap.add_argument("--idioma", default="pt-BR", help="pt-BR (padrao), pt-PT, en, es, fr, it, de ou outro (whisper detecta)")
    ap.add_argument("--paralelo", type=int, default=4, help="1 na chave gratuita")
    a = ap.parse_args()
    global STYLE, LANG_WHISPER
    nome, LANG_WHISPER = IDIOMAS.get(a.idioma, (a.idioma, "auto"))
    STYLE = ESTILO.format(nome=nome)
    lang_code = "p"
    if a.motor == "kokoro":
        if a.idioma not in KOKORO:
            sys.exit(f"kokoro nao fala {a.idioma}; idiomas: {', '.join(KOKORO)}")
        try:
            import mlx_audio  # noqa: F401
        except ImportError:
            sys.exit('motor kokoro precisa de mlx-audio: veja o "uv run --with mlx-audio ..." no topo do script')
        lang_code, voz_padrao = KOKORO[a.idioma]
        a.voz, a.tempo = a.voz or voz_padrao, a.tempo or 1.0
    ref = None
    if a.motor == "voxcpm2":
        try:
            import mlx_audio  # noqa: F401
        except ImportError:
            sys.exit('motor voxcpm2 precisa de mlx-audio: veja o "uv run --with mlx-audio ..." no topo do script')
        if a.ref:
            txt = os.path.splitext(a.ref)[0] + ".txt"
            ref = (a.ref, " ".join(open(txt).read().split()) if os.path.exists(txt) else None)
        elif a.instruct:
            os.makedirs(a.saida + "-raw", exist_ok=True)
            ref = cria_voz(a.instruct, a.saida + "-raw/voz-ref.wav")
        else:
            sys.exit('voxcpm2 precisa de --ref voz.wav ou --instruct "descricao da voz"')
        a.voz, a.tempo = a.voz or os.path.basename(ref[0]), a.tempo or 1.0
    a.voz, a.tempo = a.voz or "Charon", a.tempo or 1.08
    if not os.path.exists(WHISPER):
        sys.exit(f"modelo do whisper nao encontrado em {WHISPER}: baixe ggml-large-v3-turbo.bin e aponte WHISPER_MODEL")
    raw = a.saida + "-raw"
    os.makedirs(raw, exist_ok=True)
    U = [(s, p.strip()) for s, sec in enumerate(open(a.roteiro).read().split("==="))
         for p in sec.split("\n\n") if p.strip()]
    k = key() if a.motor == "gemini" else None
    with ThreadPoolExecutor(a.paralelo) as ex:
        res = list(ex.map(lambda x: unidade(x[0], x[1][1], a.voz, k, raw, a.modelo, a.motor, lang_code, ref), enumerate(U)))
    tokens = sum(r[3] for r in res)
    for n, (ok, cob, falta), t, _ in res:
        if not ok:
            print(f"REVER u{n:03d} {cob:.0%} tentativas={t} nao ouvido: {falta}")
    # monta: corta silencio das pontas, pausa fixa entre paragrafos, acelera e iguala volume
    apara = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
    for nome, d in (("par", PAUSA_PAR), ("sec", PAUSA_SEC)):
        ff("-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", str(d), f"{raw}/pausa-{nome}.wav")
    linha, tempos, t0 = [], [], 0.0
    with open(f"{raw}/lista.txt", "w") as f:
        for n, (s, texto) in enumerate(U):
            ff("-i", f"{raw}/u{n:03d}.wav", "-af", apara, "-ar", "24000", f"{raw}/u{n:03d}.cut.wav")
            d = dur(f"{raw}/u{n:03d}.cut.wav") / a.tempo
            linha.append((n, max(0, t0 - 0.25), t0 + d + 0.25, texto))
            tempos.append({"inicio": round(t0, 2), "fim": round(t0 + d, 2), "texto": texto})
            t0 += d
            f.write(f"file 'u{n:03d}.cut.wav'\n")
            if n + 1 < len(U):
                prox = "sec" if U[n + 1][0] != s else "par"
                f.write(f"file 'pausa-{prox}.wav'\n")
                t0 += (PAUSA_SEC if prox == "sec" else PAUSA_PAR) / a.tempo
    ff("-f", "concat", "-safe", "0", "-i", f"{raw}/lista.txt", "-af", f"atempo={a.tempo},loudnorm=I=-16:TP=-1.5:LRA=11",
       "-ar", "24000", "-ac", "1", "-b:a", "96k", f"{a.saida}.mp3")
    json.dump(tempos, open(f"{a.saida}.json", "w"), ensure_ascii=False, indent=1)
    ff("-i", f"{a.saida}.mp3", "-c:a", "libopus", "-b:a", "32k", "-ac", "1", "-ar", "48000", "-application", "voip", f"{a.saida}.ogg")
    # atestado do arquivo ENTREGUE: recorta o mp3 final no limite de cada paragrafo e confere de novo
    ff("-i", f"{a.saida}.mp3", "-ar", "16000", "-ac", "1", f"{raw}/final16.wav")

    def confere(j):
        n, ini, fim, texto = j
        ff("-i", f"{raw}/final16.wav", "-ss", f"{ini:.3f}", "-to", f"{fim:.3f}", f"{raw}/f{n:03d}.wav")
        return n, atesta(texto, ouvir(f"{raw}/f{n:03d}.wav"))
    ruins = [(n, r) for n, r in ThreadPoolExecutor(a.paralelo).map(confere, linha) if not r[0]]
    for n, (_, cob, falta) in ruins:
        print(f"FINAL REVER u{n:03d} {cob:.0%} nao ouvido: {falta}  (ouvir esse trecho antes de entregar)")
    total = dur(f"{a.saida}.mp3")
    custo = (f"motor local {a.motor} ({a.voz}), sem custo" if a.motor != "gemini" else
             f"{tokens} tokens de audio ({a.modelo}) = US$ {tokens * PRECO[a.modelo] / 1e6:.2f} (zero na chave gratuita)")
    print(f"{len(U) - len(ruins)}/{len(U)} paragrafos atestados no arquivo final | {total / 60:.1f} min | "
          f"{custo} | {a.saida}.mp3, .ogg e .json")


def check():
    """Casos reais de 24/11: falso alarme de numero/sigla tem de passar, frase faltando tem de reprovar."""
    passa = [("Detentora do E.I.N. um, dois, traço, três, quatro, cinco, seis, sete, oito, nove.",
              "Detentora do EIN 12-34-56789."),
             ("Divisão da Receita, setenta por trinta: setenta por cento pertencerão à Contratante.",
              "Divisão da receita, 70 por 30. 70% pertencerão à contratante."),
             ("conectado à porta O.B.D. dois via cabo extensor.", "conectado à porta OBD2 via cabo extensor."),
             ("Placa e Estado: exemplo, A, B, C, traço, um, dois, três, quatro, Flórida. Data: de dois mil e vinte e seis.",
              "Placa e estado. Exemplo. ABC-1234, Florida. Data: de 2026."),
             ("entre vinte e quatro e trinta fotografias", "entre 24 e 30 fotografias"),
             ("O faturamento foi de um milhão e duzentos mil reais, alta de dezoito por cento sobre dois mil e vinte e cinco.",
              "O faturamento foi de R$ 1,2 milhão, alta de 18% sobre 2025."),
             ("Abrir duas filiais até março de dois mil e vinte e sete e reduzir o C.A.C. em dez por cento.",
              "Abrir duas filiais até março de 2027 e reduzir o CAC em 10%.")]
    for roteiro, ouvido in passa:
        assert atesta(roteiro, ouvido)[0], (roteiro, toks(roteiro), toks(ouvido))
    roteiro = "supervisão executiva direta da frota e a garantia de estrito cumprimento das cláusulas deste instrumento."
    assert not atesta(roteiro, "supervisão executiva direta da frota de estrito cumprimento das cláusulas deste instrumento.")[0]
    print("check ok: 7 falsos alarmes passam, 1 frase faltando reprova")


if __name__ == "__main__":
    check() if sys.argv[1:] == ["--check"] else main()
