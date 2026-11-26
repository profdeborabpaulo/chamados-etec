/**
 * Sistema de Chamados ETEC - Comportamentos Interativos Globais
 */

document.addEventListener('DOMContentLoaded', () => {
    initPasswordToggle();
    initAlertAutoDismiss();
});

/**
 * Alterna a visualização da senha (mostrar/ocultar) no campo de login.
 */
function initPasswordToggle() {
    const toggleBtn = document.getElementById('btnTogglePassword');
    const passwordInput = document.getElementById('senha');
    const eyeIcon = document.getElementById('eyeIcon');

    if (!toggleBtn || !passwordInput || !eyeIcon) return;

    toggleBtn.addEventListener('click', () => {
        const isPassword = passwordInput.getAttribute('type') === 'password';
        const newType = isPassword ? 'text' : 'password';
        passwordInput.setAttribute('type', newType);
        
        toggleBtn.setAttribute('aria-pressed', isPassword ? 'true' : 'false');
        toggleBtn.setAttribute('title', isPassword ? 'Ocultar senha' : 'Exibir senha');

        if (isPassword) {
            // Ícone de olho riscado (senha visível)
            eyeIcon.innerHTML = `
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                <line x1="1" y1="1" x2="23" y2="23"></line>
            `;
        } else {
            // Ícone de olho normal (senha oculta)
            eyeIcon.innerHTML = `
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                <circle cx="12" cy="12" r="3"></circle>
            `;
        }
    });
}

/**
 * Desaparecimento suave automático de alertas e toasts de sucesso após 5 segundos.
 */
function initAlertAutoDismiss() {
    const dismissibles = document.querySelectorAll('.alert-success, .toast-popup, .discreet-flash-container');
    dismissibles.forEach(item => {
        setTimeout(() => {
            item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            item.style.opacity = '0';
            item.style.transform = 'translateY(-6px)';
            setTimeout(() => item.remove(), 500);
        }, 4000);
    });
}

/**
 * =========================================================================
 * CONTROLE DO MODAL DE ATRIBUIÇÃO DE CHAMADO
 * =========================================================================
 */

function openAssignModal(ticketId, ticketNum, title, room, techId) {
    const modal = document.getElementById('assignModal');
    if (!modal) return;

    const inputId = document.getElementById('modalTicketId');
    const titleElem = document.getElementById('modalTicketTitle');
    const roomElem = document.getElementById('modalTicketRoom');
    const selectTecnico = document.getElementById('selectTecnicoId');
    const radioMe = document.querySelector('input[name="assign_type"][value="me"]');
    const radioOther = document.querySelector('input[name="assign_type"][value="other"]');

    if (inputId) inputId.value = ticketId;
    if (titleElem) titleElem.textContent = `Chamado #${ticketNum} - ${title}`;
    if (roomElem) roomElem.textContent = `Sala: ${room}`;

    // Configuração inicial do rádio
    if (radioMe) radioMe.checked = true;
    toggleTechSelect(false);

    if (selectTecnico && techId) {
        selectTecnico.value = techId;
    }

    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
}

function closeAssignModal() {
    const modal = document.getElementById('assignModal');
    if (!modal) return;

    modal.style.display = 'none';
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
}

function toggleTechSelect(isOther) {
    const container = document.getElementById('techSelectContainer');
    const select = document.getElementById('selectTecnicoId');

    if (!container) return;

    if (isOther) {
        container.style.display = 'block';
        if (select) select.setAttribute('required', 'required');
    } else {
        container.style.display = 'none';
        if (select) select.removeAttribute('required');
    }
}

/**
 * Fecha modais ao clicar no fundo escuro
 */
window.addEventListener('click', (event) => {
    const assignModal = document.getElementById('assignModal');
    if (assignModal && event.target === assignModal) {
        closeAssignModal();
    }
    const userModal = document.getElementById('modalNovoUsuario');
    if (userModal && event.target === userModal) {
        userModal.style.display = 'none';
    }
});

/**
 * =========================================================================
 * CONTROLE DE ABAS (DETALHE DO CHAMADO: INFORMAÇÕES VS HISTÓRICO)
 * =========================================================================
 */

function switchDetailTab(tabName) {
    const tabBtnInfo = document.getElementById('tabBtnInfo');
    const tabBtnHistory = document.getElementById('tabBtnHistory');
    const tabContentInfo = document.getElementById('tabContentInfo');
    const tabContentHistory = document.getElementById('tabContentHistory');

    if (!tabBtnInfo || !tabBtnHistory || !tabContentInfo || !tabContentHistory) return;

    if (tabName === 'history') {
        tabBtnInfo.classList.remove('active');
        tabBtnInfo.setAttribute('aria-selected', 'false');
        tabBtnHistory.classList.add('active');
        tabBtnHistory.setAttribute('aria-selected', 'true');

        tabContentInfo.style.display = 'none';
        tabContentHistory.style.display = 'block';
    } else {
        tabBtnHistory.classList.remove('active');
        tabBtnHistory.setAttribute('aria-selected', 'false');
        tabBtnInfo.classList.add('active');
        tabBtnInfo.setAttribute('aria-selected', 'true');

        tabContentHistory.style.display = 'none';
        tabContentInfo.style.display = 'block';
    }
}

/**
 * =========================================================================
 * FORMULÁRIO FINALIZAR CHAMADO (CAMPO CONDICIONAL DE PENDÊNCIA)
 * =========================================================================
 */

function togglePendingField(isPending) {
    const group = document.getElementById('motivoPendenteGroup');
    const textarea = document.getElementById('motivo_pendente');

    if (!group) return;

    if (isPending) {
        group.style.display = 'block';
        if (textarea) {
            textarea.setAttribute('required', 'required');
            textarea.focus();
        }
    } else {
        group.style.display = 'none';
        if (textarea) {
            textarea.removeAttribute('required');
            textarea.value = '';
        }
    }
}

