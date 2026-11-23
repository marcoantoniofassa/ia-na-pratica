# Responder a um alerta de vulnerabilidade

**Para quem:** responsável técnico que recebeu um alerta de segurança (um CVE ou aviso de fornecedor) e precisa saber se o sistema é atingido.
**Precisa de:** link do aviso oficial e acesso de leitura aos repositórios e ambientes. **Resultado:** mapa de onde o componente roda, com evidência, situação e prioridade.

## Copie este prompt

```text
Saiu um alerta de segurança e preciso saber se ele nos atinge.
Alerta: [link do aviso oficial ou número do CVE].
Escopo autorizado: [repositórios, ambientes e contas que você pode ler].

Trabalhe só em leitura. Não reproduza a exploração, não reinicie
serviços e não mude produção.

1. Leia o aviso oficial. Para cada falha, liste o componente, as
   versões afetadas, as versões corrigidas e a condição que precisa
   estar presente (por exemplo, um protocolo ou módulo ativo).
2. Procure no código onde o componente aparece: dependências,
   Dockerfiles e imagens base, Compose, arquivos de configuração,
   manifests, infraestrutura como código e pipelines.
3. Em cada ambiente acessível, confira o que está em execução:
   processo, pacote, imagem e digest, configuração efetiva e portas.
   Versão declarada, versão instalada e versão em execução são
   coisas diferentes; registre as três quando possível.
4. Siga o caminho da requisição: quem recebe a conexão do visitante
   e qual protocolo chega ao componente. Um cabeçalho com o nome do
   produto não prova exposição.
5. Distribuições corrigem por backport sem mudar o número da versão.
   Quando for o caso, compare a revisão do pacote com o aviso.

Monte uma tabela com um ponto por linha: onde roda, versão, condição
presente ou ausente, evidência e situação (exposto, protegido ou não
verificável). Falta de acesso vira "não verificável", nunca "seguro".

Para cada ponto exposto, proponha a correção com ensaio em cópia
isolada, plano de retorno e a prova de que a versão corrigida é a que
está rodando depois da troca. Recarregar um serviço pode não trocar
o código em execução.

Termine com o que precisa de ação hoje, o que entra na próxima janela
e o que ficou sem verificação. Grave o relatório em local privado,
fora do repositório analisado.
```

**Confira:** cada linha da tabela aponta a evidência que sustenta a situação, e o que ficou sem acesso aparece como não verificável?

## Exemplo: NGINX2Root

Em novembro de 2026, o NGINX publicou correções para cinco falhas que ficaram conhecidas como NGINX2Root. A principal, CVE-2026-123007, está no código desde a versão 1.9.5, de 2015, e exige HTTP/2 ativo. Um NGINX que recebe só HTTP/1.1 de outro proxy na frente não aciona essa falha, mesmo com a versão afetada. O passo 4 do prompt existe para encontrar esse caso. [Avisos de segurança do NGINX](https://nginx.org/en/security_advisories.html).

Os números e versões acima são uma fotografia de 23/11/2026. Consulte o aviso vigente antes de decidir.

[Voltar ao início](../README.md)
