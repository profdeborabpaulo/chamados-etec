# PDD (Project Documentation Description) - Sistema de Chamados ETEC

## 1. Visão Geral do Projeto
O Sistema de Chamados ETEC é uma plataforma web desenvolvida para otimizar e gerenciar as solicitações de suporte técnico de informática dentro da instituição escolar. O objetivo principal é substituir o atual modelo informal (via mensagens de WhatsApp) por uma plataforma centralizada, auditável e organizada.

## 2. Problema e Solução
- **Problema atual:** Professores e funcionários relatam problemas aos técnicos via WhatsApp. O atendimento frequentemente ocorre por proximidade física da sala em que o técnico se encontra, em vez de ordem de prioridade ou tempo de espera, causando ineficiência e possíveis esquecimentos.
- **Solução proposta:** Uma plataforma onde professores registram as ocorrências em um formulário estruturado. A equipe técnica tem uma visão unificada dos chamados, podendo atribuir responsáveis, registrar o status de atendimento, controlar o tempo gasto e categorizar as ocorrências para geração de dados e histórico.

---

## 3. Stack Tecnológico e Arquitetura
- **Linguagem:** Python 3.10+
- **Framework Web:** Flask (com arquitetura Application Factory e Blueprints modulares)
- **Banco de Dados:** Supabase (PostgreSQL em nuvem, com fallback resiliente para SQLite)
- **Driver de Conexão:** psycopg2-binary
- **ORM:** SQLAlchemy (via Flask-SQLAlchemy)
- **Autenticação e Sessão:** Flask-Login com hashes de senha seguros via werkzeug.security (scrypt / pbkdf2)
- **Variáveis de Ambiente:** python-dotenv (carregando arquivo .env protegido)
- **Otimização e Performance:**
  - **Índices de Banco:** Colunas de consulta frequente indexadas no PostgreSQL (`status`, `solicitante_id`, `tecnico_id`, `created_at`, `email`, `sala`, `numero` e `ticket_id`).
  - **Cache em Memória:** Módulo pythonic thread-safe (`app/utils/cache.py`) para evitar consultas repetitivas de dados estáticos (salas, categorias e técnicos), com invalidação automática em mutações.
- **Frontend:** HTML5 semântico, CSS3 com design tokens institucionais da ETEC e JavaScript nativo (renderizado com Jinja2).

---

## 4. Perfis de Usuários e Níveis de Permissão

O sistema implementa três níveis hierárquicos de acesso com controle funcional:

### 4.1. Professor / Funcionário (Solicitante)
- **Objetivo:** Registro e acompanhamento de problemas em salas e laboratórios.
- **Permissões:**
  - Criar novos chamados com seleção estruturada de ambientes em duas etapas (tipo de espaço e sala específica).
  - Acessar a tela "Meus Chamados" (filtrada estritamente para suas próprias ocorrências).
  - Visualizar a linha do tempo e status dos seus chamados.
  - Bloqueado para: acessar chamados de terceiros, atribuir chamados ou gerenciar usuários.

### 4.2. Técnico (Suporte Operacional)
- **Objetivo:** Atendimento técnico das demandas escolares.
- **Permissões:**
  - Visualizar a lista unificada de todos os chamados da escola.
  - Criar chamados (ex: manutenção preventiva identificada espontaneamente).
  - Visualizar os detalhes completos e linha do tempo de qualquer chamado.
  - Finalizar chamados atribuídos a ele, preenchendo o formulário de solução técnica.
  - Bloqueado para: atribuir chamados a colegas e acessar a tela de gestão de usuários.

### 4.3. Técnico-Administrador (Admin)
- **Objetivo:** Gestão operacional do suporte e administração institucional.
- **Permissões:**
  - Todas as permissões do perfil Técnico.
  - **Atribuição Exclusiva:** Apenas o Técnico-Admin possui permissão para designar técnicos responsáveis pelos chamados (através do botão e modal de atribuição na listagem).
  - **Gestão de Usuários Exclusiva:** Criar e listar usuários institucionais (Professores e Técnicos) com validação de unicidade de e-mail e geração de hash.
  - Finalizar qualquer chamado do sistema.

---

## 5. Regras de Negócio e Fluxos de Atendimento

### 5.1. Fila Dinâmica de Chamados Abertos vs. Protocolo Permanente de Histórico
Para evitar identificadores astronômicos no dia a dia da escola e manter clareza na fila de trabalho, o sistema opera com dois conceitos complementares:

