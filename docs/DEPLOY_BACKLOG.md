# Backlog de Deploy: Agregador de Imóveis (Render.com)

Este documento descreve as etapas necessárias para realizar o deploy da API (FastAPI) e do Frontend (HTML Estático) na plataforma Render.

---

## Quadro de Tarefas

| ID | Categoria | Tarefa | Descrição | Status |
| :--- | :--- | :--- | :--- | :--- |
| **01** | **Código** | Ajustar `requirements.txt` | Adicionar `gunicorn` e fixar versões das dependências. | ⬜ Pendente |
| **02** | **Código** | Configurar Playwright | Definir o comando de build para instalar o Chromium e dependências de sistema. | ⬜ Pendente |
| **03** | **Frontend** | Atualizar URL da API | Alterar a constante `API_BASE` no `index.html`. | ⬜ Pendente |
| **04** | **Render** | Criar Web Service | Configurar o serviço de backend conectado ao GitHub. | ⬜ Pendente |
| **05** | **Render** | Definir Env Vars | Configurar `PYTHON_VERSION` no painel do Render. | ⬜ Pendente |

---

## Detalhamento das Atividades

### 1. Atualização de Dependências (`requirements.txt`)
Para garantir a estabilidade em produção, utilizaremos o **Gunicorn** com workers do **Uvicorn**.
* **Ação:** Certifique-se de que o arquivo contém:
    * `fastapi`
    * `uvicorn`
    * `gunicorn`
    * `requests`
    * `playwright`

### 2. Configuração do Build (Playwright)
Como o projeto utiliza automação de navegador em alguns scrapers, o ambiente Linux do Render precisa dos binários do Chromium.
* **Comando de Build:** `pip install -r requirements.txt && playwright install --with-deps chromium`

### 3. Ajuste do Ponto de Entrada da API (`api/main.py`)
A aplicação deve ser iniciada pelo Gunicorn vinculando-se à porta dinâmica fornecida pelo Render.
* **Comando de Inicialização (Start Command):** `gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

### 4. Conexão do Frontend (`index.html`)
O frontend precisa saber onde a API está hospedada fora do ambiente local.
* **Localização:** Linha ~370 do arquivo `index.html`.
* **Ação:** Substituir `"http://localhost:8000"` pela URL gerada pelo Render (ex: `https://imoveis-api.onrender.com`).

### 5. Configurações no Painel do Render
* **Service Type:** Web Service.
* **Runtime:** Python 3.
* **Environment Variables:**
    * `PYTHON_VERSION`: `3.10.0` (ou superior).
    * `PORT`: `10000` (padrão do Render).

---

## Notas de Implementação
* **CORS:** O projeto já possui o `CORSMiddleware` configurado no arquivo `api/main.py` para aceitar requisições de qualquer origem (`allow_origins=["*"]`), o que facilita o deploy inicial.
* **Cold Start:** No plano gratuito do Render, a API pode demorar até 30 segundos para responder após um período de inatividade.
