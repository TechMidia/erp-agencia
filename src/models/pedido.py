from src.models.user import db
from datetime import datetime

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.String(50), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    tipo_servico = db.Column(db.String(50), nullable=False)  # Social Media, Gráfica, Encarte, Branding, Consultoria
    descricao = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='Orçamento')  # Orçamento, Aprovado, Produção, Concluído, Cancelado
    prioridade = db.Column(db.String(20), default='Normal')  # Urgente, Alta, Normal, Baixa
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    data_entrega = db.Column(db.DateTime)
    responsavel = db.Column(db.String(50))  # Yuri, Laina, Alysson, Externo
    valor = db.Column(db.Float, default=0.0)
    custo = db.Column(db.Float, default=0.0)
    forma_pagamento = db.Column(db.String(50))  # Dinheiro, PIX, Cartão, Transferência, Boleto
    status_pagamento = db.Column(db.String(20), default='Pendente')  # Pendente, Parcial, Pago
    observacoes = db.Column(db.Text)
    arquivos = db.Column(db.Text)  # JSON string com paths dos arquivos
    
    # Relacionamentos
    demandas_social = db.relationship('DemandaSocialMedia', backref='pedido', lazy=True)
    transacoes_financeiras = db.relationship('TransacaoFinanceira', backref='pedido', lazy=True)

    def __repr__(self):
        return f'<Pedido {self.id_pedido}>'

    @property
    def margem(self):
        """Calcula a margem do pedido em percentual"""
        if self.valor and self.valor > 0:
            return ((self.valor - (self.custo or 0)) / self.valor) * 100
        return 0

    @property
    def dias_para_entrega(self):
        """Calcula quantos dias faltam para a entrega"""
        if self.data_entrega:
            delta = self.data_entrega - datetime.utcnow()
            return delta.days
        return None

    @property
    def status_prazo(self):
        """Retorna o status do prazo (Atrasado, Urgente, No Prazo)"""
        if not self.data_entrega or self.status == 'Concluído':
            return 'No Prazo'
        
        dias = self.dias_para_entrega
        if dias < 0:
            return 'Atrasado'
        elif dias <= 3:
            return 'Urgente'
        else:
            return 'No Prazo'

    def to_dict(self):
        return {
            'id': self.id,
            'id_pedido': self.id_pedido,
            'cliente_id': self.cliente_id,
            'tipo_servico': self.tipo_servico,
            'descricao': self.descricao,
            'status': self.status,
            'prioridade': self.prioridade,
            'data_pedido': self.data_pedido.isoformat() if self.data_pedido else None,
            'data_entrega': self.data_entrega.isoformat() if self.data_entrega else None,
            'responsavel': self.responsavel,
            'valor': self.valor,
            'custo': self.custo,
            'margem': self.margem,
            'forma_pagamento': self.forma_pagamento,
            'status_pagamento': self.status_pagamento,
            'observacoes': self.observacoes,
            'arquivos': self.arquivos,
            'dias_para_entrega': self.dias_para_entrega,
            'status_prazo': self.status_prazo
        }

