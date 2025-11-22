import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        # Use gpt-4o for better analytical capabilities (can fall back to gpt-4o-mini)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
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
        Create all-time summary statistics from raw data using the SAME calculation methods as the graph.
        This ensures 100% consistency between graph and LLM data.
        """
        if not raw_data:
            return {}
        
        # Use the EXACT SAME calculation methods as the graph
        # This ensures LLM sees the same data as what's displayed
        quarterly_policies = data_processor._group_by_period(raw_data, "quarter", "policies")
        quarterly_premium = data_processor._group_by_period(raw_data, "quarter", "premium")
        quarterly_commission = data_processor._group_by_period(raw_data, "quarter", "commission")
        
        yearly_policies = data_processor._group_by_period(raw_data, "year", "policies")
        yearly_premium = data_processor._group_by_period(raw_data, "year", "premium")
        yearly_commission = data_processor._group_by_period(raw_data, "year", "commission")
        
        monthly_policies = data_processor._group_by_period(raw_data, "month", "policies")
        monthly_premium = data_processor._group_by_period(raw_data, "month", "premium")
        monthly_commission = data_processor._group_by_period(raw_data, "month", "commission")
        
        # Calculate totals (sum all values to match graph calculations)
        total_policies = len(raw_data)
        # Sum from yearly data to match graph (yearly totals are most accurate)
        total_premium = sum(premium for premium in yearly_premium.values())
        total_commission = sum(commission for commission in yearly_commission.values())
        
        # Get date range
        dates = []
        for record in raw_data:
            date = data_processor._get_date_from_record(record)
            if date:
                dates.append(date)
        
        all_time = {
            "total_policies": total_policies,
            "total_premium": total_premium,
            "total_commission": total_commission,
            "date_range": {
                "earliest": min(dates).strftime("%Y-%m-%d") if dates else None,
                "latest": max(dates).strftime("%Y-%m-%d") if dates else None
            },
            "breakdowns": {
                "monthly": {
                    "policies": monthly_policies,
                    "premium": monthly_premium,
                    "commission": monthly_commission
                },
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
        }
        
        return all_time
    
    def create_inforce_summary(self, raw_data: List[Dict[str, Any]], data_processor) -> Dict[str, Any]:
        """
        Create comprehensive inforce summary with all metric types by Line.
        This provides the LLM with complete inforce data for analysis.
        """
        if not raw_data:
            return {}
        
        # Filter for inforce policies
        inforce_policies = data_processor.filter_inforce_policies(raw_data)
        
        if not inforce_policies:
            return {
                "total_inforce_policies": 0,
                "metrics": {
                    "policy_count": [],
                    "premium": [],
                    "commission": [],
                    "avg_premium": []
                }
            }
        
        # Process all metric types
        # IMPORTANT: Use the SAME processing method as the dashboard to ensure exact consistency
        policy_count_data = data_processor.process_inforce_by_line(inforce_policies, "policy_count")
        premium_data = data_processor.process_inforce_by_line(inforce_policies, "premium")
        commission_data = data_processor.process_inforce_by_line(inforce_policies, "commission")
        avg_premium_data = data_processor.process_inforce_by_line(inforce_policies, "avg_premium")
        
        # Calculate totals using the SAME method as the dashboard (sum counts from processed data)
        # This ensures 100% consistency - dashboard sums item.count from grouped data, so should we
        total_inforce_policies = sum(item.get("count", 0) for item in policy_count_data)
        total_premium = sum(item.get("value", 0) for item in premium_data)
        total_commission = sum(item.get("value", 0) for item in commission_data)
        
        return {
            "total_inforce_policies": total_inforce_policies,
            "total_premium": total_premium,
            "total_commission": total_commission,
            "metrics": {
                "policy_count": policy_count_data,
                "premium": premium_data,
                "commission": commission_data,
                "avg_premium": avg_premium_data
            }
        }
    
    def create_data_context(self, dashboard_state: Dict[str, Any], all_time_summary: Optional[Dict[str, Any]] = None, inforce_summary: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a context string describing the current dashboard state and all-time data
        """
        context_parts = []
        
        # Add current date/time context for proper interpretation of data
        today = datetime.now()
        current_date = today.strftime("%Y-%m-%d")
        current_year = today.year
        current_month = today.month
        current_quarter = (current_month - 1) // 3 + 1
        
        context_parts.append("=== CURRENT DATE AND TIME CONTEXT ===")
        context_parts.append(f"Today's Date: {current_date}")
        context_parts.append(f"Current Year: {current_year}")
        context_parts.append(f"Current Month: {current_month} ({today.strftime('%B')})")
        context_parts.append(f"Current Quarter: Q{current_quarter}")
        context_parts.append("")
        context_parts.append("CRITICAL: Use this date context to properly interpret data.")
        context_parts.append(f"- Years before {current_year} are COMPLETE historical years")
        context_parts.append(f"- The year {current_year} may be PARTIAL (data through {current_month}/{current_year})")
        context_parts.append(f"- Years after {current_year} are FUTURE/INCOMPLETE and should not be used for trend analysis")
        context_parts.append(f"- Low numbers in {current_year + 1} or later years do NOT indicate a decline - they're just incomplete")
        context_parts.append(f"- When comparing years, only compare COMPLETE years (years before {current_year})")
        context_parts.append(f"- For {current_year}, acknowledge it's partial and focus on completed periods (months/quarters)")
        context_parts.append("")
        
        # All-time summary first (if available)
        if all_time_summary:
            context_parts.append("=== ALL-TIME DATA SUMMARY ===")
            context_parts.append(f"Total Policies (All Time): {all_time_summary.get('total_policies', 0):,}")
            # Use full precision for totals - no rounding to match chart exactly
            total_premium = all_time_summary.get('total_premium', 0)
            total_commission = all_time_summary.get('total_commission', 0)
            context_parts.append(f"Total Premium (All Time): ${total_premium:,.6f} (raw value, no rounding)")
            context_parts.append(f"Total Commission (All Time): ${total_commission:,.6f} (raw value, no rounding)")
            
            date_range = all_time_summary.get('date_range', {})
            if date_range.get('earliest') and date_range.get('latest'):
                context_parts.append(f"Date Range: {date_range['earliest']} to {date_range['latest']}")
                
                # Identify which years are complete vs partial
                latest_date_str = date_range.get('latest')
                if latest_date_str:
                    try:
                        latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d")
                        latest_year = latest_date.year
                        latest_month = latest_date.month
                        
                        context_parts.append("")
                        context_parts.append("YEAR COMPLETENESS ANALYSIS:")
                        
                        # Check yearly breakdown to identify complete vs partial years
                        yearly_policies = all_time_summary.get('breakdowns', {}).get('yearly', {}).get('policies', {})
                        if yearly_policies:
                            context_parts.append("Year Status (based on current date and data availability):")
                            for year_str in sorted(yearly_policies.keys(), key=int):
                                year_int = int(year_str)
                                if year_int < current_year:
                                    context_parts.append(f"  {year_int}: COMPLETE (historical year, full year of data)")
                                elif year_int == current_year:
                                    # Check if year is complete based on current date
                                    if current_month == 12 and latest_month >= 12:
                                        context_parts.append(f"  {year_int}: COMPLETE (current year, data through {latest_month}/{latest_year})")
                                    else:
                                        context_parts.append(f"  {year_int}: PARTIAL (current year, data through {latest_month}/{latest_year} - NOT COMPLETE)")
                                else:
                                    context_parts.append(f"  {year_int}: FUTURE/INCOMPLETE (year after current date - DO NOT use for trend analysis, very low numbers are normal)")
                        
                        context_parts.append("")
                        context_parts.append(f"CRITICAL INTERPRETATION GUIDANCE:")
                        context_parts.append(f"- Only use COMPLETE years (years before {current_year}) for meaningful trend analysis and year-over-year comparisons")
                        context_parts.append(f"- Year {current_year} is PARTIAL - only use completed months/quarters, acknowledge incompleteness when discussing")
                        context_parts.append(f"- Years after {current_year} are FUTURE/INCOMPLETE - very low numbers there are NORMAL, not indicative of decline")
                        context_parts.append(f"- When asked about trends 'over the years' or 'recent years', focus on COMPLETE years only")
                        context_parts.append(f"- NEVER interpret low numbers in future years ({current_year + 1} and later) as a decline - explain they're incomplete")
                    except (ValueError, AttributeError):
                        pass
            
            context_parts.append("")
            context_parts.append("=== COMPLETE HISTORICAL DATA (STRUCTURED JSON) ===")
            context_parts.append("ALL data is provided in JSON format for accurate analysis. Use this data for calculations.")
            context_parts.append("")
            
            # Extract breakdowns
            quarterly_policies = all_time_summary.get('breakdowns', {}).get('quarterly', {}).get('policies', {})
            quarterly_premium = all_time_summary.get('breakdowns', {}).get('quarterly', {}).get('premium', {})
            quarterly_commission = all_time_summary.get('breakdowns', {}).get('quarterly', {}).get('commission', {})
            
            yearly_policies = all_time_summary.get('breakdowns', {}).get('yearly', {}).get('policies', {})
            yearly_premium = all_time_summary.get('breakdowns', {}).get('yearly', {}).get('premium', {})
            yearly_commission = all_time_summary.get('breakdowns', {}).get('yearly', {}).get('commission', {})
            
            monthly_policies = all_time_summary.get('breakdowns', {}).get('monthly', {}).get('policies', {})
            monthly_premium = all_time_summary.get('breakdowns', {}).get('monthly', {}).get('premium', {})
            monthly_commission = all_time_summary.get('breakdowns', {}).get('monthly', {}).get('commission', {})
            
            # Provide structured data ONLY (no verbose text lists to avoid confusion)
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
                },
                "monthly": {
                    "policies": monthly_policies,
                    "premium": monthly_premium,
                    "commission": monthly_commission
                }
            }
            # Serialize JSON with full precision (no rounding) to match chart exactly
            # Serialize JSON with full precision - Python's json.dumps preserves float precision
            context_parts.append(json.dumps(structured_data, indent=2, ensure_ascii=False))
            context_parts.append("")
            context_parts.append("CRITICAL: This data uses the EXACT same calculations as the dashboard graph.")
            context_parts.append("NO ROUNDING: All values are raw floats - no rounding applied anywhere.")
            context_parts.append("The JSON above contains the exact same values the chart displays (chart formats for visual display only).")
            context_parts.append("If you calculate totals/averages from this data, they will match the chart's calculations exactly.")
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
                context_parts.append(f"- Total {measure} in view: {total:,.6f} (raw value, no rounding)")
                context_parts.append(f"- Average per period: {avg:,.6f} (raw value, no rounding)")
                
                # Show sample data - use full precision to match chart exactly
                context_parts.append(f"\nSample periods in view (latest 5):")
                for item in data[-5:]:
                    label = item.get("label", "")
                    value = item.get("value", 0)
                    context_parts.append(f"  {label}: {value:,.6f} (raw value, matches chart exactly)")
        
        elif view_type == "inforce-by-line":
            metric_type = dashboard_state.get("metric_type", "policy_count")
            context_parts.append(f"Metric Type: {metric_type}")
            context_parts.append("")
            context_parts.append("IMPORTANT: INFORCE DATA EXPLANATION")
            context_parts.append("Inforce policies are those currently active RIGHT NOW (TODAY is between effective date and expiration date).")
            context_parts.append("Inforce data represents a SNAPSHOT of the current active policy portfolio, not historical trends.")
            context_parts.append("When asked about 'over the years' for inforce data, explain that inforce is a current state measurement.")
            context_parts.append("You can analyze the CURRENT distribution by line, percentages, and compare lines, but cannot show historical trends.")
            context_parts.append("For historical trends over time, refer to the all-time summary data (policies, premium, commission by period).")
            context_parts.append("")
            
            # Include comprehensive inforce summary if available
            if inforce_summary:
                context_parts.append("")
                context_parts.append("=== COMPLETE INFORCE DATA SUMMARY ===")
                # CRITICAL: Calculate total using SAME method as dashboard (sum of counts from grouped data)
                # This ensures 100% consistency - dashboard sums item.count from processed data
                policy_count_data = inforce_summary.get("metrics", {}).get("policy_count", [])
                total_inforce_from_data = sum(item.get("count", 0) for item in policy_count_data)
                context_parts.append(f"Total Inforce Policies: {total_inforce_from_data:,}")
                context_parts.append("CRITICAL: This total is calculated using the EXACT SAME method as the dashboard table.")
                context_parts.append("It sums the 'count' field from the grouped data, ensuring 100% consistency with what's displayed.")
                total_premium = inforce_summary.get('total_premium', 0)
                total_commission = inforce_summary.get('total_commission', 0)
                context_parts.append(f"Total Premium (Inforce): ${total_premium:,.6f} (raw value, no rounding)")
                context_parts.append(f"Total Commission (Inforce): ${total_commission:,.6f} (raw value, no rounding)")
                context_parts.append("")
                
                # Include all metric types breakdowns
                context_parts.append("=== INFORCE METRICS BY LINE (STRUCTURED JSON) ===")
                context_parts.append("ALL inforce data is provided in JSON format for accurate analysis.")
                context_parts.append("")
                
                metrics = inforce_summary.get("metrics", {})
                
                # Policy Count by Line
                policy_count_data = metrics.get("policy_count", [])
                if policy_count_data:
                    context_parts.append("Policy Count (Inforce) by Line:")
                    policy_count_json = {item.get("line", "Unknown"): {
                        "count": item.get("value", 0),
                        "percent": item.get("percent", 0)
                    } for item in policy_count_data}
                    context_parts.append(json.dumps(policy_count_json, indent=2, ensure_ascii=False))
                    context_parts.append("")
                
                # Premium by Line
                premium_data = metrics.get("premium", [])
                if premium_data:
                    context_parts.append("Premium (Inforce) by Line:")
                    premium_json = {item.get("line", "Unknown"): {
                        "premium": item.get("value", 0),  # Raw float, no rounding
                        "percent": item.get("percent", 0),
                        "count": item.get("count", 0)
                    } for item in premium_data}
                    context_parts.append(json.dumps(premium_json, indent=2, ensure_ascii=False))
                    context_parts.append("")
                
                # Commission by Line
                commission_data = metrics.get("commission", [])
                if commission_data:
                    context_parts.append("Commission (Inforce) by Line:")
                    commission_json = {item.get("line", "Unknown"): {
                        "commission": item.get("value", 0),  # Raw float, no rounding
                        "percent": item.get("percent", 0),
                        "count": item.get("count", 0)
                    } for item in commission_data}
                    context_parts.append(json.dumps(commission_json, indent=2, ensure_ascii=False))
                    context_parts.append("")
                
                # Average Premium by Line
                avg_premium_data = metrics.get("avg_premium", [])
                if avg_premium_data:
                    context_parts.append("Average Premium (Inforce) by Line:")
                    avg_premium_json = {item.get("line", "Unknown"): {
                        "avg_premium": item.get("value", 0),  # Raw float, no rounding
                        "count": item.get("count", 0)
                    } for item in avg_premium_data}
                    context_parts.append(json.dumps(avg_premium_json, indent=2, ensure_ascii=False))
                    context_parts.append("")
                
                context_parts.append("CRITICAL: This inforce data uses the EXACT same calculations as the dashboard.")
                context_parts.append("NO ROUNDING: All values are raw floats - no rounding applied anywhere.")
                context_parts.append("Round all dollar amounts to the nearest dollar (NO CENTS) when presenting to users.")
                context_parts.append("")
                context_parts.append("INFORCE DATA ANALYSIS CAPABILITIES:")
                context_parts.append("- Compare performance across different lines of business")
                context_parts.append("- Identify which lines have the most policies, premium, or commission")
                context_parts.append("- Calculate percentages and distributions by line")
                context_parts.append("- Analyze trends in inforce policies over time (if historical data is available)")
                context_parts.append("- Compare average premiums across different lines")
                context_parts.append("")
            
            # Current view data (what's currently displayed)
            data = dashboard_state.get("data", [])
            if data:
                total_value = sum(item.get("value", 0) for item in data)
                total_count = sum(item.get("count", 0) for item in data)
                
                context_parts.append(f"\nCurrent View Summary (Currently Displayed):")
                context_parts.append(f"- Metric Type: {metric_type}")
                context_parts.append(f"- Total Lines: {len(data)}")
                # Format total value based on metric type
                if metric_type in ["premium", "commission", "avg_premium"]:
                    formatted_total = f"${total_value:,.6f}"
                else:
                    formatted_total = f"{total_value:,.0f}"
                context_parts.append(f"- Total Value: {formatted_total} (raw value, no rounding)")
                context_parts.append(f"- Total Policies (inforce): {total_count}")
                
                # Show all lines in current view
                sorted_data = sorted(data, key=lambda x: x.get("value", 0), reverse=True)
                context_parts.append(f"\nAll Lines (by value, descending):")
                for item in sorted_data:
                    line = item.get("line", "Unknown")
                    value = item.get("value", 0)
                    percent = item.get("percent", 0) if item.get("percent") is not None else 0
                    count = item.get("count", 0) if item.get("count") is not None else 0
                    
                    # Format value based on metric type
                    if metric_type == "avg_premium":
                        formatted_value = f"${value:,.6f}"
                        context_parts.append(f"  {line}: {formatted_value} (avg, {count} policies)")
                    elif metric_type in ["premium", "commission"]:
                        formatted_value = f"${value:,.6f}"
                        context_parts.append(f"  {line}: {formatted_value} ({percent:.2f}%, {count} policies)")
                    else:  # policy_count
                        formatted_value = f"{value:,.0f}"
                        context_parts.append(f"  {line}: {formatted_value} ({percent:.2f}%, {count} policies)")
        
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
        all_time_summary: Optional[Dict[str, Any]] = None,
        inforce_summary: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Ask the LLM a question with context about the dashboard data
        """
        if not self.is_available():
            return "LLM service is not configured. Please set OPENAI_API_KEY environment variable."
        
        if conversation_history is None:
            conversation_history = []
        
        # Create context about current dashboard state, all-time data, and inforce data
        data_context = self.create_data_context(dashboard_state, all_time_summary, inforce_summary)
        
        # System prompt with enhanced reasoning structure
        system_prompt = """You are an advanced analytical assistant for an insurance dashboard. 
