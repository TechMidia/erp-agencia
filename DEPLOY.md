# 🚀 Guia de Deploy em Produção - TechMídia ERP

Este guia fornece instruções detalhadas para fazer o deploy do TechMídia ERP em ambiente de produção.

## 🎯 Opções de Deploy

### 1. VPS/Servidor Dedicado (Recomendado)
### 2. Heroku (Fácil e Rápido)
### 3. DigitalOcean App Platform
### 4. AWS EC2
### 5. Google Cloud Platform
### 6. Docker + Docker Compose

---

## 🖥️ Deploy em VPS/Servidor Dedicado

### Pré-requisitos
- Ubuntu 20.04 LTS ou superior
- Acesso root ou sudo
- Domínio configurado (opcional)

### 1. Preparação do Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências básicas
sudo apt install -y python3.11 python3.11-venv python3-pip nginx postgresql postgresql-contrib git ufw

# Configurar firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Configurar PostgreSQL

```bash
# Configurar PostgreSQL
sudo -u postgres psql

# No prompt do PostgreSQL:
CREATE DATABASE techmedia_erp;
CREATE USER techmedia WITH PASSWORD 'SuaSenhaSegura123!';
GRANT ALL PRIVILEGES ON DATABASE techmedia_erp TO techmedia;
\q
```

### 3. Configurar Aplicação

```bash
# Criar usuário para a aplicação
sudo adduser --system --group --home /var/www/techmedia-erp techmedia

# Clonar repositório
sudo git clone https://github.com/seu-usuario/techmedia-erp.git /var/www/techmedia-erp
sudo chown -R techmedia:techmedia /var/www/techmedia-erp

# Mudar para o usuário da aplicação
sudo -u techmedia -i
cd /var/www/techmedia-erp

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Criar arquivo de configuração
cat > .env << EOF
DATABASE_URL=postgresql://techmedia:SuaSenhaSegura123!@localhost/techmedia_erp
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
FLASK_ENV=production
EOF

# Testar aplicação
python src/main.py
# Ctrl+C para parar
```

### 4. Configurar Gunicorn

```bash
# Criar arquivo de configuração do Gunicorn
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "techmedia"
group = "techmedia"
EOF

# Testar Gunicorn
gunicorn -c gunicorn.conf.py src.main:app
# Ctrl+C para parar
```

### 5. Configurar Systemd Service

```bash
# Sair do usuário techmedia
exit

# Criar service file
sudo tee /etc/systemd/system/techmedia-erp.service > /dev/null << EOF
[Unit]
Description=TechMidia ERP
After=network.target

[Service]
User=techmedia
Group=techmedia
WorkingDirectory=/var/www/techmedia-erp
Environment=PATH=/var/www/techmedia-erp/venv/bin
ExecStart=/var/www/techmedia-erp/venv/bin/gunicorn -c gunicorn.conf.py src.main:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Ativar e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable techmedia-erp
sudo systemctl start techmedia-erp
sudo systemctl status techmedia-erp
```

### 6. Configurar Nginx

```bash
# Criar configuração do Nginx
sudo tee /etc/nginx/sites-available/techmedia-erp > /dev/null << EOF
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }

    location /static {
        alias /var/www/techmedia-erp/src/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    client_max_body_size 16M;
}
EOF

# Ativar site
sudo ln -s /etc/nginx/sites-available/techmedia-erp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Configurar SSL (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Configurar renovação automática
sudo crontab -e
# Adicionar linha:
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 🌊 Deploy no Heroku

### 1. Preparar Aplicação

```bash
# Criar Procfile
echo "web: gunicorn src.main:app" > Procfile

# Criar runtime.txt
echo "python-3.11.0" > runtime.txt

# Atualizar requirements.txt
echo "psycopg2-binary==2.9.7" >> requirements.txt
```

### 2. Configurar Heroku

```bash
# Instalar Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Criar aplicação
heroku create sua-app-techmedia-erp

# Adicionar PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Configurar variáveis de ambiente
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
heroku config:set FLASK_ENV=production

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Abrir aplicação
heroku open
```

---

## 🌊 Deploy no DigitalOcean App Platform

### 1. Preparar Repositório

```yaml
# Criar .do/app.yaml
name: techmedia-erp
services:
- name: web
  source_dir: /
  github:
    repo: seu-usuario/techmedia-erp
    branch: main
  run_command: gunicorn src.main:app
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: SECRET_KEY
    value: sua-chave-secreta
  - key: FLASK_ENV
    value: production
databases:
- name: techmedia-db
  engine: PG
  version: "13"
  size_slug: db-s-dev-database
```

### 2. Deploy via Interface Web
1. Acesse DigitalOcean App Platform
2. Conecte seu repositório GitHub
3. Configure as variáveis de ambiente
4. Deploy automático

---

## ☁️ Deploy na AWS EC2

### 1. Criar Instância EC2

```bash
# Conectar via SSH
ssh -i sua-chave.pem ubuntu@ip-da-instancia

