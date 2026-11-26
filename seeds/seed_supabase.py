"""Script de inicialização, criação de tabelas e reset do banco de dados (Seed).

Execução padrão (limpa dados antigos e cria o Técnico-Admin inicial):
    python seeds/seed_supabase.py

Execução com carga demonstrativa de teste:
    python seeds/seed_supabase.py --demo
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

# Garante acesso aos módulos da aplicação
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.reference_data import Room, Category
from app.models.ticket import Ticket
from app.models.ticket_history import TicketHistory
from app.utils.cache import invalidate_app_cache


def reset_and_seed_admin():
    """Limpa chamados e usuários, deixando apenas o Técnico-Administrador inicial."""
    app = create_app()

    with app.app_context():
        print("Garantindo estrutura de tabelas no banco de dados...")
        db.create_all()

        print("Limpando chamados anteriores e histórico de atendimento...")
        try:
            db.session.execute(db.text("DELETE FROM ticket_history"))
            db.session.execute(db.text("DELETE FROM tickets"))
            db.session.execute(db.text("DELETE FROM users"))
            db.session.commit()
            print("Tabelas tickets, ticket_history e users limpas com sucesso.")
        except Exception as e:
            db.session.rollback()
            print(f"Nota na limpeza de tabelas: {e}")

        # Reinicia sequências no PostgreSQL para IDs começarem do 1 novamente
        try:
            db.session.execute(db.text("ALTER SEQUENCE IF EXISTS tickets_id_seq RESTART WITH 1;"))
            db.session.execute(db.text("ALTER SEQUENCE IF EXISTS ticket_history_id_seq RESTART WITH 1;"))
            db.session.execute(db.text("ALTER SEQUENCE IF EXISTS users_id_seq RESTART WITH 1;"))
            db.session.commit()
        except Exception:
            db.session.rollback()

        # 1. Salas e Laboratórios
        if Room.query.count() == 0:
            print("Cadastrando salas e laboratórios...")
            rooms_data = [Room(nome=f"Sala {i}", categoria="sala_aula") for i in range(1, 16)]
            rooms_data += [Room(nome=f"Laboratório {i}", categoria="lab_maker") for i in range(1, 6)]
            rooms_data.append(Room(nome="Sala Maker", categoria="lab_maker"))
            rooms_data.append(Room(nome="Secretaria", categoria="administrativo"))
            db.session.bulk_save_objects(rooms_data)
            db.session.commit()
            print(f"{len(rooms_data)} salas e laboratórios cadastrados.")
        else:
            print(f"Salas e laboratórios já presentes ({Room.query.count()}).")

        # 2. Categorias Técnicas
        if Category.query.count() == 0:
            print("Cadastrando categorias técnicas...")
            categories_data = [
                Category(nome="Infraestrutura de Rede", descricao="Problemas de Wi-Fi, cabeamento e portas de switch"),
                Category(nome="Problemas de Periféricos", descricao="Teclados, mouses, monitores e impressoras"),
                Category(nome="Hardware Interno", descricao="Fonte, memória RAM, placa-mãe ou componentes danificados"),
                Category(nome="Software / Sistema Operacional", descricao="Instalação de programas, lentidão e configurações"),
                Category(nome="Projetor / Multimídia", descricao="Projetores de teto, caixas de som e adaptadores HDMI"),
                Category(nome="Outros", descricao="Demandas diversas não contempladas nas categorias padrão")
            ]
            db.session.bulk_save_objects(categories_data)
            db.session.commit()
            print(f"{len(categories_data)} categorias técnicas cadastradas.")
        else:
            print(f"Categorias já presentes ({Category.query.count()}).")

        # 3. Usuário Técnico-Administrador inicial
        admin_email = "vinicius.tectnico@tecnicoteste.com"
        admin = User(
            nome="Vinicius",
            email=admin_email,
            perfil="admin",
            cargo="Técnico-Administrador",
            ativo=True,
            avatar_cor="#8B5CF6"
        )
        admin.set_password("123")
        db.session.add(admin)
        db.session.commit()

        invalidate_app_cache()

        print("\n" + "=" * 60)
        print("BANCO DE DADOS RESETADO COM SUCESSO!")
        print(f"- Total de chamados: {Ticket.query.count()} (iniciando do zero)")
        print(f"- Usuário Admin: {admin.nome} ({admin.email})")
        print(f"- Senha padrão: 123")
        print(f"- Perfil: Técnico-Administrador (pode atribuir e gerenciar usuários)")
        print("=" * 60)


def seed_demo():
    """Popula com dados demonstrativos completos para testes rápidos."""
    reset_and_seed_admin()
    app = create_app()

    with app.app_context():
        print("Populando dados demonstrativos adicionais...")
        ana = User(
            nome="Ana Silva",
            email="ana.silva@etec.sp.gov.br",
            perfil="professor",
            cargo="Professora de Informática",
            ativo=True,
            avatar_cor="#3B82F6"
        )
        ana.set_password("123")

        carlos = User(
            nome="Carlos Souza",
            email="carlos.souza@etec.sp.gov.br",
            perfil="tecnico",
            cargo="Técnico de Suporte",
            ativo=True,
            avatar_cor="#10B981"
        )
        carlos.set_password("123")

        db.session.add_all([ana, carlos])
        db.session.commit()

        t1 = Ticket(
            numero="0001",
            titulo="Computador não liga",
            descricao="O computador não liga no laboratório 1.",
            sala="Laboratório 1",
            maquina="PC 04",
            status="Em andamento",
            solicitante_id=ana.id,
            tecnico_id=carlos.id
        )
        db.session.add(t1)
        db.session.commit()

        h1 = TicketHistory(ticket_id=t1.id, usuario_id=ana.id, evento=f"Chamado aberto por {ana.nome}")
        h2 = TicketHistory(ticket_id=t1.id, usuario_id=carlos.id, evento=f"Chamado assumido por {carlos.nome}")
        db.session.add_all([h1, h2])
        db.session.commit()

        invalidate_app_cache()
        print("Dados de demonstração populados com sucesso.")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        seed_demo()
    else:
        reset_and_seed_admin()