Your role is to perform DEEP DATA ANALYSIS that goes beyond simple reporting and provides actionable business insights.

CRITICAL DATA CONSISTENCY:
- You have access to ALL historical data in structured JSON format
- This data uses the EXACT same calculations as the dashboard graph - 100% identical
- All values are RAW FLOATS with NO ROUNDING - they match the chart exactly
- Round all dollar amounts to the nearest dollar (NO CENTS) when presenting to users
- Totals, averages, and all calculations match between chart and LLM responses

REASONING PROCESS - USE INTERNALLY BUT DO NOT SHOW IN RESPONSE:
Think through these steps internally, but only output the final synthesized answer:
1. OBSERVE: First, examine the relevant data points from the JSON structure
   - Identify which periods, measures, and values are relevant to the question
   - Note the range of values, trends, and any outliers
   
2. CALCULATE: Perform necessary mathematical analysis
   - Calculate growth rates, averages, comparisons, or statistical measures
   - Verify calculations by cross-checking against provided totals
   - Round dollar amounts to nearest dollar for presentation
   
3. PATTERN RECOGNITION: Identify underlying patterns and relationships
   - Look for seasonal patterns, cyclical trends, or correlations
   - Compare performance across different dimensions (policies vs premium vs commission)
   - Identify what's driving the numbers
   
