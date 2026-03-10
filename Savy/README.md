# 💰 SAVY - AI Personal Finance Coach

<div align="center">

![Savy Logo](https://via.placeholder.com/150x150?text=SAVY)

**Il tuo coach finanziario personale con Intelligenza Artificiale**

[![CI/CD](https://github.com/yourusername/savy/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/yourusername/savy/actions)
[![codecov](https://codecov.io/gh/yourusername/savy/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/savy)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Flutter 3.38+](https://img.shields.io/badge/flutter-3.38+-blue.svg)](https://flutter.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Features](#-features) • [Tech Stack](#-tech-stack) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🎯 Cos'è Savy?

Savy è un'applicazione di personal finance che utilizza l'intelligenza artificiale (Google Gemini) per aiutarti a:

- 📊 **Tracciare le spese** in modo automatico e intelligente
- 💡 **Ricevere consigli finanziari** personalizzati dall'AI
- 💰 **Ottimizzare le bollette** (energia, telefonia, abbonamenti)
- 📈 **Visualizzare report** dettagliati delle tue finanze
- 🤖 **Chattare con un AI coach** per domande finanziarie
- 🔔 **Ricevere promemoria** per pagamenti e scadenze

---

## ✨ Features

### 🎨 Frontend (Flutter)
- ✅ **Design moderno iOS/Revolut-style** con glassmorphism
- ✅ **Supporto Multi-Conto** con selettori dinamici (ChoiceChips) e carosello
- ✅ **Isolamento Dati Analitico** per ogni conto o visione globale
- ✅ **Onboarding interattivo** per nuovi utenti
- ✅ **Dark mode** automatico
- ✅ **Offline mode** con cache locale (Hive)
- ✅ **Biometric auth** (Face ID / Touch ID / Fingerprint)
- ✅ **Push notifications** (Firebase FCM)
- ✅ **Pull-to-refresh** su tutte le liste
- ✅ **Haptic feedback** per interazioni
- ✅ **Accessibilità** WCAG AA compliant
- ✅ **Animazioni fluide** e micro-interactions

### 🔧 Backend (FastAPI + LangGraph)
- ✅ **Architettura Multi-Conto Reale** (separazione ledger e bank_account_id)
- ✅ **AI Coach con LangGraph** (6 nodi di reasoning)
- ✅ **Google Gemini 2.0 Flash** per analisi finanziaria e insight per conto
- ✅ **JWT Authentication** con refresh tokens
- ✅ **Email verification** e password reset
- ✅ **Background jobs** con Celery
- ✅ **Caching distribuito** con Redis
- ✅ **Rate limiting** per API
- ✅ **Error monitoring** con Sentry
- ✅ **Integration tests** completi
- ✅ **Docker Compose** per deploy facile
- ✅ **Filtri Multi-Conto** sulle API Analytics e Transazioni
### 📊 Database & Infrastructure
- ✅ **MySQL 8.0** ottimizzato con indici
- ✅ **Redis 7** per cache e Celery broker
- ✅ **Nginx** reverse proxy
- ✅ **CI/CD** con GitHub Actions
- ✅ **Health checks** e monitoring
- ✅ **Structured logging** (structlog)

---

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI 0.115+
- **AI/LLM**: LangGraph, Google Gemini 2.0 Flash
- **Database**: MySQL 8.0 con SQLAlchemy ORM
- **Cache**: Redis 7
- **Background Jobs**: Celery + Celery Beat
- **Auth**: JWT con argon2 password hashing
- **Email**: SMTP (Gmail/SendGrid compatible)
- **Monitoring**: Sentry, Structlog
- **Testing**: Pytest + Integration tests

### Frontend
- **Framework**: Flutter 3.38+ / Dart 3.0+
- **State Management**: Riverpod 2.4+
- **Navigation**: GoRouter 13.0+
- **HTTP**: Dio 5.4+
- **Local Storage**: Hive (offline mode)
- **Secure Storage**: Flutter Secure Storage
- **Push Notifications**: Firebase Cloud Messaging
- **Biometric**: local_auth package
- **UI**: Custom glassmorphism + animations

### DevOps
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Reverse Proxy**: Nginx
- **Monitoring**: Sentry + Flower (Celery)

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.13+ (solo se non usi Docker)
- Flutter 3.38+ (per mobile app)
- MySQL 8.0 & Redis 7 (solo se non usi Docker)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/savy.git
cd savy
```

### 2. Setup Environment
```bash
# Copia template environment variables
cp env.docker.example .env

# Modifica .env con i tuoi valori:
# - MYSQL_PASSWORD
# - GOOGLE_API_KEY (Gemini)
# - JWT_SECRET_KEY
# - SMTP_USER, SMTP_PASSWORD
```

### 3. Start Services (Docker)
```bash
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Check health
curl http://localhost:8000/health
```

### 4. Run Frontend
```bash
cd frontend
flutter pub get
flutter run
```

**🎉 Done! L'app è in esecuzione.**

Per guida dettagliata: [QUICK_START.md](QUICK_START.md)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [DOCUMENTAZIONE_TECNICA_COMPLETA.md](DOCUMENTAZIONE_TECNICA_COMPLETA.md) | Guida tecnica completa del sistema e dei requisiti |
| [API Docs](http://localhost:8000/docs) | Swagger UI (dopo aver avviato backend) |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FLUTTER APP (iOS/Android/Web)          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Dashboard   │  │ Transactions │  │   AI Chat    │      │
│  │  Onboarding  │  │  Categories  │  │ Optimization │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                  Riverpod State Management                  │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTPS/API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     NGINX (Reverse Proxy)                   │
└─────────────────────────────┬───────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND (Python)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           LangGraph AI Agent (6 nodes)               │   │
│  │  fetch_data → analysis → affiliate → reasoning       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Auth        │  │ Categories  │  │ Chat        │        │
│  │ JWT + OAuth │  │ CRUD        │  │ AI Coach    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└────────┬─────────────────────────┬──────────────────┬──────┘
         │                         │                  │
         ▼                         ▼                  ▼
┌─────────────────┐     ┌─────────────────┐  ┌──────────────┐
│   MySQL 8.0     │     │    Redis 7      │  │ Google       │
│   Database      │     │  Cache+Celery   │  │ Gemini API   │
│   (Persistent)  │     │  (In-memory)    │  │ (External)   │
└─────────────────┘     └─────────────────┘  └──────────────┘
         ▲                         ▲
         │                         │
         └──────────┬──────────────┘
                    │
            ┌───────▼────────┐
            │  Celery Worker │
            │  + Celery Beat │
            │ (Background    │
            │    Tasks)      │
            └────────────────┘
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Unit tests
pytest tests/ -v

# Integration tests
pytest tests/test_integration.py -v

# Coverage
pytest --cov=. --cov-report=html
```

### Frontend Tests
```bash
cd frontend

# Unit & Widget tests
flutter test

# E2E tests
flutter test integration_test/app_test.dart

# Coverage
flutter test --coverage
```

---

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Registrazione utente
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/password-reset-request` - Request reset password
- `POST /api/v1/auth/verify-email` - Verifica email

### Categories
- `GET /api/v1/categories` - Lista categorie
- `POST /api/v1/categories` - Crea categoria
- `PUT /api/v1/categories/{id}` - Aggiorna categoria
- `DELETE /api/v1/categories/{id}` - Elimina categoria

### Transactions
- `GET /api/v1/transactions` - Lista transazioni
- `POST /api/v1/transactions` - Crea transazione
- `PUT /api/v1/transactions/{id}` - Aggiorna transazione

### Chat
- `POST /api/v1/chat` - Invia messaggio all'AI coach

### Reports
- `GET /api/v1/reports/spending` - Report spese per categoria

**Full API Docs**: http://localhost:8000/docs (Swagger UI)

---

## 🔐 Security

- ✅ **JWT Authentication** con access + refresh tokens
- ✅ **Password hashing** con Argon2
- ✅ **CORS** configurato per production
- ✅ **Rate limiting** 100 req/min per user
- ✅ **Input validation** con Pydantic schemas
- ✅ **SQL injection protection** con SQLAlchemy ORM
- ✅ **HTTPS** enforced in production
- ✅ **Environment variables** per secrets
- ✅ **Biometric auth** su mobile

---

## 🤝 Contributing

Contributi sono benvenuti! Per favore:

1. Fork il repository
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

### Code Style
- **Backend**: Black, Ruff, MyPy
- **Frontend**: Dart formatter, Dart analyzer

---

## 📝 License

Questo progetto è rilasciato sotto licenza MIT. Vedi [LICENSE](LICENSE) per dettagli.

---

## 👨‍💻 Author

**Savy Team**

- Website: https://savy.app
- Email: support@savy.app
- GitHub: [@yourusername](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- **Google Gemini** per l'AI model
- **LangGraph** per agent orchestration
- **Flutter** team per framework mobile
- **FastAPI** per backend framework
- Open source community

---

## 📈 Status

- ✅ **v2.0.0** - Production ready (Gennaio 2026)
- 🚀 **22/22 features** implementate
- 🧪 **Tests**: 95%+ coverage
- 📱 **Platforms**: iOS, Android, Web
- 🌍 **Languages**: Italiano, Inglese

---

<div align="center">

**Made with ❤️ in Italy**

[⬆ Torna su](#-savy---ai-personal-finance-coach)

</div>
