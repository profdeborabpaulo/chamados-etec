"""Blueprint de chamados com persistência relacional, fila dinâmica e controle de acesso por perfil."""

from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.ticket import Ticket
from app.models.ticket_history import TicketHistory
from app.models.user import User
from app.utils.decorators import tecnico_required, admin_required
from app.utils.cache import get_cached_room_categories, get_cached_categories, get_cached_tecnicos

chamados_bp = Blueprint('chamados', __name__, url_prefix='/chamados')


def _calcular_posicoes_fila(tickets):
    """Calcula dinamicamente a posição na fila (1, 2, 3...) para chamados ativos."""
    chamados_ativos = Ticket.query.filter(
        Ticket.status.in_(['Aberto', 'Em andamento'])
    ).order_by(Ticket.id.asc()).all()

    queue_map = {t.id: idx + 1 for idx, t in enumerate(chamados_ativos)}

    for t in tickets:
        t.posicao_fila = queue_map.get(t.id)

    return tickets


@chamados_bp.route('/')
@login_required
def index():
    """Redireciona para a tela adequada ao perfil logado."""
    if current_user.is_professor:
        return redirect(url_for('chamados.meus_chamados'))
    return redirect(url_for('chamados.lista'))


@chamados_bp.route('/lista')
@login_required
def lista():
    """Visão global de todos os chamados da unidade escolar (Técnicos e Admins)."""
    if current_user.is_professor:
        return redirect(url_for('chamados.meus_chamados'))

    status_filter = request.args.get('status', 'todos')
    search_term = request.args.get('busca', '').strip()
    ordem = request.args.get('ordem', 'recentes')
    data_filtro = request.args.get('data', '').strip()

    query = Ticket.query

    status_map = {
        'em-andamento': 'Em andamento',
        'em andamento': 'Em andamento',
        'resolvidos': 'Resolvido',
        'resolvido': 'Resolvido',
        'pendentes': 'Pendente',
        'pendente': 'Pendente',
        'aberto': 'Aberto',
        'abertos': 'Aberto'
    }

    if status_filter and status_filter.lower() != 'todos':
        normalized_status = status_map.get(status_filter.lower(), status_filter)
        query = query.filter(Ticket.status == normalized_status)

    if data_filtro:
        try:
            target_date = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Ticket.created_at) == target_date)
        except ValueError:
            pass

    if search_term:
        term = f"%{search_term}%"
        query = query.outerjoin(User, Ticket.solicitante_id == User.id).filter(
            db.or_(
                Ticket.titulo.ilike(term),
                Ticket.descricao.ilike(term),
                Ticket.sala.ilike(term),
                Ticket.numero.ilike(term),
                User.nome.ilike(term)
            )
        )

    # Ordenação dos resultados
    if ordem == 'antigos':
        query = query.order_by(Ticket.id.asc())
    else:
        query = query.order_by(Ticket.id.desc())

    tickets = query.all()
    tickets = _calcular_posicoes_fila(tickets)
    technicians = get_cached_tecnicos()

    return render_template(
        'chamados/lista.html',
        active_page='chamados',
        is_meus_chamados=False,
        tickets=tickets,
        technicians=technicians,
        current_status=status_filter,
        search_term=search_term,
        current_ordem=ordem,
        current_data=data_filtro
    )


