from flask import Blueprint, jsonify, request, session
from src.models.user import db
from src.models.tabela_preco import TabelaPreco
from src.models.fornecedor import Fornecedor
from datetime import datetime

tabela_preco_bp = Blueprint('tabela_preco', __name__)

# Middleware para verificar autenticação
def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Acesso negado. Faça login primeiro.'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@tabela_preco_bp.route('/tabela-precos', methods=['GET'])
@require_auth
def get_tabela_precos():
    # Filtros opcionais
    categoria = request.args.get('categoria')
    fornecedor_id = request.args.get('fornecedor_id')
    ativo = request.args.get('ativo')
    
    query = TabelaPreco.query
    
    if categoria:
        query = query.filter(TabelaPreco.categoria == categoria)
    if fornecedor_id:
        query = query.filter(TabelaPreco.fornecedor_id == fornecedor_id)
    if ativo is not None:
        query = query.filter(TabelaPreco.ativo == (ativo.lower() == 'true'))
    
    precos = query.all()
    
    # Incluir dados do fornecedor
    result = []
    for preco in precos:
        preco_dict = preco.to_dict()
        preco_dict['fornecedor_nome'] = preco.fornecedor.nome if preco.fornecedor else None
        result.append(preco_dict)
    
    return jsonify(result)

@tabela_preco_bp.route('/tabela-precos', methods=['POST'])
@require_auth
def create_tabela_preco():
    data = request.json
    
    # Validações
    if not data.get('produto_servico'):
        return jsonify({'error': 'Produto/Serviço é obrigatório'}), 400
    
    if not data.get('categoria'):
        return jsonify({'error': 'Categoria é obrigatória'}), 400
    
    if not data.get('unidade'):
        return jsonify({'error': 'Unidade é obrigatória'}), 400
    
    # Verificar se fornecedor existe (opcional)
    if data.get('fornecedor_id'):
        fornecedor = Fornecedor.query.get(data['fornecedor_id'])
        if not fornecedor:
            return jsonify({'error': 'Fornecedor não encontrado'}), 404
    
    preco = TabelaPreco(
        produto_servico=data['produto_servico'],
        categoria=data['categoria'],
        descricao=data.get('descricao'),
        preco_custo=data.get('preco_custo', 0.0),
        markup=data.get('markup', 0.0),
        unidade=data['unidade'],
        fornecedor_id=data.get('fornecedor_id'),
        ativo=data.get('ativo', True)
    )
    
    db.session.add(preco)
    db.session.commit()
    
    result = preco.to_dict()
    result['fornecedor_nome'] = preco.fornecedor.nome if preco.fornecedor else None
    return jsonify(result), 201

@tabela_preco_bp.route('/tabela-precos/<int:preco_id>', methods=['GET'])
@require_auth
def get_tabela_preco(preco_id):
    preco = TabelaPreco.query.get_or_404(preco_id)
    result = preco.to_dict()
    result['fornecedor_nome'] = preco.fornecedor.nome if preco.fornecedor else None
    return jsonify(result)

@tabela_preco_bp.route('/tabela-precos/<int:preco_id>', methods=['PUT'])
@require_auth
def update_tabela_preco(preco_id):
    preco = TabelaPreco.query.get_or_404(preco_id)
    data = request.json
    
    if data.get('fornecedor_id'):
        fornecedor = Fornecedor.query.get(data['fornecedor_id'])
        if not fornecedor:
            return jsonify({'error': 'Fornecedor não encontrado'}), 404
        preco.fornecedor_id = data['fornecedor_id']
    
    preco.produto_servico = data.get('produto_servico', preco.produto_servico)
    preco.categoria = data.get('categoria', preco.categoria)
    preco.descricao = data.get('descricao', preco.descricao)
    preco.preco_custo = data.get('preco_custo', preco.preco_custo)
    preco.markup = data.get('markup', preco.markup)
    preco.unidade = data.get('unidade', preco.unidade)
    preco.ativo = data.get('ativo', preco.ativo)
    preco.ultima_atualizacao = datetime.utcnow()
    
    db.session.commit()
    
    result = preco.to_dict()
    result['fornecedor_nome'] = preco.fornecedor.nome if preco.fornecedor else None
    return jsonify(result)

@tabela_preco_bp.route('/tabela-precos/<int:preco_id>', methods=['DELETE'])
@require_auth
def delete_tabela_preco(preco_id):
    preco = TabelaPreco.query.get_or_404(preco_id)
    db.session.delete(preco)
    db.session.commit()
    return '', 204

@tabela_preco_bp.route('/tabela-precos/stats', methods=['GET'])
@require_auth
def get_tabela_precos_stats():
    """Retorna estatísticas da tabela de preços"""
    total_produtos = TabelaPreco.query.count()
    ativos = TabelaPreco.query.filter_by(ativo=True).count()
    
    # Produtos por categoria
    categorias = db.session.query(
        TabelaPreco.categoria,
        db.func.count(TabelaPreco.id)
    ).group_by(TabelaPreco.categoria).all()
    
    # Markup médio por categoria
    markup_medio = db.session.query(
        TabelaPreco.categoria,
        db.func.avg(TabelaPreco.markup)
    ).group_by(TabelaPreco.categoria).all()
    
    return jsonify({
        'total_produtos': total_produtos,
        'ativos': ativos,
        'categorias': {cat: count for cat, count in categorias},
        'markup_medio': {cat: round(markup, 2) for cat, markup in markup_medio if markup}
    })

