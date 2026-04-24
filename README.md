# Refactor Arch — Skill de Auditoria e Refatoração MVC

Este repositório entrega uma skill para OpenAI Codex chamada `refactor-arch`. O objetivo é analisar projetos legados, identificar problemas de arquitetura, segurança e manutenção, gerar um relatório estruturado e, após confirmação, refatorar a aplicação para uma organização compatível com MVC.

Os projetos usados na validação são:

- `code-smells-project/`: API Python/Flask de e-commerce.
- `ecommerce-api-legacy/`: API Node.js/Express de LMS/e-commerce com checkout.
- `task-manager-api/`: API Python/Flask de gestão de tarefas.

## Análise Manual

### `code-smells-project`

Stack: Python, Flask, SQLite.

| Severidade | Problema | Justificativa |
|---|---|---|
| CRITICAL | Endpoint `/admin/query` executa SQL enviado pelo cliente | Permite leitura, alteração ou exclusão arbitrária de dados. Também mistura HTTP e persistência diretamente na rota. |
| CRITICAL | Endpoint `/admin/reset-db` destrói dados sem autenticação | Qualquer chamada HTTP pode apagar tabelas de negócio. É falha grave de segurança e operação. |
| CRITICAL | `SECRET_KEY` hardcoded e debug habilitado | Segredos versionados podem vazar e debug em runtime pode expor comportamento interno. |
| CRITICAL | `/health` expõe `secret_key`, caminho do banco e debug | Vaza dados sensíveis e confirma configurações perigosas para qualquer cliente. |
| CRITICAL | SQL injection em queries montadas por concatenação | Dados de entrada entram em SQL sem parametrização, comprometendo integridade e confidencialidade. |
| CRITICAL | Senhas armazenadas e retornadas em texto claro | Usuários e banco expõem credenciais diretamente, quebrando um requisito básico de segurança. |
| HIGH | `models.py` concentra persistência, regras, serialização e relatórios | O arquivo vira um god module, dificultando testes isolados e mudanças seguras. |
| HIGH | Controllers executam validação, regra de negócio, logging e resposta | A camada HTTP fica pesada e regras deixam de ser reutilizáveis fora das rotas. |
| MEDIUM | Fluxo de pedido não tem rollback explícito | Erros no meio da criação podem deixar transações inconsistentes. |
| MEDIUM | Listagens de pedidos usam padrão N+1 | O número de queries cresce conforme pedidos e itens, degradando performance. |
| LOW | Constantes de domínio ficam espalhadas em handlers | Categorias e limites ficam difíceis de reaproveitar e testar. |
| LOW | Limiares de desconto ficam como números mágicos | Regras de relatório aparecem como literais sem nome de domínio, reduzindo legibilidade e testabilidade. |

### `ecommerce-api-legacy`

Stack: Node.js, Express, SQLite.

| Severidade | Problema | Justificativa |
|---|---|---|
| CRITICAL | Credenciais e chaves hardcoded em `src/utils.js` | Inclui configuração sensível e uma chave `pk_live_...` versionada no código. |
| CRITICAL | `AppManager` concentra rotas, schema, seed, persistência, checkout, pagamento e relatórios | A classe colapsa as fronteiras MVC e torna fluxos críticos difíceis de testar e alterar. |
| HIGH | Checkout registra cartão e chave de pagamento em log | Logs podem expor dados de cartão e credenciais operacionais. |
| HIGH | Senha padrão fraca para novos usuários | A API aceita criação implícita com senha `"123456"`, enfraquecendo a segurança. |
| HIGH | Hash de senha customizado e truncado | Base64 repetido não é hash seguro, não tem salt/custo e facilita ataque offline. |
| HIGH | Relatório financeiro administrativo sem autenticação | Dados financeiros e de alunos ficam públicos para qualquer cliente com acesso à API. |
| HIGH | Exclusão de usuário deixa pagamentos e matrículas órfãos | Quebra invariantes de domínio e compromete relatórios. |
| MEDIUM | Relatório financeiro usa N+1 com callbacks aninhados | Performance degrada com o crescimento de cursos e matrículas. |
| MEDIUM | Validação do checkout é incompleta e presa à rota | Dados inválidos atravessam a fronteira pública e entram no fluxo de negócio. |
| LOW | Campos abreviados reduzem legibilidade | Variáveis como `u`, `e`, `p`, `cid` e `cc` tornam o mapeamento mais sujeito a erro. |
| LOW | Nomes de módulos genéricos ocultam responsabilidade | `utils.js` mistura config, cache, log e criptografia, dificultando descoberta de ownership. |

