from flask import Blueprint, jsonify, request, session
from src.models.user import User, db
from datetime import datetime
import json

user_bp = Blueprint('user', __name__)

# Middleware para verificar autenticação
def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Acesso negado. Faça login primeiro.'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_admin(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Acesso negado. Faça login primeiro.'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Acesso negado. Apenas administradores.'}), 403
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Rotas de autenticação
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username e password são obrigatórios'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password) and user.is_active:
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        
        # Atualizar último login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict()
        }), 200
    else:
        return jsonify({'error': 'Credenciais inválidas ou usuário inativo'}), 401

@user_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    session.clear()
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@user_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    user = User.query.get(session['user_id'])
    return jsonify(user.to_dict())

# Rotas de gerenciamento de usuários
@user_bp.route('/users', methods=['GET'])
@require_admin
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
@require_admin
def create_user():
    data = request.json
    
    # Validações
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email e password são obrigatórios'}), 400
    
    # Verificar se username já existe
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username já existe'}), 400
    
    # Verificar se email já existe
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email já existe'}), 400
    
    user = User(
        username=data['username'], 
        email=data['email'],
        role=data.get('role', 'user'),
        permissions=json.dumps(data.get('permissions', {})) if data.get('permissions') else None
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    # Usuários podem ver apenas seus próprios dados, admins podem ver todos
    current_user = User.query.get(session['user_id'])
    if current_user.role != 'admin' and current_user.id != user_id:
        return jsonify({'error': 'Acesso negado'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_admin
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # Verificar se username já existe (exceto para o próprio usuário)
    if data.get('username') and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username já existe'}), 400
    
    # Verificar se email já existe (exceto para o próprio usuário)
    if data.get('email') and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já existe'}), 400
    
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.role = data.get('role', user.role)
    user.is_active = data.get('is_active', user.is_active)
    
    if data.get('permissions'):
        user.permissions = json.dumps(data['permissions'])
    
    if data.get('password'):
        user.set_password(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Não permitir deletar o próprio usuário
    if user.id == session['user_id']:
        return jsonify({'error': 'Não é possível deletar seu próprio usuário'}), 400
    
    db.session.delete(user)
    db.session.commit()
    return '', 204

@user_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
    
    user = User.query.get(session['user_id'])
    
    if not user.check_password(current_password):
        return jsonify({'error': 'Senha atual incorreta'}), 400
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({'message': 'Senha alterada com sucesso'}), 200
