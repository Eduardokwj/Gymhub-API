# GymHub API

API principal do MVP **GymHub**, responsável pelo CRUD de exercícios, treinos e sessões de treino.  
Integra também com:
- **API Externa (WGER)**: catálogo de exercícios.
- **API Secundária (coach-svc)**: cálculos de 1RM, volume de treino e geração de plano semanal.

---

## 🎯 Objetivo
Facilitar a organização de treinos de academia, permitindo ao usuário cadastrar seus próprios exercícios e treinos, mas também consultar exercícios em uma base externa (WGER) e gerar recomendações de progressão através do **coach-svc**.

---

## 🧭 Arquitetura

```mermaid
flowchart LR
  Client[[Swagger UI]] -->|HTTP| GymHub[GymHub API (Flask)];
  GymHub <-->|SQLAlchemy| DB[(SQLite)];
  GymHub -->|/external/wger| WGER[(API Externa: WGER)];
  GymHub -->|/recommendations| CoachSVC[coach-svc (FastAPI)];
```
Requisitos

Python 3.11+

Pipenv/venv

Docker Desktop (para rodar via containers)

## Instalação Local

```bash
# criar ambiente virtual
python -m venv .venv

# ativar (Windows)
.\.venv\Scripts\activate

# ativar (Linux/Mac)
source .venv/bin/activate

# instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
```

# Crie o arquivo .env a partir do exemplo:

```bash
cp .env.example .env
```


▶️ Execução local

1. Suba o coach-svc primeiro (veja instruções no repositório dele).
2. Rode a API principal:

```bash
python app.py
```

3. Abra: http://localhost:5000/docs

▶️ Execução via Docker Compose

# Estrutura esperada:

alguma-pasta/
 ├─ gymhub-api/
 └─ coach-svc/

```bash
cd gymhub-api
cp .env.example .env
docker compose up --build
```

#Acesse:

. GymHub API: http://localhost:5000/docs

. Coach Service: http://localhost:8000/docs

Endpoints principais

Exercises

GET /exercises

POST /exercises

PUT /exercises/{id}

DELETE /exercises/{id}

Workouts

GET /workouts

POST /workouts

PUT /workouts/{id}

DELETE /workouts/{id}

Sessions

GET /sessions

POST /sessions

PUT /sessions/{id}

DELETE /sessions/{id}

Integrações

GET /external/wger/exerciseinfo

POST /recommendations


🌐 API Externa: WGER

Base: https://wger.de/api/v2

Rotas usadas: /exerciseinfo/

Principais parâmetros:

language=2 (EN), language=10 (PT)

muscles (ex.: 10 = peito)

equipment (ex.: 1 = barra)

Licença: pública e gratuita.