### `task-manager-api`

Stack: Python, Flask, Flask-SQLAlchemy.

Este projeto já possui separação inicial em `models/`, `routes/`, `services/` e `utils/`, mas a análise manual ainda identificou problemas relevantes.

| Severidade | Problema | Justificativa |
|---|---|---|
| CRITICAL | `SECRET_KEY` hardcoded e `debug=True` no boot | Configuração sensível e modo debug ficam presos ao código, inadequados para ambientes reais. |
| CRITICAL | Senhas com MD5 e retorno de `password` em `User.to_dict()` | MD5 é inadequado para senhas e a serialização expõe hash/senha na API. |
| HIGH | Token de login fake (`fake-jwt-token-<id>`) | O fluxo simula autenticação sem assinatura, expiração ou verificação real. |
| HIGH | Rotas concentram validação, persistência, serialização e regra de negócio | `task_routes.py`, `user_routes.py` e `report_routes.py` funcionam como fat controllers. |
| MEDIUM | Relatórios e listagens fazem consultas repetidas por usuário/categoria/task | Há risco de N+1 e acoplamento entre consulta e montagem de resposta. |
| MEDIUM | Validações de status, prioridade, data e email estão duplicadas | Regras aparecem em handlers e modelos, dificultando evolução consistente. |
| MEDIUM | Tratamento genérico de exceções retorna erros opacos | `except` amplo esconde causa real e dificulta testes e operação. |
| LOW | Imports e constantes sem uso ou sem nome de domínio claro | Imports como `os`, `sys`, `json` e listas inline reduzem legibilidade e sinal arquitetural. |
| LOW | Helpers genéricos misturam formatação e regra local | Funções utilitárias pouco coesas tornam difícil decidir se a regra pertence ao model, serializer ou validator. |

## Construção da Skill

### Estrutura

A skill principal canônica fica em `code-smells-project/.claude/skills/refactor-arch/SKILL.md`, com cópias sincronizadas em `.agents/skills/refactor-arch/` nos três projetos e em `refactor-arch/` na raiz para manutenção. Ela foi estruturada como um workflow sequencial:

1. **Fase 1 — Análise do projeto:** detectar linguagem, framework, runtime, dependências, entrypoints, domínio, tabelas/entidades, arquitetura atual e comandos de validação.
2. **Fase 2 — Auditoria:** consultar o catálogo, classificar problemas de MVC, SOLID, segurança e manutenção com arquivo e linha exatos, salvar o relatório e pausar com `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`.
3. **Fase 3 — Refatoração e validação:** reorganizar responsabilidades para MVC, preservar comportamento público e validar por testes/build/boot/interfaces públicas conforme a tecnologia detectada.

### Arquivos de referência

- `refactor-arch/references/severity-rubric.md`: define CRITICAL, HIGH, MEDIUM e LOW com regras de classificação.
- `refactor-arch/references/audit-report-template.md`: padroniza a saída das fases, o resumo de findings e a matriz de aceitação.
- `refactor-arch/references/project-analysis-heuristics.md`: orienta detecção de linguagem, framework, banco, domínio, entrypoints e comandos de validação.
- `refactor-arch/references/mvc-architecture-guidelines.md`: define responsabilidades alvo de Models, Views/Routes, Controllers e camadas auxiliares.
- `refactor-arch/references/mvc-refactor-playbook.md`: orienta mapeamento MVC por stack, estratégia incremental e validação.

### Anti-patterns incluídos

