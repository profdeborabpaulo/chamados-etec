"""Modelo de histórico e auditoria de ações nos chamados (Linha do Tempo)."""

from datetime import datetime, timezone
from app.extensions import db


class TicketHistory(db.Model):
    """Representa uma entrada na linha do tempo de um chamado."""
    __tablename__ = 'ticket_history'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(
        db.Integer, 
        db.ForeignKey('tickets.id', ondelete='CASCADE'), 
        nullable=False, 
        index=True
    )
    usuario_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete='SET NULL'), 
        nullable=True, 
        index=True
    )
    evento = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Relacionamento com usuário que realizou a ação
    usuario = db.relationship('User', foreign_keys=[usuario_id])

    @property
    def data(self) -> str:
        """Data abreviada para exibição na linha do tempo (ex: 12/06 10:24)."""
        return self.created_at.strftime('%d/%m %H:%M') if self.created_at else ''

    @property
    def data_completa(self) -> str:
        """Data completa para exibição formal (ex: 12/06/2026 - 10:24)."""
        return self.created_at.strftime('%d/%m/%Y - %H:%M') if self.created_at else ''

    def __getitem__(self, item: str):
        """Acesso estilo dict (hist['data']) para retrocompatibilidade."""
        return getattr(self, item)

    def __repr__(self) -> str:
        return f"<TicketHistory {self.id}: Ticket #{self.ticket_id} - {self.evento[:30]}>"