@chamados_bp.route('/meus-chamados')
@login_required
def meus_chamados():
    """Visão restrita aos chamados do professor/solicitante autenticado."""
    status_filter = request.args.get('status', 'todos')
    search_term = request.args.get('busca', '').strip()
    ordem = request.args.get('ordem', 'recentes')
    data_filtro = request.args.get('data', '').strip()

    query = Ticket.query.filter(Ticket.solicitante_id == current_user.id)

    status_map = {
        'em-andamento': 'Em andamento',
        'em andamento': 'Em andamento',
        'resolvidos': 'Resolvido',
        'resolvido': 'Resolvido',
        'pendentes': 'Pendente',
        'pendente': 'Pendente',
        'aberto': 'Aberto',
        'abertos': 'Aberto'
    }

    if status_filter and status_filter.lower() != 'todos':
        normalized_status = status_map.get(status_filter.lower(), status_filter)
        query = query.filter(Ticket.status == normalized_status)

    if data_filtro:
        try:
            target_date = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Ticket.created_at) == target_date)
        except ValueError:
            pass

    if search_term:
        term = f"%{search_term}%"
        query = query.filter(
            db.or_(
                Ticket.titulo.ilike(term),
                Ticket.descricao.ilike(term),
                Ticket.sala.ilike(term),
                Ticket.numero.ilike(term)
            )
        )

    if ordem == 'antigos':
        query = query.order_by(Ticket.id.asc())
    else:
        query = query.order_by(Ticket.id.desc())

    tickets = query.all()
    tickets = _calcular_posicoes_fila(tickets)

    return render_template(
        'chamados/lista.html',
        active_page='meus_chamados',
        is_meus_chamados=True,
        tickets=tickets,
        technicians=[],
        current_status=status_filter,
        search_term=search_term,
        current_ordem=ordem,
        current_data=data_filtro
    )


@chamados_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def criar():
    """Tela e processamento de abertura de chamado pelo solicitante."""
    room_categories = get_cached_room_categories()

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip() or current_user.nome
        descricao = request.form.get('descricao', '').strip()
        sala = request.form.get('sala', '').strip()
        maquina = request.form.get('maquina', '').strip()

        if not descricao or not sala:
            flash("Por favor, preencha todos os campos obrigatórios (*).", "error")
            return render_template(
                'chamados/criar.html',
                active_page='criar_chamado',
                room_categories=room_categories,
                form_data=request.form
            )

        palavras = descricao.split()
        titulo = " ".join(palavras[:5]) if len(palavras) >= 3 else "Solicitação de Suporte"
        if len(titulo) > 140:
            titulo = titulo[:137] + "..."

        last_ticket = Ticket.query.order_by(Ticket.id.desc()).first()
        proximo_id = (last_ticket.id + 1) if last_ticket else 1
        numero_formatado = f"{proximo_id:04d}"

        novo_chamado = Ticket(
            numero=numero_formatado,
            titulo=titulo,
            descricao=descricao,
            sala=sala,
            maquina=maquina if maquina else None,
            status='Aberto',
            solicitante_id=current_user.id
        )

        db.session.add(novo_chamado)
        db.session.flush()

        evento_inicial = TicketHistory(
            ticket_id=novo_chamado.id,
            usuario_id=current_user.id,
            evento=f"Chamado aberto por {current_user.nome}"
        )
        db.session.add(evento_inicial)
        db.session.commit()

        flash(f"Chamado #{novo_chamado.numero} criado com sucesso! A equipe técnica já foi notificada.", "success")

        if current_user.is_professor:
            return redirect(url_for('chamados.meus_chamados'))
        return redirect(url_for('chamados.lista'))

    return render_template(
        'chamados/criar.html',
        active_page='criar_chamado',
        room_categories=room_categories,
        form_data=None
    )


@chamados_bp.route('/atribuir', methods=['POST'])
@admin_required
def atribuir():
    """Atribui o chamado a um técnico. Exclusivo para Técnico-Administrador."""
    ticket_id = request.form.get('ticket_id')
    assign_type = request.form.get('assign_type', 'me')

    if assign_type == 'me':
        tecnico_id = current_user.id
    else:
        tecnico_id = request.form.get('tecnico_id')

    if not ticket_id or not tecnico_id:
        flash("Selecione um técnico válido para atribuir o chamado.", "error")
        return redirect(url_for('chamados.lista'))

    ticket = Ticket.query.get(int(ticket_id))
    tecnico = User.query.get(int(tecnico_id))

    if not ticket or not tecnico:
        flash("Chamado ou técnico não encontrado.", "error")
        return redirect(url_for('chamados.lista'))

    ticket.tecnico_id = tecnico.id
    ticket.status = 'Em andamento'

    if tecnico.id == current_user.id:
        msg_evento = f"Chamado assumido por {tecnico.nome} (Em andamento)"
    else:
        msg_evento = f"Chamado atribuído para {tecnico.nome} pelo Administrador {current_user.nome}"

    historico = TicketHistory(
        ticket_id=ticket.id,
        usuario_id=current_user.id,
        evento=msg_evento
    )
    db.session.add(historico)
    db.session.commit()

    flash(f"Chamado #{ticket.numero} atribuído para {tecnico.nome} e marcado como 'Em andamento'.", "success")
    return redirect(url_for('chamados.lista'))


