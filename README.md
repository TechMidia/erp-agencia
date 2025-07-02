# TechMídia ERP - Sistema de Gestão para Agências

Um sistema ERP completo e moderno desenvolvido especificamente para agências de marketing digital e publicidade. O sistema oferece gestão completa de clientes, projetos, demandas de social media, controle financeiro e um assistente IA integrado para análises inteligentes.

## 🚀 Características Principais

### ✨ Funcionalidades Core
- **Dashboard Inteligente** - KPIs em tempo real e gráficos interativos
- **Gestão de Clientes** - Controle completo do relacionamento com clientes
- **Pedidos & Projetos** - Gerenciamento de projetos com controle de prazos e margens
- **Demandas Social Media** - Workflow específico para demandas de redes sociais
- **Controle Financeiro** - Gestão de receitas, despesas e fluxo de caixa
- **Fornecedores** - Cadastro e gestão de fornecedores
- **Tabela de Preços** - Gestão de serviços e precificação

### 🤖 Assistente IA Integrado
- Análises automáticas de performance
- Insights baseados em dados reais
- Alertas proativos sobre problemas
- Recomendações de ações
- Chat interativo para consultas
- Score de saúde da empresa

### 🎨 Personalização de Marca
- Upload de logo da empresa
- Personalização completa de cores
- Preview em tempo real das mudanças
- Interface responsiva e moderna

### 👥 Sistema de Usuários
- Autenticação segura
- Diferentes níveis de permissão
- Gerenciamento de usuários
- Controle de acesso por funcionalidade

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.11** - Linguagem principal
- **Flask** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados (pode ser alterado para PostgreSQL/MySQL)
- **Flask-CORS** - Suporte a CORS
- **Werkzeug** - Utilitários web e segurança

### Frontend
- **HTML5** - Estrutura
- **CSS3** - Estilização com variáveis CSS para personalização
- **JavaScript ES6+** - Funcionalidades interativas
- **Bootstrap 5** - Framework CSS responsivo
- **Chart.js** - Gráficos e visualizações
- **Font Awesome** - Ícones

### Recursos Adicionais
- **Responsive Design** - Compatível com desktop e mobile
- **PWA Ready** - Preparado para ser uma Progressive Web App
- **API RESTful** - Arquitetura de API bem estruturada
- **Upload de Arquivos** - Sistema de upload seguro

## 📋 Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Git (para clonagem do repositório)

## 🚀 Instalação e Configuração

### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/techmedia-erp.git
cd techmedia-erp
```

### 2. Crie um Ambiente Virtual
```bash
python -m venv venv

# No Windows
venv\Scripts\activate

# No Linux/Mac
source venv/bin/activate
```

### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o Banco de Dados
O sistema criará automaticamente o banco de dados SQLite na primeira execução.

### 5. Execute o Sistema
```bash
python src/main.py
```

O sistema estará disponível em: `http://localhost:5000`

## 👤 Acesso Inicial

**Usuário padrão:**
- **Login:** admin
- **Senha:** admin

⚠️ **Importante:** Altere a senha padrão após o primeiro acesso!

## 📁 Estrutura do Projeto

```
techmedia-erp/
├── src/
│   ├── main.py                 # Arquivo principal da aplicação
│   ├── models/                 # Modelos do banco de dados
│   │   ├── user.py            # Modelo de usuários
│   │   ├── cliente.py         # Modelo de clientes
│   │   ├── pedido.py          # Modelo de pedidos
│   │   ├── demanda_social.py  # Modelo de demandas social media
│   │   ├── financeiro.py      # Modelo financeiro
│   │   ├── fornecedor.py      # Modelo de fornecedores
│   │   ├── tabela_preco.py    # Modelo de tabela de preços
│   │   └── configuracao.py    # Modelo de configurações
│   ├── routes/                # Rotas da API
│   │   ├── user.py           # Rotas de usuários
│   │   ├── cliente.py        # Rotas de clientes
│   │   ├── pedido.py         # Rotas de pedidos
│   │   ├── demanda_social.py # Rotas de demandas
│   │   ├── financeiro.py     # Rotas financeiras
│   │   ├── fornecedor.py     # Rotas de fornecedores
│   │   ├── tabela_preco.py   # Rotas de tabela de preços
│   │   ├── dashboard.py      # Rotas do dashboard
│   │   ├── assistente_ia.py  # Rotas do assistente IA
│   │   └── upload.py         # Rotas de upload
│   ├── static/               # Arquivos estáticos
│   │   ├── index.html        # Interface principal
│   │   ├── style.css         # Estilos CSS
│   │   ├── app.js           # JavaScript principal
│   │   └── uploads/         # Diretório de uploads
│   └── database/            # Banco de dados
│       └── app.db          # Arquivo SQLite (criado automaticamente)
├── venv/                   # Ambiente virtual (criado na instalação)
├── requirements.txt        # Dependências Python
├── README.md              # Este arquivo
├── INSTALL.md             # Guia de instalação detalhado
└── DEPLOY.md              # Guia de deploy em produção
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto para configurações personalizadas:

```env
# Configurações do Flask
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-aqui

