# Auditoria de segurança com evidências

Roteiro em português para responsáveis técnicos avaliarem código, dependências e evidências de implantação com a [security-audit da Cloudflare](https://github.com/cloudflare/security-audit-skill).

O resultado esperado é uma recomendação sustentada por código e evidências: o que precisa de ação hoje, o que pode entrar na próxima janela e o que ainda não foi verificado. Contagens de scanners não demonstram, sozinhas, falhas exploráveis no produto.

Outubro é o **Mês de Conscientização sobre Cibersegurança** (*Cybersecurity Awareness Month*), conforme a [referência do NIST](https://www.nist.gov/cybersecurity-awareness-month). A campanha oferece contexto para a revisão periódica; a urgência de cada correção deve resultar das evidências do ambiente analisado.

## Base técnica

A Cloudflare publicou a origem e a evolução desse método em [Build your own vulnerability harness](https://blog.cloudflare.com/build-your-own-vulnerability-harness/). O [repositório oficial](https://github.com/cloudflare/security-audit-skill) descreve as fases e os requisitos. O [SKILL.md](https://github.com/cloudflare/security-audit-skill/blob/main/skills/security-audit/SKILL.md) define os limites de execução e os critérios de confirmação.

O prompt adapta essas instruções ao levantamento de versões e à priorização de manutenção. A seleção inicial do perfil `quick`, a organização por ambiente e o formato da recomendação são escolhas deste roteiro. Não constituem recomendação específica da Cloudflare para qualquer empresa ou produto.

## Como usar

1. Abra o agente no projeto sob sua responsabilidade. Leia as instruções locais e preserve qualquer alteração existente.
2. Copie o [PROMPT.md](PROMPT.md), preencha o escopo no início e envie ao agente. Rode um repositório por vez. Para comparar com produção, informe também o ambiente e a revisão implantada, se conhecidos.
3. Leia o relatório e seus limites antes de decidir por correções. A execução deste prompt autoriza a auditoria delimitada, não deploy, rotação de credenciais ou reinício de serviços.

O agente precisa de leitura dos arquivos e, para a auditoria completa, subagentes independentes, Node.js para os validadores e isolamento imposto pelo sistema operacional para executar código. Quando faltar algum requisito, ele deve registrar a limitação, sem inventar teste ou resultado.

## Skill oficial

- [README e instalação](https://github.com/cloudflare/security-audit-skill#installation)
- [SKILL.md](https://github.com/cloudflare/security-audit-skill/blob/main/skills/security-audit/SKILL.md)

O comando documentado pela Cloudflare na consulta de 23/10/2026 era:

```sh
npx skills add https://github.com/cloudflare/security-audit-skill --skill security-audit
```

Confira a documentação oficial antes de instalar, inclusive seleção do agente e destino. Não execute esse comando como parte do build do produto. Registre a revisão da skill usada na auditoria.

Este repositório contém o prompt, não uma cópia nem uma modificação da skill. Não é um projeto oficial da Cloudflare. As instruções do prompt complementam o método oficial; uma limitação de acesso ou isolamento não deve ser contornada.

## O que conferir no resultado

- Revisão realmente analisada, alterações locais e comparação com o deploy.
- Versão declarada, versão instalada e versão efetivamente em execução, sem misturá-las.
- Condições de exploração, controles existentes e impacto demonstrado.
- Separação entre achados confirmados, hipóteses que precisam de validação e melhorias preventivas.
- Prioridade explicada em linguagem de negócio, correção proposta e risco de regressão.
- Testes executados, cobertura e pendências, incluindo o que não foi possível verificar.

## Fontes oficiais para a análise

| Fonte | O que verificar |
| --- | --- |
| [Cloudflare: security-audit](https://github.com/cloudflare/security-audit-skill) | Método, instalação, isolamento, validação independente e artefatos exigidos. |
| [npm: audit](https://docs.npmjs.com/cli/v11/commands/npm-audit/) | Metadados enviados ao registro e limites da análise de dependências. Consultar a versão da documentação correspondente ao CLI utilizado. |
| [Node.js: releases e suporte](https://nodejs.org/en/about/previous-releases) | Ciclo de suporte do runtime e referências para as versões disponíveis. |
| [PHP: versões suportadas](https://www.php.net/supported-versions.php) | Suporte ativo, suporte de segurança e fim de suporte. |
| [WordPress: atualização](https://wordpress.org/documentation/article/updating-wordpress/) | Procedimento de atualização e preparação de backup. Plugins exigem consulta adicional ao mantenedor. |
| [Docker Engine: notas de versão](https://docs.docker.com/engine/release-notes/) | Correções, mudanças e problemas conhecidos da versão candidata. |
| [n8n: atualização](https://docs.n8n.io/deploy/host-n8n/keep-n8n-running/update-n8n/) | Notas de migração e validação antes da atualização da instância. |

Referências consultadas em 23/10/2026. Cada execução deve consultar as fontes novamente e vincular cada conclusão ao aviso, versão ou trecho de código correspondente. A lista não certifica compatibilidade nem substitui os avisos de segurança de cada dependência.

## Tratamento dos resultados

Não coloque relatórios internos, credenciais, logs ou dumps neste repositório. Escolha uma saída privada, fora do código auditado. O prompt não pressupõe que o destinatário tenha acesso aos ambientes de outra pessoa.
