# 🚀 Savy - Deployment Guide

This guide covers deploying Savy to production.

---

## 📦 Backend Deployment Options

### Option 1: Railway (Recommended - Easiest)

1. **Create Railway Account**: https://railway.app

2. **Connect GitHub Repository**:
   ```bash
   # Push your code to GitHub first
   git push origin main
   ```

3. **Create New Project**:
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects the Dockerfile

4. **Configure Environment Variables**:
   In Railway dashboard, add:
   ```
   MYSQL_HOST=your-db-host
   MYSQL_PORT=3306
   MYSQL_USER=your-user
   MYSQL_PASSWORD=your-password
   MYSQL_DATABASE=savy
   JWT_SECRET_KEY=your-secret-key
   GEMINI_API_KEY=your-gemini-key
   ENVIRONMENT=production
   ```

5. **Deploy**: Railway auto-deploys on push!

---

### Option 2: Render.com

1. **Create Render Account**: https://render.com

2. **New Web Service**:
   - Connect GitHub repo
   - Select "Docker" as runtime
   - Root directory: `backend`

3. **Configure Environment**:
   Add all env vars in the dashboard

4. **Deploy**: Click "Create Web Service"

---

### Option 3: Fly.io

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login & Initialize**:
   ```bash
   cd backend
   fly auth login
   fly launch  # Follow prompts
   ```

3. **Set Secrets**:
   ```bash
   fly secrets set \
     MYSQL_HOST=your-host \
     MYSQL_USER=your-user \
     MYSQL_PASSWORD=your-password \
     MYSQL_DATABASE=savy \
     JWT_SECRET_KEY=your-secret \
     GEMINI_API_KEY=your-key
   ```

4. **Deploy**:
   ```bash
   fly deploy
   ```

---

## 🗄️ Database Options

### Option 1: PlanetScale (Recommended)

**Free tier: 5GB storage, 1 billion row reads/month**

1. **Create Account**: https://planetscale.com

2. **Create Database**:
   - Name: `savy`
   - Region: `eu-west` (Frankfurt)

3. **Get Connection String**:
   - Go to "Connect" → "Connect with: MySQL CLI"
   - Note the host, username, password

4. **Run Schema**:
   ```bash
   # Connect via MySQL CLI or use their web console
   mysql -h aws.connect.psdb.cloud -u your_username -p your_database < backend/db/mysql_schema.sql
   ```

5. **Enable SSL**: PlanetScale requires SSL, add to connection:
   ```python
   # In db/database.py, update connect_args:
   connect_args={"ssl": {"ssl_mode": "REQUIRED"}}
   ```

---

### Option 2: Railway MySQL

Railway can provision MySQL alongside your app:

1. In Railway project, click "New" → "Database" → "MySQL"
2. Railway auto-injects `DATABASE_URL` env var
3. Update `db/database.py` to use `DATABASE_URL` if available

---

### Option 3: Aiven MySQL

**Free tier: 5GB, 1 node**

1. Create account: https://aiven.io
2. Create MySQL service
3. Use provided connection details

---

## 📱 Frontend Configuration

Update `frontend/lib/core/constants/env.dart`:

```dart
class Env {
  // Production API URL
  static const String apiBaseUrl = 'https://your-api-url.railway.app';
  
  // OR use environment-based config:
  static String get apiBaseUrl {
    const url = String.fromEnvironment('API_URL', 
      defaultValue: 'http://10.0.2.2:8000');
    return url;
  }
}
```

Build for production:
```bash
cd frontend
flutter build apk --release --dart-define=API_URL=https://your-api.railway.app
flutter build ios --release --dart-define=API_URL=https://your-api.railway.app
```

---

## ✅ Production Checklist

### Security
- [ ] JWT_SECRET_KEY is unique and secure (64+ chars)
- [ ] CORS_ORIGINS restricted to your domains only
- [ ] HTTPS enforced (Railway/Render/Fly do this automatically)
- [ ] DEBUG=false in production
- [ ] Database uses SSL connection

### Performance
- [ ] Database has appropriate indexes
- [ ] API rate limiting enabled
- [ ] Caching for repeated queries

### Monitoring
- [ ] Health check endpoint working (`/health`)
- [ ] Error logging configured (consider Sentry)
- [ ] Performance metrics tracked

---

## 🔧 Useful Commands

```bash
# Test Docker build locally
cd backend
docker build -t savy-api .
docker run -p 8000:8000 --env-file .env savy-api

# Generate secure JWT secret
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Test API health
curl https://your-api-url.railway.app/health
```

---

## 💰 Cost Estimates

| Service | Free Tier | Paid |
|---------|-----------|------|
| Railway | $5 credit/month | $5-20/month |
| Render | 750 hours/month | $7/month |
| Fly.io | 3 shared VMs | $3-10/month |
| PlanetScale | 5GB + 1B reads | $29/month |
| Aiven | 5GB free | $19/month |

**Recommended Stack (Budget):**
- Railway (backend) + PlanetScale (DB) = ~$5-10/month

**Recommended Stack (Production):**
- Fly.io (backend) + PlanetScale Scaler (DB) = ~$30-50/month

