"""Decoradores de controle de acesso simples e funcionais."""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def tecnico_required(f):
    """Garante que apenas usuários com perfil técnico ou administrador acessem a rota."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Faça login para acessar esta funcionalidade.", "warning")
            return redirect(url_for('auth.login'))
        
        if not current_user.is_tecnico:
            flash("Acesso restrito à equipe técnica e administrativa.", "danger")
            return redirect(url_for('chamados.meus_chamados'))
            
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Garante que apenas o Técnico-Administrador acesse a funcionalidade (atribuição, gestão de usuários)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Faça login para acessar esta funcionalidade.", "warning")
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash("Apenas o Técnico-Administrador tem permissão para realizar esta ação.", "danger")
            return redirect(url_for('chamados.lista'))
            
        return f(*args, **kwargs)
    return decorated_function
