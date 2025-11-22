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
            "User-Agent": "PythonQuickbaseClient",
            "Authorization": f"QB-USER-TOKEN {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Field IDs - configurable via environment variables
        # Default: Field 10 = Effective Date, Field 13 = Premium, Field 19 = Commission
        date_field = os.getenv("QUICKBASE_DATE_FIELD", "10")
        premium_field = os.getenv("QUICKBASE_PREMIUM_FIELD", "13")
        commission_field = os.getenv("QUICKBASE_COMMISSION_FIELD", "19")
        status_field = os.getenv("QUICKBASE_STATUS_FIELD", "23")
        status_value = os.getenv("QUICKBASE_STATUS_VALUE", "Bound")
        # New fields for inforce metrics by Line
        expiration_date_field = os.getenv("QUICKBASE_EXPIRATION_DATE_FIELD", "11")
        line_field = os.getenv("QUICKBASE_LINE_FIELD", "12")
        
        # Parse comma-separated field IDs or single values
        def parse_field_id(field_str):
            try:
                return int(field_str)
            except ValueError:
                return int(field_str.split(',')[0].strip())
        
        self.date_field_id = str(parse_field_id(date_field))
        self.premium_field_id = str(parse_field_id(premium_field))
        self.commission_field_id = str(parse_field_id(commission_field))
        self.status_field_id = str(parse_field_id(status_field))
        self.status_value = status_value
        self.expiration_date_field_id = str(parse_field_id(expiration_date_field))
        self.line_field_id = str(parse_field_id(line_field))
        
        # Build select list - always include date, premium, commission
        self.select_fields = [
            parse_field_id(date_field),
            parse_field_id(premium_field),
            parse_field_id(commission_field)
        ]
        
        # Build select list for inforce metrics (includes Line and Expiration Date)
        self.select_fields_inforce = [
            parse_field_id(date_field),
            parse_field_id(expiration_date_field),
            parse_field_id(line_field),
            parse_field_id(premium_field),
            parse_field_id(commission_field)
        ]
        
        # Build where clause
        self.where_clause = f"{{{self.status_field_id}.EX.'{self.status_value}'}}"
        
        # Debug logging
        print("=" * 80)
        print("DEBUG: QuickBase Client Initialized")
        print(f"  Realm: {self.realm}")
        print(f"  API Token (first 20 chars): {self.api_token[:20]}...")
        print(f"  Base URL: {self.base_url}")
        print("=" * 80)
    
    async def fetch_data(self, include_inforce_fields: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch data from QuickBase API
        This is a placeholder - you'll need to adjust based on your QuickBase table structure
        
        Args:
            include_inforce_fields: If True, includes Line and Expiration Date fields for inforce calculations
        """
        print("\n" + "=" * 80)
        print("DEBUG: Starting QuickBase fetch_data()")
        print(f"  Include inforce fields: {include_inforce_fields}")
        print("=" * 80)
        
        async with httpx.AsyncClient() as client:
            try:
                # Query structure for policies data
                table_id = os.getenv("QUICKBASE_TABLE_ID", "your-table-id")
                
                query_url = f"{self.base_url}/records/query"
                
                # Select appropriate fields based on whether we need inforce data
                select_fields = self.select_fields_inforce if include_inforce_fields else self.select_fields
                
                # Query: Each record is a policy
                # Each policy has: Effective Date (field 10), Premium (field 13), Commission (field 19)
                # For inforce: Also includes Expiration Date (field 11), Line (field 12)
                # Policies measure = COUNT of records (no field needed)
                # Where clause filters for 'Bound' policies only
                query_payload = {
                    "from": table_id,
                    "select": select_fields,
                    "where": self.where_clause  # "{23.EX.'Bound'}" - Only Bound policies
                }
                
                print(f"DEBUG: QuickBase Request Details")
                print(f"  URL: {query_url}")
                print(f"  Table ID: {table_id}")
                print(f"  Select Fields: {select_fields} (Date={self.date_field_id}, Premium={self.premium_field_id}, Commission={self.commission_field_id})")
                if include_inforce_fields:
                    print(f"    Also includes: Expiration Date={self.expiration_date_field_id}, Line={self.line_field_id}")
                print(f"  Where Clause: {self.where_clause} (Status={self.status_value})")
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
                    mock_data = self._get_mock_data(include_inforce_fields=include_inforce_fields)
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
                mock_data = self._get_mock_data(include_inforce_fields=include_inforce_fields)
                print(f"  Generated {len(mock_data)} mock records")
                print("=" * 80)
                return mock_data
    
    def _get_mock_data(self, include_inforce_fields: bool = False) -> List[Dict[str, Any]]:
        """
        Mock data for development/testing when QuickBase API is not accessible
        
        Args:
            include_inforce_fields: If True, includes Line and Expiration Date fields
        """
        import random
        from datetime import datetime, timedelta
        
        mock_data = []
        base_date = datetime.now() - timedelta(days=365)
        lines = ["Auto", "Home", "Life", "Health", "Commercial"]  # Sample line values
        
        for i in range(100):
            date = base_date + timedelta(days=i * 3)
            # Calculate expiration date (1 year from effective date)
            exp_date = date + timedelta(days=365)
            
            record = {
                self.date_field_id: {"value": date.strftime("%Y-%m-%d")},  # Effective Date
                self.premium_field_id: {"value": random.randint(10000, 500000)},  # Premium
                self.commission_field_id: {"value": random.randint(1000, 50000)}  # Commission
            }
            
            # Add inforce fields if requested
            if include_inforce_fields:
                record[self.expiration_date_field_id] = {"value": exp_date.strftime("%Y-%m-%d")}  # Expiration Date
                record[self.line_field_id] = {"value": random.choice(lines)}  # Line
            
            mock_data.append(record)
        
        return mock_data