O catálogo cobre os problemas que apareceram nos três projetos e que tendem a ocorrer em stacks diferentes:

- God class, god module e god method.
- Fat controllers e rotas com regra de negócio.
- SQL injection e construção insegura de queries.
- Secrets, chaves e credenciais hardcoded.
- Exposição de dados sensíveis em respostas ou logs.
- Autenticação/autorização ausente em operações protegidas.
- Hash de senha inseguro ou APIs criptográficas inadequadas.
- Estado global mutável e forte acoplamento a infraestrutura.
- Padrões N+1 em acesso a dados.
- Validação duplicada, incompleta ou inconsistente.
- Tratamento genérico de erros.
- Magic numbers, magic strings e nomes pouco claros.
- Uso de APIs obsoletas ou inseguras, recomendando equivalentes modernos quando aplicável.

### Como a skill permanece agnóstica de tecnologia

A skill não assume um framework específico. Ela começa inspecionando manifests, entrypoints, dependências, rotas, modelos, arquivos de banco, comandos de boot e testes. A validação também é agnóstica: a skill procura scripts em `package.json`, `pyproject.toml`, `requirements.txt`, `pom.xml`, `build.gradle`, `Cargo.toml`, `go.mod`, `composer.json` e equivalentes, priorizando testes automatizados, depois build/typecheck/lint/syntax, boot e smoke tests da interface pública. Depois adapta MVC à stack encontrada:

- Em Flask, rotas funcionam como camada de view/HTTP, controllers ou services orquestram casos de uso, e models/repositories concentram persistência e invariantes.
- Em Express, `routes` declaram endpoints, controllers cuidam da fronteira HTTP, services executam fluxos de negócio e repositories/models isolam SQLite.
- Em projetos parcialmente organizados, a skill não força uma árvore genérica; ela melhora as fronteiras existentes.

### Desafios encontrados

- **Projetos com níveis diferentes de organização:** um projeto era quase monolítico, outro concentrava tudo em uma classe e o terceiro já tinha camadas parciais. A solução foi orientar a skill por responsabilidades, não por nomes fixos de pastas.
- **Ausência de testes formais:** os projetos não trazem suítes robustas. A skill prevê validação por boot e smoke tests quando não há `pytest`, `npm test`, build ou lint.
- **Segurança vs compatibilidade:** algumas correções mudam comportamento perigoso, como senhas fracas, logs sensíveis ou rotas administrativas abertas. A skill registra riscos e recomenda preservar contratos públicos apenas quando isso não mantém uma falha crítica.

## Resultados

### Resumo dos relatórios

| Projeto | Relatório | CRITICAL | HIGH | MEDIUM | LOW | Total | Status |
|---|---|---:|---:|---:|---:|---:|---|
| `code-smells-project` | `code-smells-project/reports/audit-project-1.md` | 6 | 4 | 4 | 2 | 16 | Auditoria e Fase 3 validadas |
| `ecommerce-api-legacy` | `ecommerce-api-legacy/reports/audit-project-2.md` | 2 | 5 | 4 | 1 | 12 | Auditoria e Fase 3 validadas |
| `task-manager-api` | `task-manager-api/reports/audit-project-3.md` | 3 | 4 | 4 | 2 | 13 | Auditoria e Fase 3 validadas |

### Comparação antes/depois da estrutura

#### `code-smells-project`

Antes:

```text
app.py
controllers.py
database.py
models.py
```

Depois observado no repositório:

```text
app.py
database.py
controllers/
models/
product_model.py
user_model.py
order_model.py
report_model.py
routes/
services/
reports/audit-project-1.md
```

Status: refatoração MVC validada. Os arquivos `product_model.py`, `user_model.py`, `order_model.py` e `report_model.py` são shims de compatibilidade; a lógica principal está em `models/`, `controllers/`, `routes/` e `services/`.

#### `ecommerce-api-legacy`

Antes:

```text
src/app.js
src/AppManager.js
src/utils.js
```

Depois:

```text
src/app.js
src/config.js
src/database.js
src/routes.js
src/controllers/
src/middleware/
src/models/
src/services/
src/validators/
reports/audit-project-2.md
reports/refactor-project-1.md
```

Status: refatoração MVC registrada em `reports/audit-project-2.md`. O `AppManager` e `utils.js` foram removidos da arquitetura runtime e as responsabilidades foram separadas em controllers, services, repositories/models, middleware, validators e composition root.

#### `task-manager-api`

Antes:

```text
app.py
database.py
models/
routes/
services/
utils/
seed.py
```

Depois observado no repositório:

```text
app.py
config.py
database.py
controllers/
models/
routes/
serializers/
services/
utils/
validators/
seed.py
reports/audit-project-3.md
```

Status: refatoração MVC validada. O workspace apresenta controllers, serializers, validators, config e services, com smoke tests registrados em `reports/audit-project-3.md`.

### Checklist de validação

#### `code-smells-project`

| Item | Status | Evidência |
|---|---|---|
| Linguagem detectada corretamente | OK | Relatório detectou Python 3.14.4 localmente. |
| Framework detectado corretamente | OK | Relatório detectou Flask 3.1.1 e Flask-CORS 5.0.1. |
| Domínio descrito corretamente | OK | E-commerce com produtos, usuários, pedidos, itens e relatório de vendas. |
| Relatório segue template | OK | Arquivo contém Fase 1, relatório de auditoria, resumo, findings e gate de confirmação. |
| Mínimo de 5 findings | OK | 16 findings. |
| Refatoração validada após Fase 3 | OK | `reports/audit-project-1.md` contém seção `PHASE 3: REFACTORING COMPLETE`. |
| Aplicação rodando após refatoração | OK | Smoke tests via Flask test client: `/`, `/health`, `/produtos`, `/usuarios`, `/pedidos`, `/relatorios/vendas` -> 200. |

#### `ecommerce-api-legacy`

| Item | Status | Evidência |
|---|---|---|
| Linguagem detectada corretamente | OK | Relatório detectou JavaScript em Node.js. |
| Framework detectado corretamente | OK | Relatório detectou Express 4.18.x e sqlite3 5.1.x. |
| Domínio descrito corretamente | OK | LMS/e-commerce com checkout, matrículas, pagamentos e relatório financeiro. |
| Relatório segue template | OK | `reports/audit-project-2.md` contém Fase 1, relatório de auditoria, resumo, findings, gate e Fase 3. |
| Mínimo de 5 findings | OK | 12 findings. |
| Refatoração validada após Fase 3 | OK | `reports/audit-project-2.md` registra validação. |
| Aplicação rodando após refatoração | OK | Smoke tests HTTP documentados no relatório de Fase 3. |

Logs registrados no relatório:

```text
GET /api/admin/financial-report -> 200
POST /api/checkout com cartão iniciando em 4 -> 200 {"msg":"Sucesso","enrollment_id":2}
POST /api/checkout com cartão iniciando em 5 -> 400 Pagamento recusado
DELETE /api/users/1 -> 200 Usuário deletado.
```

Observação: `npm install` reportou vulnerabilidades herdadas da árvore de dependências: 2 low, 1 moderate e 6 high.

#### `task-manager-api`

| Item | Status | Evidência |
|---|---|---|
| Linguagem detectada corretamente | OK | Relatório detectou Python 3.14.4 localmente. |
| Framework detectado corretamente | OK | Relatório detectou Flask 3.0.0, Flask-SQLAlchemy 3.1.1 e Flask-CORS 4.0.0. |
| Domínio descrito corretamente | OK | Task Manager API com usuários, tasks, categorias, relatórios, login e notificações. |
| Relatório segue template | OK | `reports/audit-project-3.md` contém Fase 1, relatório de auditoria, resumo, findings, gate e Fase 3. |
| Mínimo de 5 findings | OK | 13 findings. |
| Refatoração validada após Fase 3 | OK | `reports/audit-project-3.md` contém seção `PHASE 3: REFACTORING COMPLETE`. |
| Aplicação rodando após refatoração | OK | Smoke tests via Flask test client: `/`, `/health`, `/tasks`, `/users`, `/reports/summary` -> 200. |

