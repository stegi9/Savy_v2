# 🚀 SAVY - QUICK START GUIDE

Guida rapida per avviare il progetto dopo tutte le implementazioni.

---

## 📋 PREREQUISITI

### Backend
- Python 3.13+
- Docker & Docker Compose
- MySQL 8.0 (se non usi Docker)
- Redis 7 (se non usi Docker)

### Frontend
- Flutter 3.38.5+
- Dart SDK 3.0+
- Android Studio / Xcode

---

## ⚙️ SETUP INIZIALE

### 1. Clone e Installazione

```bash
# Clone repository
git clone <your-repo-url>
cd Savy

# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
flutter pub get
flutter pub run flutter_native_splash:create
```

---

### 2. Configurazione Environment Variables

#### Backend (.env)
```bash
cd backend
cp env.example .env
# Modifica .env con i tuoi valori:
# - MYSQL_PASSWORD
# - GOOGLE_API_KEY (Gemini)
# - JWT_SECRET_KEY
# - SMTP_USER, SMTP_PASSWORD (per email)
# - SENTRY_DSN (opzionale)
```

#### Docker (.env in root)
```bash
cp env.docker.example .env
# Modifica con valori reali
```

---

## 🐳 OPZIONE 1: Docker Compose (CONSIGLIATO)

### Development
```bash
# Start tutti i servizi
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Check health
curl http://localhost:8000/health

# Stop
docker-compose down
```

### Production
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Servizi disponibili**:
- Backend API: `http://localhost:8000`
- MySQL: `localhost:3306`
- Redis: `localhost:6379`
- Flower (Celery monitor): `http://localhost:5555`

---

## 💻 OPZIONE 2: Run Locale (Senza Docker)

### 1. MySQL Setup
```bash
mysql -u root -p
CREATE DATABASE savy_db;
```

### 2. Redis Setup
```bash
# MacOS
brew install redis
brew services start redis

# Linux
sudo apt install redis-server
sudo systemctl start redis
```

### 3. Backend
```bash
cd backend

# Run migrations
alembic upgrade head

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# In altro terminale: Celery Worker
celery -A celery_tasks.celery_app worker --loglevel=info

# In altro terminale: Celery Beat
celery -A celery_tasks.celery_app beat --loglevel=info
```

### 4. Frontend
```bash
cd frontend

# Run su emulatore/device
flutter run

# O build per produzione
flutter build apk --release  # Android
flutter build ios --release  # iOS
flutter build web --release  # Web
```

---

## 🧪 TESTING

### Backend Tests
```bash
cd backend

# Run all tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Integration tests only
pytest tests/test_integration.py -v
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

## 📱 CONFIGURAZIONE MOBILE

### Android

1. **Firebase** (per push notifications):
   - Scarica `google-services.json` da Firebase Console
   - Posiziona in `frontend/android/app/google-services.json`

2. **Biometric Auth**: già configurato in `AndroidManifest.xml`

### iOS

1. **Firebase**:
   - Scarica `GoogleService-Info.plist` da Firebase Console
   - Posiziona in `frontend/ios/Runner/GoogleService-Info.plist`

2. **Face ID/Touch ID**:
   - Aggiungi in `Info.plist`:
   ```xml
   <key>NSFaceIDUsageDescription</key>
   <string>Usa Face ID per accedere rapidamente</string>
   ```

3. **Certificates**: Configura signing in Xcode

---

## 🔑 API KEYS NECESSARIE

### Obbligatori
1. **Google Gemini API Key**
   - Console: https://makersuite.google.com/app/apikey
   - Var: `GOOGLE_API_KEY`

2. **JWT Secret**
   - Genera: `openssl rand -base64 32`
   - Var: `JWT_SECRET_KEY`

### Opzionali
3. **Sentry DSN** (monitoring)
   - Console: https://sentry.io
   - Var: `SENTRY_DSN`

4. **SendGrid/SMTP** (email)
   - Gmail App Password: https://myaccount.google.com/apppasswords
   - Vars: `SMTP_USER`, `SMTP_PASSWORD`

5. **Firebase** (push notifications)
   - Console: https://console.firebase.google.com
   - Download JSON/PLIST files

6. **Affiliate APIs** (opzionali)
   - Amazon Associates: `AMAZON_PARTNER_TAG`
   - Booking.com: `BOOKING_AFFILIATE_ID`

---

## 🐛 TROUBLESHOOTING

### Backend non parte
```bash
# Check MySQL connessione
docker exec -it savy_mysql mysql -uroot -p -e "SHOW DATABASES;"

