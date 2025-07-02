from flask import Blueprint, jsonify, request, session
from src.models.user import db
from src.models.demanda_social import DemandaSocialMedia
from src.models.cliente import Cliente
from src.models.pedido import Pedido
from datetime import datetime

demanda_social_bp = Blueprint('demanda_social', __name__)

# Middleware para verificar autenticação
def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Acesso negado. Faça login primeiro.'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@demanda_social_bp.route('/demandas-social', methods=['GET'])
@require_auth
def get_demandas_social():
    # Filtros opcionais
    status = request.args.get('status')
    tipo_arte = request.args.get('tipo_arte')
    cliente_id = request.args.get('cliente_id')
    prioridade = request.args.get('prioridade')
    
    query = DemandaSocialMedia.query
    
    if status:
        query = query.filter(DemandaSocialMedia.status == status)
    if tipo_arte:
        query = query.filter(DemandaSocialMedia.tipo_arte == tipo_arte)
    if cliente_id:
        query = query.filter(DemandaSocialMedia.cliente_id == cliente_id)
    if prioridade:
        query = query.filter(DemandaSocialMedia.prioridade == prioridade)
    
    demandas = query.order_by(DemandaSocialMedia.data_solicitacao.desc()).all()
    
    # Incluir dados do cliente
    result = []
    for demanda in demandas:
        demanda_dict = demanda.to_dict()
        demanda_dict['cliente_nome'] = demanda.cliente.nome if demanda.cliente else None
        result.append(demanda_dict)
    
    return jsonify(result)

@demanda_social_bp.route('/demandas-social', methods=['POST'])
@require_auth
def create_demanda_social():
    data = request.json
    
    # Validações
    if not data.get('demanda'):
        return jsonify({'error': 'Descrição da demanda é obrigatória'}), 400
    
    if not data.get('cliente_id'):
        return jsonify({'error': 'Cliente é obrigatório'}), 400
    
    if not data.get('tipo_arte'):
        return jsonify({'error': 'Tipo de arte é obrigatório'}), 400
    
    # Verificar se cliente existe
    cliente = Cliente.query.get(data['cliente_id'])
    if not cliente:
        return jsonify({'error': 'Cliente não encontrado'}), 404
    
    # Verificar se pedido existe (opcional)
    if data.get('pedido_id'):
        pedido = Pedido.query.get(data['pedido_id'])
        if not pedido:
            return jsonify({'error': 'Pedido não encontrado'}), 404
    
    demanda = DemandaSocialMedia(
        demanda=data['demanda'],
        cliente_id=data['cliente_id'],
        pedido_id=data.get('pedido_id'),
        tipo_arte=data['tipo_arte'],
        tema_conteudo=data.get('tema_conteudo'),
        status=data.get('status', 'Briefing'),
        prioridade=data.get('prioridade', 'Normal'),
        observacoes=data.get('observacoes')
    )
    
    if data.get('data_entrega'):
        demanda.data_entrega = datetime.fromisoformat(data['data_entrega'].replace('Z', '+00:00'))
    
    db.session.add(demanda)
    db.session.commit()
    
    result = demanda.to_dict()
    result['cliente_nome'] = cliente.nome
    return jsonify(result), 201

@demanda_social_bp.route('/demandas-social/<int:demanda_id>', methods=['GET'])
@require_auth
def get_demanda_social(demanda_id):
    demanda = DemandaSocialMedia.query.get_or_404(demanda_id)
    result = demanda.to_dict()
    result['cliente_nome'] = demanda.cliente.nome if demanda.cliente else None
    return jsonify(result)

@demanda_social_bp.route('/demandas-social/<int:demanda_id>', methods=['PUT'])
@require_auth
def update_demanda_social(demanda_id):
    demanda = DemandaSocialMedia.query.get_or_404(demanda_id)
    data = request.json
    
    if data.get('cliente_id'):
        cliente = Cliente.query.get(data['cliente_id'])
        if not cliente:
            return jsonify({'error': 'Cliente não encontrado'}), 404
        demanda.cliente_id = data['cliente_id']
    
    if data.get('pedido_id'):
        pedido = Pedido.query.get(data['pedido_id'])
        if not pedido:
            return jsonify({'error': 'Pedido não encontrado'}), 404
        demanda.pedido_id = data['pedido_id']
    
    demanda.demanda = data.get('demanda', demanda.demanda)
    demanda.tipo_arte = data.get('tipo_arte', demanda.tipo_arte)
    demanda.tema_conteudo = data.get('tema_conteudo', demanda.tema_conteudo)
    demanda.status = data.get('status', demanda.status)
    demanda.prioridade = data.get('prioridade', demanda.prioridade)
    demanda.observacoes = data.get('observacoes', demanda.observacoes)
    demanda.arquivo_final = data.get('arquivo_final', demanda.arquivo_final)
    demanda.aprovado = data.get('aprovado', demanda.aprovado)
    
    if data.get('data_entrega'):
        demanda.data_entrega = datetime.fromisoformat(data['data_entrega'].replace('Z', '+00:00'))
    
    db.session.commit()
    
    result = demanda.to_dict()
    result['cliente_nome'] = demanda.cliente.nome if demanda.cliente else None
    return jsonify(result)

@demanda_social_bp.route('/demandas-social/<int:demanda_id>', methods=['DELETE'])
@require_auth
def delete_demanda_social(demanda_id):
    demanda = DemandaSocialMedia.query.get_or_404(demanda_id)
    db.session.delete(demanda)
    db.session.commit()
    return '', 204

@demanda_social_bp.route('/demandas-social/stats', methods=['GET'])
@require_auth
def get_demandas_social_stats():
    """Retorna estatísticas das demandas de social media"""
    total_demandas = DemandaSocialMedia.query.count()
    em_criacao = DemandaSocialMedia.query.filter_by(status='Criação').count()
    aguardando_aprovacao = DemandaSocialMedia.query.filter_by(status='Aguardando Aprovação').count()
    urgentes = DemandaSocialMedia.query.filter_by(prioridade='Urgente').count()
    
    # Demandas por tipo de arte
    tipos_arte = db.session.query(
        DemandaSocialMedia.tipo_arte,
        db.func.count(DemandaSocialMedia.id)
    ).group_by(DemandaSocialMedia.tipo_arte).all()
    
    tipos_arte_dict = {tipo: count for tipo, count in tipos_arte}
    
    return jsonify({
        'total_demandas': total_demandas,
        'em_criacao': em_criacao,
        'aguardando_aprovacao': aguardando_aprovacao,
        'urgentes': urgentes,
        'tipos_arte': tipos_arte_dict
    })

