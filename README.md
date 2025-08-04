
# 🎓 Personalized Study Assistant (personalized_study_assistant)

This Django-based backend powers a **Personalized Study Assistant**. It exposes AI-powered tools like study plan generation, text summarization, quiz/flashcard creation, and study progress tracking — all accessible via a JSON-RPC interface with token-based authentication.

---

## 🚀 Features

✅ **Token Authentication**  
Secure access to certain endpoints using Django REST Framework's token system.

📚 **OpenAI-Powered Tools**  
Includes tools like:
- `generateStudyPlan`
- `summarizeText`
- `generateQuiz`
- `generateFlashcards`
- `recommendResources`
- `trackProgress`

🧩 **MCP-Compliant Endpoint**  
A unified endpoint (`/api/mcp/tool_psa/`) for both:
- Tool metadata discovery (via GET)
- Tool invocation (via POST)

📝 **Study Progress Persistence**  
Saves user study activity to a local SQLite database using Django ORM.

🔍 **Structured Logging**  
Uses `structlog` to generate machine-parseable JSONL logs.

🧱 **Extensible Tool Framework**  
Add new tools easily using the `@tool` decorator.

---

## 🏗️ Project Structure

```
personalized_study_assistant/
├── core/                 ← Django settings & routing
│   └── settings.py
├── tool/                 ← Main tool logic
│   ├── functions.py      # Tool implementations + registry
│   ├── models.py         # DB models for study progress
│   ├── rpc.py            # JSON-RPC GET/POST handler
│   ├── serializers.py    # Input validation for APIs
│   └── views.py          # REST views (summarize, progress)
├── logs/                 ← Structured JSON log files
├── manage.py             ← Django CLI entrypoint
├── requirements.txt      ← Project dependencies
└── .env                  ← Local environment configuration
```

---

## 🧪 Local Setup

### 1. 🐍 Clone & Create Virtual Environment

```bash
git clone https://github.com/mesajidiqbal/personalized_study_assistant.git
cd personalized_study_assistant

python3 -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 2. 📦 Install Dependencies

```bash
pip install -r requirements.txt
```
> Ensure you're using **Python 3.9+**

### 3. ⚙️ Configure Environment Variables

Create a `.env` file in the root directory:

```
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
OPENAI_API_KEY=sk-<your-openai-key>
MODEL_NAME=gpt-4o-mini
```

### 4. 🛠️ Apply Migrations

```bash
python manage.py migrate
```

### 5. 🔐 Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. 🏃 Run Development Server

```bash
python manage.py runserver
```

API is now available at:  
📍 http://127.0.0.1:8000/api/mcp/tool_psa/

---

## 🔗 Key API Endpoints

| Endpoint                      | Method | Description                              |
|-------------------------------|--------|------------------------------------------|
| `/api/mcp/tool_psa/`          | GET    | Tool discovery                           |
| `/api/mcp/tool_psa/`          | POST   | JSON-RPC tool invocation                 |
| `/api/summarize-text/`        | POST   | Summarize provided text (Auth Required)  |
| `/api/track-progress/`        | POST   | Log or retrieve progress (Auth Required) |
| `/api-token-auth/`            | POST   | Token login for authenticated users      |

---

## 📦 Example Tool Invocation

```bash
curl --location 'http://127.0.0.1:8000/api/mcp/tool_psa/' \
--header 'Content-Type: application/json' \
--data '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "generateStudyPlan",
  "params": {
    "subject": "Linear Algebra",
    "duration_weeks": 3,
    "daily_hours": 1.5
  }
}'
```

---

## 🚀 Deployment (e.g., Railway)

### 1. Add a `Procfile` to the root:

```
web: gunicorn core.wsgi --log-file -
```

### 2. Configure Environment

Set all variables from `.env` in your Railway project's **Variables** tab.

### 3. Push to GitHub and Deploy

Connect the GitHub repo to Railway. It will auto-deploy and give you a public URL like:

```
https://web-production-psa.up.railway.app/
```

Use this as your **MCP URL** in platforms like Phronetic AI.

---
