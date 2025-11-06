# from agents.base_agent import BaseAgent

# class ClarityAgent(BaseAgent):
#     def analyze(self, description: str):
#         prompt = f"""
# You are a Clarity Evaluation Agent.
# Check readability, structure, and developer understanding.

# Return JSON:
# {{
#   "clarity_score": "<0-100>",
#   "issues": ["..."],
#   "suggestions": ["..."]
# }}

# Description:
# ---
# {description}
# ---
# """
#         return self.run_prompt(prompt)


from agents.base_agent import BaseAgent

class ClarityAgent(BaseAgent):
    def analyze(self, description: str, results: dict = None):
        """
        Analyze clarity, readability, and understandability of the project description.
        Optionally use previous agent results for context.
        """
        prompt = f"""
You are a Clarity Evaluation Agent.
Your task is to evaluate the description for readability, structure,
and how easily a developer can understand and implement the project.

Previous agent results (for context):
{results}

Return JSON:
{{
  "clarity_score": "<0-100>",
  "issues": ["..."],
  "suggestions": ["..."]
}}

Description:
---
{description}
---
"""
        return self.run_prompt(prompt)