### Screenshots e logs de execução

Não há screenshots versionados no repositório. As evidências disponíveis são logs textuais registrados nos relatórios.

#### `ecommerce-api-legacy`

O relatório `ecommerce-api-legacy/reports/refactor-project-1.md` registra a aplicação rodando em smoke tests HTTP:

```text
GET /api/admin/financial-report -> 200
POST /api/checkout com cartão iniciando em 4 -> 200 {"msg":"Sucesso","enrollment_id":2}
POST /api/checkout com cartão iniciando em 5 -> 400 Pagamento recusado
DELETE /api/users/1 -> 200 Usuário deletado.
```

Também registra validação estática:

```text
find src -name '*.js' -exec node -c {} \; -> passed
Focused source scan -> no runtime occurrences of admin_master, senha_super, pk_live, paymentGatewayKey, badCrypto, globalCache, Processando cartão, AppManager, or SELECT *
```

#### `code-smells-project` e `task-manager-api`

Os relatórios `code-smells-project/reports/audit-project-1.md` e `task-manager-api/reports/audit-project-3.md` registram validação por compilação Python, instalação em virtualenv temporário e smoke tests via Flask test client.

### Comportamento em stacks diferentes

No projeto Flask de e-commerce, a skill identificou problemas típicos de APIs pequenas que cresceram sem separação clara: SQL direto, controllers pesados, secrets hardcoded e acoplamento global ao banco. No projeto Express, a skill conseguiu mapear uma arquitetura centrada em uma classe única e propor divisão por controllers, services, repositories, middleware e validators. No Task Manager, a expectativa é que a skill trate uma base parcialmente organizada sem forçar reescrita total, focando nos pontos onde as fronteiras ainda estão incorretas.

## Como Executar

### Pré-requisitos

- OpenAI Codex instalado e configurado.
- Python disponível para os projetos Flask.
- Node.js e npm disponíveis para o projeto Express.
- Dependências instaladas em cada projeto antes de validar o boot.

### Disparar a skill

Comando desejado no Codex:

```text
/refactor-arch
```

Executar em cada projeto:

```bash
cd code-smells-project
codex "/refactor-arch"
```

```bash
cd ecommerce-api-legacy
codex "/refactor-arch"
```

```bash
cd task-manager-api
codex "/refactor-arch"
```

A Fase 2 deve parar antes de editar arquivos e exibir:

```text
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Responda `y` apenas quando quiser executar a refatoração.

### Validar `code-smells-project`

```bash
cd code-smells-project
pip install -r requirements.txt
python app.py
```

Em outro terminal, validar endpoints principais:

```bash
curl http://localhost:5000/health
curl http://localhost:5000/produtos
curl http://localhost:5000/usuarios
```

### Validar `ecommerce-api-legacy`

```bash
cd ecommerce-api-legacy
npm install
npm start
```

Em outro terminal:

```bash
curl http://localhost:3000/api/admin/financial-report
curl -X POST http://localhost:3000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"usr":"Ana","eml":"ana@example.com","pwd":"senha123","c_id":1,"card":"4111111111111111"}'
```

### Validar `task-manager-api`

```bash
cd task-manager-api
pip install -r requirements.txt
python seed.py
python app.py
```

Em outro terminal:

```bash
curl http://localhost:5000/health
curl http://localhost:5000/tasks
curl http://localhost:5000/users
curl http://localhost:5000/reports/summary
```

### Critérios de sucesso

- A skill detecta linguagem, framework, domínio, entrypoints e comandos de validação.
- O relatório lista findings com severidade, arquivo e linha.
- A Fase 2 pausa antes de modificar arquivos.
- Após confirmação, a refatoração separa responsabilidades em camadas compatíveis com MVC.
- A aplicação sobe sem erros.
- Endpoints públicos principais continuam respondendo.
- O relatório final registra validações executadas, riscos restantes e pendências.
