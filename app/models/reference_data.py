"""Modelos de dados de referência (Salas e Categorias Técnicas)."""

from datetime import datetime, timezone
from app.extensions import db


class Room(db.Model):
    """Representa uma sala, laboratório ou setor da ETEC."""
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True, index=True)
    categoria = db.Column(db.String(50), nullable=False, index=True)  # 'sala_aula', 'lab_maker', 'administrativo'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<Room {self.id}: {self.nome} ({self.categoria})>"


class Category(db.Model):
    """Representa categorias técnicas de problemas e atendimento."""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True, index=True)
    descricao = db.Column(db.Text, nullable=True)
    ativo = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self) -> str:
        return f"<Category {self.id}: {self.nome}>"
