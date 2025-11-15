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
    print("\n" + "=" * 80)
    print("DEBUG: API /api/data endpoint called")
    print(f"  Request: {filter.dict()}")
    print("=" * 80)
    
    try:
        # Fetch raw data from QuickBase
        raw_data = await quickbase_client.fetch_data()
        
        print(f"\nDEBUG: Received {len(raw_data)} raw records from QuickBase")
        
        # Process and filter data
        processed_data = data_processor.process_data(
            raw_data=raw_data,
            measure=filter.measure,
            period=filter.period,
            start_date=filter.start_date,
            end_date=filter.end_date,
            since_time=filter.since_time
        )
        
        print(f"\nDEBUG: Returning {len(processed_data)} processed data points")
        print("=" * 80)
        
        return {
            "success": True,
            "data": processed_data,
            "measure": filter.measure,
            "period": filter.period
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\nERROR in /api/data:")
        print(f"  {str(e)}")
        print(f"  Traceback:\n{error_trace}")
        print("=" * 80)
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

@app.get("/api/debug/config")
async def get_debug_config():
    """Get debug configuration information"""
    import os
    return {
        "quickbase_realm": os.getenv("QUICKBASE_REALM", "NOT SET"),
        "quickbase_table_id": os.getenv("QUICKBASE_TABLE_ID", "NOT SET"),
        "quickbase_api_token_set": bool(os.getenv("QUICKBASE_API_TOKEN")),
        "quickbase_api_token_preview": os.getenv("QUICKBASE_API_TOKEN", "")[:20] + "..." if os.getenv("QUICKBASE_API_TOKEN") else "NOT SET",
        "frontend_url": os.getenv("FRONTEND_URL", "NOT SET"),
        "measure_fields": data_processor.measure_fields,
        "date_field_id": "3"
    }

@app.get("/api/debug/raw")
async def get_debug_raw():
    """Get raw QuickBase data for debugging"""
    raw_data = await quickbase_client.fetch_data()
    return {
        "record_count": len(raw_data),
        "records": raw_data[:10] if len(raw_data) > 10 else raw_data,  # First 10 records
        "all_field_ids": list(set([field_id for record in raw_data for field_id in record.keys()])) if raw_data else [],
        "sample_record_structure": raw_data[0] if raw_data else None
    }

@app.post("/api/debug/process")
async def debug_process(filter: FilterRequest):
    """Debug endpoint to see data processing step by step"""
    raw_data = await quickbase_client.fetch_data()
    
    # Get raw data info
    raw_info = {
        "count": len(raw_data),
        "sample_record": raw_data[0] if raw_data else None,
        "all_field_ids": list(set([field_id for record in raw_data for field_id in record.keys()])) if raw_data else []
    }
    
    # Process step by step
    filtered_data = data_processor._filter_by_dates(
        raw_data,
        filter.start_date,
        filter.end_date,
        filter.since_time
    )
    
    # Show measure values for first few records
    measure_samples = []
    for i, record in enumerate(filtered_data[:5]):
        date = data_processor._get_date_from_record(record)
        value = data_processor._get_measure_value(record, filter.measure)
        from datetime import datetime
        # Generate period key manually for debugging
        if filter.period == "month":
            period_key = date.strftime("%Y-%m")
        elif filter.period == "quarter":
            quarter = (date.month - 1) // 3 + 1
            period_key = f"{date.year}-Q{quarter}"
        elif filter.period == "year":
            period_key = str(date.year)
        else:
            period_key = date.strftime("%Y-%m-%d")
        
        measure_samples.append({
            "record_index": i,
            "date": date.isoformat(),
            "measure_value": value,
            "period_key": period_key,
            "full_record": record
        })
    
    grouped_data = data_processor._group_by_period(filtered_data, filter.period, filter.measure)
    final_data = data_processor._format_for_chart(grouped_data, filter.period)
    
    return {
        "raw_data_info": raw_info,
        "filtered_count": len(filtered_data),
        "measure_samples": measure_samples,
        "grouped_data": grouped_data,
        "final_data": final_data,
        "configuration": {
            "measure": filter.measure,
            "measure_field_id": data_processor.measure_fields.get(filter.measure),
            "period": filter.period,
            "date_field_id": "3"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

