# 🚂 Railway Deployment Guide

## Method 1: Deploy from GitHub (Recommended)

### Step 1: Fork Repository
1. Fork this repository to your GitHub account
2. Clone your fork locally (optional, for testing)

### Step 2: Deploy to Railway
1. Go to [Railway](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your forked `edgar-mcp-service` repository
5. Railway will automatically detect Python and start deployment

### Step 3: Configure Environment Variables
In Railway dashboard → Your Project → Variables:
```bash
SEC_API_USER_AGENT = "Crowe/EDGAR Query Engine 1.0 (brett.vantil@crowe.com)"
```

### Step 4: Get Service URL
After deployment, Railway provides a URL like:
```
https://edgar-mcp-service-production-xxxx.up.railway.app
```

### Step 5: Test Deployment
```bash
# Health check
curl https://your-railway-url.up.railway.app/health

# Company search
curl "https://your-railway-url.up.railway.app/search/company?q=Apple"
```

## Method 2: Deploy from CLI

### Prerequisites
- Railway CLI installed: `npm install -g @railway/cli`
- Railway account

### Steps
```bash
# Clone and navigate
git clone https://github.com/yourusername/edgar-mcp-service.git
cd edgar-mcp-service

# Login to Railway
railway login

# Initialize project
railway init

# Set environment variables
railway variables set SEC_API_USER_AGENT="Your Company/1.0 (your-email@example.com)"

# Deploy
railway up
```

## Integration with Your App

Once deployed, add the Railway URL to your main application's environment variables:

### For Vercel Apps:
```bash
EDGARTOOLS_SERVICE_URL=https://your-railway-url.up.railway.app
```

### For Other Apps:
```typescript
const EDGAR_MCP_URL = process.env.EDGARTOOLS_SERVICE_URL;

// Use in your application
const company = await fetch(`${EDGAR_MCP_URL}/search/company?q=Netflix`);
```

## Monitoring

### View Logs
```bash
railway logs
```

### Check Status
```bash
railway status
```

### Update Environment Variables
```bash
railway variables set KEY=VALUE
```

## Troubleshooting

### Common Issues:

1. **Build fails with Python errors**
   - Check that `requirements.txt` is present
   - Verify Python version compatibility

2. **Service starts but crashes**
   - Check logs: `railway logs`
   - Verify SEC_API_USER_AGENT is set

3. **CORS errors**
   - Service allows all origins by default
   - Check if requests are reaching the service

4. **SEC API rate limiting**
   - Ensure proper User-Agent is configured
   - Check SEC API compliance

### Support
- Railway Documentation: https://docs.railway.app
- EdgarTools Documentation: https://edgartools.readthedocs.io/