1. **Posição na Fila Dinâmica (`Fila #1`, `Fila #2`...):**
   - Aplicada exclusivamente aos chamados com status ativos (`Aberto` ou `Em andamento`).
   - Calculada em tempo real pela ordem de chegada das pendências não resolvidas.
   - Caso a equipe técnica zere todos os chamados ativos, o próximo chamado aberto volta automaticamente a receber a posição `Fila #1`.
2. **Protocolo Permanente (`#0001`, `#0002`...):**
   - Número sequencial único gerado no momento da criação e gravado no banco de dados.
   - Mantido permanentemente na linha do tempo e nos chamados finalizados (`Resolvido` ou `Pendente`) para auditoria histórica e relatórios de patrimônio.

### 5.2. Criação de Chamado
Dados coletados no formulário:
- Solicitante (preenchido automaticamente a partir da sessão ativa).
- Tipo de Ambiente (Salas de Aula 1 a 15, Laboratórios 1 a 5 e Sala Maker, Administrativo / Secretaria).
- Sala / Espaço Específico.
- Identificação da Máquina (Opcional, ex: "PC 04").
- Descrição detalhada do problema.
- Gera automaticamente o primeiro evento de auditoria na linha do tempo.

### 5.3. Atribuição de Chamado (Exclusivo Técnico-Admin)
- O Técnico-Admin seleciona o chamado na lista e abre o modal de atribuição.
- Define o técnico responsável (ou assume o chamado).
- O chamado é atualizado para status `Em andamento` e registra o evento na linha do tempo.

### 5.4. Finalização Técnica
Para concluir um chamado, o técnico preenche:
- **Ação tomada (Solução):** O que foi feito ou peças utilizadas.
- **Tempo necessário:** Tempo gasto no atendimento (em minutos).
- **Categoria técnica:** Classificação (Infraestrutura de Rede, Periféricos, Hardware Interno, Software, Projetor/Multimídia, Outros).
- **Status final:**
  - *Resolvido.*
  - *Pendente:* Caso a máquina continue inoperante, exigindo justificativa obrigatória.
- Registra a data de encerramento e o evento de finalização no histórico.

### 5.5. Filtros e Ordenação da Listagem
A visualização global de chamados permite:
- **Filtro por Status:** Todos, Em andamento, Resolvidos, Pendentes.
- **Busca Textual:** Pesquisa dinâmica por descrição, sala, número ou solicitante.
- **Filtro por Data:** Seletor para listar chamados criados em uma data específica.
- **Ordenação Bidirecional:**
  - *Mais recentes primeiro* (LIFO - padrão).
  - *Mais antigos primeiro* (FIFO - prioridade de atendimento aos chamados em espera há mais tempo).

---

## 6. Modelagem de Dados Relacional (Entidades)

### 6.1. `User` (Tabela `users`)
- `id` (PK, Integer)
- `nome` (String 150)
- `email` (String 150, Unique, Index)
- `senha_hash` (String 255)
- `perfil` (String 30, Index: 'professor', 'tecnico', 'admin')
- `cargo` (String 100)
- `ativo` (Boolean, Default True)
- `avatar_cor` (String 20)
- `created_at` / `updated_at` (DateTime UTC)

### 6.2. `Ticket` (Tabela `tickets`)
- `id` (PK, Integer)
- `numero` (String 20, Unique, Index - Protocolo permanente)
- `titulo` (String 150)
- `descricao` (Text)
- `sala` (String 100, Index)
- `maquina` (String 50, Opcional)
- `status` (String 30, Index: 'Aberto', 'Em andamento', 'Resolvido', 'Pendente')
- `solicitante_id` (FK `users.id`, Index)
- `tecnico_id` (FK `users.id`, Index, Nullable)
- `solucao` (Text, Nullable)
- `tempo_minutos` (Integer, Nullable)
- `categoria` (String 100, Nullable)
- `motivo_pendente` (Text, Nullable)
- `created_at` (DateTime UTC, Index)
- `data_finalizacao` (DateTime UTC, Nullable)

### 6.3. `TicketHistory` (Tabela `ticket_history`)
- `id` (PK, Integer)
- `ticket_id` (FK `tickets.id`, Index)
- `usuario_id` (FK `users.id`, Index, Nullable)
- `evento` (Text)
- `created_at` (DateTime UTC, Index)

### 6.4. `Room` (Tabela `rooms`)
- `id` (PK, Integer)
- `nome` (String 100, Unique, Index)
- `categoria` (String 50, Index: 'sala_aula', 'lab_maker', 'administrativo')
- `created_at` (DateTime UTC)

