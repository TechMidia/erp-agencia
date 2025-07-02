from flask import Blueprint, jsonify, request, session
from src.models.user import db
from src.models.configuracao import ConfiguracaoEmpresa
import os
from werkzeug.utils import secure_filename
import uuid

upload_bp = Blueprint('upload', __name__)

# Configurações de upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Middleware para verificar autenticação
def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Acesso negado. Faça login primeiro.'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@upload_bp.route('/upload/logo', methods=['POST'])
@require_auth
def upload_logo():
    """Upload do logo da empresa"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and allowed_file(file.filename):
            # Criar diretório de upload se não existir
            upload_dir = os.path.join(os.path.dirname(__file__), '..', 'static', UPLOAD_FOLDER)
            os.makedirs(upload_dir, exist_ok=True)
            
            # Gerar nome único para o arquivo
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            filename = f"logo_{uuid.uuid4().hex}.{file_extension}"
            filepath = os.path.join(upload_dir, filename)
            
            # Salvar arquivo
            file.save(filepath)
            
            # Atualizar configuração da empresa
            config = ConfiguracaoEmpresa.query.first()
            if not config:
                config = ConfiguracaoEmpresa()
                db.session.add(config)
            
            # Remover logo anterior se existir
            if config.logo_path:
                old_logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', config.logo_path)
                if os.path.exists(old_logo_path):
                    os.remove(old_logo_path)
            
            config.logo_path = f"{UPLOAD_FOLDER}/{filename}"
            db.session.commit()
            
            return jsonify({
                'message': 'Logo enviado com sucesso',
                'logo_path': config.logo_path,
                'logo_url': f"/static/{config.logo_path}"
            }), 200
        
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
    
    except Exception as e:
        return jsonify({'error': f'Erro no upload: {str(e)}'}), 500

@upload_bp.route('/upload/arquivo', methods=['POST'])
@require_auth
def upload_arquivo():
    """Upload genérico de arquivos"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        categoria = request.form.get('categoria', 'geral')  # geral, comprovante, tabela_precos, etc.
        
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file:
            # Criar diretório de upload se não existir
            upload_dir = os.path.join(os.path.dirname(__file__), '..', 'static', UPLOAD_FOLDER, categoria)
            os.makedirs(upload_dir, exist_ok=True)
            
            # Gerar nome único para o arquivo
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(upload_dir, filename)
            
            # Salvar arquivo
            file.save(filepath)
            
            return jsonify({
                'message': 'Arquivo enviado com sucesso',
                'filename': filename,
                'filepath': f"{UPLOAD_FOLDER}/{categoria}/{filename}",
                'url': f"/static/{UPLOAD_FOLDER}/{categoria}/{filename}"
            }), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro no upload: {str(e)}'}), 500

@upload_bp.route('/upload/remover', methods=['DELETE'])
@require_auth
def remover_arquivo():
    """Remove um arquivo do servidor"""
    try:
        data = request.json
        filepath = data.get('filepath')
        
        if not filepath:
            return jsonify({'error': 'Caminho do arquivo é obrigatório'}), 400
        
        # Verificar se o arquivo está dentro do diretório permitido
        if not filepath.startswith(UPLOAD_FOLDER):
            return jsonify({'error': 'Caminho de arquivo inválido'}), 400
        
        full_path = os.path.join(os.path.dirname(__file__), '..', 'static', filepath)
        
        if os.path.exists(full_path):
            os.remove(full_path)
            return jsonify({'message': 'Arquivo removido com sucesso'}), 200
        else:
            return jsonify({'error': 'Arquivo não encontrado'}), 404
    
    except Exception as e:
        return jsonify({'error': f'Erro ao remover arquivo: {str(e)}'}), 500

