from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json

class DataProcessor:
    def __init__(self):
        import os
        
        # Field IDs - match QuickBase client configuration
        # Policies is COUNT of records (not a field)
        # Premium = Field 13, Commission = Field 19
        self.date_field_id = os.getenv("QUICKBASE_DATE_FIELD", "10")
        self.premium_field_id = str(os.getenv("QUICKBASE_PREMIUM_FIELD", "13"))
        self.commission_field_id = str(os.getenv("QUICKBASE_COMMISSION_FIELD", "19"))
        
        # Measure fields mapping
        # Policies doesn't have a field ID - it's a count of records
        self.measure_fields = {
            "premium": self.premium_field_id,
            "commission": self.commission_field_id
        }
        
        print("\n" + "=" * 80)
        print("DEBUG: DataProcessor Initialized")
        print(f"  Each record = One Policy")
        print(f"  Date Field ID: {self.date_field_id} (Effective Date)")
        print(f"  Premium Field ID: {self.premium_field_id} (Premium value)")
        print(f"  Commission Field ID: {self.commission_field_id} (Commission value)")
        print(f"  Policies Measure: COUNT of records per period (no field ID needed)")
        print("=" * 80)
    
    def process_data(
        self,
        raw_data: List[Dict[str, Any]],
        measure: str,
        period: str,
        number_of_periods: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Process raw QuickBase data into visualization format
        
        number_of_periods: Number of latest periods to show
        - If period="month" and number_of_periods=6, shows latest 6 months
        - If period="quarter" and number_of_periods=4, shows latest 4 quarters
        - If period="year" and number_of_periods=5, shows latest 5 years
        """
        print("\n" + "=" * 80)
        print("DEBUG: DataProcessor.process_data()")
        print(f"  Input: {len(raw_data)} raw records (policies)")
        print(f"  Measure: {measure}")
        if measure == "policies":
            print(f"    → COUNT of records per period")
        else:
            print(f"    → SUM of field {self.measure_fields.get(measure, 'UNKNOWN')} per period")
        print(f"  Period: {period}")
        print(f"  Number of periods: {number_of_periods if number_of_periods else 'All'}")
        print("=" * 80)
        
        valid_measures = ["policies", "premium", "commission"]
        if measure not in valid_measures:
            raise ValueError(f"Invalid measure: {measure}. Must be one of {valid_measures}")
        
        # Group by period first (don't filter by date yet)
        grouped_data = self._group_by_period(raw_data, period, measure)
        print(f"  After grouping: {len(grouped_data)} groups")
        print(f"  Grouped data: {json.dumps(grouped_data, indent=2)}")
        
        # Format for frontend
        result = self._format_for_chart(grouped_data, period)
        
        # If number_of_periods specified, return only the latest N periods
        # This ensures we get the actual latest N periods that have data
        if number_of_periods and number_of_periods > 0:
            # Get the latest N periods from the sorted result
            result = result[-number_of_periods:]
            print(f"  Filtered to latest {number_of_periods} periods: {len(result)} data points")
            if result:
                print(f"  Period range: {result[0]['label']} to {result[-1]['label']}")
        
        print(f"  Final result: {len(result)} data points")
        if result:
            print(f"  Sample result: {json.dumps(result[:3], indent=2)}")
        print("=" * 80)
        
        return result
    
    def _filter_by_latest_periods(
        self,
        data: List[Dict[str, Any]],
        period: str,
        number_of_periods: Optional[int]
    ) -> List[Dict[str, Any]]:
        """
        Filter data to show only the latest N periods
        
        NOTE: This method is kept for backwards compatibility but is no longer used.
        Filtering now happens after grouping to ensure we get actual latest N periods.
        """
        # This method is deprecated - filtering happens after grouping now
        return data
    
    def _get_date_from_record(self, record: Dict[str, Any]) -> datetime:
        """Extract Effective Date from QuickBase record"""
        date_field_id = self.date_field_id
        
        # Debug: Show what fields are available
        available_fields = list(record.keys())
        if date_field_id not in available_fields:
            print(f"  WARNING: Date field ID '{date_field_id}' not found in record. Available fields: {available_fields}")
        
        date_field_data = record.get(date_field_id, {})
        
        # Handle both dict format {"value": X} and direct value
        if isinstance(date_field_data, dict):
            date_value = date_field_data.get("value", "")
        else:
            date_value = date_field_data
        
        # Convert to string for parsing
        if isinstance(date_value, (int, float)):
            # QuickBase date code (days since epoch) - convert to date
            # QuickBase epoch is January 1, 1970
            try:
                # Convert days since 1970-01-01 to datetime
                quickbase_epoch = datetime(1970, 1, 1)
                days = int(date_value)
                parsed_date = quickbase_epoch + timedelta(days=days)
                print(f"    DEBUG: Extracted date from field '{date_field_id}'")
                print(f"      QuickBase date code: {date_value} days")
                print(f"      Converted to date: {parsed_date}")
                return parsed_date
            except (ValueError, TypeError) as e:
                print(f"      ERROR converting QuickBase date code: {e}")
                return datetime.now()
        
        date_str = str(date_value) if date_value else ""
        
        print(f"    DEBUG: Extracting date from field '{date_field_id}'")
        print(f"      Field data: {date_field_data}")
        print(f"      Date string: '{date_str}'")
        
        if not date_str or date_str == "None":
            print(f"      WARNING: Empty date string, using current date")
            return datetime.now()
        
        try:
            # Try various date formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"]:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    print(f"      Successfully parsed date: {parsed_date} (format: {fmt})")
                    return parsed_date
                except ValueError:
                    continue
            
            print(f"      WARNING: Could not parse date '{date_str}', using current date")
        except Exception as e:
            print(f"      ERROR parsing date: {e}, using current date")
        
        # Default to current date if parsing fails
        return datetime.now()
    
    def _get_measure_value(self, record: Dict[str, Any], measure: str) -> float:
        """
        Extract measure value from record
        
        Each record is a policy with:
        - Effective Date (field 10)
        - Premium value (field 13)
        - Commission value (field 19)
        
        For measures:
        - Policies: COUNT of records (return 1.0 per record, will be summed)
        - Premium: Get value from field 13
        - Commission: Get value from field 19
        """
        # Policies is COUNT of records - return 1.0 for each record
        # When summed in _group_by_period, this becomes the count
        if measure == "policies":
            return 1.0
        
        # For premium and commission, get from respective field
        field_id = str(self.measure_fields[measure])
        
        print(f"    DEBUG: Extracting measure '{measure}' from field ID '{field_id}'")
        
        # Check if field exists
        if field_id not in record:
            available_fields = list(record.keys())
            print(f"      ERROR: Field ID '{field_id}' not found in record!")
            print(f"      Available field IDs: {available_fields}")
            print(f"      Record structure: {json.dumps(record, indent=4)}")
            return 0.0
        
        field_data = record.get(field_id, {})
        print(f"      Field data: {field_data}")
        
        # Handle both dict format {"value": X} and direct value
        if isinstance(field_data, dict):
            value = field_data.get("value", 0)
        else:
            value = field_data
        
        print(f"      Raw value: {value} (type: {type(value).__name__})")
        
        try:
            float_value = float(value)
            print(f"      Converted to float: {float_value}")
            return float_value
        except (ValueError, TypeError) as e:
            print(f"      ERROR converting to float: {e}, returning 0.0")
            return 0.0
    
    def _group_by_period(
        self,
        data: List[Dict[str, Any]],
        period: str,
        measure: str
    ) -> Dict[str, float]:
        """
        Group data by time period and sum measure values
        
        Each record is a policy. For each period:
        - Policies: COUNT (sum of 1.0 per record)
        - Premium: SUM of premium values
        - Commission: SUM of commission values
        """
        print(f"\n  DEBUG: Grouping {len(data)} records (policies) by {period}")
        if measure == "policies":
            print(f"    Measure: Policies (COUNT of records per period)")
        else:
            print(f"    Measure: {measure} (SUM of values per period)")
        
        grouped = defaultdict(float)
        
        for idx, record in enumerate(data):
            print(f"\n  Processing record {idx + 1}/{len(data)}:")
            date = self._get_date_from_record(record)
            period_key = self._get_period_key(date, period)
            value = self._get_measure_value(record, measure)
            print(f"    Period key: {period_key}")
            print(f"    Value: {value}")
            grouped[period_key] += value
            print(f"    Running total for {period_key}: {grouped[period_key]}")
        
        return dict(grouped)
    
    def _get_period_key(self, date: datetime, period: str) -> str:
        """Generate period key based on period type"""
        if period == "month":
            return date.strftime("%Y-%m")
        elif period == "quarter":
            quarter = (date.month - 1) // 3 + 1
            return f"{date.year}-Q{quarter}"
        elif period == "year":
            return str(date.year)
        else:
            return date.strftime("%Y-%m-%d")
    
    def _format_for_chart(self, grouped_data: Dict[str, float], period: str) -> List[Dict[str, Any]]:
        """Format grouped data for chart visualization"""
        # Sort by period key
        sorted_keys = sorted(grouped_data.keys())
        
        # Filter out periods with zero values (optional - can remove if you want to show zeros)
        # Also filter out future periods beyond current date to avoid showing only future dates
        now = datetime.now()
        filtered_keys = []
        
        for key in sorted_keys:
            # Skip if value is 0 (optional - comment out if you want to show zeros)
            # if grouped_data[key] == 0:
            #     continue
            
            # For month periods, check if the period is in the future
            if period == "month":
                try:
                    period_date = datetime.strptime(key, "%Y-%m")
                    # Only include periods up to current month
                    if period_date.year > now.year or (period_date.year == now.year and period_date.month > now.month):
                        print(f"  Skipping future period: {key}")
                        continue
                except:
                    pass
            elif period == "year":
                try:
                    period_year = int(key)
                    # Only include years up to current year
                    if period_year > now.year:
                        print(f"  Skipping future year: {key}")
                        continue
                except:
                    pass
            
            filtered_keys.append(key)
        
        return [
            {
                "period": key,
                "value": round(grouped_data[key], 2),
                "label": self._format_period_label(key, period)
            }
            for key in filtered_keys
        ]
    
    def _format_period_label(self, period_key: str, period: str) -> str:
        """Format period key into human-readable label"""
        if period == "month":
            try:
                date = datetime.strptime(period_key, "%Y-%m")
                return date.strftime("%b %Y")
            except:
                return period_key
        elif period == "quarter":
            return period_key.replace("-", " ")
        elif period == "year":
            return period_key
        return period_key

