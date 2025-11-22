import os
import json
from typing import Dict, List, Any, Optional

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
    
    def create_data_context(self, dashboard_state: Dict[str, Any]) -> str:
        """
        Create a context string describing the current dashboard state
        """
        context_parts = []
        
        # View type and filters
        view_type = dashboard_state.get("view_type", "time-based")
        context_parts.append(f"Current View: {view_type}")
        
        if view_type == "time-based":
            measure = dashboard_state.get("measure", "policies")
            period = dashboard_state.get("period", "month")
            number_of_periods = dashboard_state.get("number_of_periods", 10)
            
            context_parts.append(f"Measure: {measure.capitalize()}")
            context_parts.append(f"Period: {period.capitalize()}")
            context_parts.append(f"Showing latest {number_of_periods} {period}(s)")
            
            # Data summary
            data = dashboard_state.get("data", [])
            if data:
                values = [item.get("value", 0) for item in data]
                total = sum(values)
                avg = total / len(values) if values else 0
                context_parts.append(f"\nData Summary:")
                context_parts.append(f"- Data points: {len(data)}")
                context_parts.append(f"- Total {measure}: {total:,.2f}")
                context_parts.append(f"- Average per period: {avg:,.2f}")
                
                # Show sample data
                context_parts.append(f"\nSample periods (latest 5):")
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
                
                context_parts.append(f"\nData Summary:")
                context_parts.append(f"- Total Lines: {len(data)}")
                context_parts.append(f"- Total Value: {total_value:,.2f}")
                context_parts.append(f"- Total Policies: {total_count}")
                
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
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Ask the LLM a question with context about the dashboard data
        """
        if not self.is_available():
            return "LLM service is not configured. Please set OPENAI_API_KEY environment variable."
        
        if conversation_history is None:
            conversation_history = []
        
        # Create context about current dashboard state
        data_context = self.create_data_context(dashboard_state)
        
        # System prompt
        system_prompt = """You are a helpful assistant for an insurance dashboard. 
You help users understand their insurance data including policies, premiums, commissions, and inforce metrics.
You have access to the current dashboard state and can answer questions about the data, trends, and insights.

Be concise, accurate, and helpful. Format numbers nicely (use commas, dollar signs where appropriate).
If asked about something not in the current view, explain what would need to be changed to see that data."""
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add context message
        messages.append({
            "role": "system",
            "content": f"Current Dashboard State:\n{data_context}"
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