### 6.5. `Category` (Tabela `categories`)
- `id` (PK, Integer)
- `nome` (String 100, Unique, Index)
- `descricao` (Text, Nullable)
- `ativo` (Boolean, Default True, Index)
- `created_at` (DateTime UTC)

---

## 7. Estrutura de Arquivos da Aplicação

```
chamados_etec/
├── app/
│   ├── __init__.py           # Application Factory e registro de Blueprints
│   ├── extensions.py         # Instâncias de db (SQLAlchemy) e login_manager
│   ├── models/               # Modelos relacionais com índices
│   │   ├── __init__.py
│   │   ├── user.py           # Model User e permissões de perfil
│   │   ├── ticket.py         # Model Ticket com relacionamentos e properties
│   │   ├── ticket_history.py # Model TicketHistory para linha do tempo
│   │   └── reference_data.py # Models Room e Category
│   ├── routes/               # Blueprints com controle de acesso
│   │   ├── __init__.py
│   │   ├── auth.py           # Login, logout e quick-login por perfil
│   │   ├── chamados.py       # Fluxo de chamados, filtros, ordenação e atribuição
│   │   └── usuarios.py       # Gestão exclusiva de usuários pelo Técnico-Admin
│   ├── static/
│   │   ├── css/style.css     # Estilos institucionais da ETEC
│   │   ├── img/              # Logos oficiais ETEC e Centro Paula Souza
│   │   └── js/main.js        # Modais e validações dinâmicas
│   ├── templates/            # Templates Jinja2
│   │   ├── base.html         # Sidebar adaptativa por perfil
│   │   ├── auth/             # Telas de login institucional
│   │   ├── chamados/         # Lista, criação, detalhes e finalização
│   │   └── usuarios/         # Painel de usuários
│   └── utils/
│       ├── __init__.py
│       ├── cache.py          # Cache em memória com invalidação automática
│       └── decorators.py     # Decoradores @tecnico_required e @admin_required
├── seeds/
│   └── seed_supabase.py      # Script de carga inicial e reset do banco
├── .env.example              # Exemplo de variáveis de ambiente
├── .env                      # Credenciais reais de conexão (ignorado no Git)
├── config.py                 # Configurações de ambiente e pool de conexões
├── requirements.txt          # Dependências do projeto
└── run.py                    # Ponto de entrada da aplicação
```

---

## 8. Inicialização e Carga do Banco de Dados

### 8.1. Script de Reset (`seeds/seed_supabase.py`)
Para preparar o banco para demonstração a partir do zero:
```bash
python seeds/seed_supabase.py
```
- Esvazia tabelas de usuários e chamados anteriores.
- Garante o cadastro das 22 salas da ETEC e das 6 categorias técnicas.
- Cadastra exclusivamente a conta de Técnico-Administrador inicial:
  - **E-mail:** `vinicius.tectnico@tecnicoteste.com`
  - **Senha:** `123`
  - **Perfil:** `admin` (Técnico-Administrador)
  - **Total de chamados iniciais:** 0 chamados.

### 8.2. Execução do Servidor
```bash
python run.py
```
Disponível localmente em `http://127.0.0.1:5000/`.

---

## 9. Status do Roadmap

- [x] Configuração inicial do ambiente virtual e dependências instaladas.
- [x] Arquitetura com Application Factory e Blueprints modulares.
- [x] Identidade visual institucional refinada (paleta ETEC, botões encorpados, cards confortáveis).
- [x] Seleção de ambientes em duas etapas (tipo de sala + ambiente específico).
- [x] Migração de mock em memória para persistência no Supabase (PostgreSQL).
- [x] Criptografia de senhas com hash e controle de sessão via Flask-Login.
- [x] Criação de modelos relacionais com índices de performance.
- [x] Sistema de cache em memória pythonic para salas, categorias e técnicos com invalidação.
- [x] Implementação de 3 perfis funcionais: Professor, Técnico e Técnico-Administrador.
- [x] Regra de atribuição exclusiva para Técnico-Administrador.
- [x] Regra de gestão de usuários exclusiva para Técnico-Administrador.
- [x] Fila dinâmica de chamados ativos com reinício automático ao zerar pendências.
- [x] Ordenação crescente/decrescente e filtro por data na listagem.
- [x] Script de reset idempotente para homologação limpa no Supabase.
- [x] Testes de integração ponta a ponta cobrindo toda a jornada do usuário.