4. CONTEXTUALIZE: Relate findings to business implications
   - What do these patterns mean for the business?
   - What factors might explain the trends?
   - What's the significance of these findings?
   
5. SYNTHESIZE: Combine insights into a clear, narrative answer
   - Start with the direct answer to the question
   - Support with specific numbers and evidence
   - Tell the story behind the data naturally

IMPORTANT: Do NOT include the step labels (OBSERVE, CALCULATE, PATTERN RECOGNITION, CONTEXTUALIZE, SYNTHESIZE) in your response. Only output the final synthesized answer. Use the reasoning process internally to structure your thinking, but present only the natural, narrative response.

ANALYTICAL CAPABILITIES:
- Comparative Analysis: Compare periods, identify trends, calculate growth rates, percentiles
- Pattern Recognition: Identify seasonal patterns, cyclical trends, anomalies, correlations
- Best/Worst Identification: Find best/worst performing quarters, years, months for any measure
- Statistical Analysis: Calculate averages, medians, growth rates, year-over-year comparisons
- Trend Analysis: Identify upward/downward trends, growth patterns, declining periods
- Multi-dimensional Analysis: Compare policies vs premium vs commission patterns, identify relationships
- Contextual Insights: Relate findings to business implications and actionable recommendations
- INFORCE ANALYSIS: Analyze current active policies by line of business, compare distributions, calculate percentages
- Line-of-Business Analysis: Compare performance across different lines (MPL, IABEO, etc.), identify top performers

