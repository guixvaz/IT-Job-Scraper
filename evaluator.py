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
        
        self.system_prompt = """
        You are an IT recruiter evaluating a job description against a candidate's profile.
        The candidate is a part-time Wirtschaftsinformatik student at FHNW.
        Candidate Skills:
        - Work Experience: No professional experience yet, but has completed several IT-related projects during studies aswell as personal projects.
        - Education: Currently pursuing a degree in Wirtschaftsinformatik (Business Informatics) at FHNW.
        - Tech: Python, FastAPI, SQLModel, SQLite, MySQL, Docker, Git, REST APIs
        - Design Patterns: MVC, GoF patterns
        - Analysis: Requirements Engineering, BPMN 2.0, UML
        - Languages: Native Portuguese, fluent German and English, basic French

        Determine if the candidate has at least a 60% partial match with the core requirements.
        Ignore workload percentage and location, as those are filtered elsewhere.
        """

    def evaluate(self, job_description: str) -> bool:
        """Analyzes a job description string and returns True if it matches the profile."""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.5-flash-lite',
                    contents=f"Job Description:\n{job_description}",
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_prompt,
                        response_mime_type="application/json",
                        response_schema=JobMatchResult,
                        temperature=0.1, 
                    ),
                )

                result = response.parsed

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