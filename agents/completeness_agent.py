from agents.base_agent import BaseAgent

class CompletenessAgent(BaseAgent):
    def analyze(self, description: str):
        prompt = f"""
You are a Completeness Quality Checker Agent.
Check if the project description includes:
- Problem statement
- Classes / Modules / Components
- Input-output or API specs
- Database schema (if relevant)
- Expected functionality and constraints

Return JSON:
{{
  "completeness_score": "<0-100>",
  "missing_components": ["..."],
  "remarks": "summary"
}}

Description:
---
{description}
---
"""
        return self.run_prompt(prompt)
