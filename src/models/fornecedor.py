from src.models.user import db
from datetime import datetime

class Fornecedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    tipo_servico = db.Column(db.String(50), nullable=False)  # Gráfica, Aplicação, Fardamento, Outros
    contato = db.Column(db.String(200))
    whatsapp = db.Column(db.String(20))
    email = db.Column(db.String(120))
    cidade = db.Column(db.String(100))
    prazo_medio = db.Column(db.Integer)  # em dias
    avaliacao = db.Column(db.Integer)  # 1 a 5 estrelas
    status = db.Column(db.String(20), nullable=False, default='Ativo')  # Ativo, Teste, Inativo
    observacoes = db.Column(db.Text)
    tabela_precos = db.Column(db.String(255))  # Path do arquivo da tabela de preços
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    produtos_servicos = db.relationship('TabelaPreco', backref='fornecedor', lazy=True)

    def __repr__(self):
        return f'<Fornecedor {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo_servico': self.tipo_servico,
            'contato': self.contato,
            'whatsapp': self.whatsapp,
            'email': self.email,
            'cidade': self.cidade,
            'prazo_medio': self.prazo_medio,
            'avaliacao': self.avaliacao,
            'status': self.status,
            'observacoes': self.observacoes,
            'tabela_precos': self.tabela_precos,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

