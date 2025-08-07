# EdgarTools Service - Railway Deployment

This is the core EdgarTools service that provides deep SEC filing content extraction for the Universal EDGAR Query Engine.

## Features

🔍 **Universal Company Search** - Find ANY company in SEC database  
📄 **Deep Content Extraction** - Business descriptions, risk factors, financial statements  
🔗 **Full Filing Access** - Complete document analysis and parsing  
📊 **Advanced Search** - Date ranges, form types, content filtering  

## Railway Deployment

### 1. Deploy to Railway

```bash
# From the edgar_mcp root directory
cd edgartools-service
railway login
railway init
railway up
```

### 2. Set Environment Variables in Railway

```bash
SEC_API_USER_AGENT="Crowe/EDGAR Query Engine 1.0 (brett.vantil@crowe.com)"
```

### 3. Get Your Railway URL

After deployment, Railway will provide a URL like:
```
https://your-service-name.up.railway.app
```

### 4. Update Vercel Environment

In your Vercel project settings, add:
```bash
EDGARTOOLS_SERVICE_URL=https://your-service-name.up.railway.app
```

## API Endpoints

- `GET /health` - Health check
- `GET /search/company?q=Apple` - Find any company
- `POST /search/filings` - Advanced filing search
- `POST /extract/business-description` - Extract business sections
- `POST /extract/risk-factors` - Extract risk analysis
- `POST /extract/financial-statements` - Structured financial data

## Local Development

```bash
./start.sh
```

Service runs on http://localhost:8001

## Architecture

```
User Query → Vercel (Universal Engine) → Railway (EdgarTools) → SEC Database
                                     ↓
                              Rich Analysis + Citations
```

This service is the **core** of the Universal EDGAR Query Engine - it's what enables deep document analysis beyond basic SEC API metadata.