# Seguir passos do deploy em VPS (seção anterior)
```

### 2. Configurar RDS (Opcional)

```bash
# Criar instância RDS PostgreSQL
# Atualizar DATABASE_URL com endpoint do RDS
DATABASE_URL=postgresql://usuario:senha@endpoint-rds:5432/techmedia_erp
```

### 3. Configurar Load Balancer (Opcional)

```bash
# Criar Application Load Balancer
# Configurar Target Groups
# Adicionar instâncias EC2
```

---

## 🐳 Deploy com Docker

### 1. Criar Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY src/ ./src/
COPY .env .

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.main:app"]
```

### 2. Criar docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "80:5000"
    environment:
      - DATABASE_URL=postgresql://techmedia:senha@db:5432/techmedia_erp
      - SECRET_KEY=sua-chave-secreta
      - FLASK_ENV=production
    depends_on:
      - db
    volumes:
      - ./uploads:/app/src/static/uploads
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: techmedia_erp
      POSTGRES_USER: techmedia
      POSTGRES_PASSWORD: senha
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
```

### 3. Deploy

```bash
# Build e execução
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f app
```

---

## 🔧 Configurações de Produção

### 1. Variáveis de Ambiente Essenciais

```bash
# Segurança
SECRET_KEY=chave-muito-segura-de-32-caracteres
FLASK_ENV=production

# Banco de Dados
DATABASE_URL=postgresql://usuario:senha@host:5432/database

# Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads

# Email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-app
```

### 2. Configurações de Segurança

```python
# src/main.py - Adicionar configurações de produção
if os.getenv('FLASK_ENV') == 'production':
    app.config.update(
        # Segurança de sessão
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        
        # Timeout de sessão
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        
        # Segurança geral
        WTF_CSRF_ENABLED=True,
        WTF_CSRF_TIME_LIMIT=None,
    )
```

### 3. Backup Automático

```bash
# Criar script de backup
cat > /usr/local/bin/backup-techmedia.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/techmedia"
DATE=$(date +%Y%m%d_%H%M%S)

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
pg_dump -h localhost -U techmedia techmedia_erp > $BACKUP_DIR/db_$DATE.sql

# Backup dos uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/techmedia-erp/src/static/uploads

# Manter apenas os últimos 7 backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup-techmedia.sh

# Configurar cron para backup diário
sudo crontab -e
# Adicionar linha:
0 2 * * * /usr/local/bin/backup-techmedia.sh
```

### 4. Monitoramento

```bash
# Instalar htop para monitoramento
sudo apt install htop -y

# Verificar status dos serviços
sudo systemctl status techmedia-erp
sudo systemctl status nginx
sudo systemctl status postgresql

# Verificar logs
sudo journalctl -u techmedia-erp -f
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔍 Verificação Pós-Deploy

### Checklist de Verificação

- [ ] Aplicação carregando corretamente
- [ ] Login funcionando
- [ ] Todas as páginas acessíveis
- [ ] Upload de arquivos funcionando
- [ ] Banco de dados conectado
- [ ] SSL configurado (se aplicável)
- [ ] Backup configurado
- [ ] Monitoramento ativo

### Testes Funcionais

```bash
# Testar conectividade
curl -I https://seu-dominio.com

# Testar API
curl -X POST https://seu-dominio.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Testar upload
curl -X POST https://seu-dominio.com/api/upload/logo \
  -F "file=@logo.png"
```

---

## 🆘 Solução de Problemas

### Problemas Comuns

#### Erro 502 Bad Gateway
```bash
# Verificar se Gunicorn está rodando
sudo systemctl status techmedia-erp

# Verificar logs
sudo journalctl -u techmedia-erp -n 50

# Reiniciar serviço
sudo systemctl restart techmedia-erp
```

#### Erro de Permissão de Upload
```bash
# Verificar permissões
ls -la /var/www/techmedia-erp/src/static/uploads

# Corrigir permissões
sudo chown -R techmedia:techmedia /var/www/techmedia-erp/src/static/uploads
sudo chmod -R 755 /var/www/techmedia-erp/src/static/uploads
```

#### Erro de Conexão com Banco
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Testar conexão
sudo -u postgres psql -c "SELECT version();"

# Verificar configurações
sudo -u techmedia psql -h localhost -U techmedia -d techmedia_erp -c "SELECT 1;"
```

---

## 📞 Suporte

Para problemas específicos de deploy:

- 📧 Email: deploy@techmedia.com.br
- 💬 GitHub Issues: https://github.com/seu-usuario/techmedia-erp/issues
- 📚 Documentação: https://docs.techmedia.com.br

---

**Deploy realizado com sucesso? Sua agência agora tem um ERP profissional rodando em produção! 🎉**

