---
name: pdf-falado
description: Transformar um documento (PDF, Word ou texto) em áudio com voz natural, lido palavra por palavra e conferido por transcrição. Use quando alguém precisa ouvir um texto inteiro, sem resumo, no fone ou no WhatsApp. Exige Python, ffmpeg, whisper.cpp e uma chave da API Gemini.
license: MIT
---

# PDF Falado

Leitura integral, não resumo. O texto é reescrito para ser falado, a voz do Gemini lê parágrafo por parágrafo, o Whisper transcreve cada trecho e o script compara com o roteiro. Parágrafo com frase faltando é gerado de novo.

## Antes de começar

- **Requisitos:** `python3`, `ffmpeg`, `whisper-cli` (whisper.cpp) e o modelo `ggml-large-v3-turbo.bin`, com o caminho em `WHISPER_MODEL`. A chave da API Gemini fica em `GEMINI_API_KEY`. O link do modelo está no topo de `scripts/pdf-falado.py`. Testado no macOS.
- **Chave:** se `GEMINI_API_KEY` não estiver no ambiente, peça ao usuário que configure ou que cole a chave para você gravar no ambiente. Nunca grave a chave em arquivo do projeto nem a repita na resposta.
- **Privacidade:** no nível gratuito, o Google pode usar o texto enviado para melhorar os produtos, e revisores humanos podem ler trechos. Para documento sigiloso, confirme com o usuário antes de enviar ou use uma chave com faturamento.

## 1. Extrair o texto

Use a ferramenta disponível: `pdftotext -layout` para PDF, `pandoc` para Word, leitura direta para texto. Confira se veio tudo. PDF escaneado sem camada de texto precisa de OCR antes; avise o usuário em vez de seguir com texto incompleto.

## 2. Escrever o roteiro falado

Grave `roteiro.txt` com o texto inteiro, palavra por palavra, pronto para ser falado. Parágrafos separados por linha em branco; `===` numa linha separa seções e gera uma pausa maior.

- Números, valores, datas e unidades por extenso: "um milhão e duzentos mil reais", "vinte e três graus".
- Códigos, documentos, CEP e placas dígito por dígito, por extenso, **cada um em parágrafo próprio**. Dentro de parágrafo longo, a voz costuma pular sequências de dígitos.
- Siglas soletradas com pontos ("C.A.C.", "O.B.D.") e fórmulas por extenso ("cê ó dois").
- Texto em CAIXA ALTA vira caixa normal, senão a voz soletra. Marcadores de lista somem.
- Tabela vira frases: diga as colunas e depois cada linha. Campo vazio vira "campo em branco"; linha de assinatura vira "Linha de assinatura:".
- Parágrafos de até umas 120 palavras. Termine com "Fim do documento."

Não resuma, não comente e não corrija o conteúdo. Se algo for ilegível, marque e avise.

## 3. Gerar e conferir

```sh
python3 <pasta desta skill>/scripts/pdf-falado.py roteiro.txt leitura --paralelo 1
```

Use `--paralelo 1` com chave gratuita; com faturamento, até 4. Rode **uma cópia do script por vez**: cada Whisper ocupa cerca de 1,5 GB de memória, e várias cópias juntas podem travar o computador. `python3 <pasta>/scripts/pdf-falado.py --check` roda o autoteste do comparador.

O script gera cada parágrafo, confere, gera de novo até 3 vezes quando falta frase, monta o arquivo e confere o arquivo final recortado nos limites de cada parágrafo. A última linha traz parágrafos conferidos, duração e custo.

- `REVER` com trecho em "não ouvido": ajuste aquele parágrafo do roteiro e rode de novo.
- `REVER` sem trecho listado costuma ser número ou sigla escritos de outro jeito pelo Whisper. Confira a frase antes de considerar falha.
- Nunca confira com o Whisper transcrevendo o arquivo inteiro de uma vez: em áudio longo ele perde frases que existem no arquivo.

## 4. Entregar

- `leitura.mp3`: arquivo para guardar.
- `leitura.ogg`: no WhatsApp, chega como mensagem de voz, que permite acelerar.
- `leitura.json`: início e fim de cada parágrafo, útil para capítulos ou legenda.

Informe duração, quantos parágrafos passaram na conferência e o custo. Não envie o áudio a ninguém sem pedido do usuário.

## Custo e voz

Padrão: `gemini-3.8-flash-tts`, voz Charon, 8% mais rápido. Em novembro de 2026, com faturamento, custava cerca de US$ 0,014 por minuto de áudio; `--modelo gemini-3.8-flash-lite-tts` sai cerca de 24% mais barato. Os preços mudam: confira a [página oficial](https://ai.google.dev/gemini-api/docs/pricing). Outras vozes: `--voz` com um nome da [documentação de TTS](https://ai.google.dev/gemini-api/docs/speech-generation).