DATA ACCESS:
- You have complete historical data broken down by quarter, year, and month
- Each breakdown includes: policies (count), premium ($), commission ($)
- All values match the dashboard graph exactly - same source, same calculations
- Use the structured JSON data for ALL calculations - parse it carefully
- Pre-calculated insights are provided, but do your own deep analysis too
- INFORCE DATA: You also have access to complete inforce metrics by line of business
- Inforce data includes: Policy Count by Line, Premium by Line, Commission by Line, Average Premium by Line
- Inforce means policies that are currently active (TODAY is between effective date and expiration date)
- Use the inforce summary data to answer questions about current active policies by line
- All inforce values match the dashboard exactly - same filtering and calculations

CRITICAL DATE/TIME AWARENESS:
- You are given the CURRENT DATE in the context - PAY CLOSE ATTENTION TO IT
- The context explicitly tells you today's date, current year, current month, and current quarter
- Use this information to distinguish between COMPLETE years and PARTIAL/INCOMPLETE years
- Years before the current year are COMPLETE - use these for meaningful trend analysis
- The current year may be PARTIAL - only completed months/quarters should be compared to previous years
- Years after the current year are FUTURE/INCOMPLETE - they have very little data because the year hasn't started yet
- NEVER interpret low numbers in future years (after current year) as a decline - it's just incomplete data
- When analyzing trends, focus on COMPLETE years only (years before current year)
- When asked about "recent years" or "over the years", exclude incomplete/future years from analysis
- Always acknowledge in your response when discussing partial years that data is incomplete
- When you see low numbers in a year that's after the current date, explain that the year hasn't started yet or is just beginning
- For example, if current date is November 2025 and you see only 2 policies in 2026, explain that 2026 is a future/incomplete year and the low number is normal

