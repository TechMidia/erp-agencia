from src.models.user import db
from datetime import datetime

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Varejista, Prefeitura, Pessoa Física, Outros
    cidade = db.Column(db.String(100))
    populacao = db.Column(db.Integer)
    contato_principal = db.Column(db.String(200))
    whatsapp = db.Column(db.String(20))
    email = db.Column(db.String(120))
    status = db.Column(db.String(20), nullable=False, default='Prospect')  # Ativo, Prospect, Inativo, Bloqueado
    segmento = db.Column(db.String(50))  # Alimentação, Moda, Farmácia, Eletrônicos, Outros
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_contato = db.Column(db.DateTime)
    observacoes = db.Column(db.Text)
    
    # Relacionamentos
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)
    demandas_social = db.relationship('DemandaSocialMedia', backref='cliente', lazy=True)

    def __repr__(self):
        return f'<Cliente {self.nome}>'

    @property
    def valor_total(self):
        """Calcula o valor total de todos os pedidos do cliente"""
        return sum(pedido.valor or 0 for pedido in self.pedidos)

    @property
    def qtd_pedidos(self):
        """Conta a quantidade de pedidos do cliente"""
        return len(self.pedidos)

    @property
    def ticket_medio(self):
        """Calcula o ticket médio do cliente"""
        if self.qtd_pedidos > 0:
            return self.valor_total / self.qtd_pedidos
        return 0

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'cidade': self.cidade,
            'populacao': self.populacao,
            'contato_principal': self.contato_principal,
            'whatsapp': self.whatsapp,
            'email': self.email,
            'status': self.status,
            'segmento': self.segmento,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'ultimo_contato': self.ultimo_contato.isoformat() if self.ultimo_contato else None,
            'observacoes': self.observacoes,
            'valor_total': self.valor_total,
            'qtd_pedidos': self.qtd_pedidos,
            'ticket_medio': self.ticket_medio
        }

