from src.models.user import db
from datetime import datetime

class DemandaSocialMedia(db.Model):
    __tablename__ = 'demanda_social_media'
    
    id = db.Column(db.Integer, primary_key=True)
    demanda = db.Column(db.String(200), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'))
    tipo_arte = db.Column(db.String(50), nullable=False)  # Post Simples, Carrossel, Stories, Reels, Capa
    tema_conteudo = db.Column(db.Text)
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_entrega = db.Column(db.DateTime)
    status = db.Column(db.String(30), nullable=False, default='Briefing')  # Briefing, Criação, Aguardando Aprovação, Aprovado, Publicado
    prioridade = db.Column(db.String(20), default='Normal')  # Urgente, Alta, Normal
    observacoes = db.Column(db.Text)
    arquivo_final = db.Column(db.String(255))  # Path do arquivo final
    aprovado = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<DemandaSocialMedia {self.demanda}>'

    @property
    def dias_para_entrega(self):
        """Calcula quantos dias faltam para a entrega"""
        if self.data_entrega:
            delta = self.data_entrega - datetime.utcnow()
            return delta.days
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'demanda': self.demanda,
            'cliente_id': self.cliente_id,
            'pedido_id': self.pedido_id,
            'tipo_arte': self.tipo_arte,
            'tema_conteudo': self.tema_conteudo,
            'data_solicitacao': self.data_solicitacao.isoformat() if self.data_solicitacao else None,
            'data_entrega': self.data_entrega.isoformat() if self.data_entrega else None,
            'status': self.status,
            'prioridade': self.prioridade,
            'observacoes': self.observacoes,
            'arquivo_final': self.arquivo_final,
            'aprovado': self.aprovado,
            'dias_para_entrega': self.dias_para_entrega
        }

