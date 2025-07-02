from flask import Blueprint, jsonify, request, session
from src.models.user import db
from src.models.fornecedor import Fornecedor

fornecedor_bp = Blueprint('fornecedor', __name__)

# Middleware para verificar autenticação
def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Acesso negado. Faça login primeiro.'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@fornecedor_bp.route('/fornecedores', methods=['GET'])
@require_auth
def get_fornecedores():
    # Filtros opcionais
    tipo_servico = request.args.get('tipo_servico')
    status = request.args.get('status')
    cidade = request.args.get('cidade')
    
    query = Fornecedor.query
    
    if tipo_servico:
        query = query.filter(Fornecedor.tipo_servico == tipo_servico)
    if status:
        query = query.filter(Fornecedor.status == status)
    if cidade:
        query = query.filter(Fornecedor.cidade.ilike(f'%{cidade}%'))
    
    fornecedores = query.all()
    return jsonify([fornecedor.to_dict() for fornecedor in fornecedores])

@fornecedor_bp.route('/fornecedores', methods=['POST'])
@require_auth
def create_fornecedor():
    data = request.json
    
    # Validações
    if not data.get('nome'):
        return jsonify({'error': 'Nome é obrigatório'}), 400
    
    if not data.get('tipo_servico'):
        return jsonify({'error': 'Tipo de serviço é obrigatório'}), 400
    
    fornecedor = Fornecedor(
        nome=data['nome'],
        tipo_servico=data['tipo_servico'],
        contato=data.get('contato'),
        whatsapp=data.get('whatsapp'),
        email=data.get('email'),
        cidade=data.get('cidade'),
        prazo_medio=data.get('prazo_medio'),
        avaliacao=data.get('avaliacao'),
        status=data.get('status', 'Ativo'),
        observacoes=data.get('observacoes'),
        tabela_precos=data.get('tabela_precos')
    )
    
    db.session.add(fornecedor)
    db.session.commit()
    return jsonify(fornecedor.to_dict()), 201

@fornecedor_bp.route('/fornecedores/<int:fornecedor_id>', methods=['GET'])
@require_auth
def get_fornecedor(fornecedor_id):
    fornecedor = Fornecedor.query.get_or_404(fornecedor_id)
    return jsonify(fornecedor.to_dict())

@fornecedor_bp.route('/fornecedores/<int:fornecedor_id>', methods=['PUT'])
@require_auth
def update_fornecedor(fornecedor_id):
    fornecedor = Fornecedor.query.get_or_404(fornecedor_id)
    data = request.json
    
    fornecedor.nome = data.get('nome', fornecedor.nome)
    fornecedor.tipo_servico = data.get('tipo_servico', fornecedor.tipo_servico)
    fornecedor.contato = data.get('contato', fornecedor.contato)
    fornecedor.whatsapp = data.get('whatsapp', fornecedor.whatsapp)
    fornecedor.email = data.get('email', fornecedor.email)
    fornecedor.cidade = data.get('cidade', fornecedor.cidade)
    fornecedor.prazo_medio = data.get('prazo_medio', fornecedor.prazo_medio)
    fornecedor.avaliacao = data.get('avaliacao', fornecedor.avaliacao)
    fornecedor.status = data.get('status', fornecedor.status)
    fornecedor.observacoes = data.get('observacoes', fornecedor.observacoes)
    fornecedor.tabela_precos = data.get('tabela_precos', fornecedor.tabela_precos)
    
    db.session.commit()
    return jsonify(fornecedor.to_dict())

@fornecedor_bp.route('/fornecedores/<int:fornecedor_id>', methods=['DELETE'])
@require_auth
def delete_fornecedor(fornecedor_id):
    fornecedor = Fornecedor.query.get_or_404(fornecedor_id)
    db.session.delete(fornecedor)
    db.session.commit()
    return '', 204

@fornecedor_bp.route('/fornecedores/stats', methods=['GET'])
@require_auth
def get_fornecedores_stats():
    """Retorna estatísticas dos fornecedores"""
    total_fornecedores = Fornecedor.query.count()
    ativos = Fornecedor.query.filter_by(status='Ativo').count()
    
    # Fornecedores por tipo de serviço
    tipos_servico = db.session.query(
        Fornecedor.tipo_servico,
        db.func.count(Fornecedor.id)
    ).group_by(Fornecedor.tipo_servico).all()
    
    # Fornecedores por avaliação
    avaliacoes = db.session.query(
        Fornecedor.avaliacao,
        db.func.count(Fornecedor.id)
    ).filter(Fornecedor.avaliacao.isnot(None)).group_by(Fornecedor.avaliacao).all()
    
    return jsonify({
        'total_fornecedores': total_fornecedores,
        'ativos': ativos,
        'tipos_servico': {tipo: count for tipo, count in tipos_servico},
        'avaliacoes': {avaliacao: count for avaliacao, count in avaliacoes}
    })

