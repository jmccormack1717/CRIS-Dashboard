from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
from dotenv import load_dotenv

from services.quickbase_client import QuickBaseClient
from services.data_processor import DataProcessor
from services.llm_service import LLMService

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
llm_service = LLMService()

class FilterRequest(BaseModel):
    measure: str  # policies, premium, commission
    period: str  # month, quarter, year
    number_of_periods: Optional[int] = None  # Number of latest periods to show (None = all data, default handled by frontend)

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
            number_of_periods=filter.number_of_periods
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

class InforceByLineRequest(BaseModel):
    metric_type: str  # "policy_count", "premium", "commission", "avg_premium"

@app.post("/api/inforce-by-line")
async def get_inforce_by_line(request: InforceByLineRequest):
    """
    Get inforce metrics grouped by Line.
    
    Metric types:
    - "policy_count": Policy Count (inforce) by Line (Count and Percent)
    - "premium": Premium (inforce) by Line (Count and Percent)
    - "commission": Commission (inforce) by Line (Count and Percent)
    - "avg_premium": Average Premium (inforce) by Line (Bar Chart with numerical Values)
    """
    print("\n" + "=" * 80)
    print("DEBUG: API /api/inforce-by-line endpoint called")
    print(f"  Request: {request.dict()}")
    print("=" * 80)
    
    valid_metric_types = ["policy_count", "premium", "commission", "avg_premium"]
    if request.metric_type not in valid_metric_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid metric_type: {request.metric_type}. Must be one of {valid_metric_types}"
        )
    
    try:
        # Fetch raw data from QuickBase (with inforce fields)
        raw_data = await quickbase_client.fetch_data(include_inforce_fields=True)
        
        print(f"\nDEBUG: Received {len(raw_data)} raw records from QuickBase")
        
        # Process inforce data by Line
        processed_data = data_processor.process_inforce_by_line(
            raw_data=raw_data,
            metric_type=request.metric_type
        )
        
        print(f"\nDEBUG: Returning {len(processed_data)} processed data points")
        print("=" * 80)
        
        return {
            "success": True,
            "data": processed_data,
            "metric_type": request.metric_type
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\nERROR in /api/inforce-by-line:")
        print(f"  {str(e)}")
        print(f"  Traceback:\n{error_trace}")
        print("=" * 80)
        raise HTTPException(status_code=500, detail=str(e))

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
        "date_field_id": data_processor.date_field_id,
        "premium_field_id": data_processor.premium_field_id,
        "commission_field_id": data_processor.commission_field_id,
        "expiration_date_field_id": data_processor.expiration_date_field_id,
        "line_field_id": data_processor.line_field_id,
        "measure_fields": data_processor.measure_fields,
        "policies": "COUNT of records (no field ID)",
        "status_filter": {
            "field_id": quickbase_client.status_field_id,
            "value": quickbase_client.status_value,
            "where_clause": quickbase_client.where_clause
        }
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
    filtered_data = data_processor._filter_by_latest_periods(
        raw_data,
        filter.period,
        filter.number_of_periods
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
            "measure_field_id": data_processor.measure_fields.get(filter.measure) if filter.measure != "policies" else "COUNT",
            "period": filter.period,
            "number_of_periods": filter.number_of_periods,
            "date_field_id": data_processor.date_field_id
        }
    }

class LLMChatRequest(BaseModel):
    question: str
    dashboard_state: Dict[str, Any]
    conversation_history: Optional[List[Dict[str, str]]] = []

@app.post("/api/llm/chat")
async def llm_chat(request: LLMChatRequest):
    """
    Chat with LLM about dashboard data with access to all-time data
    """
    print("\n" + "=" * 80)
    print("DEBUG: API /api/llm/chat endpoint called")
    print(f"  Question: {request.question}")
    print(f"  Dashboard State: {list(request.dashboard_state.keys())}")
    print(f"  Conversation History Length: {len(request.conversation_history)}")
    print("=" * 80)
    
    try:
        # Fetch all raw data to create all-time summary and inforce summary
        print("\nDEBUG: Fetching all raw data for all-time summary and inforce summary...")
        raw_data = await quickbase_client.fetch_data(include_inforce_fields=True)
        
        # Create all-time summary with detailed breakdowns
        all_time_summary = llm_service.create_all_time_summary(
            raw_data=raw_data,
            date_field_id=data_processor.date_field_id,
            premium_field_id=data_processor.premium_field_id,
            commission_field_id=data_processor.commission_field_id,
            data_processor=data_processor
        )
        
        # Create inforce summary with all metric types
        inforce_summary = llm_service.create_inforce_summary(
            raw_data=raw_data,
            data_processor=data_processor
        )
        
        print(f"\nDEBUG: All-time summary created")
        print(f"  Total Policies: {all_time_summary.get('total_policies', 0)}")
        print(f"  Total Premium: ${all_time_summary.get('total_premium', 0):,.2f}")
        print(f"  Total Commission: ${all_time_summary.get('total_commission', 0):,.2f}")
        
        print(f"\nDEBUG: Inforce summary created")
        # Calculate total using same method as dashboard (sum of counts from grouped data)
        policy_count_data = inforce_summary.get("metrics", {}).get("policy_count", [])
        total_inforce_calculated = sum(item.get("count", 0) for item in policy_count_data)
        print(f"  Total Inforce Policies (calculated from grouped data): {total_inforce_calculated}")
        print(f"  Total Inforce Policies (from summary): {inforce_summary.get('total_inforce_policies', 0)}")
        print(f"  Total Premium (Inforce): ${inforce_summary.get('total_premium', 0):,.2f}")
        print(f"  Total Commission (Inforce): ${inforce_summary.get('total_commission', 0):,.2f}")
        
        # Ask LLM with all-time context and inforce context
        response = await llm_service.ask_question(
            question=request.question,
            dashboard_state=request.dashboard_state,
            conversation_history=request.conversation_history,
            all_time_summary=all_time_summary,
            inforce_summary=inforce_summary
        )
        
        print(f"\nDEBUG: LLM Response generated (length: {len(response)} chars)")
        print("=" * 80)
        
        return {
            "success": True,
            "response": response
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\nERROR in /api/llm/chat:")
        print(f"  {str(e)}")
        print(f"  Traceback:\n{error_trace}")
        print("=" * 80)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/llm/status")
async def llm_status():
    """
    Check if LLM service is available
    """
    return {
        "available": llm_service.is_available()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

