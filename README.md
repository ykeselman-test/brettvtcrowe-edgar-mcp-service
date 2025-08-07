# 🏛️ Edgar MCP Service

> **Model Context Protocol (MCP) Server for SEC EDGAR Database**  
> Deep financial document analysis and content extraction service

## 🚀 Quick Deploy to Railway

### One-Click Deployment:
1. **Fork this repository** to your GitHub account
2. **Connect to Railway**: Go to [Railway](https://railway.app) → New Project → Deploy from GitHub repo
3. **Set environment variable**: `SEC_API_USER_AGENT="Your Company/1.0 (your-email@example.com)"`
4. **Get your service URL** from Railway dashboard
5. **Done!** Your MCP service is live

## 🎯 What This Service Provides

### 🔍 Universal Company Search
- Find **ANY** public company by name, ticker, or partial match
- Works with Apple, Netflix, small caps, recent IPOs, etc.
- No hardcoded company lists - truly universal

### 📄 Deep Document Analysis
- **Business descriptions** from 10-K Item 1
- **Risk factors** from 10-K Item 1A  
- **Financial statements** with structured data
- **Management discussion** (MD&A) extraction
- **Full-text search** within any SEC filing

### 🔗 Advanced Filing Search
- **Date range filtering**: "filings between Jan-Mar 2024"
- **Form type filtering**: 10-K, 10-Q, 8-K, etc.
- **Content search**: "documents mentioning revenue recognition"
- **Direct SEC EDGAR links** for all results

## 📡 API Endpoints

### Company Search
```bash
GET /search/company?q=Netflix
```
Response:
```json
{
  "found": true,
  "cik": "0001065280",
  "name": "NETFLIX INC",
  "ticker": "NFLX",
  "confidence": 1.0
}
```

### Advanced Filing Search
```bash
POST /search/filings
{
  "company": "Apple",
  "form_types": ["10-K", "10-Q"],
  "date_from": "2024-01-01",
  "content_search": "artificial intelligence",
  "limit": 10
}
```

### Content Extraction
```bash
POST /extract/business-description
{
  "cik": "0000320193",
  "form_type": "10-K"
}
```

## 🏗️ Architecture

This MCP service is designed to work with AI query engines:

```
User Query → AI Engine → Edgar MCP → SEC Database
              ↓
    "Netflix's risk factors" → Company Resolution → Deep Content → Structured Response
```

### Integration Example:
```typescript
// In your AI application
const edgarMCP = 'https://your-service.up.railway.app';

// 1. Resolve company
const company = await fetch(`${edgarMCP}/search/company?q=Netflix`);

// 2. Get content
const riskFactors = await fetch(`${edgarMCP}/extract/risk-factors`, {
  method: 'POST',
  body: JSON.stringify({ cik: company.cik })
});

// 3. Use in AI analysis
const analysis = await openai.chat.completions.create({
  messages: [{ role: 'user', content: `Analyze these risk factors: ${riskFactors}` }]
});
```

## 🛠️ Manual Deployment

### Prerequisites
- Python 3.11+
- Railway account
- SEC compliance: proper User-Agent string

### Local Development
```bash
git clone <this-repo>
cd edgar-mcp-service
chmod +x start.sh
./start.sh
```

Service runs at `http://localhost:8001`

### Deploy to Railway
```bash
railway login
railway init
railway variables set SEC_API_USER_AGENT="Your Company/1.0 (email@example.com)"
railway up
```

## 📋 Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SEC_API_USER_AGENT` | ✅ | SEC API compliance identifier | `"Crowe/EDGAR Query Engine 1.0 (brett.vantil@crowe.com)"` |
| `PORT` | ⚪ | Service port (auto-set by Railway) | `8001` |

## 🔒 SEC Compliance

This service is fully compliant with SEC EDGAR API requirements:
- ✅ Proper User-Agent identification
- ✅ Rate limiting respected  
- ✅ Official SEC data sources only
- ✅ No data caching (always fresh)

## 🧪 Test Your Deployment

```bash
# Health check
curl https://your-service.up.railway.app/health

# Find any company
curl "https://your-service.up.railway.app/search/company?q=Tesla"

# Get business description
curl -X POST "https://your-service.up.railway.app/extract/business-description" \
  -H "Content-Type: application/json" \
  -d '{"cik": "0001318605", "form_type": "10-K"}'
```

## 📞 Support

This MCP service enables powerful financial analysis applications by providing:
- 🎯 **Universal access** to any SEC-registered company
- 📊 **Deep content extraction** beyond basic metadata  
- 🔍 **Advanced search** capabilities across all filings
- 🤖 **AI-ready responses** for natural language processing

Perfect for building financial analysis tools, compliance monitoring, and investment research platforms.

---

**Powered by [EdgarTools](https://github.com/dgunning/edgartools) 📈**