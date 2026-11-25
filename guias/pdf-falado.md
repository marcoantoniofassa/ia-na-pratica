# Documento inteiro em áudio, palavra por palavra

Relatório, apostila, manual ou livro, lido inteiro com voz natural e conferido frase por frase. O resultado pode ir para o fone ou para o WhatsApp como mensagem de voz, que permite ouvir em 2×.

Há três caminhos. Os exemplos usam textos fictícios.

## 1. Grátis, com ChatGPT ou Claude e uma conta Google

Uns 20 minutos de cliques, sem instalar nada. Sai um arquivo de áudio por bloco.

1. No ChatGPT ou no Claude, anexe o documento e cole:

```text
Vou transformar este documento em áudio com leitura integral. Reescreva o texto INTEIRO para ser lido em voz alta, sem resumir, sem comentar e sem pular nada.

Regras:
- Blocos de no máximo 200 palavras, com uma linha "---" entre eles. Quebre em fim de frase.
- Números, valores e datas por extenso ("um milhão e duzentos mil reais", "trinta dias").
- Códigos, documentos e placas dígito por dígito, por extenso, cada um numa frase curta.
- Siglas como as pessoas falam: a que se fala como palavra vira palavra ("Cac", "Pix"); a que se soletra fica em maiúsculas ("CPF").
- Termos em outra língua ficam na grafia original, sem traduzir.
- Fórmulas por extenso ("cê ó dois").
- Tire marcadores de lista e escreva palavras comuns em caixa normal, não em CAIXA ALTA.
- Tabela vira frase: diga as colunas e depois cada linha.
- Termine com "Fim do documento."

Fora do roteiro, no final, diga quantos blocos e quantas palavras tem cada um.
```

2. Abra [aistudio.google.com/generate-speech](https://aistudio.google.com/generate-speech), clique em *Create new dialog* e escolha a voz *Charon* em *Speaker settings*.
3. Cole um bloco, clique em *Run* e depois em *Download*. Repita até o último bloco.
4. Confira o tempo: um bloco de 200 palavras dura perto de 1min30. Bem mais curto que isso, a voz pulou texto. Gere de novo.

Em 24/11/2026, a tela gerava áudio sem chave de API, tinha botão de download e informava que o uso pela interface era gratuito.

## 2. Com agente de IA: Claude Code ou Codex

Para quem tem Claude Pro ou ChatGPT Plus. Sai um arquivo único, conferido.

1. Crie uma chave grátis em [aistudio.google.com/apikey](https://aistudio.google.com/apikey).
2. Baixe [`pdf-falado.py`](../skills/pdf-falado/scripts/pdf-falado.py) para a pasta do documento.
3. Abra o agente nessa pasta e cole:

```text
Quero a leitura integral do documento desta pasta (PDF, Word ou texto) em áudio natural, sem resumo, usando o script pdf-falado.py que está aqui.

1. Instale o que faltar: ffmpeg, whisper-cpp e o modelo ggml-large-v3-turbo.bin (o link está no topo do script). Vou colar minha chave do Gemini quando você pedir: guarde só na variável GEMINI_API_KEY, nunca em arquivo.
2. Extraia o texto e escreva roteiro.txt com ele inteiro, palavra por palavra, pronto para ser falado: números, valores e datas por extenso; códigos e documentos dígito por dígito, cada um em parágrafo próprio; siglas como as pessoas falam (Cac, Pix como palavra; CPF, CNPJ soletrados); termos em outra língua na grafia original; fórmulas por extenso; tabela como frases; sem CAIXA ALTA em palavra comum nem marcadores de lista; parágrafos separados por linha em branco.
3. Rode: python3 pdf-falado.py roteiro.txt leitura --paralelo 1
4. Se aparecer REVER, corrija aquele parágrafo do roteiro e rode de novo. Rode uma cópia do script por vez.
5. No fim, me diga a duração e quantos parágrafos passaram na conferência.
```

Você recebe `leitura.mp3` para guardar e `leitura.ogg`, que o WhatsApp trata como mensagem de voz.

**Sem custo e sem o texto sair do computador:** em Mac com Apple Silicon, peça para rodar com `--motor kokoro` (o topo do script mostra o comando com `uv`). Não precisa de chave; a voz é um pouco menos natural que a do Gemini.

## 3. Avançado: instalar como skill

Para quem já usa agente no dia a dia. A skill fica instalada no seu usuário e responde a pedidos como "transforma este PDF em áudio" em qualquer pasta. Cole no Claude Code ou no Codex:

```text
Instale a skill pdf-falado do repositório https://github.com/marcoantoniofassa/ia-na-pratica no meu usuário, para eu pedir "transforma este documento em áudio" em qualquer pasta.

1. Leia skills/pdf-falado/SKILL.md e scripts/pdf-falado.py antes de instalar.
2. Instale com: npx skills add https://github.com/marcoantoniofassa/ia-na-pratica --skill pdf-falado
   Escolha este agente e a instalação global. Sem Node 22 ou mais recente, clone o repositório e copie skills/pdf-falado para a pasta de skills do agente (Claude Code: ~/.claude/skills/; Codex: ~/.codex/skills/). Se já existir uma skill com esse nome, pergunte antes de sobrescrever.
3. Instale as dependências que faltarem: python3, ffmpeg e whisper.cpp (no macOS: brew install ffmpeg whisper-cpp). Baixe o modelo ggml-large-v3-turbo.bin (link no topo do script) para uma pasta fixa e grave o caminho em WHISPER_MODEL no meu perfil de shell.
4. Peça minha chave do Gemini (aistudio.google.com/apikey) e grave em GEMINI_API_KEY no perfil de shell ou no gerenciador de segredos que eu já uso. Nunca em arquivo de projeto e nunca na resposta.
5. Se este for um Mac com Apple Silicon, instale também o motor local: brew install espeak-ng e confirme que o uv está instalado. Rode o autoteste: python3 <pasta da skill>/scripts/pdf-falado.py --check. Depois gere um teste com um roteiro de dois parágrafos e me mostre a última linha do relatório.
6. Me diga onde a skill ficou, como chamá-la e o que ficou pendente. Não instale nada além do listado.
```

## Antes de enviar um documento

No uso gratuito (tela do AI Studio ou chave sem faturamento), o Google pode usar o texto enviado para melhorar os próprios produtos, e revisores humanos podem ler trechos ([termos da API Gemini](https://ai.google.dev/gemini-api/terms)). Para documento sigiloso, use uma chave com faturamento. Em novembro de 2026, custava cerca de US$ 0,014 por minuto de áudio ([preços](https://ai.google.dev/gemini-api/docs/pricing)).

## O que foi testado

O caminho 1 foi conferido na tela do AI Studio em 24/11/2026. Os caminhos 2 e 3 usam o script, testado no macOS com documentos de até 15 minutos de áudio, sempre com todos os parágrafos conferidos. A instalação por `npx skills add` foi testada a partir de uma cópia local do repositório, no escopo de projeto e para o Claude Code: a skill chega com o script. Linux, Windows e a instalação global não foram testados. O comportamento da skill depende do agente: confira se ela foi carregada antes de confiar no resultado.
