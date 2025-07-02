// Configurações globais
const API_BASE = '/api';
let currentUser = null;
let currentPage = 'dashboard';

// Utilitários
const showToast = (message, type = 'info') => {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    toast.className = `toast ${type === 'error' ? 'bg-danger text-white' : type === 'success' ? 'bg-success text-white' : ''}`;
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
};

const showLoading = (show = true) => {
    document.getElementById('loadingSpinner').style.display = show ? 'flex' : 'none';
};

const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value || 0);
};

const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('pt-BR');
};

const formatDateTime = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('pt-BR');
};

// API Helper
const api = {
    async request(endpoint, options = {}) {
        showLoading(true);
        try {
            const response = await fetch(`${API_BASE}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Erro na requisição');
            }
            
            return data;
        } catch (error) {
            showToast(error.message, 'error');
            throw error;
        } finally {
            showLoading(false);
        }
    },

    get(endpoint) {
        return this.request(endpoint);
    },

    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
};

// Autenticação
const auth = {
    async login(username, password) {
        try {
            const response = await api.post('/login', { username, password });
            currentUser = response.user;
            document.getElementById('currentUser').textContent = currentUser.username;
            this.showMainLayout();
            showToast('Login realizado com sucesso!', 'success');
            await this.loadCompanyConfig();
            return response;
        } catch (error) {
            showToast('Erro no login: ' + error.message, 'error');
            throw error;
        }
    },

    async logout() {
        try {
            await api.post('/logout');
            currentUser = null;
            this.showLoginModal();
            showToast('Logout realizado com sucesso!', 'success');
        } catch (error) {
            showToast('Erro no logout: ' + error.message, 'error');
        }
    },

    showLoginModal() {
        document.getElementById('mainLayout').style.display = 'none';
        const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
        loginModal.show();
    },

    showMainLayout() {
        const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
        if (loginModal) loginModal.hide();
        document.getElementById('mainLayout').style.display = 'flex';
        navigation.loadPage('dashboard');
    },

    async loadCompanyConfig() {
        try {
            const config = await api.get('/configuracao');
            document.getElementById('companyName').textContent = config.nome_empresa;
            
            if (config.logo_path) {
                const logo = document.getElementById('companyLogo');
                logo.src = `/static/${config.logo_path}`;
                logo.style.display = 'block';
            }
            
            // Aplicar cores personalizadas
            document.documentElement.style.setProperty('--primary-color', config.cor_primaria);
            document.documentElement.style.setProperty('--secondary-color', config.cor_secundaria);
            document.documentElement.style.setProperty('--success-color', config.cor_sucesso);
            document.documentElement.style.setProperty('--danger-color', config.cor_perigo);
            document.documentElement.style.setProperty('--warning-color', config.cor_aviso);
            document.documentElement.style.setProperty('--info-color', config.cor_info);
        } catch (error) {
            console.error('Erro ao carregar configuração:', error);
        }
    }
};

// Navegação
const navigation = {
    loadPage(page) {
        currentPage = page;
        
        // Atualizar menu ativo
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-page="${page}"]`).classList.add('active');
        
        // Atualizar título da página
        const pageTitle = document.getElementById('pageTitle');
        const titles = {
            'dashboard': 'Dashboard',
            'clientes': 'Clientes',
            'pedidos': 'Pedidos & Projetos',
            'demandas': 'Demandas Social Media',
            'financeiro': 'Financeiro',
            'fornecedores': 'Fornecedores',
            'tabela-precos': 'Tabela de Preços',
            'assistente-ia': 'Assistente IA',
            'configuracoes': 'Configurações',
            'usuarios': 'Gerenciar Usuários'
        };
        pageTitle.textContent = titles[page] || 'Página';
        
        // Carregar conteúdo da página
        this.renderPage(page);
    },

    async renderPage(page) {
        const content = document.getElementById('pageContent');
        content.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';
        
        try {
            switch (page) {
                case 'dashboard':
                    await this.renderDashboard(content);
                    break;
                case 'clientes':
                    await this.renderClientes(content);
                    break;
                case 'pedidos':
                    await this.renderPedidos(content);
                    break;
                case 'demandas':
                    await this.renderDemandas(content);
                    break;
                case 'financeiro':
                    await this.renderFinanceiro(content);
                    break;
                case 'fornecedores':
                    await this.renderFornecedores(content);
                    break;
                case 'tabela-precos':
                    await this.renderTabelaPrecos(content);
                    break;
                case 'assistente-ia':
                    await this.renderAssistenteIA(content);
                    break;
                case 'configuracoes':
                    await this.renderConfiguracoes(content);
                    break;
                case 'usuarios':
                    await this.renderUsuarios(content);
                    break;
                default:
                    content.innerHTML = '<div class="alert alert-warning">Página não encontrada</div>';
            }
        } catch (error) {
            content.innerHTML = `<div class="alert alert-danger">Erro ao carregar página: ${error.message}</div>`;
        }
    },

    async renderDashboard(content) {
        const dashboard = await api.get('/dashboard');
        const kpis = dashboard.kpis;
        const graficos = dashboard.graficos;
        
        content.innerHTML = `
            <div class="fade-in">
                <!-- KPIs Row -->
                <div class="row mb-4">
                    <div class="col-md-3 mb-3">
                        <div class="kpi-card">
                            <div class="kpi-value">${kpis.total_clientes}</div>
                            <div class="kpi-label">Total de Clientes</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="kpi-card success">
                            <div class="kpi-value">${formatCurrency(kpis.faturamento_mes)}</div>
                            <div class="kpi-label">Faturamento do Mês</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="kpi-card warning">
                            <div class="kpi-value">${kpis.pedidos_em_andamento}</div>
                            <div class="kpi-label">Pedidos em Andamento</div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="kpi-card ${kpis.pedidos_atrasados > 0 ? 'danger' : 'info'}">
                            <div class="kpi-value">${kpis.pedidos_atrasados}</div>
                            <div class="kpi-label">Pedidos Atrasados</div>
                        </div>
                    </div>
                </div>

                <!-- Charts Row -->
                <div class="row mb-4">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Faturamento dos Últimos Meses</h5>
                            </div>
                            <div class="card-body">
                                <canvas id="faturamentoChart"></canvas>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Pedidos por Status</h5>
                            </div>
                            <div class="card-body">
                                <canvas id="statusChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Top Clientes -->
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Top 5 Clientes</h5>
                            </div>
                            <div class="card-body">
                                <div class="table-responsive">
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>Cliente</th>
                                                <th>Valor Total</th>
                                                <th>Pedidos</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${graficos.top_clientes.map(cliente => `
                                                <tr>
                                                    <td>${cliente.nome}</td>
                                                    <td>${formatCurrency(cliente.valor_total)}</td>
                                                    <td>${cliente.qtd_pedidos}</td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Resumo Financeiro</h5>
                            </div>
                            <div class="card-body">
                                <div class="row text-center">
                                    <div class="col-4">
                                        <h6 class="text-success">Receitas</h6>
                                        <h5>${formatCurrency(kpis.receitas_mes)}</h5>
                                    </div>
                                    <div class="col-4">
                                        <h6 class="text-danger">Despesas</h6>
                                        <h5>${formatCurrency(kpis.despesas_mes)}</h5>
                                    </div>
                                    <div class="col-4">
                                        <h6 class="${kpis.saldo_mes >= 0 ? 'text-success' : 'text-danger'}">Saldo</h6>
                                        <h5>${formatCurrency(kpis.saldo_mes)}</h5>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Renderizar gráficos
        this.renderCharts(graficos);
    },

    renderCharts(graficos) {
        // Gráfico de Faturamento
        const faturamentoCtx = document.getElementById('faturamentoChart').getContext('2d');
        new Chart(faturamentoCtx, {
            type: 'line',
            data: {
                labels: graficos.faturamento_historico.map(item => item.mes),
                datasets: [{
                    label: 'Faturamento',
                    data: graficos.faturamento_historico.map(item => item.valor),
                    borderColor: 'rgb(0, 123, 255)',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                }
            }
        });

        // Gráfico de Status dos Pedidos
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        const statusData = graficos.pedidos_por_status;
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(statusData),
                datasets: [{
                    data: Object.values(statusData),
                    backgroundColor: [
                        '#007bff',
                        '#28a745',
                        '#ffc107',
                        '#dc3545',
                        '#6c757d'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    },

    async renderClientes(content) {
        const clientes = await api.get('/clientes');
        
        content.innerHTML = `
            <div class="fade-in">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h4>Gerenciar Clientes</h4>
                    <button class="btn btn-primary" onclick="clienteModal()">
                        <i class="fas fa-plus me-2"></i>Novo Cliente
                    </button>
                </div>
                
                <div class="card">
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Nome</th>
                                        <th>Tipo</th>
                                        <th>Cidade</th>
                                        <th>Status</th>
                                        <th>Valor Total</th>
                                        <th>Ações</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${clientes.map(cliente => `
                                        <tr>
                                            <td>${cliente.nome}</td>
                                            <td>${cliente.tipo}</td>
                                            <td>${cliente.cidade || '-'}</td>
                                            <td><span class="status-badge status-${cliente.status.toLowerCase()}">${cliente.status}</span></td>
                                            <td>${formatCurrency(cliente.valor_total)}</td>
                                            <td>
                                                <button class="btn btn-sm btn-outline-primary" onclick="editarCliente(${cliente.id})">
                                                    <i class="fas fa-edit"></i>
                                                </button>
                                                <button class="btn btn-sm btn-outline-danger" onclick="excluirCliente(${cliente.id})">
                                                    <i class="fas fa-trash"></i>
                                                </button>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    async renderAssistenteIA(content) {
        const relatorio = await api.get('/assistente-ia/relatorio-completo');
        
        content.innerHTML = `
            <div class="fade-in">
                <div class="row mb-4">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">
                                    <i class="fas fa-robot me-2"></i>
                                    Assistente IA - Análise Inteligente
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-8">
                                        <div class="ia-chat" id="iaChat">
                                            <div class="ia-message assistant">
                                                <strong>Assistente IA:</strong><br>
                                                Olá! Sou seu assistente inteligente. Posso ajudar com análises dos seus dados, 
                                                insights sobre performance e responder perguntas sobre o negócio.
                                            </div>
                                        </div>
                                        <div class="mt-3">
                                            <div class="input-group">
                                                <input type="text" class="form-control" id="iaPergunta" 
                                                       placeholder="Faça uma pergunta sobre seus dados...">
                                                <button class="btn btn-primary" onclick="enviarPerguntaIA()">
                                                    <i class="fas fa-paper-plane"></i>
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="card bg-light">
                                            <div class="card-body text-center">
                                                <h3 class="text-primary">${relatorio.score_saude}/100</h3>
                                                <p class="mb-0">Score de Saúde da Empresa</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Insights e Alertas -->
                <div class="row mb-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">
                                    <i class="fas fa-lightbulb me-2"></i>
                                    Insights
                                </h6>
                            </div>
                            <div class="card-body">
                                ${relatorio.analise_geral.insights.map(insight => `
                                    <div class="alert alert-${insight.tipo === 'success' ? 'success' : 'info'} alert-sm">
                                        <strong>${insight.titulo}</strong><br>
                                        ${insight.descricao}
                                    </div>
                                `).join('') || '<p class="text-muted">Nenhum insight disponível no momento.</p>'}
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">
                                    <i class="fas fa-exclamation-triangle me-2"></i>
                                    Alertas
                                </h6>
                            </div>
                            <div class="card-body">
                                ${relatorio.analise_geral.alertas.map(alerta => `
                                    <div class="alert alert-${alerta.tipo === 'danger' ? 'danger' : 'warning'} alert-sm">
                                        <strong>${alerta.titulo}</strong><br>
                                        ${alerta.descricao}
                                    </div>
                                `).join('') || '<p class="text-muted">Nenhum alerta no momento.</p>'}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Recomendações -->
                <div class="row">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">
                                    <i class="fas fa-tasks me-2"></i>
                                    Ações Recomendadas
                                </h6>
                            </div>
                            <div class="card-body">
                                ${relatorio.analise_geral.recomendacoes.map(rec => `
                                    <div class="alert alert-info alert-sm">
                                        <strong>${rec.titulo}</strong><br>
                                        ${rec.descricao}
                                        <span class="badge bg-${rec.prioridade === 'alta' ? 'danger' : 'warning'} ms-2">
                                            ${rec.prioridade}
                                        </span>
                                    </div>
                                `).join('') || '<p class="text-muted">Nenhuma recomendação no momento.</p>'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    async renderConfiguracoes(content) {
        const config = await api.get('/configuracao');
        
        content.innerHTML = `
            <div class="fade-in">
                <div class="row">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-header">
                                <h5 class="mb-0">Configurações da Empresa</h5>
                            </div>
                            <div class="card-body">
                                <form id="configForm">
                                    <div class="row">
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label">Nome da Empresa</label>
                                            <input type="text" class="form-control" id="nomeEmpresa" value="${config.nome_empresa}">
                                        </div>
                                        <div class="col-md-6 mb-3">
                                            <label class="form-label">Logo da Empresa</label>
                                            <input type="file" class="form-control" id="logoFile" accept="image/*">
                                            ${config.logo_path ? `<small class="text-muted">Logo atual: ${config.logo_path}</small>` : ''}
                                        </div>
                                    </div>
                                    
                                    <h6 class="mt-4 mb-3">Personalização de Cores</h6>
                                    <div class="row">
                                        <div class="col-md-4 mb-3">
                                            <label class="form-label">Cor Primária</label>
                                            <input type="color" class="form-control color-picker" id="corPrimaria" value="${config.cor_primaria}">
                                        </div>
                                        <div class="col-md-4 mb-3">
                                            <label class="form-label">Cor de Sucesso</label>
                                            <input type="color" class="form-control color-picker" id="corSucesso" value="${config.cor_sucesso}">
                                        </div>
                                        <div class="col-md-4 mb-3">
                                            <label class="form-label">Cor de Perigo</label>
                                            <input type="color" class="form-control color-picker" id="corPerigo" value="${config.cor_perigo}">
                                        </div>
                                    </div>
                                    
                                    <div class="d-flex gap-2">
                                        <button type="submit" class="btn btn-primary">
                                            <i class="fas fa-save me-2"></i>Salvar Configurações
                                        </button>
                                        <button type="button" class="btn btn-secondary" onclick="resetarCores()">
                                            <i class="fas fa-undo me-2"></i>Resetar Cores
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">Preview das Cores</h6>
                            </div>
                            <div class="card-body">
                                <div class="mb-2">
                                    <button class="btn btn-primary btn-sm w-100">Botão Primário</button>
                                </div>
                                <div class="mb-2">
                                    <button class="btn btn-success btn-sm w-100">Botão Sucesso</button>
                                </div>
                                <div class="mb-2">
                                    <button class="btn btn-danger btn-sm w-100">Botão Perigo</button>
                                </div>
                                <div class="alert alert-primary alert-sm">
                                    Exemplo de alerta primário
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Event listeners para preview em tempo real
        document.getElementById('corPrimaria').addEventListener('change', (e) => {
            document.documentElement.style.setProperty('--primary-color', e.target.value);
        });
        
        document.getElementById('corSucesso').addEventListener('change', (e) => {
            document.documentElement.style.setProperty('--success-color', e.target.value);
        });
        
        document.getElementById('corPerigo').addEventListener('change', (e) => {
            document.documentElement.style.setProperty('--danger-color', e.target.value);
        });

        // Form submit
        document.getElementById('configForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await salvarConfiguracoes();
        });
    }
};

// Funções específicas
async function enviarPerguntaIA() {
    const input = document.getElementById('iaPergunta');
    const pergunta = input.value.trim();
    
    if (!pergunta) return;
    
    const chat = document.getElementById('iaChat');
    
    // Adicionar pergunta do usuário
    chat.innerHTML += `
        <div class="ia-message user">
            <strong>Você:</strong><br>
            ${pergunta}
        </div>
    `;
    
    input.value = '';
    
    try {
        const response = await api.post('/assistente-ia/pergunta', { pergunta });
        
        // Adicionar resposta do assistente
        chat.innerHTML += `
            <div class="ia-message assistant">
                <strong>Assistente IA:</strong><br>
                ${response.resposta}
            </div>
        `;
        
        chat.scrollTop = chat.scrollHeight;
    } catch (error) {
        chat.innerHTML += `
            <div class="ia-message assistant">
                <strong>Assistente IA:</strong><br>
                Desculpe, ocorreu um erro ao processar sua pergunta.
            </div>
        `;
    }
}

async function salvarConfiguracoes() {
    const logoFile = document.getElementById('logoFile').files[0];
    
    try {
        // Upload do logo se selecionado
        if (logoFile) {
            const formData = new FormData();
            formData.append('file', logoFile);
            
            const uploadResponse = await fetch('/api/upload/logo', {
                method: 'POST',
                body: formData
            });
            
            if (!uploadResponse.ok) {
                throw new Error('Erro no upload do logo');
            }
        }
        
        // Salvar configurações
        const configData = {
            nome_empresa: document.getElementById('nomeEmpresa').value,
            cor_primaria: document.getElementById('corPrimaria').value,
            cor_sucesso: document.getElementById('corSucesso').value,
            cor_perigo: document.getElementById('corPerigo').value
        };
        
        await api.put('/configuracao', configData);
        showToast('Configurações salvas com sucesso!', 'success');
        
        // Recarregar configurações
        await auth.loadCompanyConfig();
    } catch (error) {
        showToast('Erro ao salvar configurações: ' + error.message, 'error');
    }
}

function resetarCores() {
    document.getElementById('corPrimaria').value = '#007bff';
    document.getElementById('corSucesso').value = '#28a745';
    document.getElementById('corPerigo').value = '#dc3545';
    
    document.documentElement.style.setProperty('--primary-color', '#007bff');
    document.documentElement.style.setProperty('--success-color', '#28a745');
    document.documentElement.style.setProperty('--danger-color', '#dc3545');
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Login form
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        await auth.login(username, password);
    });

    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', () => {
        auth.logout();
    });

    // Navigation
    document.querySelectorAll('[data-page]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navigation.loadPage(e.target.closest('[data-page]').dataset.page);
        });
    });

    // Sidebar toggle
    document.getElementById('sidebarToggle').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('show');
    });

    // Enter key para pergunta IA
    document.addEventListener('keypress', (e) => {
        if (e.target.id === 'iaPergunta' && e.key === 'Enter') {
            enviarPerguntaIA();
        }
    });

    // Inicializar
    auth.showLoginModal();
});

