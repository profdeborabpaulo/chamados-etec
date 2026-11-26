"""Modelo de dados de Usuários com suporte ao Flask-Login e hash criptográfico."""

from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    """Representa professores, técnicos e administradores institucionais da ETEC."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(30), nullable=False, default='professor', index=True)  # 'professor', 'tecnico', 'admin'
    cargo = db.Column(db.String(100), nullable=True)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    avatar_cor = db.Column(db.String(20), default='#3B82F6', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def set_password(self, password: str) -> None:
        """Gera hash seguro com Werkzeug."""
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Valida a senha informada contra o hash armazenado."""
        if not self.senha_hash:
            return False
        return check_password_hash(self.senha_hash, password)

    @property
    def primeiro_nome(self) -> str:
        """Retorna o primeiro nome para saudações amigáveis."""
        return self.nome.split()[0] if self.nome else ''

    @property
    def is_admin(self) -> bool:
        """Verifica se o usuário é Administrador Técnico."""
        return self.perfil == 'admin'

    @property
    def is_tecnico(self) -> bool:
        """Verifica se o usuário tem privilégio técnico ou administrativo."""
        return self.perfil in ('tecnico', 'admin')

    @property
    def is_professor(self) -> bool:
        """Verifica se o usuário é professor/solicitante."""
        return self.perfil == 'professor'

    @property
    def can_assign(self) -> bool:
        """Apenas o técnico-admin pode atribuir chamados."""
        return self.perfil == 'admin'

    @property
    def can_manage_users(self) -> bool:
        """Apenas o técnico-admin pode gerenciar e cadastrar usuários."""
        return self.perfil == 'admin'

    def __getitem__(self, item: str):
        """Permite acesso estilo dicionário (ex: user['nome']) para compatibilidade."""
        return getattr(self, item)

    def to_dict(self) -> dict:
        """Serialização para dicionário simples."""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'perfil': self.perfil,
            'cargo': self.cargo,
            'ativo': self.ativo,
            'avatar_cor': self.avatar_cor
        }

    def __repr__(self) -> str:
        return f"<User {self.id}: {self.email} ({self.perfil})>"
