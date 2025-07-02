# 📋 Guia de Instalação Detalhado - TechMídia ERP

Este guia fornece instruções passo a passo para instalar e configurar o TechMídia ERP em diferentes ambientes.

## 🖥️ Requisitos do Sistema

### Requisitos Mínimos
- **Sistema Operacional:** Windows 10, macOS 10.14, Ubuntu 18.04 ou superior
- **Python:** 3.11 ou superior
- **RAM:** 2GB mínimo (4GB recomendado)
- **Espaço em Disco:** 500MB livres
- **Navegador:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

### Requisitos Recomendados para Produção
- **Sistema Operacional:** Ubuntu 20.04 LTS ou CentOS 8
- **Python:** 3.11
- **RAM:** 8GB ou superior
- **Espaço em Disco:** 10GB livres
- **CPU:** 2 cores ou superior
- **Banco de Dados:** PostgreSQL 13+ ou MySQL 8+

## 🚀 Instalação Rápida (Desenvolvimento)

### 1. Preparação do Ambiente

#### Windows
```cmd
# Instalar Python (se não estiver instalado)
# Baixe de: https://python.org/downloads/

# Verificar instalação
python --version
pip --version

# Instalar Git (se não estiver instalado)
# Baixe de: https://git-scm.com/downloads
```

#### macOS
```bash
# Instalar Homebrew (se não estiver instalado)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python
brew install python@3.11

# Instalar Git
brew install git
```

#### Ubuntu/Debian
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install python3.11 python3.11-venv python3-pip git -y

# Verificar instalação
python3.11 --version
pip3 --version
```

### 2. Download e Configuração

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/techmedia-erp.git
cd techmedia-erp

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar o sistema
python src/main.py
```

### 3. Primeiro Acesso
1. Abra o navegador e acesse: `http://localhost:5000`
2. Use as credenciais padrão:
   - **Usuário:** admin
   - **Senha:** admin
3. Altere a senha após o primeiro login!

## 🔧 Instalação Avançada

### Configuração com PostgreSQL

#### 1. Instalar PostgreSQL
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib -y

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib -y
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql

# macOS
brew install postgresql
brew services start postgresql
```

#### 2. Criar Banco de Dados
```sql
# Conectar ao PostgreSQL
sudo -u postgres psql

# Criar usuário e banco
CREATE USER techmedia WITH PASSWORD 'senha_segura';
CREATE DATABASE techmedia_erp OWNER techmedia;
GRANT ALL PRIVILEGES ON DATABASE techmedia_erp TO techmedia;
\q
```

#### 3. Configurar Aplicação
```bash
# Instalar driver PostgreSQL
pip install psycopg2-binary

# Criar arquivo .env
cat > .env << EOF
DATABASE_URL=postgresql://techmedia:senha_segura@localhost/techmedia_erp
SECRET_KEY=sua_chave_secreta_muito_segura_aqui
FLASK_ENV=production
EOF
```

#### 4. Atualizar Configuração
Edite `src/main.py` e adicione:
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração do banco
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
```

### Configuração com MySQL

#### 1. Instalar MySQL
```bash
# Ubuntu/Debian
sudo apt install mysql-server -y
sudo mysql_secure_installation

# CentOS/RHEL
sudo yum install mysql-server -y
sudo systemctl enable mysqld
sudo systemctl start mysqld
sudo mysql_secure_installation
```

#### 2. Criar Banco de Dados
```sql
# Conectar ao MySQL
mysql -u root -p

# Criar usuário e banco
CREATE DATABASE techmedia_erp;
CREATE USER 'techmedia'@'localhost' IDENTIFIED BY 'senha_segura';
GRANT ALL PRIVILEGES ON techmedia_erp.* TO 'techmedia'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. Configurar Aplicação
```bash
# Instalar driver MySQL
pip install PyMySQL

# Atualizar .env
DATABASE_URL=mysql+pymysql://techmedia:senha_segura@localhost/techmedia_erp
```

## 🐳 Instalação com Docker

### 1. Criar Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY .env .

EXPOSE 5000

CMD ["python", "src/main.py"]
```