ANALYSIS APPROACH:
Think through these questions internally, but only output the final answer:
1. What data points do I need to examine? (Identify relevant JSON paths)
2. What calculations are required? (Growth rates, averages, comparisons)
3. What patterns emerge from the calculations? (Trends, correlations, anomalies)
4. Why might these patterns exist? (Business context, market factors)
5. What's the key insight? (The answer to the question)
6. Present only the natural narrative answer with supporting numbers

Always verify your numbers by:
- Cross-checking calculations against provided totals
- Comparing to pre-calculated insights
- Ensuring consistency with the dashboard view

CRITICAL: Your response should be a natural narrative answer only. Do NOT include internal reasoning steps, calculation methods, or thinking process labels. Just provide the final synthesized answer directly.

RESPONSE STYLE:
- Write in plain, natural business language - you're talking to insurance professionals
- NEVER mention "JSON", "data", "queries", "backend", "API", or any technical terms
- NEVER use markdown formatting like ## headers, **bold**, or bullet points with - or *
- Use simple paragraphs and natural formatting
- Start with the direct answer to the question
- Support with specific numbers and data points (rounded to nearest dollar)
- Provide rankings, comparisons, and trends in plain language
- Include growth rates, percentages, and changes when relevant
- Format numbers nicely (use commas, dollar signs where appropriate)
- IMPORTANT: Round all dollar amounts (premium, commission) to the nearest dollar - NO CENTS (e.g., $1,198,730 not $1,198,730.05)
- Be concise but comprehensive - aim for 2-3 focused paragraphs
- Write like a business analyst who understands the insurance industry
- Balance analytical rigor with natural storytelling

