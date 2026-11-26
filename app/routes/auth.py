"""Blueprint de autenticação integrada com SQLAlchemy e Flask-Login."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Redirecionamento inicial baseado no status de login."""
    if current_user.is_authenticated:
        if current_user.is_professor:
            return redirect(url_for('chamados.meus_chamados'))
        return redirect(url_for('chamados.lista'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Tela e processamento de login institucional."""
    if current_user.is_authenticated:
        if current_user.is_professor:
            return redirect(url_for('chamados.meus_chamados'))
        return redirect(url_for('chamados.lista'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')

        if not email or not senha:
            flash("Por favor, preencha todos os campos para entrar.", "error")
            return render_template('auth/login.html', email=email)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(senha):
            if not user.ativo:
                flash("Este usuário institucional está inativo. Contate o suporte.", "error")
                return render_template('auth/login.html', email=email)

            login_user(user)

            # Sincroniza chaves de sessão para retrocompatibilidade
            session['user_id'] = user.id
            session['user_nome'] = user.nome
            session['user_email'] = user.email
            session['user_perfil'] = user.perfil
            session['user_cargo'] = user.cargo
            session['user_avatar_cor'] = user.avatar_cor

            flash(f"Login realizado com sucesso! Bem-vindo(a), {user.nome}.", "success")
            
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)

            if user.is_professor:
                return redirect(url_for('chamados.meus_chamados'))
            return redirect(url_for('chamados.lista'))
        else:
            flash("E-mail institucional ou senha inválidos. Verifique os dados digitados.", "error")
            return render_template('auth/login.html', email=email)

    return render_template('auth/login.html')


@auth_bp.route('/quick-login/<role>')
def quick_login(role):
    """Atalho para testes rápidos de avaliação com um clique."""
    if role == 'admin':
        user = User.query.filter_by(email='vinicius.tectnico@tecnicoteste.com').first()
        if not user:
            user = User.query.filter_by(perfil='admin').first()
    elif role == 'tecnico':
        user = User.query.filter_by(perfil='tecnico').first()
        if not user:
            user = User.query.filter_by(perfil='admin').first()
    else:
        user = User.query.filter_by(perfil='professor').first()

    if user:
        login_user(user)

        session['user_id'] = user.id
        session['user_nome'] = user.nome
        session['user_email'] = user.email
        session['user_perfil'] = user.perfil
        session['user_cargo'] = user.cargo
        session['user_avatar_cor'] = user.avatar_cor

        next_url = request.args.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)

        perfil_label = 'Técnico-Admin' if user.is_admin else ('Técnico' if user.is_tecnico else 'Professor')
        flash(f"Entrou como {user.nome} ({perfil_label}).", "success")
        return redirect(url_for('chamados.lista' if user.is_tecnico else 'chamados.meus_chamados'))

    flash("Usuário de teste não encontrado no banco.", "error")
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    """Encerra a sessão do usuário."""
    logout_user()
    session.clear()
    flash("Você se desconectou.", "info")
    return redirect(url_for('auth.login'))
