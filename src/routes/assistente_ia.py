from flask import Blueprint, jsonify, request, session
from src.models.user import db
from src.models.cliente import Cliente
from src.models.pedido import Pedido
from src.models.demanda_social import DemandaSocialMedia
from src.models.financeiro import TransacaoFinanceira
from datetime import datetime, timedelta
import json

assistente_ia_bp = Blueprint('assistente_ia', __name__)

# Middleware para verificar autenticação
def require_auth(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Acesso negado. Faça login primeiro.'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

class AssistenteIA:
    """Assistente IA para análise de dados do ERP"""
    
    @staticmethod
    def analisar_performance_geral():
        """Analisa a performance geral da empresa"""
        insights = []
        alertas = []
        recomendacoes = []
        
        # Análise de clientes
        total_clientes = Cliente.query.count()
        clientes_ativos = Cliente.query.filter_by(status='Ativo').count()
        prospects = Cliente.query.filter_by(status='Prospect').count()
        
        if total_clientes > 0:
            taxa_conversao = (clientes_ativos / total_clientes) * 100
            if taxa_conversao < 50:
                alertas.append({
                    'tipo': 'warning',
                    'titulo': 'Taxa de Conversão Baixa',
                    'descricao': f'Apenas {taxa_conversao:.1f}% dos clientes estão ativos. Considere estratégias de reativação.',
                    'categoria': 'clientes'
                })
            else:
                insights.append({
                    'tipo': 'success',
                    'titulo': 'Boa Taxa de Conversão',
                    'descricao': f'Taxa de conversão de {taxa_conversao:.1f}% está acima da média.',
                    'categoria': 'clientes'
                })
        
        if prospects > clientes_ativos:
            recomendacoes.append({
                'titulo': 'Foque na Conversão de Prospects',
                'descricao': f'Você tem {prospects} prospects vs {clientes_ativos} clientes ativos. Intensifique o follow-up.',
                'prioridade': 'alta',
                'categoria': 'vendas'
            })
        
        # Análise de pedidos
        pedidos_atrasados = Pedido.query.filter(
            Pedido.data_entrega < datetime.utcnow(),
            Pedido.status != 'Concluído'
        ).count()
        
        if pedidos_atrasados > 0:
            alertas.append({
                'tipo': 'danger',
                'titulo': 'Pedidos Atrasados',
                'descricao': f'{pedidos_atrasados} pedidos estão atrasados. Revise os prazos e capacidade da equipe.',
                'categoria': 'operacional'
            })
        
        # Análise financeira
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        receitas_mes = db.session.query(db.func.sum(TransacaoFinanceira.valor)).filter(
            TransacaoFinanceira.tipo == 'Receita',
            TransacaoFinanceira.data >= inicio_mes
        ).scalar() or 0
        
        despesas_mes = db.session.query(db.func.sum(TransacaoFinanceira.valor)).filter(
            TransacaoFinanceira.tipo == 'Despesa',
            TransacaoFinanceira.data >= inicio_mes
        ).scalar() or 0
        
        if despesas_mes > receitas_mes:
            alertas.append({
                'tipo': 'danger',
                'titulo': 'Despesas Superiores às Receitas',
                'descricao': f'Este mês as despesas (R$ {despesas_mes:.2f}) superam as receitas (R$ {receitas_mes:.2f}).',
                'categoria': 'financeiro'
            })
        
        # Análise de margem
        pedidos_concluidos = Pedido.query.filter_by(status='Concluído').all()
        if pedidos_concluidos:
            margens = [p.margem for p in pedidos_concluidos if p.valor and p.valor > 0]
            if margens:
                margem_media = sum(margens) / len(margens)
                if margem_media < 20:
                    alertas.append({
                        'tipo': 'warning',
                        'titulo': 'Margem Baixa',
                        'descricao': f'Margem média de {margem_media:.1f}% está abaixo do recomendado (20%+).',
                        'categoria': 'financeiro'
                    })
                    recomendacoes.append({
                        'titulo': 'Otimize a Margem de Lucro',
                        'descricao': 'Revise a tabela de preços e negocie melhores condições com fornecedores.',
                        'prioridade': 'alta',
                        'categoria': 'financeiro'
                    })
        
        return {
            'insights': insights,
            'alertas': alertas,
            'recomendacoes': recomendacoes
        }
    
    @staticmethod
    def analisar_tendencias():
        """Analisa tendências dos últimos meses"""
        tendencias = []
        
        # Análise de faturamento dos últimos 6 meses
        faturamentos = []
        for i in range(6):
            data_ref = datetime.now().replace(day=1) - timedelta(days=30 * i)
            inicio = data_ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            fim = (inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            faturamento = db.session.query(db.func.sum(Pedido.valor)).filter(
                Pedido.data_pedido >= inicio,
                Pedido.data_pedido <= fim,
                Pedido.status == 'Concluído'
            ).scalar() or 0
            
            faturamentos.insert(0, faturamento)
        
        # Calcular tendência
        if len(faturamentos) >= 3:
            ultimos_3 = sum(faturamentos[-3:]) / 3
            primeiros_3 = sum(faturamentos[:3]) / 3
            
            if ultimos_3 > primeiros_3 * 1.1:
                tendencias.append({
                    'tipo': 'crescimento',
                    'titulo': 'Faturamento em Crescimento',
                    'descricao': f'Faturamento cresceu {((ultimos_3/primeiros_3-1)*100):.1f}% nos últimos meses.',
                    'categoria': 'financeiro'
                })
            elif ultimos_3 < primeiros_3 * 0.9:
                tendencias.append({
                    'tipo': 'declinio',
                    'titulo': 'Faturamento em Declínio',
                    'descricao': f'Faturamento caiu {((1-ultimos_3/primeiros_3)*100):.1f}% nos últimos meses.',
                    'categoria': 'financeiro'
                })
        
        return tendencias
    
    @staticmethod
    def sugerir_acoes():
        """Sugere ações baseadas nos dados atuais"""
        acoes = []
        
        # Verificar demandas urgentes
        demandas_urgentes = DemandaSocialMedia.query.filter_by(prioridade='Urgente').count()
        if demandas_urgentes > 0:
            acoes.append({
                'titulo': 'Priorizar Demandas Urgentes',
                'descricao': f'Existem {demandas_urgentes} demandas marcadas como urgentes.',
                'tipo': 'acao_imediata',
                'categoria': 'operacional'
            })
        
        # Verificar clientes sem contato recente
        um_mes_atras = datetime.now() - timedelta(days=30)
        clientes_sem_contato = Cliente.query.filter(
            Cliente.ultimo_contato < um_mes_atras,
            Cliente.status == 'Ativo'
        ).count()
        
        if clientes_sem_contato > 0:
            acoes.append({
                'titulo': 'Reativar Relacionamento com Clientes',
                'descricao': f'{clientes_sem_contato} clientes ativos não têm contato há mais de 30 dias.',
                'tipo': 'relacionamento',
                'categoria': 'vendas'
            })
        
        # Verificar oportunidades de upsell
        clientes_com_poucos_pedidos = Cliente.query.all()
        clientes_oportunidade = [c for c in clientes_com_poucos_pedidos if c.qtd_pedidos == 1 and c.status == 'Ativo']
        
        if clientes_oportunidade:
            acoes.append({
                'titulo': 'Oportunidades de Upsell',
                'descricao': f'{len(clientes_oportunidade)} clientes ativos fizeram apenas 1 pedido. Ofereça novos serviços.',
                'tipo': 'oportunidade',
                'categoria': 'vendas'
            })
        
        return acoes

@assistente_ia_bp.route('/assistente-ia/analise-geral', methods=['GET'])
@require_auth
def get_analise_geral():
    """Retorna análise geral da performance"""
    try:
        analise = AssistenteIA.analisar_performance_geral()
        return jsonify(analise)
    except Exception as e:
        return jsonify({'error': f'Erro na análise: {str(e)}'}), 500

@assistente_ia_bp.route('/assistente-ia/tendencias', methods=['GET'])
@require_auth
def get_tendencias():
    """Retorna análise de tendências"""
    try:
        tendencias = AssistenteIA.analisar_tendencias()
        return jsonify({'tendencias': tendencias})
    except Exception as e:
        return jsonify({'error': f'Erro na análise de tendências: {str(e)}'}), 500

@assistente_ia_bp.route('/assistente-ia/sugestoes', methods=['GET'])
@require_auth
def get_sugestoes():
    """Retorna sugestões de ações"""
    try:
        acoes = AssistenteIA.sugerir_acoes()
        return jsonify({'acoes': acoes})
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar sugestões: {str(e)}'}), 500

@assistente_ia_bp.route('/assistente-ia/relatorio-completo', methods=['GET'])
@require_auth
def get_relatorio_completo():
    """Retorna relatório completo do assistente IA"""
    try:
        analise_geral = AssistenteIA.analisar_performance_geral()
        tendencias = AssistenteIA.analisar_tendencias()
        acoes = AssistenteIA.sugerir_acoes()
        
        # Estatísticas resumidas
        total_clientes = Cliente.query.count()
        total_pedidos = Pedido.query.count()
        pedidos_mes = Pedido.query.filter(
            Pedido.data_pedido >= datetime.now().replace(day=1)
        ).count()
        
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'resumo': {
                'total_clientes': total_clientes,
                'total_pedidos': total_pedidos,
                'pedidos_mes': pedidos_mes
            },
            'analise_geral': analise_geral,
            'tendencias': tendencias,
            'acoes_sugeridas': acoes,
            'score_saude': AssistenteIA.calcular_score_saude()
        }
        
        return jsonify(relatorio)
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar relatório: {str(e)}'}), 500

@assistente_ia_bp.route('/assistente-ia/pergunta', methods=['POST'])
@require_auth
def responder_pergunta():
    """Responde perguntas específicas sobre os dados"""
    try:
        data = request.json
        pergunta = data.get('pergunta', '').lower()
        
        resposta = AssistenteIA.processar_pergunta(pergunta)
        return jsonify({'resposta': resposta})
    except Exception as e:
        return jsonify({'error': f'Erro ao processar pergunta: {str(e)}'}), 500

# Métodos auxiliares para o AssistenteIA
def calcular_score_saude():
    """Calcula um score de saúde da empresa (0-100)"""
    score = 100
    
    # Penalizar por pedidos atrasados
    pedidos_atrasados = Pedido.query.filter(
        Pedido.data_entrega < datetime.utcnow(),
        Pedido.status != 'Concluído'
    ).count()
    total_pedidos = Pedido.query.count()
    
    if total_pedidos > 0:
        taxa_atraso = pedidos_atrasados / total_pedidos
        score -= taxa_atraso * 30
    
    # Penalizar por margem baixa
    pedidos_concluidos = Pedido.query.filter_by(status='Concluído').all()
    if pedidos_concluidos:
        margens = [p.margem for p in pedidos_concluidos if p.valor and p.valor > 0]
        if margens:
            margem_media = sum(margens) / len(margens)
            if margem_media < 20:
                score -= (20 - margem_media) * 2
    
    # Bonificar por crescimento
    inicio_mes = datetime.now().replace(day=1)
    mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)
    
    pedidos_mes_atual = Pedido.query.filter(Pedido.data_pedido >= inicio_mes).count()
    pedidos_mes_anterior = Pedido.query.filter(
        Pedido.data_pedido >= mes_anterior,
        Pedido.data_pedido < inicio_mes
    ).count()
    
    if pedidos_mes_anterior > 0 and pedidos_mes_atual > pedidos_mes_anterior:
        score += 10
    
    return max(0, min(100, round(score)))