# Configurações do Banco de Dados
DATABASE_URL=sqlite:///app.db

# Configurações de Upload
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=uploads
```

### Banco de Dados Alternativo
Para usar PostgreSQL ou MySQL, altere a configuração em `src/main.py`:

```python
# PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:senha@localhost/techmedia_erp'

# MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://usuario:senha@localhost/techmedia_erp'
```

## 🚀 Deploy em Produção

### Opção 1: Servidor VPS/Dedicado
Consulte o arquivo `DEPLOY.md` para instruções detalhadas de deploy.

### Opção 2: Docker
```bash
# Build da imagem
docker build -t techmedia-erp .

# Executar container
docker run -p 5000:5000 techmedia-erp
```

### Opção 3: Heroku
```bash
# Login no Heroku
heroku login

# Criar aplicação
heroku create sua-app-erp

# Deploy
git push heroku main
```

## 📊 Funcionalidades Detalhadas

### Dashboard
- KPIs em tempo real (clientes, faturamento, pedidos)
- Gráficos de faturamento histórico
- Análise de pedidos por status
- Top 5 clientes
- Resumo financeiro mensal

### Gestão de Clientes
- Cadastro completo com dados de contato
- Classificação por tipo (Pessoa Física/Jurídica)
- Status (Ativo, Inativo, Prospect, Bloqueado)
- Histórico de pedidos e valor total
- Controle de último contato

### Pedidos & Projetos
- Workflow completo (Orçamento → Aprovado → Produção → Concluído)
- Controle de prazos e datas de entrega
- Cálculo automático de margem de lucro
- Anexos e observações
- Relatórios de performance

### Demandas Social Media
- Workflow específico para redes sociais
- Controle de prioridade (Urgente, Alta, Normal, Baixa)
- Status específicos (Briefing, Criação, Aprovação, Publicado)
- Gestão de prazos e responsáveis

### Controle Financeiro
- Receitas e despesas categorizadas
- Fluxo de caixa
- Relatórios financeiros
- Controle de contas a pagar/receber
- Análise de margem por projeto

### Assistente IA
- Análise automática de performance
- Detecção de pedidos atrasados
- Alertas de margem baixa
- Sugestões de ações
- Chat interativo para consultas
- Score de saúde da empresa (0-100)

## 🔒 Segurança

- Senhas criptografadas com hash seguro
- Sessões protegidas
- Validação de entrada de dados
- Upload seguro de arquivos
- Proteção contra CSRF
- Sanitização de dados

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte técnico ou dúvidas:
- 📧 Email: suporte@techmedia.com.br
- 📱 WhatsApp: (11) 99999-9999
- 🌐 Site: https://techmedia.com.br

## 🔄 Atualizações

### Versão 1.0.0 (Atual)
- ✅ Sistema completo de ERP
- ✅ Assistente IA integrado
- ✅ Personalização de marca
- ✅ Interface responsiva
- ✅ Sistema de usuários

### Próximas Versões
- 🔄 Integração com APIs de redes sociais
- 🔄 Relatórios avançados em PDF
- 🔄 Notificações push
- 🔄 App mobile
- 🔄 Integração com sistemas de pagamento

---

**Desenvolvido com ❤️ para agências que querem crescer de forma inteligente.**

