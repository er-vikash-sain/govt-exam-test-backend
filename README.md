# AI-Powered Exam Preparation Platform

A comprehensive platform for AI-generated exam preparation content, built with FastAPI, Next.js, and PostgreSQL.

## 🚀 Features

- **AI-Powered Content Generation**: Generate questions and explanations using OpenAI/Anthropic
- **Comprehensive Exam Coverage**: Support for SSC, Banking, Railways, and other Indian competitive exams
- **Smart Quiz Engine**: Dynamic quiz generation with difficulty-based question selection
- **Real-time Analytics**: Detailed performance tracking and insights
- **Multi-language Support**: English and Hindi with extensible language support
- **B2B Features**: Institute management and white-labeling capabilities
- **Mobile-First Design**: Responsive PWA with offline support

## 🏗️ Architecture

- **Backend**: FastAPI with async/await support
- **Database**: PostgreSQL 16 with SQLAlchemy 2.0
- **Cache**: Redis for session management and job queues
- **Background Jobs**: Celery for AI content generation
- **Frontend**: Next.js 14 with React 18
- **Authentication**: JWT-based with role-based access control

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0
- **Cache**: Redis 7
- **Task Queue**: Celery
- **Validation**: Pydantic v2

### Frontend
- **Framework**: Next.js 14
- **Language**: TypeScript
- **UI Library**: React 18
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query
- **PWA**: Service Workers

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured logging with structlog

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 16
- Redis 7

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd exam-prep-platform
```

### 2. Environment Setup

```bash
# Copy environment file
cp env.example .env

# Edit .env with your configuration
nano .env
```

### 3. Start with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Manual Setup (Alternative)

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database setup
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the Application

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Celery Flower**: http://localhost:5555

## 📚 API Documentation

The API is fully documented with OpenAPI/Swagger:

- **Interactive Docs**: `/docs` (Swagger UI)
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`

## 🗄️ Database Schema

The platform uses a comprehensive database schema with:

- **Users & Authentication**: User management, roles, sessions
- **Exam Catalog**: States, exam bodies, exams, syllabi, topics
- **Content Management**: Questions, options, explanations
- **Quiz Engine**: Quizzes, attempts, scoring
- **AI Integration**: Job management, content generation
- **Payments**: Wallets, transactions, subscriptions
- **Community**: Threads, posts, institutes

## 🔧 Development

### Project Structure

```
├── app/                    # Backend application
│   ├── api/               # API endpoints
│   ├── core/              # Core configuration
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   ├── workers/           # Background tasks
│   └── utils/             # Utility functions
├── tests/                 # Test suite
├── alembic/               # Database migrations
├── docker-compose.yml     # Development environment
└── requirements.txt       # Python dependencies
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🌐 Deployment

### Production Deployment

1. **Environment Variables**: Set production values in `.env`
2. **Database**: Use managed PostgreSQL service
3. **Redis**: Use managed Redis service
4. **Container Registry**: Push to your registry
5. **Kubernetes**: Deploy with Helm charts

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key

# Optional
ANTHROPIC_API_KEY=your-anthropic-key
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
```

## 📊 Monitoring

### Health Checks

- **API Health**: `/health`
- **Database**: Connection and query performance
- **Redis**: Connection and memory usage
- **Background Jobs**: Celery worker status

### Metrics

- **Application**: Request/response times, error rates
- **Database**: Query performance, connection pool
- **Infrastructure**: CPU, memory, disk usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions

## 🗺️ Roadmap

- [ ] **Phase 1**: Core platform with basic AI generation
- [ ] **Phase 2**: Advanced analytics and study planning
- [ ] **Phase 3**: B2B features and white-labeling
- [ ] **Phase 4**: Mobile apps and offline support
- [ ] **Phase 5**: Advanced AI features and personalization

---

**Built with ❤️ for Indian students preparing for competitive exams**
