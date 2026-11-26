"""
Base de dados simulada (Mock Data) para o Protótipo Navegável do Sistema de Chamados ETEC.
Permite testar todos os fluxos com persistência em memória durante a execução do servidor.
"""

from copy import deepcopy

# Usuários pré-cadastrados para teste
INITIAL_USERS = [
    {
        "id": 1,
        "nome": "Ana Silva",
        "email": "ana.silva@etec.sp.gov.br",
        "senha": "123",
        "perfil": "professor",
        "cargo": "Professora de Informática",
        "ativo": True,
        "avatar_cor": "#3B82F6"
    },
    {
        "id": 2,
        "nome": "Carlos Souza",
        "email": "carlos.souza@etec.sp.gov.br",
        "senha": "123",
        "perfil": "tecnico",
        "cargo": "Técnico de Suporte",
        "ativo": True,
        "avatar_cor": "#10B981"
    },
    {
        "id": 3,
        "nome": "Mariana Costa",
        "email": "mariana.costa@etec.sp.gov.br",
        "senha": "123",
        "perfil": "tecnico",
        "cargo": "Técnica de Redes",
        "ativo": True,
        "avatar_cor": "#8B5CF6"
    },
    {
        "id": 4,
        "nome": "Roberto Lima",
        "email": "roberto.lima@etec.sp.gov.br",
        "senha": "123",
        "perfil": "professor",
        "cargo": "Professor de Administração",
        "ativo": True,
        "avatar_cor": "#F59E0B"
    }
]

# Estrutura definitiva de salas da escola por categorias
ROOM_CATEGORIES = {
    "sala_aula": {
        "label": "Salas de Aula",
        "salas": [f"Sala {i}" for i in range(1, 16)]
    },
    "lab_maker": {
        "label": "Laboratórios / Maker",
        "salas": [f"Laboratório {i}" for i in range(1, 6)] + ["Sala Maker"]
    },
    "administrativo": {
        "label": "Administrativo",
        "salas": ["Secretaria"]
    }
}

# Lista plana consolidada com todas as salas para validação e retrocompatibilidade
LOCATIONS = (
    ROOM_CATEGORIES["sala_aula"]["salas"] +
    ROOM_CATEGORIES["lab_maker"]["salas"] +
    ROOM_CATEGORIES["administrativo"]["salas"]
)

# Categorias para finalização de chamados
CATEGORIES = [
    "Infraestrutura de Rede",
    "Problemas de Periféricos",
    "Hardware Interno",
    "Software / Sistema Operacional",
    "Projetor / Multimídia",
    "Outros"
]

