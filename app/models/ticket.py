"""Modelo de dados de Chamados (Tickets) com relacionamentos e propriedades formatadas."""

from datetime import datetime, timezone
from app.extensions import db


class Ticket(db.Model):
    """Representa um chamado de suporte técnico na ETEC."""
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), nullable=False, unique=True, index=True)  # Ex: '0042'
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    sala = db.Column(db.String(100), nullable=False, index=True)
    maquina = db.Column(db.String(50), nullable=True)
    status = db.Column(
        db.String(30), 
        nullable=False, 
        default='Aberto', 
        index=True
    )  # 'Aberto', 'Em andamento', 'Resolvido', 'Pendente'

    solicitante_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete='RESTRICT'), 
        nullable=False, 
        index=True
    )
    tecnico_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete='SET NULL'), 
        nullable=True, 
        index=True
    )

    solucao = db.Column(db.Text, nullable=True)
    tempo_minutos = db.Column(db.Integer, nullable=True)
    categoria = db.Column(db.String(100), nullable=True)
    motivo_pendente = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    data_finalizacao = db.Column(db.DateTime, nullable=True)

    # Relacionamentos ORM
    solicitante = db.relationship('User', foreign_keys=[solicitante_id], backref=db.backref('chamados_abertos', lazy='dynamic'))
    tecnico = db.relationship('User', foreign_keys=[tecnico_id], backref=db.backref('chamados_atendidos', lazy='dynamic'))
    historico = db.relationship('TicketHistory', backref='ticket', cascade='all, delete-orphan', order_by='TicketHistory.created_at.asc()')

    @property
    def solicitante_nome(self) -> str:
        """Nome do solicitante para exibição direta em templates."""
        return self.solicitante.nome if self.solicitante else 'Solicitante Desconhecido'

    @property
    def tecnico_nome(self) -> str:
        """Nome do técnico responsável para exibição direta em templates."""
        return self.tecnico.nome if self.tecnico else 'Não atribuído'

    @property
    def data_abertura(self) -> str:
        """Data abreviada para cards e listagens (ex: 12/06 10:24)."""
        return self.created_at.strftime('%d/%m %H:%M') if self.created_at else ''

    @property
    def data_completa(self) -> str:
        """Data completa para telas de detalhe (ex: 12/06/2026 - 10:24)."""
        return self.created_at.strftime('%d/%m/%Y - %H:%M') if self.created_at else ''

    def __getitem__(self, item: str):
        """Suporte a acesso estilo dicionário (ticket['status']) para total retrocompatibilidade."""
        return getattr(self, item)

    def __repr__(self) -> str:
        return f"<Ticket #{self.numero}: {self.titulo} [{self.status}]>"
