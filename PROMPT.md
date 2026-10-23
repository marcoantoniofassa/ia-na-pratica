# Prompt: auditoria de segurança e atualizações

## Escopo desta execução

- Responsável técnico: [nome]
- Repositório e pastas autorizadas: [caminhos]
- Branch ou revisão de referência: [ref, ou descobrir sem trocar o checkout]
- Ambiente de interesse: [local / desenvolvimento / staging / produção]
- Sites e hospedagem relacionados: [somente os autorizados; pode ser desconhecido]
- Diretório privado de saída, fora do repositório auditado: [caminho]
- Limite de custo ou chamadas de agentes: [opcional]
- Sinais de incidente ou achados anteriores: [descrever, ou desconhecido]

Atue como especialista em desenvolvimento e segurança. Execute uma auditoria delimitada ao escopo acima usando a skill oficial security-audit da Cloudflare:

[Repositório e README oficiais](https://github.com/cloudflare/security-audit-skill) e [SKILL.md oficial](https://github.com/cloudflare/security-audit-skill/blob/main/skills/security-audit/SKILL.md).

O objetivo é determinar o risco sustentado por evidências e recomendar o que corrigir agora e o que pode esperar. Esta execução é de análise. Não autoriza corrigir o produto, atualizar dependências, fazer deploy, mudar permissões, rotacionar credenciais, reiniciar serviços ou enviar mensagens a outras pessoas.

## 1. Prepare a análise

Leia o README e o SKILL.md oficiais antes de começar. Se a instalação for necessária, siga o procedimento oficial em um destino apropriado, sem alterar a configuração do projeto por conveniência. Registre a origem e a revisão da skill. Se não conseguir utilizá-la, explique exatamente o que faltou.

Use o modo completo da skill, inicialmente no perfil `quick`, com um repositório por execução. Siga todas as fases exigidas, inclusive cobertura, validação independente e validadores dos registros. O perfil quick reduz a abrangência; não reduz os requisitos de evidência. Se o escopo ou orçamento não comportar esse perfil, proponha um recorte antes de iniciar. Não apresente uma análise parcial como auditoria completa.

Respeite as instruções locais do projeto. Descubra sistema operacional, estrutura, comandos e hospedagem a partir das fontes autorizadas. Pergunte somente o que não puder descobrir e for indispensável. A ausência de relato sobre invasão significa desconhecido, não ausência de incidente.

Registre o commit analisado, branch, estado das alterações locais e data. Confira se o checkout está antigo em relação à referência indicada. Leia a revisão correta sem trocar de branch, fazer reset, stash, merge ou sobrescrever alterações existentes. Não atribua a produção um problema encontrado apenas em uma branch antiga.

## 2. Separe código, computador e hospedagem

Mantenha três grupos de evidências: código e dependências; computador de desenvolvimento; configuração e versões da hospedagem.

Faça a auditoria da skill em código e fixtures locais. Não use serviços implantados, identidades reais, bancos de produção ou outros usuários como alvos de teste. Respeite os limites da skill para endpoints e planos de controle em operação.

Quando um fato depender da hospedagem, peça ao responsável uma observação administrativa específica e somente leitura, como a versão do binário, digest da imagem ou política aplicada. Registre a origem dessa evidência. Não presuma que ter credenciais disponíveis autoriza consultar outros ambientes. Não execute a aplicação ou seus comandos de manutenção para descobrir sua versão.

Diferencie expressamente:

- Versão declarada em manifesto, Dockerfile, pipeline ou Terraform.
- Versão resolvida no lockfile ou instalada em uma imagem.
- Versão observada no processo ou contêiner em execução.
- Versão mais recente e suportada na documentação oficial.

Uma tag `latest`, um Dockerfile ou o Node do terminal não prova qual versão está rodando em produção. Separe Node usado somente no build de um frontend estático do runtime que atende requisições. Em serviços distribuídos, confira cada componente relevante, como main, worker, webhook e task runner do n8n.

## 3. Preserve segurança e evidências

Se houver suspeita de comprometimento, interrompa mudanças e execução de código do alvo. Preserve as evidências existentes e apresente uma sequência de contenção e investigação, com o impacto de cada ação. Não apague logs, arquivos ou histórico para limpar o ambiente.

Não imprima, reproduza em relatórios, grave em novas cópias ou envie senhas, tokens, chaves privadas, cookies de sessão ou dumps. Não carregue o ambiente inteiro. Use os mecanismos de autenticação existentes apenas dentro do escopo autorizado.

Se encontrar uma credencial literal, registre caminho, linha, revisão e tipo, sem o valor. Não teste sua validade fazendo chamadas com ela. Separe presença confirmada no código, validade desconhecida, permissões desconhecidas e evidência de uso indevido. Procure registros anteriores de rotação ou revogação, mas não trate uma anotação antiga como prova atual. Proponha a verificação pelo responsável e a substituição coordenada dos consumidores; apagar o texto não revoga a credencial.

Antes de enviar metadados a ferramentas externas, identifique destino e conteúdo. Por exemplo, a [documentação de npm audit](https://docs.npmjs.com/cli/v11/commands/npm-audit/) descreve o envio de nomes e versões de dependências ao registro configurado. Confira o comportamento da versão instalada, inclusive dados adicionais enviados em mecanismos de fallback. Se isso não estiver autorizado, peça autorização específica e continue o trabalho local independente. Nunca use `npm audit fix --force` nesta auditoria.

## 4. Analise atualizações e explorabilidade

Use fontes oficiais para Node.js, PHP, WordPress, plugins, dependências, imagens Docker, sistema operacional e n8n, conforme existirem no escopo. Não invente essas tecnologias onde não forem usadas.

Pontos de partida: [suporte do Node.js](https://nodejs.org/en/about/previous-releases), [suporte do PHP](https://www.php.net/supported-versions.php), [atualização do WordPress](https://wordpress.org/documentation/article/updating-wordpress/), [notas do Docker Engine](https://docs.docker.com/engine/release-notes/) e [atualização do n8n](https://docs.n8n.io/deploy/host-n8n/keep-n8n-running/update-n8n/). Para cada conclusão, cite o aviso ou documento específico, URL, data da consulta e versões afetadas e corrigidas. Distinga uma afirmação do fornecedor de uma inferência feita durante a análise; não use a reputação da fonte para validar uma conclusão que ela não sustenta.

Compare suporte, correções de segurança, avisos oficiais, engines, lockfiles, código consumidor e notas de migração. Uma versão mais nova não é automaticamente compatível. Respeite pins existentes: descubra por que foram fixados e se o impedimento foi resolvido. Em imagens de terceiros, como n8n, prefira avaliar a atualização da imagem oficial completa a substituir seu Node isoladamente.

Para cada alerta de scanner, confira:

1. Qual versão e componente estão afetados e em qual ambiente são consumidos.
2. Que dado ou ação um agente menos confiável consegue controlar.
3. Qual caminho leva essa entrada à função vulnerável.
4. Quais opções, permissões e condições são necessárias para exploração.
5. Quais controles existentes impedem ou limitam o efeito.
6. Qual impacto concreto foi demonstrado e qual fato ainda falta.

Separe dependências de desenvolvimento, build e runtime. Deduplicate avisos da mesma causa. Contagem de pacotes afetados não equivale a quantidade de brechas abertas. Dependência vulnerável, tag mutável, firewall desligado ou runtime fora de suporte, isoladamente, não comprovam invasão nem exploração no produto.

Use as categorias e o esquema oficial da skill: `confirmed`, `needs_validation` e `rejected`. Atribua severidade apenas a achados confirmados, limitada ao impacto demonstrado. Mantenha melhorias preventivas em seção própria. Nunca marque como confirmado algo que depende de uma configuração de produção não observada.

## 5. Valide sem atingir produção

Execute código controlado pelo alvo somente se conseguir impor todos os controles exigidos pela skill: rede externa bloqueada, loopback isolado quando necessário, ambiente vazio com allowlist explícita e valores fictícios, HOME/cache/temporários locais ao scratch, fonte e toolchain somente leitura, escrita restrita ao scratch e limites baixos de CPU, memória, processos, arquivos, disco e tempo.

Não exponha home do host, credenciais, sockets de controle, diretórios de outros agentes ou serviços compartilhados ao código do alvo. Não instale nem deixe builds buscarem dependências. Use apenas ferramentas e dependências já disponíveis. Um worktree ou contêiner, sozinho, não comprova esse isolamento.

Se faltar qualquer controle, não execute o código. Registre o bloqueio de validação e o teste seguro necessário. Use identidades, dados e segredos fictícios; pare no efeito mínimo necessário. Siga a separação de autoria e verificação e a promoção segura de artefatos definidas pela skill. Não execute provas de conceito em endpoints reais.

## 6. Entregue uma decisão clara

Gere e valide os artefatos exigidos pela skill no diretório privado de saída. Uma execução incompleta deve registrar o motivo e a cobertura faltante, conforme o contrato oficial.

Na resposta ao responsável, comece pela recomendação: agir hoje, programar na próxima janela ou acompanhar. Explique o dano possível, as condições e o que sustenta esse prazo. Diferencie urgência de investigação de urgência para alterar produção. Não crie emergência a partir de uma contagem de scanner nem prometa que é seguro esperar sem evidência.

Inclua:

- Escopo e revisão analisados, fontes e ambientes realmente observados.
- Tabela de versões declaradas, resolvidas, em execução e candidatas à atualização, com desconhecidos explícitos.
- Achados confirmados e hipóteses pendentes em tabelas separadas, com caminhos, linhas, condições e evidência.
- Melhorias preventivas e alertas descartados, com justificativas.
- Correção mínima proposta por projeto, impacto operacional, compatibilidade a testar e dependências entre mudanças.
- Plano de backup e restauração a validar antes de uma futura atualização, incluindo bancos, volumes e material de recuperação necessário, sem copiar segredos para o relatório.
- Como iniciar cada projeto em ambiente isolado, com os comandos encontrados no repositório e os pré-requisitos. Se não foi testado, diga.
- Testes realmente executados, limitações, cobertura e pendências. Não confunda leitura de fonte com teste funcional.

Finalize informando que nenhuma atualização foi executada por este prompt. Qualquer correção posterior deve ter escopo próprio, preservar alterações e dados, tratar um projeto por vez e exigir autorização explícita antes de alterações em produção ou reinícios.
