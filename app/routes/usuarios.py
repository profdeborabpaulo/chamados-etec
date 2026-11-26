"""Blueprint de gestão institucional de usuários (Professores e Técnicos)."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models.user import User
from app.utils.decorators import admin_required
from app.utils.cache import invalidate_app_cache

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')


@usuarios_bp.route('/')
@admin_required
def lista():
    """Listagem de todos os usuários institucionais cadastrados."""
    users = User.query.order_by(User.nome.asc()).all()

    return render_template(
        'usuarios/lista.html',
        active_page='usuarios',
        users=users
    )


@usuarios_bp.route('/novo', methods=['POST'])
@admin_required
def novo():
    """Cadastro de novo usuário institucional com hash criptográfico."""
    nome = request.form.get('nome', '').strip()
    email = request.form.get('email', '').strip().lower()
    perfil = request.form.get('perfil', 'professor')
    cargo = request.form.get('cargo', '').strip()
    senha = request.form.get('senha', '').strip() or '123'

    if not nome or not email:
        flash("Preencha nome e e-mail institucional para cadastrar.", "error")
        return redirect(url_for('usuarios.lista'))

    # Validação de unicidade de e-mail institucional
    usuario_existente = User.query.filter_by(email=email).first()
    if usuario_existente:
        flash("Já existe um usuário institucional cadastrado com este e-mail.", "error")
        return redirect(url_for('usuarios.lista'))

    avatar_cores = {
        'professor': '#3B82F6',
        'tecnico': '#10B981',
        'admin': '#8B5CF6'
    }

    novo_usuario = User(
        nome=nome,
        email=email,
        perfil=perfil,
        cargo=cargo or ("Professor" if perfil == "professor" else "Técnico de Suporte"),
        ativo=True,
        avatar_cor=avatar_cores.get(perfil, '#3B82F6')
    )
    novo_usuario.set_password(senha)

    db.session.add(novo_usuario)
    db.session.commit()

    # Invalida cache de técnicos caso um novo técnico tenha sido cadastrado
    invalidate_app_cache()

    flash(f"Usuário institucional {nome} cadastrado com sucesso!", "success")
    return redirect(url_for('usuarios.lista'))
