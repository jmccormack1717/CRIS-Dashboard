import httpx
import os
from typing import Dict, List, Any
from datetime import datetime

class QuickBaseClient:
    def __init__(self):
        self.api_token = os.getenv("QUICKBASE_API_TOKEN", "bykzhu_bmc9_0_ba7azbmc6yyhx8bn868vh6dgm4h")
        self.base_url = "https://api.quickbase.com/v1"
        self.headers = {
            "QB-Realm-Hostname": os.getenv("QUICKBASE_REALM", "your-realm.quickbase.com"),
            "Authorization": f"QB-USER-TOKEN {self.api_token}",
            "Content-Type": "application/json"
        }
    
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from QuickBase API
        This is a placeholder - you'll need to adjust based on your QuickBase table structure
        """
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
                
                response = await client.post(
                    query_url,
                    headers=self.headers,
                    json=query_payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
                else:
                    # Fallback to mock data for development
                    print(f"QuickBase API Error: {response.status_code} - {response.text}")
                    return self._get_mock_data()
            
            except Exception as e:
                print(f"Error fetching QuickBase data: {str(e)}")
                # Return mock data for development/testing
                return self._get_mock_data()
    
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