### 2. Criar docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://techmedia:senha@db:5432/techmedia_erp
    depends_on:
      - db
    volumes:
      - ./uploads:/app/src/static/uploads

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: techmedia_erp
      POSTGRES_USER: techmedia
      POSTGRES_PASSWORD: senha
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### 3. Executar com Docker
```bash
# Build e execução
docker-compose up -d

# Verificar logs
docker-compose logs -f app

# Parar serviços
docker-compose down
```

## 🌐 Configuração para Produção

### 1. Configurações de Segurança
```python
# src/main.py - Adicionar configurações de produção
if os.getenv('FLASK_ENV') == 'production':
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
    )
```

### 2. Servidor WSGI (Gunicorn)
```bash
# Instalar Gunicorn
pip install gunicorn

# Executar em produção
gunicorn --bind 0.0.0.0:5000 --workers 4 src.main:app

# Ou criar arquivo gunicorn.conf.py
cat > gunicorn.conf.py << EOF
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
EOF

# Executar com configuração
gunicorn -c gunicorn.conf.py src.main:app
```

### 3. Proxy Reverso (Nginx)
```nginx
# /etc/nginx/sites-available/techmedia-erp
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /caminho/para/techmedia-erp/src/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 4. SSL com Let's Encrypt
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado
sudo certbot --nginx -d seu-dominio.com

# Renovação automática
sudo crontab -e
# Adicionar linha:
0 12 * * * /usr/bin/certbot renew --quiet
```

### 5. Systemd Service
```ini
# /etc/systemd/system/techmedia-erp.service
[Unit]
Description=TechMidia ERP
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/techmedia-erp
Environment=PATH=/var/www/techmedia-erp/venv/bin
ExecStart=/var/www/techmedia-erp/venv/bin/gunicorn -c gunicorn.conf.py src.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar serviço
sudo systemctl daemon-reload
sudo systemctl enable techmedia-erp
sudo systemctl start techmedia-erp
sudo systemctl status techmedia-erp
```

## 🔧 Solução de Problemas

### Problemas Comuns

#### Erro: "ModuleNotFoundError"
```bash
# Verificar se o ambiente virtual está ativo
which python
# Deve mostrar o caminho do venv

# Reinstalar dependências
pip install -r requirements.txt
```

#### Erro: "Permission denied" no upload
```bash
# Criar diretório de uploads
mkdir -p src/static/uploads
chmod 755 src/static/uploads

# No Linux, verificar permissões
sudo chown -R $USER:$USER src/static/uploads
```

#### Erro de conexão com banco de dados
```bash
# Verificar se o serviço está rodando
sudo systemctl status postgresql
# ou
sudo systemctl status mysql

# Testar conexão
psql -h localhost -U techmedia -d techmedia_erp
# ou
mysql -h localhost -u techmedia -p techmedia_erp
```

#### Porta 5000 já em uso
```bash
# Verificar processo usando a porta
sudo lsof -i :5000

# Matar processo se necessário
sudo kill -9 PID

# Ou usar porta diferente
python src/main.py --port 8000
```

### Logs e Debugging

#### Habilitar logs detalhados
```python
# src/main.py - Adicionar no início
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Verificar logs do sistema
```bash
# Logs da aplicação
tail -f /var/log/techmedia-erp.log

# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs do sistema
sudo journalctl -u techmedia-erp -f
```

## 📞 Suporte

Se você encontrar problemas durante a instalação:

1. Verifique os logs de erro
2. Consulte a seção de solução de problemas
3. Procure por issues similares no GitHub
4. Entre em contato com o suporte técnico

**Contatos:**
- 📧 Email: suporte@techmedia.com.br
- 💬 GitHub Issues: https://github.com/seu-usuario/techmedia-erp/issues
- 📱 WhatsApp: (11) 99999-9999

---

**Instalação concluída com sucesso? Acesse o sistema e comece a gerenciar sua agência de forma inteligente! 🚀**

