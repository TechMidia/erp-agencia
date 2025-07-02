from flask import Blueprint, jsonify, request, session
from src.models.user import db
from src.models.financeiro import TransacaoFinanceira
from src.models.pedido import Pedido
from datetime import datetime, timedelta

financeiro_bp = Blueprint('financeiro', __name__)

# Middleware para verificar autenticação
def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Acesso negado. Faça login primeiro.'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@financeiro_bp.route('/financeiro', methods=['GET'])
@require_auth
def get_transacoes():
    # Filtros opcionais
    tipo = request.args.get('tipo')
    categoria = request.args.get('categoria')
    status = request.args.get('status')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    query = TransacaoFinanceira.query
    
    if tipo:
        query = query.filter(TransacaoFinanceira.tipo == tipo)
    if categoria:
        query = query.filter(TransacaoFinanceira.categoria == categoria)
    if status:
        query = query.filter(TransacaoFinanceira.status == status)
    if data_inicio:
        query = query.filter(TransacaoFinanceira.data >= datetime.fromisoformat(data_inicio))
    if data_fim:
        query = query.filter(TransacaoFinanceira.data <= datetime.fromisoformat(data_fim))
    
    transacoes = query.order_by(TransacaoFinanceira.data.desc()).all()
    return jsonify([transacao.to_dict() for transacao in transacoes])

@financeiro_bp.route('/financeiro', methods=['POST'])
@require_auth
def create_transacao():
    data = request.json
    
    # Validações
    if not data.get('descricao'):
        return jsonify({'error': 'Descrição é obrigatória'}), 400
    
    if not data.get('tipo'):
        return jsonify({'error': 'Tipo é obrigatório'}), 400
    
    if not data.get('categoria'):
        return jsonify({'error': 'Categoria é obrigatória'}), 400
    
    if not data.get('valor'):
        return jsonify({'error': 'Valor é obrigatório'}), 400
    
    # Verificar se pedido existe (opcional)
    if data.get('pedido_id'):
        pedido = Pedido.query.get(data['pedido_id'])
        if not pedido:
            return jsonify({'error': 'Pedido não encontrado'}), 404
    
    transacao = TransacaoFinanceira(
        descricao=data['descricao'],
        tipo=data['tipo'],
        categoria=data['categoria'],
        valor=data['valor'],
        status=data.get('status', 'Pendente'),
        cliente_fornecedor=data.get('cliente_fornecedor'),
        forma_pagamento=data.get('forma_pagamento'),
        pedido_id=data.get('pedido_id'),
        observacoes=data.get('observacoes'),
        comprovante=data.get('comprovante')
    )
    
    if data.get('data'):
        transacao.data = datetime.fromisoformat(data['data'].replace('Z', '+00:00'))
    
    db.session.add(transacao)
    db.session.commit()
    return jsonify(transacao.to_dict()), 201

@financeiro_bp.route('/financeiro/<int:transacao_id>', methods=['GET'])
@require_auth
def get_transacao(transacao_id):
    transacao = TransacaoFinanceira.query.get_or_404(transacao_id)
    return jsonify(transacao.to_dict())

@financeiro_bp.route('/financeiro/<int:transacao_id>', methods=['PUT'])
@require_auth
def update_transacao(transacao_id):
    transacao = TransacaoFinanceira.query.get_or_404(transacao_id)
    data = request.json
    
    if data.get('pedido_id'):
        pedido = Pedido.query.get(data['pedido_id'])
        if not pedido:
            return jsonify({'error': 'Pedido não encontrado'}), 404
        transacao.pedido_id = data['pedido_id']
    
    transacao.descricao = data.get('descricao', transacao.descricao)
    transacao.tipo = data.get('tipo', transacao.tipo)
    transacao.categoria = data.get('categoria', transacao.categoria)
    transacao.valor = data.get('valor', transacao.valor)
    transacao.status = data.get('status', transacao.status)
    transacao.cliente_fornecedor = data.get('cliente_fornecedor', transacao.cliente_fornecedor)
    transacao.forma_pagamento = data.get('forma_pagamento', transacao.forma_pagamento)
    transacao.observacoes = data.get('observacoes', transacao.observacoes)
    transacao.comprovante = data.get('comprovante', transacao.comprovante)
    
    if data.get('data'):
        transacao.data = datetime.fromisoformat(data['data'].replace('Z', '+00:00'))
    
    db.session.commit()
    return jsonify(transacao.to_dict())

