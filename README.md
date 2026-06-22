# Locadora — Sistema de Gestão de Frota

MVP de um sistema web para locadoras de veículos de pequeno porte (frota de 5 a 30
carros). Substitui o controle em planilhas por uma gestão operacional com
dashboard operacional, cadastro de veículos/clientes, contratos de locação,
manutenção e multas.

Construído com **Django 5 + Templates + Tailwind/Alpine/HTMX** (tudo via
CDN, sem build step de frontend).

---

## 1. Requisitos do sistema

- **Python 3.11+**
- **pip** e **venv**
- **PostgreSQL 13+** — apenas para rodar em produção (em desenvolvimento usa SQLite,
  sem instalação adicional)

---

## 2. Instalação passo a passo

> Os comandos abaixo usam sintaxe do **Windows PowerShell**. Em Linux/macOS,
> troque `venv\Scripts\activate` por `source venv/bin/activate`.

```powershell
# 1. Clonar o repositório
git clone https://github.com/Maldinni/Locadora-app.git
cd Locadora-app

# 2. Criar e ativar o ambiente virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
copy .env.example .env
#    Edite o .env se necessário. O padrão já roda em desenvolvimento (SQLite).

# 5. Aplicar as migrações do banco
python manage.py migrate

# 6. Popular com dados de demonstração (opcional, recomendado)
python manage.py seed_demo

# 7. Subir o servidor
python manage.py runserver
```

Acesse: **http://127.0.0.1:8000**

---

## 3. Usuários de demonstração

Criados pelo comando `seed_demo`:

| Perfil        | Usuário (login)          | Senha      | Acesso                          |
|---------------|--------------------------|------------|---------------------------------|
| Administrador | `admin@locadora.com`     | `admin123` | Total, incluindo financeiro     |
| Operador      | `operador@locadora.com`  | `op123`    | Operacional, **sem** financeiro |

> O login é feito com o **e-mail no campo de usuário**.

---

## 4. Dados de demonstração

`python manage.py seed_demo` recria o cenário do zero (apaga os dados anteriores) com:

- 2 usuários (admin + operador)
- 8 veículos com status variados (1 em manutenção)
- 15 clientes fictícios em pt_BR (o primeiro com **CNH vencida**, para demonstrar o bloqueio)
- 20 locações (3 ativas + 17 encerradas no último trimestre, com atrasos ocasionais)
- 10 registros de manutenção (3 com revisão já vencida, para acionar o alerta do dashboard)
- 3 multas pendentes vinculadas a contratos

Os dados usam seed fixo (`42`), então a geração é reproduzível.

---

## 5. Funcionalidades

- **Autenticação** — login/logout, troca de senha, dois perfis (Admin/Operador),
  todas as rotas protegidas.
- **Dashboard** — cards de frota (total/disponíveis/alugados/manutenção), próximos
  vencimentos de IPVA/seguro, revisões preventivas pendentes e, para o Admin, um
  balanço simples do mês (receita × gasto: consórcio, manutenção e rastreador).
- **Veículos** — CRUD com filtro por status, busca por placa/modelo e troca rápida de
  status via HTMX (pede motivo ao marcar manutenção).
- **Clientes** — CRUD com validação de CPF (dígitos verificadores), histórico de
  locações na página de detalhe e bloqueio de contrato para CNH vencida.
- **Locações** — CRUD + fluxo de devolução. Ao abrir contrato o veículo vira "alugado";
  na devolução volta a "disponível", atualiza a quilometragem e calcula multa por atraso.
- **Manutenção** — histórico cronológico por veículo, com próxima revisão por km/data.
- **Multas** — controle com status (pendente/pago/contestado), vinculadas ao cliente
  quando há contrato associado.

---

## 6. Configuração de ambiente

A escolha do ambiente é feita pela variável `DJANGO_SETTINGS_MODULE` no `.env`:

| Ambiente          | Módulo de settings              | Banco       | DEBUG |
|-------------------|---------------------------------|-------------|-------|
| Desenvolvimento   | `locadora.settings.development` | SQLite      | True  |
| Produção          | `locadora.settings.production`  | PostgreSQL  | False |

Outras variáveis (ver `.env.example`):

- `SECRET_KEY` — chave secreta do Django (gere uma nova para produção).
- `ALLOWED_HOSTS` — hosts permitidos, separados por vírgula.
- `POSTGRES_*` — credenciais do banco em produção.
- `MULTA_DIARIA_ATRASO` — valor (R$) da multa por dia de atraso na devolução.

### Rodando em produção (PostgreSQL)

```powershell
# Gere uma SECRET_KEY forte:
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"

# No .env, defina:
#   DJANGO_SETTINGS_MODULE=locadora.settings.production
#   SECRET_KEY=<a chave gerada acima>
#   ALLOWED_HOSTS=seu-dominio.com
#   POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_HOST / POSTGRES_PORT

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser   # cria o primeiro acesso admin
```

Notas do ambiente de produção:

- **SECRET_KEY é obrigatória** — o app recusa subir com a chave padrão de
  desenvolvimento (levanta `ImproperlyConfigured`).
- **Arquivos estáticos** são servidos pelo **WhiteNoise** (sem nginx/Apache
  separado); por isso o `collectstatic` é necessário antes de subir.
- Já vêm habilitados HTTPS redirect, cookies seguros e HSTS.

---

## 7. Estrutura do projeto

```
Locadora-app/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── locadora/                 # projeto Django
│   ├── settings/             # base / development / production
│   ├── urls.py
│   ├── views.py              # DashboardView
│   └── wsgi.py
├── apps/
│   ├── common/               # TimeStampedModel, mixins de form, templatetags
│   ├── accounts/             # autenticação, perfis, seed_demo
│   ├── veiculos/
│   ├── clientes/
│   ├── locacoes/
│   ├── manutencao/
│   └── multas/
├── templates/                # base.html, partials/ e templates por app
└── static/css/custom.css
```

---

## 8. Testes

A suíte cobre as regras de negócio críticas (validação de CPF/CNH, cálculos de
locação, troca de status do veículo e permissões admin/operador):

```powershell
python manage.py test apps
```

---

## 9. Stack técnica

- **Backend:** Python 3.11+, Django 5.x
- **Frontend:** Django Templates + Tailwind CSS (CDN), Alpine.js, HTMX
- **Banco:** SQLite (dev) / PostgreSQL (prod)
- **Dados fake:** Faker (pt_BR)
