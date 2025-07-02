from flask import Blueprint, jsonify, request, session
from src.models.user import db
from src.models.cliente import Cliente
from datetime import datetime

cliente_bp = Blueprint('cliente', __name__)

# Middleware para verificar autenticação
def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Acesso negado. Faça login primeiro.'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@cliente_bp.route('/clientes', methods=['GET'])
@require_auth
def get_clientes():
    # Filtros opcionais
    status = request.args.get('status')
    tipo = request.args.get('tipo')
    cidade = request.args.get('cidade')
    
    query = Cliente.query
    
    if status:
        query = query.filter(Cliente.status == status)
    if tipo:
        query = query.filter(Cliente.tipo == tipo)
    if cidade:
        query = query.filter(Cliente.cidade.ilike(f'%{cidade}%'))
    
    clientes = query.all()
    return jsonify([cliente.to_dict() for cliente in clientes])

@cliente_bp.route('/clientes', methods=['POST'])
@require_auth
def create_cliente():
    data = request.json
    
    # Validações
    if not data.get('nome'):
        return jsonify({'error': 'Nome é obrigatório'}), 400
    
    if not data.get('tipo'):
        return jsonify({'error': 'Tipo é obrigatório'}), 400
    
    cliente = Cliente(
        nome=data['nome'],
        tipo=data['tipo'],
        cidade=data.get('cidade'),
        populacao=data.get('populacao'),
        contato_principal=data.get('contato_principal'),
        whatsapp=data.get('whatsapp'),
        email=data.get('email'),
        status=data.get('status', 'Prospect'),
        segmento=data.get('segmento'),
        observacoes=data.get('observacoes')
    )
    
    db.session.add(cliente)
    db.session.commit()
    return jsonify(cliente.to_dict()), 201

@cliente_bp.route('/clientes/<int:cliente_id>', methods=['GET'])
@require_auth
def get_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    return jsonify(cliente.to_dict())

@cliente_bp.route('/clientes/<int:cliente_id>', methods=['PUT'])
@require_auth
def update_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    data = request.json
    
    cliente.nome = data.get('nome', cliente.nome)
    cliente.tipo = data.get('tipo', cliente.tipo)
    cliente.cidade = data.get('cidade', cliente.cidade)
    cliente.populacao = data.get('populacao', cliente.populacao)
    cliente.contato_principal = data.get('contato_principal', cliente.contato_principal)
    cliente.whatsapp = data.get('whatsapp', cliente.whatsapp)
    cliente.email = data.get('email', cliente.email)
    cliente.status = data.get('status', cliente.status)
    cliente.segmento = data.get('segmento', cliente.segmento)
    cliente.observacoes = data.get('observacoes', cliente.observacoes)
    
    if data.get('ultimo_contato'):
        cliente.ultimo_contato = datetime.fromisoformat(data['ultimo_contato'].replace('Z', '+00:00'))
    
    db.session.commit()
    return jsonify(cliente.to_dict())

@cliente_bp.route('/clientes/<int:cliente_id>', methods=['DELETE'])
@require_auth
def delete_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    db.session.delete(cliente)
    db.session.commit()
    return '', 204

@cliente_bp.route('/clientes/stats', methods=['GET'])
@require_auth
def get_clientes_stats():
    """Retorna estatísticas dos clientes"""
    total_clientes = Cliente.query.count()
    clientes_ativos = Cliente.query.filter_by(status='Ativo').count()
    prospects = Cliente.query.filter_by(status='Prospect').count()
    
    # Top 5 clientes por valor total
    top_clientes = Cliente.query.all()
    top_clientes.sort(key=lambda x: x.valor_total, reverse=True)
    top_5 = [cliente.to_dict() for cliente in top_clientes[:5]]
    
    return jsonify({
        'total_clientes': total_clientes,
        'clientes_ativos': clientes_ativos,
        'prospects': prospects,
        'top_clientes': top_5
    })

