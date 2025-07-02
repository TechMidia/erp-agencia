from flask import Blueprint, jsonify, request, session
from src.models.user import db
from src.models.cliente import Cliente
from src.models.pedido import Pedido
from src.models.demanda_social import DemandaSocialMedia
from src.models.financeiro import TransacaoFinanceira
from src.models.configuracao import ConfiguracaoEmpresa
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

# Middleware para verificar autenticação
def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Acesso negado. Faça login primeiro.'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@dashboard_bp.route('/dashboard', methods=['GET'])
@require_auth
def get_dashboard():
    """Retorna todos os KPIs do dashboard principal"""
    
    # Período atual (mês atual)
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # KPIs de Clientes
    total_clientes = Cliente.query.count()
    clientes_ativos = Cliente.query.filter_by(status='Ativo').count()
    novos_clientes_mes = Cliente.query.filter(Cliente.data_cadastro >= inicio_mes).count()
    
    # KPIs de Pedidos
    total_pedidos = Pedido.query.count()
    pedidos_em_andamento = Pedido.query.filter(Pedido.status.in_(['Aprovado', 'Produção'])).count()
    pedidos_atrasados = Pedido.query.filter(
        Pedido.data_entrega < datetime.utcnow(),
        Pedido.status != 'Concluído'
    ).count()
    
    # Faturamento do mês
    faturamento_mes = db.session.query(db.func.sum(Pedido.valor)).filter(
        Pedido.data_pedido >= inicio_mes,
        Pedido.status == 'Concluído'
    ).scalar() or 0
    
    # Margem média
    pedidos_concluidos = Pedido.query.filter_by(status='Concluído').all()
    margem_media = 0
    if pedidos_concluidos:
        margens = [p.margem for p in pedidos_concluidos if p.valor and p.valor > 0]
        margem_media = sum(margens) / len(margens) if margens else 0
    
    # KPIs Financeiros
    receitas_mes = db.session.query(db.func.sum(TransacaoFinanceira.valor)).filter(
        TransacaoFinanceira.tipo == 'Receita',
        TransacaoFinanceira.data >= inicio_mes,
        TransacaoFinanceira.data <= fim_mes
    ).scalar() or 0
    
    despesas_mes = db.session.query(db.func.sum(TransacaoFinanceira.valor)).filter(
        TransacaoFinanceira.tipo == 'Despesa',
        TransacaoFinanceira.data >= inicio_mes,
        TransacaoFinanceira.data <= fim_mes
    ).scalar() or 0
    
    saldo_mes = receitas_mes - despesas_mes
    
    # KPIs de Demandas Social Media
    demandas_em_criacao = DemandaSocialMedia.query.filter_by(status='Criação').count()
    demandas_aguardando = DemandaSocialMedia.query.filter_by(status='Aguardando Aprovação').count()
    demandas_urgentes = DemandaSocialMedia.query.filter_by(prioridade='Urgente').count()
    
    # Pedidos por status (para gráfico)
    pedidos_por_status = db.session.query(
        Pedido.status,
        db.func.count(Pedido.id)
    ).group_by(Pedido.status).all()
    
    # Faturamento dos últimos 6 meses (para gráfico)
    faturamento_historico = []
    for i in range(6):
        data_ref = datetime.now().replace(day=1) - timedelta(days=30 * i)
        inicio = data_ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fim = (inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        faturamento = db.session.query(db.func.sum(Pedido.valor)).filter(
            Pedido.data_pedido >= inicio,
            Pedido.data_pedido <= fim,
            Pedido.status == 'Concluído'
        ).scalar() or 0
        
        faturamento_historico.insert(0, {
            'mes': inicio.strftime('%Y-%m'),
            'valor': faturamento
        })
    
    # Top 5 clientes por valor
    top_clientes = Cliente.query.all()
    top_clientes.sort(key=lambda x: x.valor_total, reverse=True)
    top_5_clientes = [
        {
            'nome': cliente.nome,
            'valor_total': cliente.valor_total,
            'qtd_pedidos': cliente.qtd_pedidos
        }
        for cliente in top_clientes[:5]
    ]
    
    return jsonify({
        'kpis': {
            'total_clientes': total_clientes,
            'clientes_ativos': clientes_ativos,
            'novos_clientes_mes': novos_clientes_mes,
            'total_pedidos': total_pedidos,
            'pedidos_em_andamento': pedidos_em_andamento,
            'pedidos_atrasados': pedidos_atrasados,
            'faturamento_mes': faturamento_mes,
            'margem_media': round(margem_media, 2),
            'receitas_mes': receitas_mes,
            'despesas_mes': despesas_mes,
            'saldo_mes': saldo_mes,
            'demandas_em_criacao': demandas_em_criacao,
            'demandas_aguardando': demandas_aguardando,
            'demandas_urgentes': demandas_urgentes
        },
        'graficos': {
            'pedidos_por_status': {status: count for status, count in pedidos_por_status},
            'faturamento_historico': faturamento_historico,
            'top_clientes': top_5_clientes
        }
    })

@dashboard_bp.route('/configuracao', methods=['GET'])
@require_auth
def get_configuracao():
    """Retorna a configuração da empresa"""
    config = ConfiguracaoEmpresa.query.first()
    if not config:
        # Criar configuração padrão se não existir
        config = ConfiguracaoEmpresa()
        db.session.add(config)
        db.session.commit()
    
    return jsonify(config.to_dict())

@dashboard_bp.route('/configuracao', methods=['PUT'])
@require_auth
def update_configuracao():
    """Atualiza a configuração da empresa"""
    config = ConfiguracaoEmpresa.query.first()
    if not config:
        config = ConfiguracaoEmpresa()
        db.session.add(config)
    
    data = request.json
    
    config.nome_empresa = data.get('nome_empresa', config.nome_empresa)
    config.logo_path = data.get('logo_path', config.logo_path)
    config.cor_primaria = data.get('cor_primaria', config.cor_primaria)
    config.cor_secundaria = data.get('cor_secundaria', config.cor_secundaria)
    config.cor_sucesso = data.get('cor_sucesso', config.cor_sucesso)
    config.cor_perigo = data.get('cor_perigo', config.cor_perigo)
    config.cor_aviso = data.get('cor_aviso', config.cor_aviso)
    config.cor_info = data.get('cor_info', config.cor_info)
    config.tema_escuro = data.get('tema_escuro', config.tema_escuro)
    
    db.session.commit()
    return jsonify(config.to_dict())