def processar_pergunta(pergunta):
    """Processa perguntas em linguagem natural"""
    pergunta = pergunta.lower()
    
    if 'faturamento' in pergunta or 'receita' in pergunta:
        inicio_mes = datetime.now().replace(day=1)
        faturamento = db.session.query(db.func.sum(Pedido.valor)).filter(
            Pedido.data_pedido >= inicio_mes,
            Pedido.status == 'Concluído'
        ).scalar() or 0
        return f"O faturamento deste mês é de R$ {faturamento:.2f}."
    
    elif 'cliente' in pergunta:
        total = Cliente.query.count()
        ativos = Cliente.query.filter_by(status='Ativo').count()
        return f"Você tem {total} clientes cadastrados, sendo {ativos} ativos."
    
    elif 'pedido' in pergunta:
        total = Pedido.query.count()
        andamento = Pedido.query.filter(Pedido.status.in_(['Aprovado', 'Produção'])).count()
        return f"Existem {total} pedidos no total, com {andamento} em andamento."
    
    elif 'atraso' in pergunta:
        atrasados = Pedido.query.filter(
            Pedido.data_entrega < datetime.utcnow(),
            Pedido.status != 'Concluído'
        ).count()
        return f"Há {atrasados} pedidos atrasados no momento."
    
    else:
        return "Desculpe, não entendi sua pergunta. Tente perguntar sobre faturamento, clientes, pedidos ou atrasos."

# Adicionar métodos ao AssistenteIA
AssistenteIA.calcular_score_saude = staticmethod(calcular_score_saude)
AssistenteIA.processar_pergunta = staticmethod(processar_pergunta)

