# Auditoria de segurança com evidências

Um ponto de partida em português para revisar a segurança de um app feito com IA. Se você mantém o código, o roteiro técnico vem depois do checklist.

## Comece aqui se você criou um aplicativo com IA

Você pode começar mesmo sem saber programar. Use seu próprio app ou um projeto que você tenha autorização para revisar. Nesta etapa, a IA lê o código e levanta pontos para conferir com quem mantém o app.

1. Identifique onde estão os arquivos do projeto e quem cuida da hospedagem. Se não souber, peça essa informação ao responsável.
2. Em um agente autorizado a ler essa pasta, copie o pedido abaixo e preencha os campos. Um chat sem acesso aos arquivos só consegue orientar a partir do que você fornecer.
3. Leia o resultado com quem mantém o aplicativo. Peça uma decisão para cada pendência antes de publicar ou alterar o sistema em uso.

```text
Quero uma revisão preventiva do meu aplicativo [nome], para [uso e público].
O código autorizado para leitura está em [pasta ou repositório].
Ambiente em uso, se conhecido: [descreva ou escreva "não sei"].

Leia somente esse código e os documentos que eu fornecer. Não acesse sistemas
de terceiros, não execute testes de invasão, não altere arquivos ou serviços,
não instale ferramentas e não publique nada. Se precisar de acesso adicional,
explique o que falta antes de agir.

Verifique, quando houver evidência disponível: acesso de usuários e
administradores; proteção de dados pessoais; senhas e chaves expostas;
dependências e atualizações; cópias de segurança e recuperação; registros
de erros; e configurações de publicação. Não exiba segredos ou dados pessoais.

Para cada item, explique em português simples o risco, a evidência sem dados
sensíveis, a ação proposta, quem deve decidir e como conferir a correção.
Separe o que foi observado, o que é hipótese e o que não pôde ser verificado.
Não trate ausência de evidência como prova de segurança. Não faça correções.
```

Não cole senhas, chaves, dados de clientes ou relatórios privados na conversa. Se algo sensível aparecer no resultado, trate-o em um canal privado com o responsável técnico.

### Escreva uma regra que você consiga conferir

Uma spec de segurança descreve o que o app precisa proteger e como você vai verificar isso. Comece com uma regra.

| Campo | Exemplo para um app de pedidos |
| --- | --- |
| O que precisa ser protegido? | Os pedidos de cada loja. |
| Quem pode ver? | Somente quem tem acesso àquela loja. |
| Como conferir? | Num ambiente de teste, com duas lojas e dados fictícios, confirme que cada conta vê apenas os pedidos da própria loja. |
| Quem aprova? | A pessoa responsável pelo app confere o resultado antes da publicação. |

Se você usa uma ferramenta que gera o app, inclua a regra no pedido e peça que quem mantém o sistema confira a implementação e os testes. Registre como pendente qualquer regra que ainda não tenha evidência.

### Checklist para decidir os próximos passos

- [ ] A resposta identifica o aplicativo, os arquivos revisados e o que ficou fora do alcance.
- [ ] Cada preocupação tem evidência verificável ou está marcada como hipótese ou pendência.
- [ ] O responsável sabe quem pode acessar os dados e quais permissões precisam ser revistas.
- [ ] Há uma pessoa responsável e um prazo para cada correção ou verificação pendente.
- [ ] Antes de uma mudança, a equipe definiu como validar o resultado e voltar atrás se necessário.
- [ ] Uma pessoa com capacidade técnica revisou as recomendações e confirmou as correções com evidências.

Se algum item não puder ser comprovado, registre-o como pendente. Para uma investigação técnica mais profunda, encaminhe este guia e o [prompt de auditoria](../PROMPT.md) ao responsável. Testes adicionais e mudanças em produção precisam de autorização específica.

## Base técnica

Roteiro em português para responsáveis técnicos avaliarem código, dependências e evidências de implantação com a [security-audit da Cloudflare](https://github.com/cloudflare/security-audit-skill).

O resultado esperado é uma recomendação sustentada por código e evidências: o que precisa de ação hoje, o que pode entrar na próxima janela e o que ainda não foi verificado. Contagens de scanners não demonstram, sozinhas, falhas exploráveis no produto.

Outubro é o **Mês de Conscientização sobre Cibersegurança** (*Cybersecurity Awareness Month*), conforme a [referência do NIST](https://www.nist.gov/cybersecurity-awareness-month). A campanha oferece contexto para a revisão periódica; a urgência de cada correção deve resultar das evidências do ambiente analisado.

A Cloudflare publicou a origem e a evolução desse método em [Build your own vulnerability harness](https://blog.cloudflare.com/build-your-own-vulnerability-harness/). O [repositório oficial](https://github.com/cloudflare/security-audit-skill) descreve as fases e os requisitos. O [SKILL.md](https://github.com/cloudflare/security-audit-skill/blob/main/skills/security-audit/SKILL.md) define os limites de execução e os critérios de confirmação.

O prompt adapta essas instruções ao levantamento de versões e à priorização de manutenção. A seleção inicial do perfil `quick`, a organização por ambiente e o formato da recomendação são escolhas deste roteiro. Não constituem recomendação específica da Cloudflare para qualquer empresa ou produto.

## Como usar

1. Abra o agente no projeto sob sua responsabilidade. Leia as instruções locais e preserve qualquer alteração existente.
2. Copie o [prompt de auditoria](../PROMPT.md), preencha o escopo no início e envie ao agente. Rode um repositório por vez. Para comparar com produção, informe também o ambiente e a revisão implantada, se conhecidos.
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
