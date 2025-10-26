import os
from typing import Dict

class SolutionWriterAgent:
    def __init__(self, ai_client=None):
        self.ai_client = ai_client

    def read_src_files(self, src_directory: str) -> Dict[str, str]:
        src_files = {}
        for root, _, files in os.walk(src_directory):
            for f in files:
                if f.endswith((".cs", ".ts", ".js", ".py")):
                    path = os.path.join(root, f)
                    with open(path, "r", encoding="utf-8") as file:
                        src_files[path] = file.read()
        return src_files

    def write_solution(self, src_directory: str, project_description: str) -> Dict:
        src_files = self.read_src_files(src_directory)
        write_summary = {}
        print(f"[SolutionWriterAgent] Found {len(src_files)} source files to process.")
        print(src_files)

        for path, content in src_files.items():
            print(f"\n[SolutionWriterAgent] Processing file: {path}")

            prompt = f"""
You are an expert developer.
Modify the file strictly based on the following project description.
Do NOT hallucinate, invent new logic, or deviate from the requirements.

Project Description:
{project_description}

Existing File Content:
{content}

Return only the full corrected file content.
"""

            if not self.ai_client:
                raise RuntimeError("AI client not initialized in SolutionWriterAgent")

            ai_response = self.ai_client.generate_code(prompt)
            print(f"[SolutionWriterAgent] File updated with AI output ✅")

            with open(path, "w", encoding="utf-8") as f:
                f.write(ai_response)

            write_summary[path] = "updated"

        return write_summary