EXAMPLE RESPONSES:
Good: "Commission performance has been strong in recent years. In 2024, commissions reached $1,198,730, representing an 11.5% increase from the previous year. The peak performance was in 2024, followed by a decline in 2025 to $696,866, which represents a 42% decrease. This pattern suggests potential market challenges or strategic shifts in that period."

Bad (includes reasoning steps): "OBSERVE: Looking at yearly commission data... CALCULATE: The growth rate is... PATTERN RECOGNITION: The trend shows... CONTEXTUALIZE: This suggests... SYNTHESIZE: Commission performance has been strong..."

Bad (markdown/technical): "## Analysis: \n**Commission Trends:**\n- 2024: $1,198,730.05\n- Looking at the JSON data..."

Remember: Only output the final natural narrative answer. Use the reasoning steps internally to structure your thinking, but do not include them in your response.

EXAMPLE QUESTIONS YOU CAN ANSWER:
- "What quarter do we historically do the best in?" → Analyze all quarters, find the best performers, explain in plain language
- "Compare Q1 performance across all years" → Compare Q1 across years, explain trends naturally (only use complete years)
- "Is there a seasonal pattern?" → Identify patterns and explain them like you're in a business meeting
- "What's our growth rate?" → Calculate and explain growth trends in business terms (only compare complete years)
- "Which year had the best performance?" → Compare years and explain which performed best and why (exclude future/incomplete years)
- "How have inforce line policies been over the years?" → Use the inforce summary data to analyze current inforce policies by line
- "Which line of business has the most inforce policies?" → Compare policy counts across lines from the inforce data
- "What percentage of inforce premium comes from MPL?" → Use the premium by line data to calculate percentages
- "How does inforce commission compare across lines?" → Use the commission by line data to compare and rank lines
- "What's the average premium by line for inforce policies?" → Use the avg_premium data to compare averages across lines

