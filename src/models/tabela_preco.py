from src.models.user import db
from datetime import datetime

class TabelaPreco(db.Model):
    __tablename__ = 'tabela_preco'
    
    id = db.Column(db.Integer, primary_key=True)
    produto_servico = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)  # Social Media, Gráfica, Encarte, Branding, Consultoria
    descricao = db.Column(db.Text)
    preco_custo = db.Column(db.Float, nullable=False, default=0.0)
    markup = db.Column(db.Float, nullable=False, default=0.0)  # em percentual
    unidade = db.Column(db.String(20), nullable=False)  # Unidade, m², Pacote, Mês, Projeto
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedor.id'))
    ativo = db.Column(db.Boolean, default=True)
    ultima_atualizacao = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TabelaPreco {self.produto_servico}>'

    @property
    def preco_venda(self):
        """Calcula o preço de venda baseado no custo e markup"""
        if self.preco_custo and self.markup:
            return self.preco_custo * (1 + self.markup / 100)
        return self.preco_custo

    def to_dict(self):
        return {
            'id': self.id,
            'produto_servico': self.produto_servico,
            'categoria': self.categoria,
            'descricao': self.descricao,
            'preco_custo': self.preco_custo,
            'markup': self.markup,
            'preco_venda': self.preco_venda,
            'unidade': self.unidade,
            'fornecedor_id': self.fornecedor_id,
            'ativo': self.ativo,
            'ultima_atualizacao': self.ultima_atualizacao.isoformat() if self.ultima_atualizacao else None
        }

