import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = None
        
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                print(f"LLM Service initialized with model: {self.model}")
            except ImportError:
                print("WARNING: openai package not installed. Install with: pip install openai")
        else:
            print("WARNING: OPENAI_API_KEY not set. LLM features will be disabled.")
    
    def is_available(self) -> bool:
        return self.client is not None
    
    def create_all_time_summary(self, raw_data: List[Dict[str, Any]], date_field_id: str, premium_field_id: str, commission_field_id: str, data_processor) -> Dict[str, Any]:
        """
        Create all-time summary statistics from raw data, including detailed breakdowns
        """
        if not raw_data:
            return {}
        
        all_time = {
            "total_policies": len(raw_data),
            "total_premium": 0.0,
            "total_commission": 0.0,
            "date_range": {"earliest": None, "latest": None},
            "breakdowns": {
                "monthly": {"policies": {}, "premium": {}, "commission": {}},
                "quarterly": {"policies": {}, "premium": {}, "commission": {}},
                "yearly": {"policies": {}, "premium": {}, "commission": {}}
            }
        }
        
        dates = []
        
        # Process all records to get totals and breakdowns
        for record in raw_data:
            # Get date
            date = data_processor._get_date_from_record(record)
            if date:
                dates.append(date)
            
            # Get premium
            premium = data_processor._get_measure_value(record, "premium")
            all_time["total_premium"] += premium
            
            # Get commission
            commission = data_processor._get_measure_value(record, "commission")
            all_time["total_commission"] += commission
            
            # Get policy count (1 per record)
            policy_count = data_processor._get_measure_value(record, "policies")
            
            if date:
                # Add to monthly breakdown
                month_key = date.strftime("%Y-%m")
                all_time["breakdowns"]["monthly"]["policies"][month_key] = all_time["breakdowns"]["monthly"]["policies"].get(month_key, 0) + policy_count
                all_time["breakdowns"]["monthly"]["premium"][month_key] = all_time["breakdowns"]["monthly"]["premium"].get(month_key, 0) + premium
                all_time["breakdowns"]["monthly"]["commission"][month_key] = all_time["breakdowns"]["monthly"]["commission"].get(month_key, 0) + commission
                
                # Add to quarterly breakdown
                quarter = (date.month - 1) // 3 + 1
                quarter_key = f"{date.year}-Q{quarter}"
                all_time["breakdowns"]["quarterly"]["policies"][quarter_key] = all_time["breakdowns"]["quarterly"]["policies"].get(quarter_key, 0) + policy_count
                all_time["breakdowns"]["quarterly"]["premium"][quarter_key] = all_time["breakdowns"]["quarterly"]["premium"].get(quarter_key, 0) + premium
                all_time["breakdowns"]["quarterly"]["commission"][quarter_key] = all_time["breakdowns"]["quarterly"]["commission"].get(quarter_key, 0) + commission
                
                # Add to yearly breakdown
                year_key = str(date.year)
                all_time["breakdowns"]["yearly"]["policies"][year_key] = all_time["breakdowns"]["yearly"]["policies"].get(year_key, 0) + policy_count
                all_time["breakdowns"]["yearly"]["premium"][year_key] = all_time["breakdowns"]["yearly"]["premium"].get(year_key, 0) + premium
                all_time["breakdowns"]["yearly"]["commission"][year_key] = all_time["breakdowns"]["yearly"]["commission"].get(year_key, 0) + commission
        
        if dates:
            all_time["date_range"]["earliest"] = min(dates).strftime("%Y-%m-%d")
            all_time["date_range"]["latest"] = max(dates).strftime("%Y-%m-%d")
        
        return all_time
    
    def create_data_context(self, dashboard_state: Dict[str, Any], all_time_summary: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a context string describing the current dashboard state and all-time data
        """
        context_parts = []
        
        # All-time summary first (if available)
        if all_time_summary:
            context_parts.append("=== ALL-TIME DATA SUMMARY ===")
            context_parts.append(f"Total Policies (All Time): {all_time_summary.get('total_policies', 0):,}")
            context_parts.append(f"Total Premium (All Time): ${all_time_summary.get('total_premium', 0):,.2f}")
            context_parts.append(f"Total Commission (All Time): ${all_time_summary.get('total_commission', 0):,.2f}")
            
            date_range = all_time_summary.get('date_range', {})
            if date_range.get('earliest') and date_range.get('latest'):
                context_parts.append(f"Date Range: {date_range['earliest']} to {date_range['latest']}")
            
            context_parts.append("")
            context_parts.append("=== DETAILED BREAKDOWNS ===")
            context_parts.append("You have access to ALL historical data broken down by Month, Quarter, and Year.")
            context_parts.append("")
            
            # Add quarterly breakdown for policies
            quarterly_policies = all_time_summary.get('breakdowns', {}).get('quarterly', {}).get('policies', {})
            if quarterly_policies:
                context_parts.append("Quarterly Policy Count (All Time):")
                sorted_quarters = sorted(quarterly_policies.items())
                for quarter, count in sorted_quarters:
                    context_parts.append(f"  {quarter}: {int(count):,}")
                context_parts.append("")
            
            # Add yearly breakdown for policies
            yearly_policies = all_time_summary.get('breakdowns', {}).get('yearly', {}).get('policies', {})
            if yearly_policies:
                context_parts.append("Yearly Policy Count (All Time):")
                sorted_years = sorted(yearly_policies.items())
                for year, count in sorted_years:
                    context_parts.append(f"  {year}: {int(count):,}")
                context_parts.append("")
            
            # Add quarterly premium breakdown
            quarterly_premium = all_time_summary.get('breakdowns', {}).get('quarterly', {}).get('premium', {})
            if quarterly_premium:
                context_parts.append("Quarterly Premium (All Time):")
                sorted_quarters = sorted(quarterly_premium.items())
                for quarter, premium in sorted_quarters:
                    context_parts.append(f"  {quarter}: ${premium:,.2f}")
                context_parts.append("")
            
            # Add yearly premium breakdown
            yearly_premium = all_time_summary.get('breakdowns', {}).get('yearly', {}).get('premium', {})
            if yearly_premium:
                context_parts.append("Yearly Premium (All Time):")
                sorted_years = sorted(yearly_premium.items())
                for year, premium in sorted_years:
                    context_parts.append(f"  {year}: ${premium:,.2f}")
                context_parts.append("")
            
            context_parts.append("Note: You also have monthly breakdowns available for detailed analysis.")
            context_parts.append("")
        
        # View type and filters
        view_type = dashboard_state.get("view_type", "time-based")
        context_parts.append("=== CURRENT DASHBOARD VIEW ===")
        context_parts.append(f"View Type: {view_type}")
        
        if view_type == "time-based":
            measure = dashboard_state.get("measure", "policies")
            period = dashboard_state.get("period", "month")
            number_of_periods = dashboard_state.get("number_of_periods", 10)
            
            context_parts.append(f"Measure: {measure.capitalize()}")
            context_parts.append(f"Period: {period.capitalize()}")
            context_parts.append(f"Showing latest {number_of_periods} {period}(s) (filtered view)")
            
            # Data summary
            data = dashboard_state.get("data", [])
            if data:
                values = [item.get("value", 0) for item in data]
                total = sum(values)
                avg = total / len(values) if values else 0
                context_parts.append(f"\nCurrent View Summary:")
                context_parts.append(f"- Data points: {len(data)}")
                context_parts.append(f"- Total {measure} in view: {total:,.2f}")
                context_parts.append(f"- Average per period: {avg:,.2f}")
                
                # Show sample data
                context_parts.append(f"\nSample periods in view (latest 5):")
                for item in data[-5:]:
                    label = item.get("label", "")
                    value = item.get("value", 0)
                    context_parts.append(f"  {label}: {value:,.2f}")
        
        elif view_type == "inforce-by-line":
            metric_type = dashboard_state.get("metric_type", "policy_count")
            context_parts.append(f"Metric Type: {metric_type}")
            
            data = dashboard_state.get("data", [])
            if data:
                total_value = sum(item.get("value", 0) for item in data)
                total_count = sum(item.get("count", 0) for item in data)
                
                context_parts.append(f"\nCurrent View Summary:")
                context_parts.append(f"- Total Lines: {len(data)}")
                context_parts.append(f"- Total Value: {total_value:,.2f}")
                context_parts.append(f"- Total Policies (inforce): {total_count}")
                
                # Show top lines
                sorted_data = sorted(data, key=lambda x: x.get("value", 0), reverse=True)
                context_parts.append(f"\nTop Lines (by value):")
                for item in sorted_data[:5]:
                    line = item.get("line", "Unknown")
                    value = item.get("value", 0)
                    percent = item.get("percent", 0)
                    context_parts.append(f"  {line}: {value:,.2f} ({percent}%)")
        
        return "\n".join(context_parts)
    
    async def ask_question(
        self,
        question: str,
        dashboard_state: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None,
        all_time_summary: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Ask the LLM a question with context about the dashboard data
        """
        if not self.is_available():
            return "LLM service is not configured. Please set OPENAI_API_KEY environment variable."
        
        if conversation_history is None:
            conversation_history = []
        
        # Create context about current dashboard state and all-time data
        data_context = self.create_data_context(dashboard_state, all_time_summary)
        
        # System prompt
        system_prompt = """You are a helpful assistant for an insurance dashboard. 
You help users understand their insurance data including policies, premiums, commissions, and inforce metrics.

IMPORTANT: You have access to ALL historical data with detailed breakdowns, not just what's currently displayed in the dashboard.
- You have quarterly, yearly, and monthly breakdowns for policies, premium, and commission
- You can answer questions about any time period (all-time, specific years, quarters, months, etc.)
- You can analyze trends, patterns, and comparisons across any time period
- When asked about quarterly performance, use the quarterly breakdown data provided
- When asked about yearly trends, use the yearly breakdown data provided
- You can compare periods, identify best/worst performing quarters, years, etc.
- Be specific about whether your answer refers to the current filtered view or all-time data

Be concise, accurate, and helpful. Format numbers nicely (use commas, dollar signs where appropriate)."""
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add context message
        messages.append({
            "role": "system",
            "content": f"Dashboard Data Context:\n{data_context}"
        })
        
        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            messages.append(msg)
        
        # Add current question
        messages.append({
            "role": "user",
            "content": question
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return f"Error getting response from LLM: {str(e)}"