# Check Redis
docker exec -it savy_redis redis-cli ping

# Check logs
docker-compose logs backend
```

### Frontend compilation errors
```bash
# Clean e rebuild
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs

# Check Flutter doctor
flutter doctor -v
```

### Celery tasks non eseguiti
```bash
# Check Celery worker logs
docker-compose logs celery_worker

# Check Redis connection
redis-cli ping

# Manually trigger task (debug)
python -c "from celery_tasks import send_verification_email; send_verification_email.delay('test@test.com', 'Test', 'token123')"
```

### Database migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📊 MONITORING

### Health Checks
```bash
# Basic health
curl http://localhost:8000/health

# Detailed health (DB, Redis, Cache, LLM)
curl http://localhost:8000/health/detailed
```

### Celery Tasks Monitor (Flower)
```bash
# Access Flower UI
open http://localhost:5555
```

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### Sentry (se configurato)
- Dashboard: https://sentry.io
- View errors, performance, releases

---

## 🔐 SECURITY CHECKLIST PRE-PRODUZIONE

- [ ] Cambiato `JWT_SECRET_KEY` con valore sicuro (32+ chars)
- [ ] Cambiato `MYSQL_PASSWORD` dal default
- [ ] Cambiato `REDIS_PASSWORD` dal default
- [ ] Configurato HTTPS (SSL certificates)
- [ ] Configurato CORS restrittivo (`CORS_ORIGINS`)
- [ ] Abilitato firewall su porte DB (3306, 6379)
- [ ] Configurato backup automatici database
- [ ] Configurato Sentry per monitoring
- [ ] Disabilitato debug mode (`ENVIRONMENT=production`)
- [ ] Configurato rate limiting appropriato
- [ ] Verificato email SMTP funzionante
- [ ] Test notifiche push Firebase

---

## 📚 DOCUMENTAZIONE AGGIUNTIVA

- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Redoc**: `http://localhost:8000/redoc`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Database Schema**: `backend/db/mysql_schema.sql`
- **Architecture**: Vedi `.cursorrules` nel progetto

---

## 🎯 FIRST RUN CHECKLIST

1. ✅ Installato dipendenze (Python + Flutter)
2. ✅ Configurato `.env` files
3. ✅ Avviato Docker Compose (o MySQL + Redis locali)
4. ✅ Run migrations database
5. ✅ Configurato Firebase (per push notifications)
6. ✅ Generato splash screen (`flutter_native_splash`)
7. ✅ Testato backend: `curl http://localhost:8000/health`
8. ✅ Testato frontend: `flutter run`
9. ✅ Creato utente di test via `/api/v1/auth/register`
10. ✅ Verificato email service funzionante

---

## 💡 TIPS

- **Hot reload** backend: Uvicorn auto-reload è attivo in dev
- **Hot reload** frontend: `r` in terminale Flutter per hot reload
- **Database GUI**: Usa DBeaver, TablePlus, o MySQL Workbench per gestire DB
- **API Testing**: Usa Postman collection (crea da Swagger export)
- **Git hooks**: Pre-commit hooks per linting (opzionale)

---

## 🆘 SUPPORTO

In caso di problemi:
1. Check logs: `docker-compose logs -f`
2. Check health endpoints
3. Verifica environment variables
4. Controlla firewall/porte
5. Review `IMPLEMENTATION_SUMMARY.md` per dettagli implementazioni

---

**Buon coding! 🚀**

*Savy v2.0.0 - Production Ready*
