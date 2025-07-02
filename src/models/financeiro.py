from src.models.user import db
from datetime import datetime

class TransacaoFinanceira(db.Model):
    __tablename__ = 'transacao_financeira'
    
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # Receita, Despesa
    categoria = db.Column(db.String(50), nullable=False)  # Vendas, Fornecedores, Salários, Ferramentas, Marketing, Escritório, Outros
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Pendente')  # Pago, Pendente, Atrasado
    cliente_fornecedor = db.Column(db.String(200))
    forma_pagamento = db.Column(db.String(50))  # Dinheiro, PIX, Cartão, Transferência, Boleto
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'))
    observacoes = db.Column(db.Text)
    comprovante = db.Column(db.String(255))  # Path do arquivo de comprovante

    def __repr__(self):
        return f'<TransacaoFinanceira {self.descricao}>'

    def to_dict(self):
        return {
            'id': self.id,
            'descricao': self.descricao,
            'tipo': self.tipo,
            'categoria': self.categoria,
            'valor': self.valor,
            'data': self.data.isoformat() if self.data else None,
            'status': self.status,
            'cliente_fornecedor': self.cliente_fornecedor,
            'forma_pagamento': self.forma_pagamento,
            'pedido_id': self.pedido_id,
            'observacoes': self.observacoes,
            'comprovante': self.comprovante
        }

