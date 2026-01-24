# 💰 Savy - AI Personal Finance Coach

**Savy** è un Personal Finance Coach AI-native che trasforma la gestione del denaro da un compito passivo a un'azione attiva, aiutandoti a risparmiare in tempo reale attraverso l'intelligenza artificiale.

![Flutter](https://img.shields.io/badge/Flutter-3.38-blue?logo=flutter)
![Python](https://img.shields.io/badge/Python-3.10+-green?logo=python)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)
![Gemini](https://img.shields.io/badge/Google_Gemini-AI-purple?logo=google)
![Salt Edge](https://img.shields.io/badge/Salt_Edge-Fake_Integration-blue?logo=bancolombia)

---

## 🌟 Features Principali

### 🏦 Integrazione Bancaria (Novità!)
- **Open Banking Simulator**: Collega il tuo conto bancario tramite integrazione Salt Edge (Ambiente Fake/Sandbox).
- **Sync Automatico**: Importa transazioni e saldo con un click.
- **Auto-Categorizzazione**: Le transazioni importate vengono categorizzate automaticamente dall'AI.

### 🎨 Esperienza Utente Avanzata
- **Dark Mode**: Supporto completo per tema chiaro e scuro, sincronizzato con le impostazioni di sistema o manuale.
- **Localizzazione**: Interfaccia completamente tradotta in Italiano 🇮🇹 e Inglese 🇬🇧.
- **UI Moderna**: Grafici interattivi, skeleton loaders e animazioni fluide.

### 🤖 Intelligenza Artificiale
- **Financial Coach**: Chatta con "Savy Coach" per consigli su spese e budget (es. *"Posso permettermi questa cena?"*).
- **Analisi Spese**: L'AI analizza i tuoi pattern di spesa e suggerisce dove risparmiare.
- **Categorizzazione Intelligente**: Riconosce automaticamente merchant e tipologia di spesa.

### 📊 Gestione Finanziaria
- **Dashboard Completa**: Panoramica di saldo, entrate, uscite e budget mensile.
- **Transazioni**: Aggiungi, modifica ed elimina transazioni manualmente o sincronizzale.
- **Spese Ricorrenti**: Gestione bollette e abbonamenti con scadenze.
- **Categorie Personalizzate**: Crea categorie con colori unici ed icone dedicate.

### 🛍️ Smart Savings & Affiliate Aggregator (Nuovo!)
Savy evolve in un aggregatore universale di offerte. Per ogni categoria di spesa, l'app identifica proattivamente opportunità di risparmio:
- **Verticali Coperti**: Bollette, Shopping (Amazon), Viaggi, Hotel, Benzina, Spesa, Telefonia Mobile, e altro.
- **Interazione via Chat**: Chiedi al Coach *"Trovami l'offerta migliore per un hotel a Roma"* o *"Voglio risparmiare sulla bolletta luce"*.
- **Vantaggio Doppio**: L'utente ottiene sconti esclusivi o prezzi migliori; la piattaforma genera revenue tramite affiliazione sicura.
- **Offerte Contestuali**: Suggerimenti automatici basati sulle tue transazioni recenti (es. hai speso tanto in benzina? Ecco un cashback).

---

## 🏗️ Architettura

### Stack Tecnologico

**Frontend:**
- **Flutter** (Dart) - Cross-platform (Android, iOS)
- **Riverpod** - State Management reattivo
- **Go Router** - Navigazione dichiarativa e deep linking
- **Fl Chart** - Libreria grafici performante
- **Shared Preferences** - Persistenza locale settings

**Backend:**
- **Python 3.10+** con **FastAPI**
- **LangChain** + **Google Gemini** - Orchestrazione AI
- **MySQL 8.0** - Database relazionale
- **SQLAlchemy** - ORM
- **Salt Edge (Fake)** - Simulazione Open Banking

---

## 🚀 Quick Start

### Prerequisiti

- **Python 3.10+**
- **Flutter 3.38+**
- **MySQL 8.0+**
- **Google Gemini API Key** ([Ottieni qui](https://makersuite.google.com/app/apikey))

### 1️⃣ Setup Backend

```bash
cd backend

# Crea virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows

# Installa dipendenze
pip install -r requirements.txt

# Configura variabili ambiente
cp .env.example .env
# Modifica .env con:
# - GEMINI_API_KEY
# - MYSQL_CREDENTIALS

# Inizializza Database
mysql -u root -p savy_db < db/mysql_schema.sql

# Avvia server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2️⃣ Setup Frontend

```bash
cd frontend

# Installa dipendenze
flutter pub get

# Avvia App
flutter run
```

**Nota per Emulatore Android:** Il backend è raggiungibile su `http://10.0.2.2:8000`.

---

## 🔐 Sicurezza & Privacy

- **Autenticazione JWT**: Login sicuro con token.
- **No Real Banking Data**: L'integrazione bancaria attuale utilizza dati simulati (Sandbox), nessun dato reale viene processato.
- **Dati Locali**: Le preferenze di tema e lingua sono salvate localmente sul dispositivo.

---

## 👨‍💻 Autore

**Stefano** - Sviluppo Full Stack & AI Integration

---

## 📄 Licenza

Progetto proprietario. Tutti i diritti riservati.


![Flutter](https://img.shields.io/badge/Flutter-3.38-blue?logo=flutter)
![Python](https://img.shields.io/badge/Python-3.10+-green?logo=python)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)
![Gemini](https://img.shields.io/badge/Google_Gemini-AI-purple?logo=google)

---

## 🌟 Features Principali

### ✅ Implementate (MVP)

- **🤖 Categorizzazione AI Dinamica**: L'AI analizza il contesto delle transazioni (es. Amazon → Elettronica o Casa)
- **💬 "Cocktail Check" (Financial Coach)**: Chiedi in linguaggio naturale: *"Posso spendere 10€ per un cocktail stasera?"*
- **⚡ Motore di Ottimizzazione**: Scansiona bollette (luce, gas, telco) e identifica offerte migliori
- **📊 Report Dettagliati**: Visualizza grafici e distribuzione spese per categoria con budget tracking
- **📂 Categorie Personalizzate**: Crea e gestisci le tue categorie di spesa custom
- **📱 Schermata Transazioni**: Gestisci transazioni con auto-categorizzazione AI e confidence score

### ✅ Recentemente Aggiunte

- 🔐 **Autenticazione JWT** - Login/Registrazione con token sicuro
- 📅 **Gestione bollette ricorrenti** - UI completa per le spese fisse
- ⚙️ **Settings sincronizzati** - Impostazioni utente salvate su backend
- 💀 **Skeleton Loaders** - UX migliorata durante il caricamento
- 🔄 **Error Handling** - Messaggi user-friendly con retry

### 🔜 Roadmap

- 🔗 Connessione bancaria automatica (Open Banking API)
- 🎯 AI predittiva per analisi finanziaria avanzata
- 💳 Passaggio fornitori in 1-click
- 🌐 Multi-account e multi-utente
- 📲 Notifiche push (in attesa fix package Flutter)

---

## 🏗️ Architettura

### Stack Tecnologico

**Frontend:**
- Flutter (Dart) - Cross-platform (Android, iOS, Web)
- Riverpod - State management
- Go Router - Navigazione dichiarativa
- FL Chart - Grafici interattivi

**Backend:**
- Python 3.10+ con FastAPI
- LangChain + Google Gemini - AI/LLM
- MySQL 8.0 - Database relazionale
- SQLAlchemy - ORM
- Pydantic - Validazione dati

**Architettura Backend:**
```
3-Layer Architecture:
├── Repository Layer (Data Access)
├── Service Layer (Business Logic)
└── Controller Layer (API Endpoints)
```

**Architettura Frontend:**
```
Clean Architecture + Feature-First:
├── core/ (router, theme, services)
├── features/ (domain, data, presentation)
└── shared/ (widgets, utils)
```

---

## 🚀 Quick Start

### Prerequisiti

- **Python 3.10+**
- **Flutter 3.38+**
- **MySQL 8.0+**
- **Google Gemini API Key** ([Ottieni qui](https://makersuite.google.com/app/apikey))

### 1️⃣ Setup Backend

```bash
cd backend

# Crea virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Installa dipendenze
pip install -r requirements.txt

# Configura variabili ambiente
cp .env.example .env
# Modifica .env con le tue credenziali

# Crea database MySQL
mysql -u root -p
CREATE DATABASE savy_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Esegui schema SQL
mysql -u root -p savy_db < db/mysql_schema.sql

# Avvia server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend sarà disponibile su:** `http://localhost:8000`
**Documentazione API:** `http://localhost:8000/docs`

### 2️⃣ Setup Frontend

```bash
cd frontend

# Installa dipendenze
flutter pub get

# Avvia emulatore Android/iOS
flutter emulators --launch <emulator-id>

# Esegui app
flutter run
```

**Per emulatore Android, il backend è raggiungibile su:** `http://10.0.2.2:8000`

---

## 📁 Struttura del Progetto

```
Savy/
├── backend/
│   ├── api/routes/          # Controllers (FastAPI routers)
│   ├── db/                  # Database config & migrations
│   ├── models/              # SQLAlchemy ORM models
│   ├── repositories/        # Data access layer
│   ├── services/            # Business logic
│   ├── nodes/               # LangGraph AI nodes
│   ├── utils/               # Utilities
│   ├── config.py            # App configuration
│   ├── main.py              # FastAPI entry point
│   └── requirements.txt     # Python dependencies
│
├── frontend/
│   ├── lib/
│   │   ├── core/            # App-wide (router, theme, services)
│   │   ├── features/        # Feature modules
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── chat/
│   │   │   ├── transactions/
│   │   │   ├── categories/
│   │   │   ├── reports/
│   │   │   ├── optimization/
│   │   │   ├── settings/
│   │   │   └── onboarding/
│   │   ├── shared/          # Reusable widgets
│   │   ├── main.dart        # App entry point
│   │   └── app.dart         # MaterialApp config
│   └── pubspec.yaml         # Flutter dependencies
│
├── .cursorrules             # Cursor AI rules
├── .gitignore
├── README.md
└── DEPLOY.md                # Deployment guide
```

---

## 🔧 Configurazione

### Backend (.env)

```env
# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=savy_db

# Google Gemini AI
GEMINI_API_KEY=your_api_key_here

# JWT
JWT_SECRET_KEY=your_secret_key_32_chars_min
JWT_ALGORITHM=HS256

# App
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### Frontend (env.dart)

```dart
class Env {
  static const apiBaseUrl = 'http://10.0.2.2:8000';  // Android emulator
  // static const apiBaseUrl = 'http://localhost:8000';  // iOS simulator
}
```

---

## 🧪 Testing

### Backend

```bash
cd backend
pytest tests/ -v
```

### Frontend

```bash
cd frontend
flutter test
flutter analyze
```

---

## 📊 Database Schema

Il database MySQL include le seguenti tabelle principali:

- `profiles` - Profili utente con saldo e impostazioni
- `user_categories` - Categorie di spesa personalizzate
- `transactions` - Transazioni finanziarie con AI categorization
- `recurring_bills` - Bollette ricorrenti
- `optimization_leads` - Opportunità di ottimizzazione identificate dall'AI
- `partners` - Partner fornitori per ottimizzazioni

**Schema completo:** `backend/db/mysql_schema.sql`

---

## 🤖 AI Features

### Categorizzazione Intelligente

L'AI analizza:
- Nome del merchant
- Importo della transazione
- Descrizione (se disponibile)
- Contesto storico

Esempio:
- "Amazon - €50 - Cuffie Bluetooth" → **Elettronica** (confidence: 95%)
- "Amazon - €12 - Detersivo" → **Casa** (confidence: 85%)

### Financial Coach (Cocktail Check)

```
User: "Posso spendere 50€ per una cena fuori?"

AI Coach:
"Sì, ma ricorda che la prossima settimana hai l'addebito 
della palestra (€40). Se spendi ora, rimarrai con solo 
€30 per imprevisti fino a fine mese. Consiglio: limita 
la spesa a €30 per maggiore sicurezza."
```

---

## 🐛 Troubleshooting

### Backend non si avvia

- Verifica che MySQL sia in esecuzione
- Controlla le credenziali in `.env`
- Verifica che il database `savy_db` esista

### Frontend non si connette al backend

- **Android Emulator**: Usa `http://10.0.2.2:8000`
- **iOS Simulator**: Usa `http://localhost:8000`
- Verifica che il backend sia in ascolto su `0.0.0.0:8000`

### Errori di compilazione Flutter

```bash
flutter clean
flutter pub get
flutter run
```

---

## 📄 Licenza

Questo progetto è proprietario. Tutti i diritti riservati.

---

## 👨‍💻 Autore

**Stefano** - [GitHub](https://github.com/stefa)

---

## 🙏 Ringraziamenti

- **Google Gemini** per l'AI/LLM
- **Flutter Team** per il framework cross-platform
- **FastAPI** per il backend veloce e moderno
- **Community Open Source** per le librerie utilizzate

---

## 📚 Documentazione

- [Deployment Guide](DEPLOY.md) - Guida al deploy
- [API Docs](http://localhost:8000/docs) - Swagger UI (quando il backend è attivo)

---

**⭐ Se questo progetto ti è utile, lascia una stella su GitHub!**
