"""Módulo central de modelos SQLAlchemy da aplicação."""

from app.models.user import User
from app.models.reference_data import Room, Category
from app.models.ticket import Ticket
from app.models.ticket_history import TicketHistory

__all__ = [
    'User',
    'Room',
    'Category',
    'Ticket',
    'TicketHistory'
]
