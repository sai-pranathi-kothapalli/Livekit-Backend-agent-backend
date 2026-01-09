# Backend Deployment Steps for Render

This guide will help you deploy the backend to Render. You need to create **TWO separate services**:
1. **API Server** (Web Service) - Handles HTTP requests
2. **Agent Worker** (Background Worker) - Handles LiveKit agent connections

---

## Prerequisites

- GitHub repository: `https://github.com/sai-pranathi-kothapalli/livekit`
- Render account (sign up at https://render.com)
- All environment variables ready (from your `.env` file)

---

## Step 1: Deploy API Server (Web Service)

### 1.1 Create New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account if not already connected
4. Select repository: **`sai-pranathi-kothapalli/livekit`**
5. Click **"Connect"**

### 1.2 Configure API Server

Fill in the following settings:

**Basic Settings:**
- **Name**: `livekit-api-server` (or any name you prefer)
- **Region**: Choose closest to your users (e.g., `Oregon (US West)`)
- **Branch**: `main`
- **Root Directory**: `backend` ⚠️ **IMPORTANT: Set this to `backend`**

**Build & Deploy:**
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  uvicorn app.api.main:app --host 0.0.0.0 --port $PORT
  ```
  ⚠️ **Note**: Remove `reload=True` for production (Render handles this)

**Instance Type:**
- For testing: **Free** tier (512 MB RAM, 0.1 CPU)
- For production: **Starter** ($7/month) or higher

### 1.3 Add Environment Variables

Click **"Environment"** tab and add ALL these variables (copy from your `.env` file):

**Required - LiveKit:**
```
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_AGENT_NAME=my-interviewer
```

**Required - Deepgram (Speech-to-Text):**
```
DEEPGRAM_API_KEY=your_deepgram_api_key
DEEPGRAM_MODEL=nova-2
DEEPGRAM_LANGUAGE=en
DEEPGRAM_SMART_FORMAT=true
DEEPGRAM_INTERIM_RESULTS=true
```

**Required - ElevenLabs (Text-to-Speech):**
```
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=LQMC3j3fn1LA9ZhI4o8g
ELEVENLABS_MODEL=eleven_multilingual_v2
```

**Required - Google Gemini (LLM):**
```
GOOGLE_API_KEY=your_google_api_key
GOOGLE_LLM_MODEL=gemini-2.0-flash-exp
```

**Required - Supabase:**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

**Optional - SMTP Email:**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_NAME=Codegnan Team
SMTP_FROM_EMAIL=noreply@codegnan.com
```

**Optional - Server Config:**
```
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
FRONTEND_URL=https://your-frontend-url.com
LOG_LEVEL=INFO
```

### 1.4 Deploy API Server

1. Click **"Create Web Service"**
2. Wait for build to complete (usually 2-5 minutes)
3. Your API will be available at: `https://livekit-api-server.onrender.com` (or your custom domain)

### 1.5 Verify API Server

1. Check health endpoint: `https://your-api-url.onrender.com/healthz`
2. Should return: `{"status": "ok", "service": "interview-scheduling-api"}`

---

## Step 2: Deploy Agent Worker (Background Worker)

### 2.1 Create New Background Worker

1. In Render Dashboard, click **"New +"** → **"Background Worker"**
2. Select the same repository: **`sai-pranathi-kothapalli/livekit`**
3. Click **"Connect"**

### 2.2 Configure Agent Worker

Fill in the following settings:

**Basic Settings:**
- **Name**: `livekit-agent-worker` (or any name you prefer)
- **Region**: **Same region as API Server** (important for low latency)
- **Branch**: `main`
- **Root Directory**: `backend` ⚠️ **IMPORTANT: Set this to `backend`**

**Build & Deploy:**
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  python agent.py dev
  ```

**Instance Type:**
- For testing: **Free** tier (512 MB RAM, 0.1 CPU)
- For production: **Starter** ($7/month) or higher

### 2.3 Add Environment Variables

Click **"Environment"** tab and add **THE SAME environment variables** as the API Server:

Copy all the same variables from Step 1.3 (LiveKit, Deepgram, ElevenLabs, Google Gemini, Supabase, etc.)

⚠️ **Important**: The Agent Worker needs the same environment variables as the API Server.

### 2.4 Deploy Agent Worker

1. Click **"Create Background Worker"**
2. Wait for build to complete
3. Check logs to verify agent is connecting to LiveKit

### 2.5 Verify Agent Worker

1. Go to **"Logs"** tab in Render
2. Look for messages like:
   - `🔧 AGENT WORKER STARTING`
   - `Agent Name: 'my-interviewer'`
   - `Status: Registering with LiveKit Cloud...`
   - `Waiting for job dispatch...`

---

## Step 3: Update Frontend Configuration

After deploying, update your frontend's `.env` file:

```env
NEXT_PUBLIC_API_URL=https://your-api-url.onrender.com
```

Replace `your-api-url.onrender.com` with your actual Render API URL.

---

## Step 4: Test the Deployment

1. **Test API Server:**
   ```bash
   curl https://your-api-url.onrender.com/healthz
   ```

2. **Test Agent:**
   - Schedule an interview from the frontend
   - Check if the agent joins the interview room
   - Verify agent responds to questions

---

## Troubleshooting

### API Server Issues

**Problem**: Build fails
- **Solution**: Check that `Root Directory` is set to `backend`
- Verify `requirements.txt` exists in `backend/` folder

**Problem**: Health check fails
- **Solution**: Check logs for errors
- Verify all environment variables are set correctly

### Agent Worker Issues

**Problem**: Agent doesn't join interviews
- **Solution**: 
  - Check logs for connection errors
  - Verify `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, and `LIVEKIT_URL` are correct
  - Ensure `LIVEKIT_AGENT_NAME` matches your LiveKit configuration

**Problem**: Agent crashes on startup
- **Solution**: 
  - Check Python version (should be 3.10+)
  - Verify all dependencies are installed
  - Check logs for specific error messages

### Common Issues

**Problem**: Environment variables not loading
- **Solution**: Restart the service after adding environment variables

**Problem**: Services can't communicate
- **Solution**: Ensure both services are in the same region

---

## Cost Estimation

**Free Tier (Testing):**
- API Server: Free
- Agent Worker: Free
- **Total: $0/month**

**Starter Tier (Production):**
- API Server: $7/month
- Agent Worker: $7/month
- **Total: $14/month**

**Standard Tier (Recommended for Production):**
- API Server: $25/month (2 GB RAM, 1 CPU)
- Agent Worker: $25/month (2 GB RAM, 1 CPU)
- **Total: $50/month**

---

## Next Steps

1. Set up custom domains (optional)
2. Configure auto-deploy from main branch
3. Set up monitoring and alerts
4. Configure SSL certificates (automatic on Render)

---

## Important Notes

- ⚠️ **Root Directory**: Always set to `backend` for both services
- ⚠️ **Environment Variables**: Must be set for both services
- ⚠️ **Region**: Keep both services in the same region
- ⚠️ **Start Command**: Use production-ready commands (no `reload=True`)
- ⚠️ **Health Check**: API Server has `/healthz` endpoint for monitoring

---

## Support

If you encounter issues:
1. Check Render logs for both services
2. Verify environment variables are set correctly
3. Test locally first to ensure code works
4. Check Render status page: https://status.render.com

