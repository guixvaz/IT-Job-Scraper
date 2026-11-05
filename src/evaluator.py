import os
import time
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai
from google.genai import types

# Ensure environment variables are loaded
load_dotenv()

class JobMatchResult(BaseModel):
    is_match: bool
    reasoning: str

class GeminiEvaluator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        self.client = genai.Client(api_key=api_key)

        # Load the profile dynamically from the markdown file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        profile_path = os.path.join(base_dir, "candidate_profile.md")
        
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                candidate_profile = f.read()
        except FileNotFoundError:
            candidate_profile = "Candidate profile not found."

        self.system_prompt = f"""
        You are an IT recruiter evaluating a job description against a candidate's profile.
        
        Candidate Profile:
        {candidate_profile}

        Determine if the candidate has at least a 60% partial match with the core requirements.
        Ignore workload percentage and location, as those are filtered elsewhere.
        """

    def clean_job_description(self, text: str) -> str:
        """Strips out boilerplate and limits text length to reduce token usage."""

        if not text:
            return ""
            
        # 1. Truncate extreme length (e.g., cap at 4000 characters ~ 1000 tokens)
        max_chars = 4000
        if len(text) > max_chars:
            text = text[:max_chars]
            
        # 2. Strip common boilerplate sections that don't contain requirements
        # Splitting at these markers drops the footer text (benefits, EEO statements, contact info)
        boilerplate_markers = [
            "Wir bieten", 
            "Unser Angebot",
            "What we offer",
            "Benefits",
            "Equal Opportunity Employer",
            "Wir freuen uns auf deine Bewerbung"
        ]
        
        for marker in boilerplate_markers:
            if marker in text:
                text = text.split(marker)[0]
                
        return text.strip()

    def evaluate(self, job_description: str) -> bool:
        """Analyzes a job description string and returns True if it matches the profile."""

        cleaned_description = self.clean_job_description(job_description)
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.5-flash-lite',
                    contents=f"Job Description:\n{cleaned_description}",
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_prompt,
                        response_mime_type="application/json",
                        response_schema=JobMatchResult,
                        temperature=0.1, 
                    ),
                )

                result = response.parsed

                if not isinstance(result, JobMatchResult):
                    print("    -> API ERROR: Unexpected response format")
                    return True

                if result.is_match:
                    print(f"    -> GEMINI MATCHED: {result.reasoning}")
                    return True
                else:
                    print(f"    -> GEMINI REJECTED: {result.reasoning}")
                    return False

            except Exception as e:
                error_str = str(e)
                # Catch overload or rate-limit errors and retry
                if "503" in error_str or "429" in error_str:
                    if attempt < max_retries - 1:
                        sleep_time = 2 ** attempt  # Waits 1s, then 2s
                        print(f"    -> API overloaded. Retrying in {sleep_time}s (Attempt {attempt + 1}/{max_retries})...")
                        time.sleep(sleep_time)
                        continue
                
                print(f"    -> API ERROR: {e}")
                return True # Default to keeping the job if all retries fail or it's a different error