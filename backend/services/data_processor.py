from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

class DataProcessor:
    def __init__(self):
        self.measure_fields = {
            "policies": 6,  # Field ID for policies
            "premium": 7,   # Field ID for premium
            "commission": 8 # Field ID for commission
        }
    
    def process_data(
        self,
        raw_data: List[Dict[str, Any]],
        measure: str,
        period: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        since_time: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Process raw QuickBase data into visualization format
        """
        if measure not in self.measure_fields:
            raise ValueError(f"Invalid measure: {measure}. Must be one of {list(self.measure_fields.keys())}")
        
        # Parse dates and filter
        filtered_data = self._filter_by_dates(raw_data, start_date, end_date, since_time)
        
        # Group by period
        grouped_data = self._group_by_period(filtered_data, period, measure)
        
        # Format for frontend
        return self._format_for_chart(grouped_data, period)
    
    def _filter_by_dates(
        self,
        data: List[Dict[str, Any]],
        start_date: Optional[str],
        end_date: Optional[str],
        since_time: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Filter data based on date range or since_time"""
        filtered = data
        
        if since_time:
            # Parse since_time (e.g., "2024-01-01" or "30days" or "6months")
            cutoff_date = self._parse_since_time(since_time)
            filtered = [
                item for item in filtered
                if self._get_date_from_record(item) >= cutoff_date
            ]
        
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            filtered = [
                item for item in filtered
                if self._get_date_from_record(item) >= start
            ]
        
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            filtered = [
                item for item in filtered
                if self._get_date_from_record(item) <= end
            ]
        
        return filtered
    
    def _parse_since_time(self, since_time: str) -> datetime:
        """Parse since_time string into datetime"""
        since_time = since_time.lower().strip()
        
        # Try direct date format
        try:
            return datetime.strptime(since_time, "%Y-%m-%d")
        except ValueError:
            pass
        
        # Try relative time formats
        if "day" in since_time:
            days = int(''.join(filter(str.isdigit, since_time)))
            return datetime.now() - timedelta(days=days)
        elif "month" in since_time:
            months = int(''.join(filter(str.isdigit, since_time)))
            return datetime.now() - timedelta(days=months * 30)
        elif "year" in since_time:
            years = int(''.join(filter(str.isdigit, since_time)))
            return datetime.now() - timedelta(days=years * 365)
        
        # Default to 30 days
        return datetime.now() - timedelta(days=30)
    
    def _get_date_from_record(self, record: Dict[str, Any]) -> datetime:
        """Extract date from QuickBase record"""
        date_field_id = "3"  # Adjust based on your schema
        date_str = record.get(date_field_id, {}).get("value", "")
        
        try:
            # Try various date formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
        except:
            pass
        
        # Default to current date if parsing fails
        return datetime.now()
    
    def _get_measure_value(self, record: Dict[str, Any], measure: str) -> float:
        """Extract measure value from record"""
        field_id = str(self.measure_fields[measure])
        value = record.get(field_id, {}).get("value", 0)
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _group_by_period(
        self,
        data: List[Dict[str, Any]],
        period: str,
        measure: str
    ) -> Dict[str, float]:
        """Group data by time period and sum measure values"""
        grouped = defaultdict(float)
        
        for record in data:
            date = self._get_date_from_record(record)
            period_key = self._get_period_key(date, period)
            value = self._get_measure_value(record, measure)
            grouped[period_key] += value
        
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
        
        return [
            {
                "period": key,
                "value": round(grouped_data[key], 2),
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

