# 🐳 Savy - Architettura e Docker

## Struttura del Progetto

```
Savy/
├── backend/                    # 🐍 API FastAPI
│   ├── api/                    # Controllers (endpoints HTTP)
│   ├── db/                     # Database config e connessione
│   ├── models/                 # SQLAlchemy ORM models
│   ├── nodes/                  # LangGraph AI nodes
│   ├── repositories/           # Data Access Layer
│   ├── services/               # Business Logic
│   │   ├── affiliate/          # Sistema affiliazioni
│   │   ├── cache_service.py    # Redis caching
│   │   ├── intent_detector.py  # LLM intent detection
│   │   └── llm_service.py      # Google Gemini integration
│   ├── scripts/                # Utility scripts
│   ├── tests/                  # Unit tests
│   ├── utils/                  # Helper functions
│   ├── config.py               # Environment config
│   ├── graph.py                # LangGraph state machine
│   ├── main.py                 # FastAPI entrypoint
│   ├── schemas.py              # Pydantic models
│   ├── worker.py               # Background jobs
│   ├── Dockerfile              # Dev container
│   ├── Dockerfile.prod         # Production container
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # 📱 Flutter App
│   ├── lib/                    # Dart source code
│   ├── android/                # Android config
│   ├── test/                   # Widget tests
│   └── pubspec.yaml            # Flutter dependencies
│
├── nginx/                      # ⚖️ Load Balancer
│   └── nginx.conf              # Nginx configuration
│
├── docker-compose.yml          # 🚀 Production setup
└── docker-compose.dev.yml      # 💻 Development setup
```

---

## 🐳 Docker Architecture

### Production (`docker-compose.yml`)

```
                         ┌──────────────────────────────────┐
                         │         Internet (Users)          │
                         └───────────────┬──────────────────┘
                                         │
                         ┌───────────────▼──────────────────┐
                         │       NGINX (Port 80/443)         │
                         │  • Load Balancing (least_conn)    │
                         │  • Rate Limiting (10 req/s)       │
                         │  • Gzip Compression               │
                         │  • SSL Termination                │
                         └───────────────┬──────────────────┘
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              │                          │                          │
    ┌─────────▼─────────┐      ┌─────────▼─────────┐      ┌─────────▼─────────┐
    │   API Replica 1   │      │   API Replica 2   │      │      Worker       │
    │   ┌───────────┐   │      │   ┌───────────┐   │      │   Background      │
    │   │ Gunicorn  │   │      │   │ Gunicorn  │   │      │   Tasks           │
    │   │ 4 workers │   │      │   │ 4 workers │   │      │   • Sync banks    │
    │   │ (Uvicorn) │   │      │   │ (Uvicorn) │   │      │   • Notifications │
    │   └───────────┘   │      │   └───────────┘   │      │   • Analytics     │
    └─────────┬─────────┘      └─────────┬─────────┘      └─────────┬─────────┘
              │                          │                          │
              └──────────────────────────┼──────────────────────────┘
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              │                          │                          │
    ┌─────────▼─────────┐      ┌─────────▼─────────┐      ┌─────────▼─────────┐
    │      MySQL        │      │      Redis        │      │  Google Gemini    │
    │   (Database)      │      │    (Caching)      │      │     (LLM API)     │
    │   • Users         │      │   • LLM cache     │      │   • Chat AI       │
    │   • Transactions  │      │   • Rate limits   │      │   • Categorization│
    │   • Categories    │      │   • Sessions      │      │   • Analysis      │
    └───────────────────┘      └───────────────────┘      └───────────────────┘
```

---

## Services Explained

### 1. **API** (FastAPI)
- **Replicas**: 2 (scalabile fino a N)
- **Workers per replica**: 4 Uvicorn workers
- **Capacità totale**: ~500+ utenti contemporanei
- **Auto-restart**: Su crash o memory leak

### 2. **NGINX** (Load Balancer)
- **Algoritmo**: `least_conn` (invia al server meno carico)
- **Rate Limiting**:
  - API generica: 10 req/s per IP
  - Chat (LLM): 2 req/s per IP (protegge da abusi)
- **Compressione**: Gzip per risposte JSON

### 3. **Redis** (Cache)
- **Scopo**: Riduce latenza e chiamate LLM
- **TTL**: 5 minuti default
- **Eviction**: LRU (Least Recently Used)
- **Uso memoria**: Max 256 MB

### 4. **MySQL** (Database)
- **Dati persistenti**: Utenti, transazioni, categorie
- **Volume Docker**: I dati sopravvivono ai restart
- **Backup**: Configurabile con cron + mysqldump

### 5. **Worker** (Background)
- **Task asincroni**: Sync banche, notifiche push
- **Coda**: Redis-based (RQ o Celery)
- **Retry**: Automatico su failure

---

## Commands

### 🔧 Development (Locale)

```bash
# Avvia solo MySQL + Redis
docker-compose -f docker-compose.dev.yml up -d

# Verifica che siano attivi
docker-compose -f docker-compose.dev.yml ps

# Avvia backend locale
cd backend
.\.venv\Scripts\activate
python -m uvicorn main:app --reload

# Stop
docker-compose -f docker-compose.dev.yml down
```

### 🚀 Production

```bash
# Build e avvia tutto
docker-compose up -d --build

# Scala a 4 API replicas
docker-compose up -d --scale api=4

# Vedi logs in tempo reale
docker-compose logs -f api

# Restart solo l'API
docker-compose restart api

# Stop tutto
docker-compose down

# Stop e rimuovi volumi (⚠️ cancella dati!)
docker-compose down -v
```

### 📊 Monitoring

```bash
# Stato servizi
docker-compose ps

# Uso risorse
docker stats

# Health check
curl http://localhost/health

# Logs Nginx
docker-compose logs nginx
```

---

## Environment Variables

Copia `.env.example` → `.env` e compila:

| Variabile | Obbligatoria | Descrizione |
|-----------|--------------|-------------|
| `MYSQL_PASSWORD` | ✅ | Password database |
| `GEMINI_API_KEY` | ✅ | Google AI API key |
| `JWT_SECRET_KEY` | ✅ | Chiave per token auth |
| `REDIS_URL` | ⚪ | `redis://redis:6379/0` |
| `AMAZON_ACCESS_KEY` | ⚪ | Per affiliazioni reali |
| `BOOKING_API_KEY` | ⚪ | Per hotel reali |

---

## Performance Attese

| Metrica | Dev (uvicorn) | Prod (Docker) |
|---------|---------------|---------------|
| Utenti contemporanei | ~50 | ~500+ |
| Latenza API (P95) | 200ms | 100ms |
| Tempo risposta LLM | 2-5s | 2-5s (cache: <100ms) |
| Requests/secondo | ~100 | ~1000+ |
| Uptime | - | 99.9% (health checks) |

---

## FAQ

**Q: Posso usare Docker Desktop su Windows?**
A: Sì, ma abilita WSL2 per performance migliori.

**Q: Quanto spazio occupa Docker?**
A: ~500 MB per le immagini + dati database.

**Q: Come aggiorno il codice in produzione?**
A: `git pull && docker-compose up -d --build`

**Q: Come faccio backup del database?**
A: `docker-compose exec db mysqldump -u root -p savy_db > backup.sql`
