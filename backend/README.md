# Backend API - Asylum Appointment Bot

FastAPI backend for the Asylum Appointment Bot web interface.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip or poetry for dependency management

### Installation

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run development server**:
   ```bash
   python run_dev.py
   ```

   The API will be available at: http://localhost:8000

## 📁 Project Structure

```
backend/
├── src/
│   ├── api/          # API routes and endpoints
│   ├── auth/         # Authentication and authorization
│   ├── models/       # Database models
│   ├── services/     # Business logic services
│   ├── websocket/    # WebSocket endpoints
│   ├── config.py     # Configuration management
│   ├── database.py   # Database setup and connections
│   └── main.py       # FastAPI application factory
├── tests/
│   ├── contract/     # API contract tests
│   ├── integration/  # Service integration tests
│   └── unit/         # Unit tests
├── .env.example      # Environment variables template
├── requirements.txt  # Python dependencies
└── run_dev.py       # Development server runner
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

- **Database**: SQLite database path
- **Security**: JWT secret key and token expiration
- **CORS**: Allowed origins for frontend
- **Bot Integration**: Path to existing bot files
- **Logging**: Log level and output format

### Default Credentials

The application creates default accounts on first startup:

- **Developer**: `developer@asylum-bot.local` / `dev_password_change_me`
- **User**: `user@asylum-bot.local` / `user_password_change_me`

**⚠️ Change these passwords in production!**

## 🛠️ Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test type
python -m pytest tests/contract/
python -m pytest tests/integration/
python -m pytest tests/unit/

# Run with coverage
python -m pytest --cov=src
```

### Code Quality

```bash
# Format code
python -m black src/ tests/

# Sort imports
python -m isort src/ tests/

# Lint code
python -m flake8 src/ tests/

# Type checking
python -m mypy src/
```

## 📖 API Documentation

When running in development mode, interactive API documentation is available:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔗 Available Endpoints

### Health & Info
- `GET /health` - Health check endpoint
- `GET /` - API information

### Authentication (To be implemented)
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Current user info
- `POST /api/auth/logout` - User logout

### Bot Control (To be implemented)
- `GET /api/bot/status` - Get bot status
- `POST /api/bot/start` - Start bot monitoring
- `POST /api/bot/stop` - Stop bot monitoring
- `GET /api/bot/logs` - Get bot logs
- `GET /api/bot/statistics` - Get bot statistics

### WebSocket (To be implemented)
- `WS /ws/logs` - Real-time log streaming

## 🔒 Security Features

- **JWT Authentication**: Token-based authentication
- **Role-based Access**: Developer vs User permissions
- **CORS Protection**: Configurable cross-origin access
- **Request Logging**: Comprehensive request/response logging
- **Input Validation**: Pydantic model validation
- **Error Handling**: Secure error responses

## 🚢 Deployment

### Development
```bash
python run_dev.py
```

### Production
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Docker (Coming soon)
```bash
docker build -t asylum-bot-api .
docker run -p 8000:8000 asylum-bot-api
```

## ✅ Implementation Status

### Completed (T001-T003)
- ✅ Project structure with FastAPI dependencies
- ✅ Environment variable configuration
- ✅ FastAPI application with CORS and middleware
- ✅ Database configuration setup
- ✅ Logging and error handling
- ✅ Health check endpoints

### Next Steps (T004-T019)
- 🔄 Authentication system (JWT tokens, password hashing)
- 🔄 Database models (WebUser, WebSession, ActivityLog, BotStatus)
- 🔄 Authentication endpoints and middleware
- 🔄 Bot control API development

## 🤝 Contributing

1. Follow the task breakdown in `specs/001-a-bot-that/tasks-fullstack.md`
2. Write tests first (TDD approach)
3. Implement functionality to make tests pass
4. Run code quality checks before committing
5. Update documentation as needed

## 📝 Notes

- This backend integrates with the existing bot functionality
- Database models extend the current SQLite schema
- Authentication is required for bot control operations
- Real-time features use WebSocket connections
- All sensitive operations require proper authorization