@financeiro_bp.route('/financeiro/<int:transacao_id>', methods=['DELETE'])
@require_auth
def delete_transacao(transacao_id):
    transacao = TransacaoFinanceira.query.get_or_404(transacao_id)
    db.session.delete(transacao)
    db.session.commit()
    return '', 204

@financeiro_bp.route('/financeiro/stats', methods=['GET'])
@require_auth
def get_financeiro_stats():
    """Retorna estatísticas financeiras"""
    # Período atual (mês atual)
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Receitas do mês
    receitas_mes = db.session.query(db.func.sum(TransacaoFinanceira.valor)).filter(
        TransacaoFinanceira.tipo == 'Receita',
        TransacaoFinanceira.data >= inicio_mes,
        TransacaoFinanceira.data <= fim_mes
    ).scalar() or 0
    
    # Despesas do mês
    despesas_mes = db.session.query(db.func.sum(TransacaoFinanceira.valor)).filter(
        TransacaoFinanceira.tipo == 'Despesa',
        TransacaoFinanceira.data >= inicio_mes,
        TransacaoFinanceira.data <= fim_mes
    ).scalar() or 0
    
    # Saldo do mês
    saldo_mes = receitas_mes - despesas_mes
    
    # Transações pendentes
    pendentes = TransacaoFinanceira.query.filter_by(status='Pendente').count()
    
    # Receitas por categoria
    receitas_categoria = db.session.query(
        TransacaoFinanceira.categoria,
        db.func.sum(TransacaoFinanceira.valor)
    ).filter(
        TransacaoFinanceira.tipo == 'Receita',
        TransacaoFinanceira.data >= inicio_mes,
        TransacaoFinanceira.data <= fim_mes
    ).group_by(TransacaoFinanceira.categoria).all()
    
    # Despesas por categoria
    despesas_categoria = db.session.query(
        TransacaoFinanceira.categoria,
        db.func.sum(TransacaoFinanceira.valor)
    ).filter(
        TransacaoFinanceira.tipo == 'Despesa',
        TransacaoFinanceira.data >= inicio_mes,
        TransacaoFinanceira.data <= fim_mes
    ).group_by(TransacaoFinanceira.categoria).all()
    
    return jsonify({
        'receitas_mes': receitas_mes,
        'despesas_mes': despesas_mes,
        'saldo_mes': saldo_mes,
        'pendentes': pendentes,
        'receitas_categoria': {cat: valor for cat, valor in receitas_categoria},
        'despesas_categoria': {cat: valor for cat, valor in despesas_categoria}
    })

@financeiro_bp.route('/financeiro/fluxo-caixa', methods=['GET'])
@require_auth
def get_fluxo_caixa():
    """Retorna dados para o fluxo de caixa dos últimos 12 meses"""
    meses = []
    receitas = []
    despesas = []
    
    for i in range(12):
        # Calcular o mês
        data_ref = datetime.now().replace(day=1) - timedelta(days=30 * i)
        inicio_mes = data_ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fim_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # Receitas do mês
        receita_mes = db.session.query(db.func.sum(TransacaoFinanceira.valor)).filter(
            TransacaoFinanceira.tipo == 'Receita',
            TransacaoFinanceira.data >= inicio_mes,
            TransacaoFinanceira.data <= fim_mes
        ).scalar() or 0
        
        # Despesas do mês
        despesa_mes = db.session.query(db.func.sum(TransacaoFinanceira.valor)).filter(
            TransacaoFinanceira.tipo == 'Despesa',
            TransacaoFinanceira.data >= inicio_mes,
            TransacaoFinanceira.data <= fim_mes
        ).scalar() or 0
        
        meses.insert(0, inicio_mes.strftime('%Y-%m'))
        receitas.insert(0, receita_mes)
        despesas.insert(0, despesa_mes)
    
    return jsonify({
        'meses': meses,
        'receitas': receitas,
        'despesas': despesas
    })

