import os
from dotenv import load_dotenv
from groq import AsyncGroq, APIConnectionError, APIError

load_dotenv()

class LLMGateway:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key:
            raise ValueError("GROQ_API_KEY is missing in your .env file.")
        self.client = AsyncGroq(api_key=api_key)

    async def generate_tailored_resume(self, job_description: str, base_cv: str) -> str:
        prompt = f"""
You are an expert ATS Resume Engineer. Tailor the candidate's ACTUAL background to highlight the most relevant skills, projects, and experiences for the target job description.

CRITICAL IDENTITY & TRUTHFULNESS MANDATE:
1. CANDIDATE NAME MUST BE: Abdullah Tauseef.
2. Use ONLY the real experiences, companies (NonchTech, Upwork, Aizonix, MCS NUST, SLB), projects, education (NUTECH), and metrics from the BASE CV below.
3. ABSOLUTELY DO NOT invent fake names, companies, degrees, or dates.
4. Select and reframe the bullet points and projects that match the TARGET JOB DESCRIPTION best.

TARGET JOB DESCRIPTION:
{job_description[:4000]}

ACTUAL BASE CV:
{base_cv}

OUTPUT FORMAT RULES:
- Output clean, semantic HTML body elements (div, h1, h2, ul, li, p, span).
- DO NOT output outer <html>, <head>, or <body> tags.
- Sections:
  - Header: Abdullah Tauseef | AI Automation Engineer | Contact details
  - PROFESSIONAL SUMMARY (3-4 concise sentences tailored to the job description)
  - TECHNICAL SKILLS (Grouped logically and emphasized for the JD)
  - PROFESSIONAL EXPERIENCE (NonchTech, Upwork, Aizonix, NUST, SLB)
  - SELECTED PROJECTS (Pick 3-4 most relevant projects)
  - RESEARCH & PUBLICATION (ICEAI-2026 paper)
  - EDUCATION & CERTIFICATIONS (NUTECH, Codebasics)
- DO NOT wrap output in markdown code blocks (no ```html). Start directly with HTML elements.
"""
        try:
            response = await self.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )

            content = response.choices[0].message.content.strip()

            if content.startswith("```"):
                lines = content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines).strip()

            return content

        except APIConnectionError as e:
            raise RuntimeError("Failed to connect to Groq API. Check internet connection.") from e
        except APIError as e:
            raise RuntimeError(f"Groq API Error: {e.message}") from e