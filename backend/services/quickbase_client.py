import httpx
import os
import json
from typing import Dict, List, Any
from datetime import datetime

class QuickBaseClient:
    def __init__(self):
        self.api_token = os.getenv("QUICKBASE_API_TOKEN", "bykzhu_bmc9_0_ba7azbmc6yyhx8bn868vh6dgm4h")
        self.base_url = "https://api.quickbase.com/v1"
        self.realm = os.getenv("QUICKBASE_REALM", "your-realm.quickbase.com")
        self.headers = {
            "QB-Realm-Hostname": self.realm,
            "Authorization": f"QB-USER-TOKEN {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Debug logging
        print("=" * 80)
        print("DEBUG: QuickBase Client Initialized")
        print(f"  Realm: {self.realm}")
        print(f"  API Token (first 20 chars): {self.api_token[:20]}...")
        print(f"  Base URL: {self.base_url}")
        print("=" * 80)
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from QuickBase API
        This is a placeholder - you'll need to adjust based on your QuickBase table structure
        """
        print("\n" + "=" * 80)
        print("DEBUG: Starting QuickBase fetch_data()")
        print("=" * 80)
        
        async with httpx.AsyncClient() as client:
            try:
                # Example query - adjust table ID and fields based on your QuickBase setup
                table_id = os.getenv("QUICKBASE_TABLE_ID", "your-table-id")
                
                query_url = f"{self.base_url}/records/query"
                
                # Basic query structure - modify based on your table schema
                query_payload = {
                    "from": table_id,
                    "select": [3, 6, 7, 8],  # Field IDs - adjust to match your schema
                    # "where": "{}"  # Add filters if needed
                }
                
                print(f"DEBUG: QuickBase Request Details")
                print(f"  URL: {query_url}")
                print(f"  Table ID: {table_id}")
                print(f"  Field IDs: [3, 6, 7, 8]")
                print(f"  Headers: {json.dumps({k: v if k != 'Authorization' else 'QB-USER-TOKEN ***' for k, v in self.headers.items()}, indent=2)}")
                print(f"  Payload: {json.dumps(query_payload, indent=2)}")
                
                response = await client.post(
                    query_url,
                    headers=self.headers,
                    json=query_payload,
                    timeout=30.0
                )
                
                print(f"\nDEBUG: QuickBase Response")
                print(f"  Status Code: {response.status_code}")
                print(f"  Response Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  Full Response: {json.dumps(data, indent=2)[:2000]}...")  # First 2000 chars
                    
                    records = data.get("data", [])
                    print(f"\nDEBUG: Extracted Records")
                    print(f"  Number of records: {len(records)}")
                    
                    if records:
                        print(f"  First record structure:")
                        print(f"    {json.dumps(records[0], indent=4)}")
                        print(f"\n  All field IDs in first record: {list(records[0].keys())}")
                        
                        # Show all fields from first record
                        print(f"\n  Field breakdown for first record:")
                        for field_id, field_data in records[0].items():
                            print(f"    Field ID '{field_id}': {field_data}")
                    
                    print("\n" + "=" * 80)
                    return records
                else:
                    # Fallback to mock data for development
                    print(f"\nERROR: QuickBase API Error")
                    print(f"  Status Code: {response.status_code}")
                    print(f"  Response Text: {response.text}")
                    print("\nFalling back to mock data...")
                    mock_data = self._get_mock_data()
                    print(f"  Generated {len(mock_data)} mock records")
                    print("=" * 80)
                    return mock_data
            
            except Exception as e:
                print(f"\nEXCEPTION: Error fetching QuickBase data")
                print(f"  Exception Type: {type(e).__name__}")
                print(f"  Exception Message: {str(e)}")
                import traceback
                print(f"  Traceback:\n{traceback.format_exc()}")
                print("\nFalling back to mock data...")
                mock_data = self._get_mock_data()
                print(f"  Generated {len(mock_data)} mock records")
                print("=" * 80)
                return mock_data
    
    def _get_mock_data(self) -> List[Dict[str, Any]]:
        """
        Mock data for development/testing when QuickBase API is not accessible
        """
        import random
        from datetime import datetime, timedelta
        
        mock_data = []
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(100):
            date = base_date + timedelta(days=i * 3)
            mock_data.append({
                "3": {"value": date.strftime("%Y-%m-%d")},  # Date field
                "6": {"value": random.randint(1, 50)},  # Policies count
                "7": {"value": random.randint(10000, 500000)},  # Premium amount
                "8": {"value": random.randint(1000, 50000)}  # Commission amount
            })
        
        return mock_data