# Chamados iniciais baseados nos mockups da apresentação (#0038 a #0042)
INITIAL_TICKETS = [
    {
        "id": 42,
        "numero": "0042",
        "titulo": "Computador não liga",
        "descricao": "O computador não liga, não aparece sinal de energia ao pressionar o botão de ligar.",
        "sala": "Laboratório 1",
        "maquina": "PC 04",
        "solicitante_id": 1,
        "solicitante_nome": "Ana Silva",
        "tecnico_id": 2,
        "tecnico_nome": "Carlos Souza",
        "status": "Em andamento",  # 'Aberto', 'Em andamento', 'Resolvido', 'Pendente'
        "data_abertura": "12/06 10:24",
        "data_completa": "12/06/2026 - 10:24",
        "historico": [
            {"data": "12/06 10:24", "evento": "Chamado aberto por Ana Silva"},
            {"data": "12/06 10:30", "evento": "Chamado assumido por Carlos Souza (Em andamento)"}
        ],
        "solucao": None,
        "tempo_minutos": None,
        "categoria": None,
        "motivo_pendente": None
    },
    {
        "id": 41,
        "numero": "0041",
        "titulo": "Impressora sem conexão",
        "descricao": "Impressora da sala de professores não responde aos comandos de impressão via rede.",
        "sala": "Sala 203",
        "maquina": "Impressora HP Laser",
        "solicitante_id": 4,
        "solicitante_nome": "Roberto Lima",
        "tecnico_id": 3,
        "tecnico_nome": "Mariana Costa",
        "status": "Em andamento",
        "data_abertura": "12/06 09:15",
        "data_completa": "12/06/2026 - 09:15",
        "historico": [
            {"data": "12/06 09:15", "evento": "Chamado aberto por Roberto Lima"},
            {"data": "12/06 09:20", "evento": "Chamado atribuído para Mariana Costa"}
        ],
        "solucao": None,
        "tempo_minutos": None,
        "categoria": None,
        "motivo_pendente": None
    },
    {
        "id": 40,
        "numero": "0040",
        "titulo": "Projetor não funciona",
        "descricao": "Lâmpada do projetor acende em vermelho e o equipamento desliga após 2 minutos.",
        "sala": "Sala 101",
        "maquina": "Projetor Epson",
        "solicitante_id": 1,
        "solicitante_nome": "Ana Silva",
        "tecnico_id": 2,
        "tecnico_nome": "Carlos Souza",
        "status": "Pendente",
        "data_abertura": "11/06 16:32",
        "data_completa": "11/06/2026 - 16:32",
        "historico": [
            {"data": "11/06 16:32", "evento": "Chamado aberto por Ana Silva"},
            {"data": "11/06 17:00", "evento": "Marcado como Pendente por Carlos Souza: Aguardando reposição da lâmpada pelo fornecedor."}
        ],
        "solucao": "Inspecionada a lâmpada, necessária troca de peça.",
        "tempo_minutos": 25,
        "categoria": "Projetor / Multimídia",
        "motivo_pendente": "Aguardando reposição de lâmpada pelo fornecedor."
    },
    {
        "id": 39,
        "numero": "0039",
        "titulo": "Rede instável",
        "descricao": "Oscilação constante na rede cabeada durante a aula no laboratório 2.",
        "sala": "Laboratório 2",
        "maquina": "",
        "solicitante_id": 1,
        "solicitante_nome": "Ana Silva",
        "tecnico_id": 2,
        "tecnico_nome": "Carlos Souza",
        "status": "Em andamento",
        "data_abertura": "11/06 14:30",
        "data_completa": "11/06/2026 - 14:30",
        "historico": [
            {"data": "11/06 14:30", "evento": "Chamado aberto por Ana Silva"},
            {"data": "11/06 14:45", "evento": "Chamado atribuído a Carlos Souza"}
        ],
        "solucao": None,
        "tempo_minutos": None,
        "categoria": None,
        "motivo_pendente": None
    },
    {
        "id": 38,
        "numero": "0038",
        "titulo": "Mouse com defeito",
        "descricao": "Botão esquerdo com clique duplo involuntário, impedindo uso normal.",
        "sala": "Sala 204",
        "maquina": "PC 02",
        "solicitante_id": 4,
        "solicitante_nome": "Roberto Lima",
        "tecnico_id": 2,
        "tecnico_nome": "Carlos Souza",
        "status": "Resolvido",
        "data_abertura": "10/06 11:03",
        "data_completa": "10/06/2026 - 11:03",
        "historico": [
            {"data": "10/06 11:03", "evento": "Chamado aberto por Roberto Lima"},
            {"data": "10/06 11:15", "evento": "Chamado concluído com status Resolvido"}
        ],
        "solucao": "Substituição do mouse por unidade reserva funcional.",
        "tempo_minutos": 15,
        "categoria": "Problemas de Periféricos",
        "motivo_pendente": None
    }
]

