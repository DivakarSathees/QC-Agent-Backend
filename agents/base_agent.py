import json
import google.generativeai as genai
from config.settings import GEMINI_API_KEY

class BaseAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    def run_prompt(self, prompt: str):
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Clean non-JSON outputs
            if not text.startswith("{"):
                start = text.find("{")
                end = text.rfind("}")
                text = text[start:end + 1]

            return json.loads(text)
        except Exception as e:
            return {"status": "error", "error": str(e)}
        
    def run_code_prompt(self, prompt: str) -> str:
        """
        Sends the prompt to Gemini and returns the raw text output.
        This method never attempts JSON parsing — it always returns plain text.
        """
        try:
            response = self.model.generate_content(prompt)
            text = (response.text or "").strip()
            print(f"[BaseAgent] ✅ Gemini response length: {len(text)}")
            return text
        except Exception as e:
            print(f"[BaseAgent] ❌ Error while generating content: {e}")
            return f"ERROR: {str(e)}"

    def generate_code(self, prompt: str) -> str:
        """
        Generates code safely, removing markdown fences and extra text.
        """
        raw_text = self.run_code_prompt(prompt)

        # If the model adds markdown fences, clean them
        if isinstance(raw_text, str):
            cleaned = raw_text.strip()

            if cleaned.startswith("```"):
                # remove ``` markers and language specifiers like ```csharp
                lines = cleaned.splitlines()
                if len(lines) > 2:
                    # remove first and last fence lines
                    cleaned = "\n".join(lines[1:-1])
                else:
                    cleaned = cleaned.replace("```", "").strip()

            return cleaned

        # Fallback: convert any non-string output to string
        return str(raw_text)

    # def generate_code(self, prompt: str) -> str:
    #     """
    #     Wrapper for generating code. Cleans markdown fences and returns code.
    #     """
    #     raw_text = self.run_prompt(prompt)

    #     # Only clean text if valid string
    #     if isinstance(raw_text, str):
    #         # Remove markdown-style code fences if present
    #         if raw_text.startswith("```") and raw_text.endswith("```"):
    #             lines = raw_text.splitlines()
    #             if len(lines) >= 3:
    #                 raw_text = "\n".join(lines[1:-1])
    #     else:
    #         raw_text = str(raw_text)

    #     return raw_text
    
# import google.generativeai as genai
# from config.settings import GEMINI_API_KEY

# class BaseAgent:
#     def __init__(self, model_name="gemini-2.5-flash"):
#         genai.configure(api_key=GEMINI_API_KEY)
#         self.model = genai.GenerativeModel(model_name)

#     def run_prompt(self, prompt: str) -> str:
#         """Run a prompt and return raw text (no JSON parsing)."""
#         try:
#             print("\n[BaseAgent] Sending prompt to Gemini...\n")  # Debug
#             response = self.model.generate_content(prompt)
#             text = response.text.strip()
#             print("[BaseAgent] Response received ✅\n")
#             return text
#         except Exception as e:
#             print(f"[BaseAgent] Gemini API error: {e}")
#             return f"/* Gemini generation failed: {e} */"

#     def generate_code(self, prompt: str) -> str:
#         """Generate clean code text."""
#         code = self.run_prompt(prompt)

#         # Remove code fences like ```cs or ```python
#         if code.startswith("```"):
#             lines = code.splitlines()
#             code = "\n".join(
#                 line for line in lines if not line.strip().startswith("```")
#             )

#         return code.strip()
