# Sistema de Chamados ETEC

Plataforma web desenvolvida para a centralização, organização e atendimento de solicitações de suporte técnico de informática na unidade escolar da **Etec Antonio Furlan**.

---

## Informações Acadêmicas

- **Instituição:** Etec Antonio Furlan
- **Curso:** Informática Para Internet
- **Turma:** Turma B
- **Professora Responsável:** Débora ([@profdeborapaulo](https://github.com/profdeborapaulo))
- **Integrantes da Equipe:**
  - Lucas Olegário
  - Marianna Fernanda
  - Vinicius Belloni
  - Vinicius Santos

---

## Sobre o Projeto

O sistema foi concebido para solucionar o gargalo histórico da comunicação de problemas técnicos via WhatsApp, fornecendo um fluxo transparente, rastreável e ordenado por fila de chegada, garantindo:
1. **Atendimento Justo:** Chamados organizados cronologicamente e por criticidade.
2. **Prevenção de Duplicidade:** Mecanismo de atribuição formal ("Em andamento") que impede múltiplos técnicos atuando sobre a mesma máquina.
3. **Histórico e Auditoria:** Registro permanente de todas as intervenções realizadas nos equipamentos e dependências da instituição.
4. **Métricas para Gestão:** Coleta de tempo de atendimento em minutos e classificação rigorosa por categorias de problemas.

---

## Perfis de Acesso

- **Professor / Solicitante:** Abertura simplificada de chamados com identificação da sala e equipamento, e acompanhamento do status em tempo real.
- **Técnico-Administrador:** Visão global do painel de ocorrências, atribuição de chamados para si ou colegas, encerramento com relatório técnico e gestão de contas institucionais.

---

## Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Framework Web:** Flask (Application Factory & Blueprints)
- **Banco de Dados:** Supabase (PostgreSQL)
- **ORM:** SQLAlchemy (Flask-SQLAlchemy)
- **Autenticação:** Flask-Login / Werkzeug Security (Hashing de senhas)
- **Frontend:** HTML5, CSS3 estruturado com variáveis e Flexbox, JavaScript nativo e templates Jinja2.

---

## Como Executar o Projeto Localmente

### 1. Clonar ou Acessar o Diretório
```bash
cd chamados_etec
```

### 2. Configurar o Ambiente Virtual
**No Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**No Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Executar a Aplicação
```bash
python run.py
```

Acesse o sistema no navegador através do endereço:  
`http://127.0.0.1:5000/`

---

## Credenciais de Teste para Avaliação

| Perfil | E-mail Institucional | Senha |
|---|---|---|
| **Professor** | `ana.silva@etec.sp.gov.br` | `123` |
| **Técnico de TI** | `carlos.souza@etec.sp.gov.br` | `123` |

*A tela de login também conta com botões de atalho rápido (Quick Login) para testes imediatos de cada perfil sem necessidade de digitação.*
