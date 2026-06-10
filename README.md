# Locadora — Sistema de Gestão de Frota

MVP de um sistema web para locadoras de veículos de pequeno porte (frota de 5 a 30
carros). Substitui o controle em planilhas por uma gestão operacional com
dashboard em tempo real, cadastro de veículos/clientes, contratos de locação,
manutenção, multas e relatório financeiro.

Construído com **Django 5 + Templates + Tailwind/Alpine/HTMX/Chart.js** (tudo via
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
- **Dashboard** — cards de frota (total/disponíveis/alugados/manutenção), receita do
  mês, próximos vencimentos de IPVA/seguro, revisões preventivas pendentes e gráficos
  (receita dos últimos 6 meses + distribuição por status).
- **Veículos** — CRUD com filtro por status, busca por placa/modelo e troca rápida de
  status via HTMX (pede motivo ao marcar manutenção).
- **Clientes** — CRUD com validação de CPF (dígitos verificadores), histórico de
  locações na página de detalhe e bloqueio de contrato para CNH vencida.
- **Locações** — CRUD + fluxo de devolução. Ao abrir contrato o veículo vira "alugado";
  na devolução volta a "disponível", atualiza a quilometragem e calcula multa por atraso.
- **Manutenção** — histórico cronológico por veículo, com próxima revisão por km/data.
- **Multas** — controle com status (pendente/pago/contestado), vinculadas ao cliente
  quando há contrato associado.
- **Relatório financeiro** (somente Admin) — filtro por período, receita, custos de
  manutenção, lucro estimado e **exportação CSV**.

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
# No .env, defina:
#   DJANGO_SETTINGS_MODULE=locadora.settings.production
#   SECRET_KEY=<uma-chave-forte>
#   ALLOWED_HOSTS=seu-dominio.com
#   POSTGRES_DB / POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_HOST / POSTGRES_PORT

python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser   # cria o primeiro acesso admin
```

O módulo de produção já habilita HTTPS redirect, cookies seguros e HSTS.

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
│   ├── multas/
│   └── relatorios/
├── templates/                # base.html, partials/ e templates por app
└── static/css/custom.css
```

---

## 8. Stack técnica

- **Backend:** Python 3.11+, Django 5.x
- **Frontend:** Django Templates + Tailwind CSS (CDN), Alpine.js, HTMX, Chart.js
- **Banco:** SQLite (dev) / PostgreSQL (prod)
- **Dados fake:** Faker (pt_BR)
