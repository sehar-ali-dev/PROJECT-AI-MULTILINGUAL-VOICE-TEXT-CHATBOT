# Multilingual AI Voice & Language Processing Platform

A production-style multilingual AI platform for speech-to-text, translation, and text-to-speech with human-in-the-loop workflow.

## Tech Stack

- **Backend**: Python, FastAPI, Pydantic, SQLAlchemy
- **Database**: SQLite (development), PostgreSQL (production)
- **AI**: OpenAI API (with Mocked AI provider for development)
- **Frontend**: HTML, CSS, JavaScript (lightweight)
- **Authentication**: JWT + bcrypt

## Project Structure

```
ai-language-platform/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── core/
│   │   │   └── config.py       # Configuration settings
│   │   ├── db/
│   │   │   └── database.py     # SQLAlchemy database setup
│   │   ├── providers/           # AI provider interfaces
│   │   │   ├── speech_to_text.py
│   │   │   ├── translation.py
│   │   │   └── text_to_speech.py
│   │   └── services/
│   │       └── mock_ai.py      # Mock AI for development
│   └── tests/
├── frontend/
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
- `PROJECT_NAME`: Project name
- `SECRET_KEY`: JWT secret key (change in production)
- `DATABASE_URL`: Database connection string
- `OPENAI_API_KEY`: OpenAI API key (for production mode)
- `USE_MOCK_AI`: Set to `True` for development (free, instant responses)

### 5. Run the Backend

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 6. Verify Health Check

Visit: `http://localhost:8000/health`

Expected response:
```json
{
  "status": "ok",
  "mock_ai": true
}
```

## Development Mode vs Production Mode

### Development Mode (Default)
- `USE_MOCK_AI=True` in `.env`
- **Cost**: 100% Free
- **Speed**: Instant responses
- **Usage**: Coding, UI design, feature verification, testing

### Production Mode
- `USE_MOCK_AI=False` in `.env`
- Requires valid `OPENAI_API_KEY`
- **Cost**: Paid per API call
- **Usage**: Real end-to-end testing with actual AI

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Architecture

The platform follows a modular architecture with:
- **Provider Abstraction Layer**: AI providers are replaceable
- **Service Layer**: Business logic separated from routes
- **Human-in-the-Loop**: AI transcriptions are never overwritten by human corrections
- **Language-Agnostic**: Support for multiple languages without hardcoding

## Phases

The project is developed in phases:
1. **Phase 1**: Project Setup & Architecture (Current)
2. **Phase 2**: Login & Authentication
3. **Phase 3**: Dashboard & Basic UI
4. **Phase 4**: Audio Upload & Microphone
5. **Phase 5**: Speech-to-Text
6. **Phase 6**: AI Transcription Display
7. **Phase 7**: Human Review & Correction
8. **Phase 8**: AI vs Human Comparison
9. **Phase 9**: Multilingual Translation
10. **Phase 10**: Text-to-Speech
11. **Phase 11**: Complete Audio Translation Workflow
12. **Phase 12**: Text Chat & Voice Assistant
13. **Phase 13**: Conversation & Processing History
14. **Phase 14**: Async Processing & Job Management
15. **Phase 15**: Reviewer & Admin System
16. **Phase 16**: API Development
17. **Phase 17**: Security Hardening
18. **Phase 18**: Testing & Quality Assurance
19. **Phase 19**: Documentation
20. **Phase 20**: Deployment & Maintenance

## Current Status

**Phase 1 Complete**: Backend architecture is ready with:
- FastAPI application with CORS middleware
- Health check endpoint
- Configuration management with Pydantic Settings
- Database setup with SQLAlchemy
- AI provider interfaces (STT, Translation, TTS)
- Mock AI provider for development
