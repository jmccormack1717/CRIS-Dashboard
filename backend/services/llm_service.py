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
            
            # Add quarterly commission breakdown
            quarterly_commission = all_time_summary.get('breakdowns', {}).get('quarterly', {}).get('commission', {})
            if quarterly_commission:
                context_parts.append("Quarterly Commission (All Time):")
                sorted_quarters = sorted(quarterly_commission.items())
                for quarter, commission in sorted_quarters:
                    context_parts.append(f"  {quarter}: ${commission:,.2f}")
                context_parts.append("")
            
            # Add yearly commission breakdown
            yearly_commission = all_time_summary.get('breakdowns', {}).get('yearly', {}).get('commission', {})
            if yearly_commission:
                context_parts.append("Yearly Commission (All Time):")
                sorted_years = sorted(yearly_commission.items())
                for year, commission in sorted_years:
                    context_parts.append(f"  {year}: ${commission:,.2f}")
                context_parts.append("")
            
            # Add structured JSON data for easier parsing and analysis
            context_parts.append("=== STRUCTURED DATA FOR ANALYSIS (JSON FORMAT) ===")
            context_parts.append("Use this structured data for calculations, comparisons, and deep analysis:")
            structured_data = {
                "quarterly": {
                    "policies": quarterly_policies,
                    "premium": quarterly_premium,
                    "commission": quarterly_commission
                },
                "yearly": {
                    "policies": yearly_policies,
                    "premium": yearly_premium,
                    "commission": yearly_commission
                }
            }
            context_parts.append(json.dumps(structured_data, indent=2))
            context_parts.append("")
            
            # Add pre-calculated analytical insights
            insights = self.create_analytical_insights(all_time_summary)
            if insights and insights.strip():
                context_parts.append("=== PRE-CALCULATED ANALYTICAL INSIGHTS ===")
                context_parts.append("These insights are pre-calculated to help with analysis:")
                context_parts.append(insights)
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
    
    def create_analytical_insights(self, all_time_summary: Dict[str, Any]) -> str:
        """
        Create pre-calculated analytical insights for the LLM
        """
        insights = []
        breakdowns = all_time_summary.get('breakdowns', {})
        
        # Quarterly insights
        quarterly_commission = breakdowns.get('quarterly', {}).get('commission', {})
        quarterly_premium = breakdowns.get('quarterly', {}).get('premium', {})
        quarterly_policies = breakdowns.get('quarterly', {}).get('policies', {})
        
        if quarterly_commission:
            sorted_comm = sorted(quarterly_commission.items(), key=lambda x: x[1], reverse=True)
            if sorted_comm:
                best_q_comm = sorted_comm[0]
                worst_q_comm = sorted_comm[-1]
                insights.append(f"Best Commission Quarter: {best_q_comm[0]} (${best_q_comm[1]:,.2f})")
                insights.append(f"Worst Commission Quarter: {worst_q_comm[0]} (${worst_q_comm[1]:,.2f})")
        
        if quarterly_premium:
            sorted_prem = sorted(quarterly_premium.items(), key=lambda x: x[1], reverse=True)
            if sorted_prem:
                best_q_prem = sorted_prem[0]
                worst_q_prem = sorted_prem[-1]
                insights.append(f"Best Premium Quarter: {best_q_prem[0]} (${best_q_prem[1]:,.2f})")
                insights.append(f"Worst Premium Quarter: {worst_q_prem[0]} (${worst_q_prem[1]:,.2f})")
        
        if quarterly_policies:
            sorted_pol = sorted(quarterly_policies.items(), key=lambda x: x[1], reverse=True)
            if sorted_pol:
                best_q_pol = sorted_pol[0]
                worst_q_pol = sorted_pol[-1]
                insights.append(f"Best Policy Quarter: {best_q_pol[0]} ({int(best_q_pol[1]):,} policies)")
                insights.append(f"Worst Policy Quarter: {worst_q_pol[0]} ({int(worst_q_pol[1]):,} policies)")
        
        # Yearly insights
        yearly_commission = breakdowns.get('yearly', {}).get('commission', {})
        yearly_premium = breakdowns.get('yearly', {}).get('premium', {})
        yearly_policies = breakdowns.get('yearly', {}).get('policies', {})
        
        if yearly_commission:
            sorted_comm = sorted(yearly_commission.items(), key=lambda x: x[1], reverse=True)
            if sorted_comm:
                best_y_comm = sorted_comm[0]
                worst_y_comm = sorted_comm[-1]
                insights.append(f"Best Commission Year: {best_y_comm[0]} (${best_y_comm[1]:,.2f})")
                insights.append(f"Worst Commission Year: {worst_y_comm[0]} (${worst_y_comm[1]:,.2f})")
        
        if yearly_premium:
            sorted_prem = sorted(yearly_premium.items(), key=lambda x: x[1], reverse=True)
            if sorted_prem:
                best_y_prem = sorted_prem[0]
                worst_y_prem = sorted_prem[-1]
                insights.append(f"Best Premium Year: {best_y_prem[0]} (${best_y_prem[1]:,.2f})")
                insights.append(f"Worst Premium Year: {worst_y_prem[0]} (${worst_y_prem[1]:,.2f})")
        
        if yearly_policies:
            sorted_pol = sorted(yearly_policies.items(), key=lambda x: x[1], reverse=True)
            if sorted_pol:
                best_y_pol = sorted_pol[0]
                worst_y_pol = sorted_pol[-1]
                insights.append(f"Best Policy Year: {best_y_pol[0]} ({int(best_y_pol[1]):,} policies)")
                insights.append(f"Worst Policy Year: {worst_y_pol[0]} ({int(worst_y_pol[1]):,} policies)")
        
        # Calculate growth rates for yearly data
        if yearly_commission and len(yearly_commission) > 1:
            sorted_years = sorted([int(y) for y in yearly_commission.keys()])
            if len(sorted_years) >= 2:
                recent_years = sorted_years[-3:]  # Last 3 years
                for i in range(1, len(recent_years)):
                    current_year = str(recent_years[i])
                    prev_year = str(recent_years[i-1])
                    if current_year in yearly_commission and prev_year in yearly_commission:
                        current_val = yearly_commission[current_year]
                        prev_val = yearly_commission[prev_year]
                        if prev_val > 0:
                            growth_rate = ((current_val - prev_val) / prev_val) * 100
                            insights.append(f"Commission Growth {prev_year}→{current_year}: {growth_rate:+.1f}%")
        
        # Top 3 quarters/years for each measure
        if quarterly_commission and len(quarterly_commission) >= 3:
            sorted_comm = sorted(quarterly_commission.items(), key=lambda x: x[1], reverse=True)
            top3 = sorted_comm[:3]
            insights.append("Top 3 Commission Quarters:")
            for idx, (q, val) in enumerate(top3, 1):
                insights.append(f"  {idx}. {q}: ${val:,.2f}")
        
        if yearly_commission and len(yearly_commission) >= 3:
            sorted_comm = sorted(yearly_commission.items(), key=lambda x: x[1], reverse=True)
            top3 = sorted_comm[:3]
            insights.append("Top 3 Commission Years:")
            for idx, (y, val) in enumerate(top3, 1):
                insights.append(f"  {idx}. {y}: ${val:,.2f}")
        
        # Seasonal pattern analysis (compare Q1, Q2, Q3, Q4 averages across years)
        if quarterly_commission:
            q1_values = [v for k, v in quarterly_commission.items() if k.endswith('-Q1')]
            q2_values = [v for k, v in quarterly_commission.items() if k.endswith('-Q2')]
            q3_values = [v for k, v in quarterly_commission.items() if k.endswith('-Q3')]
            q4_values = [v for k, v in quarterly_commission.items() if k.endswith('-Q4')]
            
            if q1_values and q2_values and q3_values and q4_values:
                avg_q1 = sum(q1_values) / len(q1_values)
                avg_q2 = sum(q2_values) / len(q2_values)
                avg_q3 = sum(q3_values) / len(q3_values)
                avg_q4 = sum(q4_values) / len(q4_values)
                
                quarterly_averages = [
                    ("Q1", avg_q1),
                    ("Q2", avg_q2),
                    ("Q3", avg_q3),
                    ("Q4", avg_q4)
                ]
                quarterly_averages.sort(key=lambda x: x[1], reverse=True)
                
                insights.append("Quarterly Averages (Commission) - All Years:")
                for q, avg in quarterly_averages:
                    insights.append(f"  {q}: ${avg:,.2f} (average across all years)")
        
        return "\n".join(insights)
    
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
        system_prompt = """You are an advanced analytical assistant for an insurance dashboard. 
Your role is to perform DEEP DATA ANALYSIS that goes beyond simple reporting and provides actionable business insights.

ANALYTICAL CAPABILITIES:
1. **Comparative Analysis**: Compare periods, identify trends, calculate growth rates, percentiles
2. **Pattern Recognition**: Identify seasonal patterns, cyclical trends, anomalies, correlations
3. **Best/Worst Identification**: Find best/worst performing quarters, years, months for any measure (policies, premium, commission)
4. **Statistical Analysis**: Calculate averages, medians, growth rates, year-over-year comparisons
5. **Trend Analysis**: Identify upward/downward trends, growth patterns, declining periods
6. **Multi-dimensional Analysis**: Compare policies vs premium vs commission patterns, identify relationships
7. **Contextual Insights**: Relate findings to business implications and actionable recommendations

DATA ACCESS:
- You have COMPLETE historical data broken down by Month, Quarter, and Year
- Data includes: Policies (count), Premium ($), Commission ($) for ALL periods
- You have both human-readable summaries AND structured JSON data for calculations
- Pre-calculated insights show best/worst periods - USE THESE but also do your own analysis

ANALYSIS APPROACH:
- When asked "What quarter do we historically do the best in?", analyze ALL quarters, find patterns, provide rankings
- Calculate growth rates, compare year-over-year, identify trends
- Look for seasonal patterns (e.g., Q4 always stronger, Q1 consistently weaker)
- Provide rankings: "Top 3 quarters for commission are..."
- Calculate statistics: averages, growth rates, percentiles
- Explain WHY patterns might exist based on the data
- Be analytical, not just descriptive - provide insights and recommendations

RESPONSE STYLE:
- Start with the direct answer to the question
- Support with specific numbers and data points
- Provide rankings, comparisons, and trends
- Include growth rates, percentages, and changes when relevant
- Format numbers nicely (use commas, dollar signs where appropriate)
- Be concise but comprehensive

EXAMPLE QUESTIONS YOU CAN ANSWER:
- "What quarter do we historically do the best in?" → Analyze all quarters, rank them, show top performers
- "Compare Q1 performance across all years" → Year-over-year Q1 comparison with trends
- "Is there a seasonal pattern?" → Analyze quarterly patterns across years
- "What's our growth rate?" → Calculate and explain growth trends
- "Which year had the best performance?" → Multi-metric analysis (policies, premium, commission)"""
        
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
                max_tokens=1000  # Increased for more detailed analytical responses
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return f"Error getting response from LLM: {str(e)}"