@chamados_bp.route('/<int:ticket_id>/visualizar')
@login_required
def detalhe(ticket_id):
    """Exibe a visualização detalhada do chamado e a sua linha do tempo cronológica."""
    ticket = Ticket.query.get_or_404(ticket_id)

    if current_user.is_professor and ticket.solicitante_id != current_user.id:
        flash("Você só tem permissão para visualizar chamados abertos por você.", "warning")
        return redirect(url_for('chamados.meus_chamados'))

    # Se estiver aberto ou em andamento, calcula a posição atual na fila
    if ticket.status in ('Aberto', 'Em andamento'):
        anteriores = Ticket.query.filter(
            Ticket.status.in_(['Aberto', 'Em andamento']),
            Ticket.id <= ticket.id
        ).count()
        ticket.posicao_fila = anteriores
    else:
        ticket.posicao_fila = None

    return render_template(
        'chamados/detalhe.html',
        active_page='chamados' if current_user.is_tecnico else 'meus_chamados',
        ticket=ticket
    )


@chamados_bp.route('/<int:ticket_id>/finalizar', methods=['GET', 'POST'])
@tecnico_required
def finalizar(ticket_id):
    """Formulário de fechamento técnico do chamado."""
    ticket = Ticket.query.get_or_404(ticket_id)

    # Regra de negócio: Técnico só pode finalizar chamados atribuídos a ele (Admin pode finalizar qualquer um)
    if not current_user.is_admin and ticket.tecnico_id != current_user.id:
        flash("Você só tem permissão para finalizar chamados atribuídos a você.", "warning")
        return redirect(url_for('chamados.detalhe', ticket_id=ticket.id))

    categories = get_cached_categories()

    if request.method == 'POST':
        solucao = request.form.get('solucao', '').strip()
        tempo_minutos_raw = request.form.get('tempo_minutos', '').strip()
        categoria = request.form.get('categoria', '').strip()
        status_conclusao = request.form.get('status_conclusao', 'Resolvido')
        motivo_pendente = request.form.get('motivo_pendente', '').strip()

        if not solucao or not tempo_minutos_raw or not categoria:
            flash("Preencha todos os campos obrigatórios para concluir o chamado.", "error")
            return render_template(
                'chamados/finalizar.html',
                active_page='chamados',
                ticket=ticket,
                categories=categories,
                form_data=request.form
            )

        if status_conclusao == 'Pendente' and not motivo_pendente:
            flash("Para chamados pendentes, o motivo deve ser informado.", "error")
            return render_template(
                'chamados/finalizar.html',
                active_page='chamados',
                ticket=ticket,
                categories=categories,
                form_data=request.form
            )

        try:
            tempo_minutos = int(tempo_minutos_raw)
        except ValueError:
            tempo_minutos = 0

        ticket.solucao = solucao
        ticket.tempo_minutos = tempo_minutos
        ticket.categoria = categoria
        ticket.status = status_conclusao
        ticket.motivo_pendente = motivo_pendente if status_conclusao == 'Pendente' else None
        ticket.data_finalizacao = datetime.now(timezone.utc)

        if status_conclusao == 'Resolvido':
            evento = f"Chamado resolvido por {current_user.nome} ({tempo_minutos} min - {categoria})"
        else:
            evento = f"Chamado marcado como Pendente por {current_user.nome}. Motivo: {motivo_pendente}"

        historico = TicketHistory(
            ticket_id=ticket.id,
            usuario_id=current_user.id,
            evento=evento
        )
        db.session.add(historico)
        db.session.commit()

        flash(f"Chamado #{ticket.numero} finalizado com status '{status_conclusao}'!", "success")
        return redirect(url_for('chamados.detalhe', ticket_id=ticket.id))

    return render_template(
        'chamados/finalizar.html',
        active_page='chamados',
        ticket=ticket,
        categories=categories,
        form_data=None
    )
