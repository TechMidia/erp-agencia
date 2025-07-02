from src.models.user import db
from datetime import datetime

class ConfiguracaoEmpresa(db.Model):
    __tablename__ = 'configuracao_empresa'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_empresa = db.Column(db.String(200), nullable=False, default='TechMídia Agência')
    logo_path = db.Column(db.String(255))  # Path do arquivo de logo
    cor_primaria = db.Column(db.String(7), default='#007bff')  # Hex color
    cor_secundaria = db.Column(db.String(7), default='#6c757d')  # Hex color
    cor_sucesso = db.Column(db.String(7), default='#28a745')  # Hex color
    cor_perigo = db.Column(db.String(7), default='#dc3545')  # Hex color
    cor_aviso = db.Column(db.String(7), default='#ffc107')  # Hex color
    cor_info = db.Column(db.String(7), default='#17a2b8')  # Hex color
    tema_escuro = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ConfiguracaoEmpresa {self.nome_empresa}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome_empresa': self.nome_empresa,
            'logo_path': self.logo_path,
            'cor_primaria': self.cor_primaria,
            'cor_secundaria': self.cor_secundaria,
            'cor_sucesso': self.cor_sucesso,
            'cor_perigo': self.cor_perigo,
            'cor_aviso': self.cor_aviso,
            'cor_info': self.cor_info,
            'tema_escuro': self.tema_escuro,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

