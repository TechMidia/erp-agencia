import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.cliente import cliente_bp
from src.routes.pedido import pedido_bp
from src.routes.demanda_social import demanda_social_bp
from src.routes.financeiro import financeiro_bp
from src.routes.fornecedor import fornecedor_bp
from src.routes.tabela_preco import tabela_preco_bp
from src.routes.dashboard import dashboard_bp
from src.routes.assistente_ia import assistente_ia_bp
from src.routes.upload import upload_bp

# Importar todos os modelos para que sejam criados no banco
from src.models.cliente import Cliente
from src.models.pedido import Pedido
from src.models.demanda_social import DemandaSocialMedia
from src.models.financeiro import TransacaoFinanceira
from src.models.fornecedor import Fornecedor
from src.models.tabela_preco import TabelaPreco
from src.models.configuracao import ConfiguracaoEmpresa

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para todas as rotas
CORS(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(cliente_bp, url_prefix='/api')
app.register_blueprint(pedido_bp, url_prefix='/api')
app.register_blueprint(demanda_social_bp, url_prefix='/api')
app.register_blueprint(financeiro_bp, url_prefix='/api')
app.register_blueprint(fornecedor_bp, url_prefix='/api')
app.register_blueprint(tabela_preco_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')
app.register_blueprint(assistente_ia_bp, url_prefix='/api')
app.register_blueprint(upload_bp, url_prefix='/api')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    
    # Criar usuário admin padrão se não existir
    from src.models.user import User
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@techmidiaagencia.com',
            role='admin'
        )
        admin_user.set_password('admin')
        db.session.add(admin_user)
        
        # Criar configuração padrão da empresa
        config = ConfiguracaoEmpresa()
        db.session.add(config)
        
        db.session.commit()
        print("Usuário admin criado com sucesso!")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
