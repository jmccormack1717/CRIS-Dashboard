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
        self.expiration_date_field_id = str(os.getenv("QUICKBASE_EXPIRATION_DATE_FIELD", "15"))  # Field 15 - Expiration Date
        self.line_field_id = str(os.getenv("QUICKBASE_LINE_FIELD", "168"))  # Field 168 - Line of Business
        
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
        
        # Default to 10 if not provided or invalid
        if not number_of_periods or number_of_periods <= 0:
            number_of_periods = 10
            print(f"  Number of periods: Using default (10)")
        else:
            print(f"  Number of periods: {number_of_periods}")
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
        
        # Return only the latest N periods (always filter, default is 10)
        if result and len(result) > 0:
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
        """
        Format grouped data for chart visualization
        
        IMPORTANT: No rounding - keeps raw float values to ensure exact match with LLM data.
        Frontend will handle display formatting (toLocaleString/toFixed) for visual presentation only.
        """
        # Sort by period key
        sorted_keys = sorted(grouped_data.keys())
        
        # Include all periods, including future ones
        # (Previously filtered out future periods, but user wants to see all data)
        
        return [
            {
                "period": key,
                "value": grouped_data[key],  # NO ROUNDING - keep raw float for exact match with LLM
                "label": self._format_period_label(key, period)
            }
            for key in sorted_keys
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
    
    def _get_expiration_date_from_record(self, record: Dict[str, Any]) -> Optional[datetime]:
        """Extract Expiration Date from QuickBase record"""
        exp_date_data = record.get(self.expiration_date_field_id, {})
        
        # Handle both dict format {"value": X} and direct value
        if isinstance(exp_date_data, dict):
            exp_date_value = exp_date_data.get("value", "")
        else:
            exp_date_value = exp_date_data
        
        # Handle QuickBase date code (days since epoch)
        if isinstance(exp_date_value, (int, float)):
            try:
                quickbase_epoch = datetime(1970, 1, 1)
                days = int(exp_date_value)
                return quickbase_epoch + timedelta(days=days)
            except (ValueError, TypeError):
                return None
        
        # Convert to string for parsing
        exp_date_str = str(exp_date_value) if exp_date_value else ""
        
        if not exp_date_str or exp_date_str == "None":
            return None
        
        # Try various date formats
        for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"]:
            try:
                return datetime.strptime(exp_date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def filter_inforce_policies(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter policies to only include those that are currently inforce.
        Inforce means: TODAY() is between effective date and expiration date.
        """
        today = datetime.now()
        inforce_policies = []
        
        print(f"\nDEBUG: Filtering for inforce policies")
        print(f"  Today's date: {today.date()}")
        print(f"  Total policies: {len(raw_data)}")
        
        for record in raw_data:
            # Get effective date
            eff_date = self._get_date_from_record(record)
            if not eff_date:
                continue
            
            # Get expiration date
            exp_date = self._get_expiration_date_from_record(record)
            if not exp_date:
                continue
            
            # Check if today is between effective date and expiration date (inclusive)
            # Compare dates (ignoring time)
            eff_date_only = eff_date.date()
            exp_date_only = exp_date.date()
            today_only = today.date()
            
            if eff_date_only <= today_only <= exp_date_only:
                inforce_policies.append(record)
        
        print(f"  Inforce policies: {len(inforce_policies)}")
        return inforce_policies
    
    def get_line_value(self, record: Dict[str, Any]) -> str:
        """Extract Line value from QuickBase record"""
        line_data = record.get(self.line_field_id, {})
        
        # Handle both dict format {"value": X} and direct value
        if isinstance(line_data, dict):
            line_value = line_data.get("value", "")
        else:
            line_value = str(line_data) if line_data else ""
        
        # Return "Unknown" if empty
        return str(line_value).strip() if line_value else "Unknown"
    
    def process_inforce_by_line(
        self,
        raw_data: List[Dict[str, Any]],
        metric_type: str  # "policy_count", "premium", "commission", "avg_premium"
    ) -> List[Dict[str, Any]]:
        """
        Process inforce policies grouped by Line.
        
        Args:
            raw_data: Raw policy records from QuickBase
            metric_type: Type of metric to calculate
                - "policy_count": Count and percent of policies by Line
                - "premium": Premium and percent by Line
                - "commission": Commission and percent by Line
                - "avg_premium": Average premium by Line (for bar chart)
        
        Returns:
            List of dicts with Line, value, count, and percent
        """
        # Filter for inforce policies
        inforce_policies = self.filter_inforce_policies(raw_data)
        
        if not inforce_policies:
            return []
        
        # Group by Line
        line_data = defaultdict(lambda: {"count": 0, "premium": 0.0, "commission": 0.0})
        
        for record in inforce_policies:
            line = self.get_line_value(record)
            premium = self._get_measure_value(record, "premium")
            commission = self._get_measure_value(record, "commission")
            
            line_data[line]["count"] += 1
            line_data[line]["premium"] += premium
            line_data[line]["commission"] += commission
        
        # Calculate totals for percent calculation
        total_count = sum(data["count"] for data in line_data.values())
        total_premium = sum(data["premium"] for data in line_data.values())
        total_commission = sum(data["commission"] for data in line_data.values())
        
        # Build result based on metric type
        result = []
        for line, data in sorted(line_data.items()):
            count = data["count"]
            premium = data["premium"]
            commission = data["commission"]
            avg_premium = premium / count if count > 0 else 0.0
            
            if metric_type == "policy_count":
                percent = (count / total_count * 100) if total_count > 0 else 0.0
                result.append({
                    "line": line,
                    "count": count,
                    "value": count,  # NO ROUNDING - keep raw float
                    "percent": round(percent, 2)  # Percent can be rounded for display
                })
            elif metric_type == "premium":
                percent = (premium / total_premium * 100) if total_premium > 0 else 0.0
                result.append({
                    "line": line,
                    "count": count,
                    "value": premium,  # NO ROUNDING - keep raw float for exact match with LLM
                    "percent": round(percent, 2)  # Percent can be rounded for display
                })
            elif metric_type == "commission":
                percent = (commission / total_commission * 100) if total_commission > 0 else 0.0
                result.append({
                    "line": line,
                    "count": count,
                    "value": commission,  # NO ROUNDING - keep raw float for exact match with LLM
                    "percent": round(percent, 2)  # Percent can be rounded for display
                })
            elif metric_type == "avg_premium":
                result.append({
                    "line": line,
                    "count": count,
                    "value": avg_premium,  # NO ROUNDING - keep raw float for exact match with LLM
                    "label": line  # For chart display
                })
        
        return result

