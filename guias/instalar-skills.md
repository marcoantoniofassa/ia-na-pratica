# Instalar uma skill é opcional

Os [prompts](../README.md) funcionam por cópia e cola. Este guia é para quem já usa um agente com suporte a skills e tem autorização para adicionar instruções ao projeto.

## Antes da instalação

Leia o `SKILL.md` escolhido. Ele contém o que será pedido ao agente. Confira o agente de destino, a pasta do projeto e se já existe uma skill com o mesmo nome; preserve personalizações existentes.

O [Skills CLI, da Vercel Labs](https://github.com/vercel-labs/skills), documenta instalação por repositório e seleção de skill e agente. Na consulta de 23/10/2026, exigia Node.js 22.20 ou mais recente. Confira o requisito atual no projeto oficial.

## Pelo terminal

Dentro do projeto de destino, o comando abaixo seleciona apenas a skill `explicar-projeto`:

```sh
npx skills add https://github.com/marcoantoniofassa/ia-na-pratica --skill explicar-projeto
```

Escolha o agente quando o instalador perguntar e confira o destino antes de aceitar. Para outra skill, substitua o nome por `organizar-pedido` ou `conferir-entrega`.

O comando usa a rede e pode baixar o CLI, além dos arquivos da skill. Por padrão, o CLI documenta instalação no projeto atual; uma instalação global tem escopo maior. Não execute dentro de uma pasta desconhecida. Política de telemetria e opções: [documentação oficial](https://github.com/vercel-labs/skills/blob/main/docs/troubleshooting.md#telemetry).

Esta receita segue a documentação do instalador. Ela não foi executada em todos os agentes ou sistemas operacionais. Se houver falha, preserve a mensagem, confira a documentação e não use permissões elevadas apenas para tentar novamente.

## Peça ajuda ao agente

Se não usa terminal, copie este pedido para um agente que tenha acesso autorizado ao projeto:

```text
Verifique se este agente aceita skills. Leia o SKILL.md de explicar-projeto
em https://github.com/marcoantoniofassa/ia-na-pratica e a documentação
oficial de instalação aplicável. Instale somente essa skill neste projeto,
se houver suporte e permissão, preservando configurações existentes.
Informe o destino e confirme se o agente consegue descobrir a skill.
Se faltar acesso, explique o passo manual. Não declare instalação concluída
sem verificar. Não instale outras ferramentas por consequência.
```

## Confira o resultado

Peça: “Use explicar-projeto para explicar esta pasta, sem alterar arquivos.” Verifique se a skill foi carregada, se a resposta cita o material consultado e se desconhecidos ficaram explícitos. Uma pasta instalada não prova que o agente a carregou.

A instalação da [security-audit da Cloudflare](auditoria-seguranca.md) é separada e tem outros requisitos. Não substitua a skill oficial pelas três skills desta coleção.
