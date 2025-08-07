"""
EdgarTools Microservice for Deep SEC Filing Content Extraction
Handles all content-heavy operations that the direct SEC API cannot efficiently provide
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
from edgar import Company, Filing, set_identity
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set identity for SEC compliance
set_identity(os.getenv("SEC_API_USER_AGENT", "Crowe/EDGAR Query Engine 1.0 (brett.vantil@crowe.com)"))

app = FastAPI(title="EdgarTools Content Service", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now - configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add startup event to log service info
@app.on_event("startup")
async def startup_event():
    port = os.getenv("PORT", "8001")
    logger.info(f"🚀 EdgarTools service starting on port {port}")
    logger.info("🔍 Ready to process SEC EDGAR queries")
    
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("💤 EdgarTools service shutting down")

# Request/Response Models
class ExtractionRequest(BaseModel):
    cik: str
    accession_number: Optional[str] = None
    form_type: Optional[str] = "10-K"
    sections: Optional[List[str]] = None

class BusinessDescriptionResponse(BaseModel):
    cik: str
    company_name: str
    description: str
    source: str
    extracted_at: str

class RiskFactorsResponse(BaseModel):
    cik: str
    company_name: str
    risk_factors: List[Dict[str, Any]]
    source: str
    extracted_at: str

class FinancialDataResponse(BaseModel):
    cik: str
    company_name: str
    financial_data: Dict[str, Any]
    source: str
    period: str

class FilingComparisonResponse(BaseModel):
    cik: str
    company_name: str
    changes: Dict[str, Any]
    filing1: str
    filing2: str

class FilingSearchRequest(BaseModel):
    company: Optional[str] = None  # Company name or ticker
    cik: Optional[str] = None
    form_types: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    content_search: Optional[str] = None  # Search within filing contents
    limit: Optional[int] = 10

class FilingSearchResponse(BaseModel):
    query: Dict[str, Any]
    results: List[Dict[str, Any]]
    total_found: int

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "edgartools-content"}

@app.get("/search/company")
async def search_company(q: str):
    """Search for any company by name or ticker"""
    try:
        # Try direct ticker/name lookup with EdgarTools
        company = Company(q)
        return {
            "found": True,
            "cik": company.cik,
            "name": company.name,
            "ticker": getattr(company, 'ticker', getattr(company, 'tickers', 'N/A')),
            "confidence": 1.0
        }
    except Exception as e:
        logger.error(f"Company search failed for '{q}': {str(e)}")
        return {
            "found": False,
            "query": q,
            "error": str(e)
        }

@app.post("/search/filings", response_model=FilingSearchResponse)
async def search_filings(request: FilingSearchRequest):
    """Search filings with flexible criteria including content search"""
    try:
        # Resolve company if provided
        company = None
        if request.company:
            company = Company(request.company)
        elif request.cik:
            company = Company(request.cik)
        
        # Get filings based on criteria
        if company:
            filings = company.get_filings(
                form=request.form_types[0] if request.form_types else None,
                n=request.limit
            )
        else:
            # Search across all companies - EdgarTools may not support this directly
            return FilingSearchResponse(
                query=request.dict(),
                results=[],
                total_found=0
            )
        
        results = []
        for filing in filings:
            # Filter by date if specified
            if request.date_from and filing.filing_date < request.date_from:
                continue
            if request.date_to and filing.filing_date > request.date_to:
                continue
            
            # If content search specified, search within filing
            if request.content_search:
                try:
                    # Get filing text and search
                    text = filing.text()
                    if request.content_search.lower() not in text.lower():
                        continue
                except:
                    continue
            
            results.append({
                "accession_number": filing.accession_number,
                "form": filing.form,
                "filing_date": str(filing.filing_date),
                "company": filing.company.name,
                "cik": filing.cik,
                "url": filing.url
            })
        
        return FilingSearchResponse(
            query=request.dict(),
            results=results,
            total_found=len(results)
        )
        
    except Exception as e:
        logger.error(f"Filing search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract/business-description", response_model=BusinessDescriptionResponse)
async def extract_business_description(request: ExtractionRequest):
    """Extract business description from 10-K Item 1"""
    try:
        logger.info(f"Extracting business description for CIK: {request.cik}")
        
        # Get company and filing
        company = Company(request.cik)
        
        if request.accession_number:
            # Get specific filing
            filing = company.get_filing(accession_number=request.accession_number)
        else:
            # Get latest 10-K
            filings = company.get_filings(form=request.form_type)
            if not filings:
                raise HTTPException(status_code=404, detail=f"No {request.form_type} filings found")
            filing = filings[0]
        
        # Extract business section (EdgarTools API may vary)
        try:
            business_text = filing.business
        except AttributeError:
            # Fallback to extracting from full text
            try:
                full_text = str(filing.text()) if hasattr(filing, 'text') else str(filing)
                business_text = extract_section_from_text(full_text, "item 1", "item 1a")
            except:
                business_text = f"Business information available for {company.name} - content extraction may need refinement"
        
        return BusinessDescriptionResponse(
            cik=request.cik,
            company_name=company.name,
            description=business_text[:5000],  # Limit length
            source=f"{filing.form} - {filing.filing_date}",
            extracted_at=filing.accession_number
        )
        
    except Exception as e:
        logger.error(f"Error extracting business description: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract/risk-factors", response_model=RiskFactorsResponse)
async def extract_risk_factors(request: ExtractionRequest):
    """Extract risk factors from 10-K Item 1A"""
    try:
        logger.info(f"Extracting risk factors for CIK: {request.cik}")
        
        company = Company(request.cik)
        
        if request.accession_number:
            filing = company.get_filing(accession_number=request.accession_number)
        else:
            filings = company.get_filings(form=request.form_type)
            if not filings:
                raise HTTPException(status_code=404, detail=f"No {request.form_type} filings found")
            filing = filings[0]
        
        # Extract risk factors
        risk_text = filing.risk_factors
        if not risk_text:
            full_text = filing.text
            risk_text = extract_section_from_text(full_text, "item 1a", "item 1b")
        
        # Parse risk factors into structured format
        risk_factors = parse_risk_factors(risk_text)
        
        return RiskFactorsResponse(
            cik=request.cik,
            company_name=company.name,
            risk_factors=risk_factors[:20],  # Limit to top 20
            source=f"{filing.form} - {filing.filing_date}",
            extracted_at=filing.accession_number
        )
        
    except Exception as e:
        logger.error(f"Error extracting risk factors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract/financial-statements", response_model=FinancialDataResponse)
async def extract_financial_statements(request: ExtractionRequest):
    """Extract and structure financial statements"""
    try:
        logger.info(f"Extracting financial statements for CIK: {request.cik}")
        
        company = Company(request.cik)
        
        # Get financials
        financials = company.financials
        
        if not financials:
            raise HTTPException(status_code=404, detail="No financial data found")
        
        # Structure the financial data
        financial_data = {
            "income_statement": financials.income_statement.to_dict() if hasattr(financials, 'income_statement') else {},
            "balance_sheet": financials.balance_sheet.to_dict() if hasattr(financials, 'balance_sheet') else {},
            "cash_flow": financials.cash_flow_statement.to_dict() if hasattr(financials, 'cash_flow_statement') else {},
            "key_metrics": extract_key_metrics(financials)
        }
        
        return FinancialDataResponse(
            cik=request.cik,
            company_name=company.name,
            financial_data=financial_data,
            source="XBRL Data",
            period=str(financials.period) if hasattr(financials, 'period') else "Latest"
        )
        
    except Exception as e:
        logger.error(f"Error extracting financial statements: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract/mda", response_model=Dict[str, Any])
async def extract_mda(request: ExtractionRequest):
    """Extract Management Discussion & Analysis"""
    try:
        logger.info(f"Extracting MD&A for CIK: {request.cik}")
        
        company = Company(request.cik)
        
        if request.accession_number:
            filing = company.get_filing(accession_number=request.accession_number)
        else:
            filings = company.get_filings(form=request.form_type)
            if not filings:
                raise HTTPException(status_code=404, detail=f"No {request.form_type} filings found")
            filing = filings[0]
        
        # Extract MD&A section
        mda_text = filing.mda
        if not mda_text:
            full_text = filing.text
            mda_text = extract_section_from_text(full_text, "item 7", "item 7a")
        
        return {
            "cik": request.cik,
            "company_name": company.name,
            "mda": mda_text[:10000],  # Limit length
            "source": f"{filing.form} - {filing.filing_date}",
            "highlights": extract_mda_highlights(mda_text)
        }
        
    except Exception as e:
        logger.error(f"Error extracting MD&A: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare/filings", response_model=FilingComparisonResponse)
async def compare_filings(cik: str, filing1_accession: str, filing2_accession: str):
    """Compare two filings to identify changes"""
    try:
        logger.info(f"Comparing filings for CIK: {cik}")
        
        company = Company(cik)
        filing1 = company.get_filing(accession_number=filing1_accession)
        filing2 = company.get_filing(accession_number=filing2_accession)
        
        # Compare key sections
        changes = {
            "business_changes": compare_text_sections(filing1.business, filing2.business),
            "risk_changes": compare_text_sections(filing1.risk_factors, filing2.risk_factors),
            "financial_highlights": compare_financial_data(filing1, filing2)
        }
        
        return FilingComparisonResponse(
            cik=cik,
            company_name=company.name,
            changes=changes,
            filing1=filing1_accession,
            filing2=filing2_accession
        )
        
    except Exception as e:
        logger.error(f"Error comparing filings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/insider-transactions")
async def search_insider_transactions(cik: str, limit: int = 50):
    """Get recent insider transactions"""
    try:
        logger.info(f"Searching insider transactions for CIK: {cik}")
        
        company = Company(cik)
        # Get Form 4 filings
        form4_filings = company.get_filings(form="4").latest(limit)
        
        transactions = []
        for filing in form4_filings:
            transaction_data = extract_insider_transaction(filing)
            if transaction_data:
                transactions.append(transaction_data)
        
        return {
            "cik": cik,
            "company_name": company.name,
            "transactions": transactions,
            "count": len(transactions)
        }
        
    except Exception as e:
        logger.error(f"Error searching insider transactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def extract_section_from_text(full_text: str, start_marker: str, end_marker: str) -> str:
    """Extract a section from filing text based on markers"""
    import re
    
    # Normalize text and markers
    text_lower = full_text.lower()
    start_pattern = re.compile(f"{start_marker}[.\s\-]*", re.IGNORECASE)
    end_pattern = re.compile(f"{end_marker}[.\s\-]*", re.IGNORECASE)
    
    start_match = start_pattern.search(text_lower)
    if not start_match:
        return ""
    
    start_idx = start_match.end()
    end_match = end_pattern.search(text_lower, start_idx)
    end_idx = end_match.start() if end_match else len(text_lower)
    
    return full_text[start_idx:end_idx].strip()

def parse_risk_factors(risk_text: str) -> List[Dict[str, Any]]:
    """Parse risk factors into structured format"""
    import re
    
    risk_factors = []
    
    # Split by common patterns (bullets, numbers, headers)
    patterns = [
        r'\n\s*[•·\-\*]\s*([^\n]+)',
        r'\n\s*\d+\.\s*([^\n]+)',
        r'\n\s*([A-Z][^.!?]*(?:Risk|Uncertain|Threat|Challenge)[^.!?]*[.!?])'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, risk_text, re.MULTILINE)
        for match in matches[:20]:  # Limit to prevent too many
            if len(match) > 50:  # Skip short matches
                risk_factors.append({
                    "risk": match.strip(),
                    "category": categorize_risk(match),
                    "severity": assess_severity(match)
                })
    
    return risk_factors

def categorize_risk(risk_text: str) -> str:
    """Categorize risk based on keywords"""
    text_lower = risk_text.lower()
    
    categories = {
        "Cybersecurity": ["cyber", "data breach", "security", "hack"],
        "Regulatory": ["regulation", "compliance", "legal", "law"],
        "Market": ["market", "competition", "demand", "customer"],
        "Financial": ["financial", "credit", "liquidity", "debt"],
        "Operational": ["operation", "supply", "manufacturing", "production"],
        "Technology": ["technology", "innovation", "obsolete", "intellectual property"],
        "Environmental": ["climate", "environmental", "sustainability", "carbon"]
    }
    
    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    
    return "General"

def assess_severity(risk_text: str) -> str:
    """Assess risk severity based on language"""
    text_lower = risk_text.lower()
    
    if any(word in text_lower for word in ["material adverse", "significant harm", "substantial loss"]):
        return "High"
    elif any(word in text_lower for word in ["adverse", "negative", "impact"]):
        return "Medium"
    else:
        return "Low"

def extract_key_metrics(financials) -> Dict[str, Any]:
    """Extract key financial metrics"""
    metrics = {}
    
    try:
        if hasattr(financials, 'income_statement'):
            income = financials.income_statement
            metrics['revenue'] = income.get('Revenue', income.get('TotalRevenue', 0))
            metrics['net_income'] = income.get('NetIncome', income.get('NetIncomeLoss', 0))
            metrics['gross_profit'] = income.get('GrossProfit', 0)
        
        if hasattr(financials, 'balance_sheet'):
            balance = financials.balance_sheet
            metrics['total_assets'] = balance.get('TotalAssets', 0)
            metrics['total_liabilities'] = balance.get('TotalLiabilities', 0)
            metrics['shareholders_equity'] = balance.get('ShareholdersEquity', 0)
    except:
        pass
    
    return metrics

def extract_mda_highlights(mda_text: str) -> List[str]:
    """Extract key highlights from MD&A"""
    highlights = []
    
    # Look for sentences with key financial terms
    import re
    sentences = re.split(r'[.!?]+', mda_text)
    
    keywords = ['increased', 'decreased', 'grew', 'declined', 'improved', 'deteriorated',
                'revenue', 'profit', 'margin', 'growth', 'performance']
    
    for sentence in sentences[:100]:  # Check first 100 sentences
        if any(keyword in sentence.lower() for keyword in keywords) and len(sentence) > 50:
            highlights.append(sentence.strip())
            if len(highlights) >= 5:
                break
    
    return highlights

def compare_text_sections(text1: str, text2: str) -> Dict[str, Any]:
    """Compare two text sections for changes"""
    # Simple comparison - in production, use more sophisticated diff algorithms
    return {
        "length_change": len(text2) - len(text1),
        "significant_change": abs(len(text2) - len(text1)) > len(text1) * 0.1
    }

def compare_financial_data(filing1, filing2) -> Dict[str, Any]:
    """Compare financial data between filings"""
    # Placeholder - implement actual financial comparison
    return {
        "revenue_change": "Not implemented",
        "profit_change": "Not implemented"
    }

def extract_insider_transaction(filing) -> Optional[Dict[str, Any]]:
    """Extract insider transaction data from Form 4"""
    try:
        # Placeholder - implement actual Form 4 parsing
        return {
            "filing_date": str(filing.filing_date),
            "transaction_type": "Unknown",
            "shares": 0,
            "price": 0
        }
    except:
        return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)