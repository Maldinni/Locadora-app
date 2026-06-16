# Deploy no VPS da Locaweb (512 MB) — Loca Fácil

Guia para subir o sistema em produção num VPS pequeno (Ubuntu), usando
**SQLite + Gunicorn + Nginx + WhiteNoise**. Pensado para a versão enxuta
(branch `remover-bi-relatorios`).

> Substitua ao longo do guia:
> - `SEU_IP` → o IP do seu VPS
> - `locafacil` → o usuário que você criar (pode manter esse nome)

---

## Parte 1 — Criar o VPS na Locaweb

1. No painel do VPS, em **"Escolha um Sistema Operacional"**, escolha a aba
   **Sistema Operacional** (NÃO "Aplicações") → **Ubuntu** (de preferência a
   versão **LTS** mais recente, ex.: 22.04 ou 24.04).
   - A aba "Aplicações" (WordPress, Node.js…) não serve para Django.
2. Conclua a criação e anote: **IP do servidor**, **usuário** (`root`) e **senha**.

---

## Parte 2 — Primeiro acesso e preparação do servidor

Acesse por SSH (no PowerShell/terminal do seu PC):

```bash
ssh root@SEU_IP
```

### 2.1 Atualizar o sistema

```bash
apt update && apt upgrade -y
```

### 2.2 Criar um usuário (não usar root para a aplicação)

```bash
adduser locafacil           # defina uma senha
usermod -aG sudo locafacil
```

### 2.3 Criar swap de 2 GB (ESSENCIAL com 512 MB de RAM)

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
free -h                     # confira que "Swap" mostra 2 Gi
```

### 2.4 Instalar os pacotes necessários

```bash
apt install -y python3 python3-venv python3-pip git nginx
```

Agora troque para o usuário criado (o resto do guia roda como `locafacil`):

```bash
su - locafacil
```

---

## Parte 3 — Baixar e configurar a aplicação

### 3.1 Clonar o repositório (branch enxuta)

```bash
cd ~
git clone https://github.com/Maldinni/Locadora-app.git
cd Locadora-app
git checkout remover-bi-relatorios
```

### 3.2 Criar a virtualenv e instalar dependências

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

> Usamos SQLite, então **não** precisa instalar o `requirements-postgres.txt`.

### 3.3 Criar o arquivo `.env`

Gere uma SECRET_KEY:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

Crie o `.env` (copie do exemplo e edite):

```bash
cp .env.example .env
nano .env
```

Deixe assim (cole a chave gerada e troque o IP):

```
SECRET_KEY=COLE_A_CHAVE_GERADA
DJANGO_SETTINGS_MODULE=locadora.settings.production
ALLOWED_HOSTS=SEU_IP
ENABLE_HTTPS=0
DB_ENGINE=sqlite
MULTA_DIARIA_ATRASO=150.00
```

> `ENABLE_HTTPS=0` porque vamos começar acessando por IP (HTTP). Ligamos o
> HTTPS na Parte 6, quando você tiver um domínio.

### 3.4 Migrar o banco, criar o admin e coletar estáticos

```bash
python manage.py migrate
python manage.py createsuperuser     # crie seu acesso de admin real
python manage.py collectstatic --noinput
```

> O login é pelo **e-mail**; informe um e-mail válido no `createsuperuser`.

### 3.5 Testar rápido (opcional)

```bash
gunicorn locadora.wsgi:application -c gunicorn.conf.py
```
Se subir sem erros, pare com `Ctrl+C` e siga para o serviço definitivo.

---

## Parte 4 — Gunicorn como serviço (systemd)

```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/locafacil.service
```

Confira o usuário/caminhos no arquivo (se você usou outro nome de usuário):

```bash
sudo nano /etc/systemd/system/locafacil.service
```

Ative e inicie:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now locafacil
sudo systemctl status locafacil      # deve aparecer "active (running)"
```

> Logs: `journalctl -u locafacil -f`

---

## Parte 5 — Nginx (proxy reverso)

```bash
sudo cp deploy/nginx-locafacil.conf /etc/nginx/sites-available/locafacil
sudo nano /etc/nginx/sites-available/locafacil   # troque server_name para SEU_IP
sudo ln -s /etc/nginx/sites-available/locafacil /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t                         # deve dizer "syntax is ok"
sudo systemctl reload nginx
```

Abra no navegador: **http://SEU_IP** → deve aparecer a tela de login do Loca Fácil.

> Se a Locaweb tiver firewall, libere as portas **80** (e **443** para HTTPS depois).

---

## Parte 6 — HTTPS com domínio (quando tiver) 

Faça isto só depois de ter um **domínio apontando para o IP do VPS** (registro
DNS tipo A → SEU_IP).

```bash
# 1) Adicione o domínio ao .env e ligue o HTTPS:
nano ~/Locadora-app/.env
#   ALLOWED_HOSTS=SEU_IP,seudominio.com.br,www.seudominio.com.br
#   ENABLE_HTTPS=1

# 2) Atualize o server_name do Nginx para o domínio:
sudo nano /etc/nginx/sites-available/locafacil   # server_name seudominio.com.br www.seudominio.com.br;

# 3) Instale o certificado gratuito (Let's Encrypt):
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seudominio.com.br -d www.seudominio.com.br

# 4) Reinicie a aplicação:
sudo systemctl restart locafacil
sudo systemctl reload nginx
```

O Certbot já configura o redirecionamento para HTTPS e renova sozinho.

---

## Manutenção

### Atualizar o sistema quando o código mudar

```bash
cd ~/Locadora-app
source .venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart locafacil
```

### Backup (faça periodicamente!)

Tudo que importa são dois caminhos — copie-os para um local seguro:

```bash
cp ~/Locadora-app/db.sqlite3 ~/backup-db-$(date +%F).sqlite3
tar czf ~/backup-media-$(date +%F).tar.gz -C ~/Locadora-app media
```

> O `db.sqlite3` guarda todos os dados; a pasta `media/` guarda os contratos
> `.docx` gerados. Baixe esses arquivos para fora do VPS de tempos em tempos.

---

## Resumo da arquitetura

```
Navegador --HTTP(S)--> Nginx (porta 80/443) --proxy--> Gunicorn (127.0.0.1:8000)
                                                          └── Django + WhiteNoise (estáticos)
                                                          └── SQLite (db.sqlite3, modo WAL)
```
