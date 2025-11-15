from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
from dotenv import load_dotenv

from services.quickbase_client import QuickBaseClient
from services.data_processor import DataProcessor

load_dotenv()

app = FastAPI(title="CRIS Dashboard API")

# CORS middleware for React frontend
# Get frontend URL from environment variable, with fallback to localhost for development
frontend_urls = [
    "http://localhost:3000",
    "http://localhost:5173",
]
if os.getenv("FRONTEND_URL"):
    frontend_urls.append(os.getenv("FRONTEND_URL"))
    # Also add with https if not already present
    if not os.getenv("FRONTEND_URL").startswith("https"):
        frontend_urls.append(os.getenv("FRONTEND_URL").replace("http://", "https://"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_urls,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
quickbase_client = QuickBaseClient()
data_processor = DataProcessor()

class FilterRequest(BaseModel):
    measure: str  # policies, premium, commission
    period: str  # month, quarter, year
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    since_time: Optional[str] = None  # Period since time

@app.get("/")
async def root():
    return {"message": "CRIS Dashboard API"}

@app.post("/api/data")
async def get_visualization_data(filter: FilterRequest):
    """
    Get filtered visualization data based on measure, period, and time filters
    """
    try:
        # Fetch raw data from QuickBase
        raw_data = await quickbase_client.fetch_data()
        
        # Process and filter data
        processed_data = data_processor.process_data(
            raw_data=raw_data,
            measure=filter.measure,
            period=filter.period,
            start_date=filter.start_date,
            end_date=filter.end_date,
            since_time=filter.since_time
        )
        
        return {
            "success": True,
            "data": processed_data,
            "measure": filter.measure,
            "period": filter.period
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/filters/measures")
async def get_available_measures():
    """Get list of available measures"""
    return {
        "measures": ["policies", "premium", "commission"]
    }

@app.get("/api/filters/periods")
async def get_available_periods():
    """Get list of available periods"""
    return {
        "periods": ["month", "quarter", "year"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

