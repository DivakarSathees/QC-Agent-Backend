# import os
# from typing import Dict

# class SolutionWriterAgent:
#     def __init__(self, ai_client=None):
#         self.ai_client = ai_client

#     def read_src_files(self, src_directory: str) -> Dict[str, str]:
#         src_files = {}
#         for root, _, files in os.walk(src_directory):
#             for f in files:
#                 if f.endswith((".cs", ".ts", ".js", ".py")):
#                     path = os.path.join(root, f)
#                     with open(path, "r", encoding="utf-8") as file:
#                         src_files[path] = file.read()
#         return src_files

#     def write_solution(self, src_directory: str, project_description: str) -> Dict:
#         src_files = self.read_src_files(src_directory)
#         write_summary = {}
#         print(f"[SolutionWriterAgent] Found {len(src_files)} source files to process.")
#         print(src_files)

#         for path, content in src_files.items():
#             print(f"\n[SolutionWriterAgent] Processing file: {path}")

#             prompt = f"""
# You are an expert developer.
# Modify the file strictly based on the following project description.
# Do NOT hallucinate, invent new logic, or deviate from the requirements.

# Project Description:
# {project_description}

# Existing File Content:
# {content}

# Return only the full corrected file content.
# """

#             if not self.ai_client:
#                 raise RuntimeError("AI client not initialized in SolutionWriterAgent")

#             ai_response = self.ai_client.generate_code(prompt)
#             print(f"[SolutionWriterAgent] File updated with AI output ✅")

#             with open(path, "w", encoding="utf-8") as f:
#                 f.write(ai_response)

#             write_summary[path] = "updated"

#         return write_summary


import os
import json
from typing import Dict

class SolutionWriterAgent:
    def __init__(self, ai_client=None):
        self.ai_client = ai_client

    def read_src_files(self, src_directory: str) -> Dict[str, str]:
        """
        Recursively reads all .cs, .ts, .js, and .py source files
        and returns {filepath: content}.
        """
        src_files = {}
        for root, _, files in os.walk(src_directory):
            for f in files:
                if f.endswith((".cs", ".ts", ".js", ".py")):
                    path = os.path.join(root, f)
                    with open(path, "r", encoding="utf-8") as file:
                        src_files[path] = file.read()
        return src_files

    def write_solution(self, src_directory: str, project_description: str) -> Dict:
        """
        Uses AI once to modify all files as per the project description.
        The model must return JSON of structure:
        {
            "files": {
                "<filepath>": "<updated_content>"
            },
            "notes": "<explanation of what was changed and why>"
        }
        """
        src_files = self.read_src_files(src_directory)
        print(f"[SolutionWriterAgent] Found {len(src_files)} source files to process.")

        if not self.ai_client:
            raise RuntimeError("AI client not initialized in SolutionWriterAgent")

        # Build the unified prompt
        prompt = f"""
You are an expert software developer.

Your task is to modify a multi-file project STRICTLY based on the provided project description.
- DO NOT invent new logic or functionality beyond what the description specifies.
- If you add or change anything not explicitly requested, you MUST explain it in the "notes" section.
- Maintain consistent naming and logic across all files.
- Do not remove unrelated existing logic unless the description requires it.

### Project Description:
{project_description}

### Source Files (JSON):
{json.dumps(src_files, indent=2)}

### Expected Output JSON:
{{
  "files": {{
    "path/to/file1.cs": "updated file content",
    "path/to/file2.ts": "updated file content"
  }},
  "notes": "Explain any changes made or additions beyond the description."
}}

Return only valid JSON — no markdown, no extra commentary.
"""

        # Run AI once for all files
        ai_response = self.ai_client.generate_code(prompt)

        # Ensure string → dict conversion
        try:
            result = json.loads(ai_response)
        except Exception as e:
            print(f"[SolutionWriterAgent] ❌ Failed to parse AI response as JSON: {e}")
            return {
                "status": "error",
                "error": str(e),
                "raw_response": ai_response
            }

        # Write files
        # updated_files = result.get("files", {})
        # for path, new_content in updated_files.items():
        #     if os.path.exists(path):
        #         with open(path, "w", encoding="utf-8") as f:
        #             f.write(new_content)
        #     else:
        #         # Create missing directories if necessary
        #         print(f"[SolutionWriterAgent] Creating new file at: {path}")
        #         os.makedirs(os.path.dirname(path), exist_ok=True)
        #         with open(path, "w", encoding="utf-8") as f:
        #             f.write(new_content)

        # print(f"[SolutionWriterAgent] ✅ Updated {len(updated_files)} files successfully.")
        # return {
        #     "status": "success",
        #     "updated_files": list(updated_files.keys()),
        #     "notes": result.get("notes", "")
        # }



        # updated_files = result.get("files", {})
        # for relative_path, new_content in updated_files.items():
        #     abs_path = os.path.join(src_directory, relative_path)
        #     os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        #     with open(abs_path, "w", encoding="utf-8") as f:
        #         f.write(new_content)
        #     print(f"[SolutionWriterAgent] ✅ Wrote {relative_path}")

        # print(f"[SolutionWriterAgent] ✅ Updated {len(updated_files)} files successfully.")
        # return {
        #     "status": "success",
        #     "updated_files": list(updated_files.keys()),
        #     "notes": result.get("notes", "")
        # }
    
        updated_files = result.get("files", {})
        for ai_path, new_content in updated_files.items():
            # Normalize the path to handle cases like WORKSPACE/springapp/...
            normalized_path = os.path.normpath(ai_path)
            print(f"[SolutionWriterAgent] Processing AI path: {ai_path} → Normalized: {normalized_path}")
            # Try to strip any leading part that overlaps with src_directory name
            src_dir_name = os.path.basename(src_directory)
            parts = normalized_path.split(os.sep)
            if src_dir_name in parts:
                # Keep only the part starting from src_dir_name
                normalized_path = os.path.join(*parts[parts.index(src_dir_name) + 1:])

            # Join safely under src_directory
            abs_path = os.path.join(src_directory, normalized_path)

            # Ensure it doesn't escape the project root (security & correctness)
            abs_path = os.path.normpath(abs_path)
            if not abs_path.startswith(os.path.abspath(src_directory)):
                print(f"[⚠️ Warning] Skipping unsafe path outside src_directory: {ai_path}")
                continue

            # Create directories and write file
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            print(f"[SolutionWriterAgent] ✅ Wrote file: {abs_path}")