DATE AWARENESS EXAMPLES:
- If asked about "trends in recent years" and current date is November 2025, focus on years 2024 and earlier (complete years)
- If you see only 2 policies in 2026 and current date is November 2025, explain that 2026 is a future/incomplete year and low numbers are normal
- When comparing year-over-year growth, only compare complete years (years before current year)
- Acknowledge partial year data explicitly: "In 2025 (through November), we have..." rather than treating it as complete"""
        
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
        
        # Enhance user question - guide reasoning but emphasize natural output and date awareness
        enhanced_question = f"""{question}

IMPORTANT: Check the CURRENT DATE context provided above. Remember that:
- Years after the current date are incomplete/future years - do NOT interpret low numbers there as declines
- Only compare COMPLETE years (years before current year) for meaningful trend analysis
- If discussing the current year or future years, acknowledge they are incomplete/partial

Think through your analysis internally, then provide a natural, narrative answer with supporting evidence. Round all dollar amounts to the nearest dollar. Do not include reasoning steps, calculation methods, or labels like "OBSERVE" or "CALCULATE" in your response - just provide the final synthesized answer."""
        
        # Add enhanced question
        messages.append({
            "role": "user",
            "content": enhanced_question
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,  # Lower temperature for analytical focus with natural storytelling
                max_tokens=1000  # Increased for more detailed analytical responses
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return f"Error getting response from LLM: {str(e)}"

