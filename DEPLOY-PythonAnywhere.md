# Deploy de demonstração no PythonAnywhere (grátis)

Guia para colocar a Locadora no ar **de graça** (sem cartão) para mostrar ao
cliente. Usa SQLite e WhiteNoise — não precisa configurar banco Postgres nem
mapeamento de estáticos.

> Seu app ficará em `https://SEU_USUARIO.pythonanywhere.com`.
> Troque `SEU_USUARIO` pelos seus dados nos comandos abaixo.

---

## 1. Criar a conta

1. Acesse **pythonanywhere.com** → **Pricing & signup** → **Create a Beginner account** (plano grátis).
2. Confirme o e-mail e faça login.

## 2. Clonar o repositório

No painel: **Consoles** → **Bash**. No console, rode:

```bash
git clone https://github.com/Maldinni/Locadora-app.git
cd Locadora-app
```

## 3. Criar a virtualenv e instalar dependências

```bash
mkvirtualenv --python=/usr/bin/python3.11 locadora-venv
pip install -r requirements.txt
```

> `mkvirtualenv` já ativa a venv (o nome `(locadora-venv)` aparece no prompt).
> Se reabrir o console depois, reative com: `workon locadora-venv`.

## 4. Preparar banco, estáticos e dados de demonstração

Ainda no Bash (com a venv ativa):

```bash
export DJANGO_SETTINGS_MODULE=locadora.settings.demo
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_demo
```

Gere uma SECRET_KEY (copie o valor que aparecer — vamos colar no passo 7):

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

## 5. Criar o Web app

1. Painel → aba **Web** → **Add a new web app** → **Next**.
2. Em framework, escolha **Manual configuration** (NÃO o assistente de Django).
3. Escolha **Python 3.11** → **Next**.

## 6. Apontar a virtualenv

Na aba **Web**, seção **Virtualenv**, informe:

```
/home/SEU_USUARIO/.virtualenvs/locadora-venv
```

## 7. Configurar o arquivo WSGI

Na aba **Web** → seção **Code** → clique no link do **WSGI configuration file**
(algo como `/var/www/SEU_USUARIO_pythonanywhere_com_wsgi.py`).

Apague **todo** o conteúdo e cole (ajustando `SEU_USUARIO` e a SECRET_KEY):

```python
import os
import sys

path = "/home/SEU_USUARIO/Locadora-app"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "locadora.settings.demo"
os.environ["SECRET_KEY"] = "COLE_AQUI_A_CHAVE_GERADA_NO_PASSO_4"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Salve (botão **Save** no topo).

## 8. Reload e teste

1. Volte ao topo da aba **Web** → clique no botão verde **Reload**.
2. Acesse `https://SEU_USUARIO.pythonanywhere.com` → deve abrir a tela de login.

### Acessos da demo

| Perfil        | Usuário                  | Senha      |
|---------------|--------------------------|------------|
| Administrador | `admin@locadora.com`     | `admin123` |
| Operador      | `operador@locadora.com`  | `op123`    |

---

## Atualizar a demo depois (quando o código mudar)

No console Bash:

```bash
workon locadora-venv
cd ~/Locadora-app
git pull
python manage.py migrate
python manage.py collectstatic --noinput
```

Depois clique em **Reload** na aba Web.

## Resetar os dados da demo

```bash
cd ~/Locadora-app
export DJANGO_SETTINGS_MODULE=locadora.settings.demo
python manage.py seed_demo
```

## Observações

- **SQLite** é suficiente para a demonstração; os dados ficam no servidor.
- Este ambiente é **só para demonstração** (credenciais fixas e simples). Não
  cadastre dados reais de clientes.
- Os arquivos estáticos são servidos pelo **WhiteNoise** — não é preciso
  configurar a seção "Static files" do PythonAnywhere.
- Conta grátis: o app é desativado após ~3 meses de inatividade; para reativar,
  basta logar no PythonAnywhere e clicar **Reload**.
