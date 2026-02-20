from ..services.llm_client import LLMClient
from ..utils.prompt_loader import RESUME_ANALYZER_PROMPT

class ResumeAnalyzerAgent:
    def __init__(self):
        self.llm_client = LLMClient()

    async def analyze(self, resume_text: str) -> dict:
        # Limit text length to speed up analysis
        truncated_text = resume_text[:6000]
        prompt = f"Here is the candidate's resume text:\n\n{truncated_text}"
        response = await self.llm_client.generate_json(prompt, RESUME_ANALYZER_PROMPT)
        
        default_structure = {
            "skills": [],
            "projects": [],
            "experience": [],
            "achievements": []
        }

        if "error" in response:
            return default_structure
        
        # Merge with default to ensure all keys exist
        for key in default_structure:
            if key not in response:
                response[key] = default_structure[key]
                        
        return response
