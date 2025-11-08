# Deployment Guide

This guide covers deploying the Vibeathon application to various platforms: Replit, Netlify, and Vercel.

## Prerequisites

Before deploying, ensure you have:
1. All required API keys (see `.env.example`)
2. A database (SQLite for development, PostgreSQL recommended for production)
3. Node.js 20+ and Python 3.11+ installed

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required variables:
- `GEMINI_API_KEY` - Google Gemini API key for AI features
- `JWT_SECRET` - Secret key for JWT token generation (use a strong random string)
- `DATABASE_URL` - Database connection string
- `PORT` - Server port (default: 5000)

Optional variables:
- `YOUTUBE_API_KEY` - For YouTube search functionality
- `JUDGE0_API_KEY` - For code execution features
- `CORS_ORIGINS` - Comma-separated list of allowed origins

## Deployment Options

### 1. Replit Deployment

Replit is configured to run both the Node.js backend and Python backend.

**Steps:**
1. Import this repository to Replit
2. Set environment variables in Replit Secrets:
   - Add all variables from `.env.example`
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Click "Run" to start the application
5. The app will be available at your Replit URL

**Configuration Files:**
- `.replit` - Replit configuration
- `replit.nix` - System packages
- `start_python_backend.sh` - Python backend startup script

**Notes:**
- The default workflow starts the Node.js server on port 5000
- Python backend runs separately on port 8001
- Both services need to run for full functionality

### 2. Netlify Deployment

Netlify is configured for static frontend deployment with serverless functions.

**Steps:**
1. Connect your GitHub repository to Netlify
2. Configure build settings:
   - Build command: `npm run build`
   - Publish directory: `dist/public`
3. Set environment variables in Netlify dashboard:
   - Add all variables from `.env.example`
4. Deploy

**Configuration File:**
- `netlify.toml` - Netlify configuration with redirects

**Notes:**
- The Python backend needs to be deployed separately (e.g., on Railway, Render, or Fly.io)
- Update `CORS_ORIGINS` to include your Netlify URL
- API routes are proxied via serverless functions

### 3. Vercel Deployment

Vercel supports both frontend and Node.js backend deployment.

**Steps:**
1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in the project directory
3. Set environment variables:
   ```bash
   vercel env add GEMINI_API_KEY
   vercel env add JWT_SECRET
   # Add other variables...
   ```
4. Deploy: `vercel --prod`

**Configuration File:**
- `vercel.json` - Vercel configuration

**Notes:**
- The Python backend needs to be deployed separately
- Node.js backend runs as serverless functions
- Update `CORS_ORIGINS` to include your Vercel URL

## Python Backend Deployment

The Python backend (FastAPI) can be deployed to:

### Option A: Railway
1. Create a new project on Railway
2. Connect your GitHub repository
3. Add a new service and select "Deploy from GitHub repo"
4. Set the start command: `uvicorn python_backend.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

### Option B: Render
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn python_backend.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables
5. Deploy

### Option C: Fly.io
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Create a `fly.toml` file (see example below)
3. Run `fly launch`
4. Set secrets: `fly secrets set GEMINI_API_KEY=your_key`
5. Deploy: `fly deploy`

Example `fly.toml`:
```toml
app = "your-app-name"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

## Database Configuration

### Development
- SQLite is used by default (`DATABASE_URL=sqlite:///./agentverse.db`)

### Production
- PostgreSQL is recommended
- Update `DATABASE_URL` to your PostgreSQL connection string
- Example: `postgresql://user:password@host:5432/dbname`

### Database Migrations
Run database migrations on startup (handled automatically by the app):
```bash
# Python backend creates tables automatically on startup
uvicorn python_backend.main:app --host 0.0.0.0 --port 8001
```

## Security Considerations

1. **Never commit `.env` file** - It's in `.gitignore` for a reason
2. **Use strong JWT_SECRET** - Generate with: `openssl rand -hex 32`
3. **Update CORS_ORIGINS** - Only allow your production domains
4. **Rotate API keys** - Regularly update your API keys
5. **Use HTTPS** - Always use HTTPS in production
6. **Database backups** - Set up regular database backups

## Troubleshooting

### Build Failures
- Ensure all dependencies are installed: `npm install` and `pip install -r requirements.txt`
- Check Node.js and Python versions match requirements
- Review build logs for specific errors

### CORS Errors
- Update `CORS_ORIGINS` in `.env` to include your frontend URL
- Ensure the Python backend URL is correctly configured in the frontend

### Database Errors
- Verify `DATABASE_URL` is correct
- Check database permissions
- Ensure database server is running and accessible

### Python Dependencies
- For image processing features, ensure system packages are installed:
  - `tesseract-ocr` for OCR
  - `poppler-utils` for PDF processing
  - `libmagic` for file type detection

## Monitoring and Logs

- **Replit**: View logs in the Console tab
- **Netlify**: Check Functions logs in the Netlify dashboard
- **Vercel**: View logs in the Vercel dashboard
- **Railway/Render**: Check logs in their respective dashboards

## Support

For issues or questions:
1. Check the README.md
2. Review documentation in `IMPLEMENTATION_SUMMARY.md` and `PYTHON_BACKEND.md`
3. Open an issue on GitHub