class MockDatabase:
    """Gerenciador central de dados em memória para o protótipo."""
    def __init__(self):
        self.users = deepcopy(INITIAL_USERS)
        self.tickets = deepcopy(INITIAL_TICKETS)
        self.locations = list(LOCATIONS)
        self.room_categories = deepcopy(ROOM_CATEGORIES)
        self.categories = list(CATEGORIES)
        self._next_ticket_id = 43
        self._next_user_id = 5

    def find_user_by_email(self, email):
        clean_email = email.strip().lower()
        for user in self.users:
            if user["email"].lower() == clean_email:
                return user
        return None

    def find_user_by_id(self, user_id):
        for user in self.users:
            if user["id"] == int(user_id):
                return user
        return None

    def get_technicians(self):
        return [u for u in self.users if u["perfil"] == "tecnico" and u["ativo"]]

    def authenticate(self, email, senha):
        user = self.find_user_by_email(email)
        if user and user["ativo"] and user["senha"] == senha:
            return user
        return None

    def get_all_tickets(self, status_filter=None, search_term=None):
        results = self.tickets
        if status_filter and status_filter.lower() != "todos":
            results = [t for t in results if t["status"].lower() == status_filter.lower()]
        
        if search_term:
            q = search_term.lower().strip()
            results = [
                t for t in results
                if q in t["titulo"].lower()
                or q in t["descricao"].lower()
                or q in t["sala"].lower()
                or q in t["solicitante_nome"].lower()
                or q in t["numero"].lower()
            ]
        return results

    def get_tickets_by_requester(self, user_id, status_filter=None):
        user_tickets = [t for t in self.tickets if t["solicitante_id"] == int(user_id)]
        if status_filter and status_filter.lower() != "todos":
            user_tickets = [t for t in user_tickets if t["status"].lower() == status_filter.lower()]
        return user_tickets

    def get_ticket_by_id(self, ticket_id):
        for t in self.tickets:
            if t["id"] == int(ticket_id):
                return t
        return None

    def create_ticket(self, titulo, descricao, sala, maquina, solicitante_user):
        new_id = self._next_ticket_id
        self._next_ticket_id += 1
        num_str = f"{new_id:04d}"
        
        new_ticket = {
            "id": new_id,
            "numero": num_str,
            "titulo": titulo or "Chamado Técnico",
            "descricao": descricao,
            "sala": sala,
            "maquina": maquina or "",
            "solicitante_id": solicitante_user["id"],
            "solicitante_nome": solicitante_user["nome"],
            "tecnico_id": None,
            "tecnico_nome": None,
            "status": "Aberto",
            "data_abertura": "Hoje",
            "data_completa": "Hoje",
            "historico": [
                {"data": "Hoje", "evento": f"Chamado #{num_str} aberto por {solicitante_user['nome']}"}
            ],
            "solucao": None,
            "tempo_minutos": None,
            "categoria": None,
            "motivo_pendente": None
        }
        self.tickets.insert(0, new_ticket)
        return new_ticket

    def assign_ticket(self, ticket_id, tecnico_id):
        ticket = self.get_ticket_by_id(ticket_id)
        tecnico = self.find_user_by_id(tecnico_id)
        if ticket and tecnico:
            ticket["tecnico_id"] = tecnico["id"]
            ticket["tecnico_nome"] = tecnico["nome"]
            ticket["status"] = "Em andamento"
            ticket["historico"].append({
                "data": "Hoje",
                "evento": f"Atribuído para {tecnico['nome']} (Status: Em andamento)"
            })
            return True
        return False

    def finish_ticket(self, ticket_id, solucao, tempo_minutos, categoria, status_final, motivo_pendente=None):
        ticket = self.get_ticket_by_id(ticket_id)
        if ticket:
            ticket["solucao"] = solucao
            ticket["tempo_minutos"] = tempo_minutos
            ticket["categoria"] = categoria
            ticket["status"] = "Resolvido" if status_final.lower() == "resolvido" else "Pendente"
            ticket["motivo_pendente"] = motivo_pendente if ticket["status"] == "Pendente" else None
            ticket["historico"].append({
                "data": "Hoje",
                "evento": f"Chamado concluído como {ticket['status']}"
            })
            return True
        return False

# Instância compartilhada em memória
db = MockDatabase()
