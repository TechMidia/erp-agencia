from flask import Blueprint, jsonify, request, session
from src.models.user import db
from src.models.pedido import Pedido
from src.models.cliente import Cliente
from datetime import datetime
import uuid

pedido_bp = Blueprint('pedido', __name__)

# Middleware para verificar autenticação
def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Acesso negado. Faça login primeiro.'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@pedido_bp.route('/pedidos', methods=['GET'])
@require_auth
def get_pedidos():
    # Filtros opcionais
    status = request.args.get('status')
    tipo_servico = request.args.get('tipo_servico')
    responsavel = request.args.get('responsavel')
    cliente_id = request.args.get('cliente_id')
    
    query = Pedido.query
    
    if status:
        query = query.filter(Pedido.status == status)
    if tipo_servico:
        query = query.filter(Pedido.tipo_servico == tipo_servico)
    if responsavel:
        query = query.filter(Pedido.responsavel == responsavel)
    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)
    
    pedidos = query.order_by(Pedido.data_pedido.desc()).all()
    
    # Incluir dados do cliente
    result = []
    for pedido in pedidos:
        pedido_dict = pedido.to_dict()
        pedido_dict['cliente_nome'] = pedido.cliente.nome if pedido.cliente else None
        result.append(pedido_dict)
    
    return jsonify(result)

@pedido_bp.route('/pedidos', methods=['POST'])
@require_auth
def create_pedido():
    data = request.json
    
    # Validações
    if not data.get('cliente_id'):
        return jsonify({'error': 'Cliente é obrigatório'}), 400
    
    if not data.get('tipo_servico'):
        return jsonify({'error': 'Tipo de serviço é obrigatório'}), 400
    
    # Verificar se cliente existe
    cliente = Cliente.query.get(data['cliente_id'])
    if not cliente:
        return jsonify({'error': 'Cliente não encontrado'}), 404
    
    # Gerar ID único do pedido
    id_pedido = data.get('id_pedido') or f"PED-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    pedido = Pedido(
        id_pedido=id_pedido,
        cliente_id=data['cliente_id'],
        tipo_servico=data['tipo_servico'],
        descricao=data.get('descricao'),
        status=data.get('status', 'Orçamento'),
        prioridade=data.get('prioridade', 'Normal'),
        responsavel=data.get('responsavel'),
        valor=data.get('valor', 0.0),
        custo=data.get('custo', 0.0),
        forma_pagamento=data.get('forma_pagamento'),
        status_pagamento=data.get('status_pagamento', 'Pendente'),
        observacoes=data.get('observacoes')
    )
    
    if data.get('data_entrega'):
        pedido.data_entrega = datetime.fromisoformat(data['data_entrega'].replace('Z', '+00:00'))
    
    db.session.add(pedido)
    db.session.commit()
    
    result = pedido.to_dict()
    result['cliente_nome'] = cliente.nome
    return jsonify(result), 201

@pedido_bp.route('/pedidos/<int:pedido_id>', methods=['GET'])
@require_auth
def get_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    result = pedido.to_dict()
    result['cliente_nome'] = pedido.cliente.nome if pedido.cliente else None
    return jsonify(result)

@pedido_bp.route('/pedidos/<int:pedido_id>', methods=['PUT'])
@require_auth
def update_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    data = request.json
    
    if data.get('cliente_id'):
        cliente = Cliente.query.get(data['cliente_id'])
        if not cliente:
            return jsonify({'error': 'Cliente não encontrado'}), 404
        pedido.cliente_id = data['cliente_id']
    
    pedido.tipo_servico = data.get('tipo_servico', pedido.tipo_servico)
    pedido.descricao = data.get('descricao', pedido.descricao)
    pedido.status = data.get('status', pedido.status)
    pedido.prioridade = data.get('prioridade', pedido.prioridade)
    pedido.responsavel = data.get('responsavel', pedido.responsavel)
    pedido.valor = data.get('valor', pedido.valor)
    pedido.custo = data.get('custo', pedido.custo)
    pedido.forma_pagamento = data.get('forma_pagamento', pedido.forma_pagamento)
    pedido.status_pagamento = data.get('status_pagamento', pedido.status_pagamento)
    pedido.observacoes = data.get('observacoes', pedido.observacoes)
    
    if data.get('data_entrega'):
        pedido.data_entrega = datetime.fromisoformat(data['data_entrega'].replace('Z', '+00:00'))
    
    db.session.commit()
    
    result = pedido.to_dict()
    result['cliente_nome'] = pedido.cliente.nome if pedido.cliente else None
    return jsonify(result)

@pedido_bp.route('/pedidos/<int:pedido_id>', methods=['DELETE'])
@require_auth
def delete_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    db.session.delete(pedido)
    db.session.commit()
    return '', 204

@pedido_bp.route('/pedidos/stats', methods=['GET'])
@require_auth
def get_pedidos_stats():
    """Retorna estatísticas dos pedidos"""
    total_pedidos = Pedido.query.count()
    em_andamento = Pedido.query.filter(Pedido.status.in_(['Aprovado', 'Produção'])).count()
    concluidos = Pedido.query.filter_by(status='Concluído').count()
    atrasados = Pedido.query.filter(
        Pedido.data_entrega < datetime.utcnow(),
        Pedido.status != 'Concluído'
    ).count()
    
    # Faturamento do mês atual
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
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
    
    return jsonify({
        'total_pedidos': total_pedidos,
        'em_andamento': em_andamento,
        'concluidos': concluidos,
        'atrasados': atrasados,
        'faturamento_mes': faturamento_mes,
        'margem_media': margem_media
    })

