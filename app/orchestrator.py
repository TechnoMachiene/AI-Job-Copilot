import uuid
import asyncio
from typing import Dict, Any
from app.config import settings
from app.schemas import (
    TaskType, MatchEvaluation, ResumeOutput, CoverLetterOutput, 
    HREmailOutput, ParsedCandidateProfile
)
from app.services.cv_parser import CVParserService
from app.services.job_search_service import JobSearchService
from app.services.scraper_service import ScraperService
from app.services.llm_gateway import LLMGateway
from app.services.document_engine import DocumentEngine
from app.services.outreach.email_adapter import EmailAdapter
from app.services.outreach.playwright_adapter import PlaywrightATSAdapter

HUNT_JOBS_STORE: Dict[str, Dict[str, Any]] = {}

class AutoHuntOrchestrator:
    @staticmethod
    def initialize_hunt(role: str, location: str) -> str:
        hunt_id = str(uuid.uuid4())[:8]
        HUNT_JOBS_STORE[hunt_id] = {
            "status": "INITIALIZING",
            "role": role,
            "location": location,
            "candidate_profile": None,
            "jobs_found": 0,
            "jobs_processed": 0,
            "results": [],
            "logs": [f"Initialized Auto-Hunt for role '{role}' in '{location}'"]
        }
        return hunt_id

    @staticmethod
    async def run_auto_hunt(hunt_id: str, cv_bytes: bytes, max_jobs: int):
        job_data = HUNT_JOBS_STORE[hunt_id]
        
        try:
            # 1. Parse CV
            job_data["status"] = "PARSING_CV"
            job_data["logs"].append("Extracting text from uploaded PDF CV...")
            raw_cv_text = CVParserService.extract_text_from_pdf(cv_bytes)
            
            job_data["logs"].append("LLM is structuring candidate profile from CV...")
            profile = LLMGateway.execute_llm_task(
                task_type=TaskType.PARSE_CV_PROFILE,
                context={"raw_cv_text": raw_cv_text},
                response_schema=ParsedCandidateProfile
            )
            job_data["candidate_profile"] = profile.model_dump()
            job_data["logs"].append(f"Parsed CV for candidate: {profile.name}")

            # 2. Surf Web for Jobs via Browser Engine
            job_data["status"] = "SURFING_THE_WEB"
            job_data["logs"].append(f"Surfing web for '{job_data['role']}' jobs in '{job_data['location']}'...")
            
            urls = await JobSearchService.search_live_jobs(
                role=job_data['role'], 
                location=job_data['location'], 
                max_results=max_jobs
            )
            
            job_data["jobs_found"] = len(urls)
            job_data["logs"].append(f"Found {len(urls)} live ATS job URLs to apply for.")

            if not urls:
                job_data["status"] = "COMPLETED"
                job_data["logs"].append("No matching job URLs found on search engine.")
                return

            # 3. Iterate & Auto-Apply
            job_data["status"] = "APPLYING_LOOP"
            for index, url in enumerate(urls, start=1):
                job_data["logs"].append(f"Processing Job [{index}/{len(urls)}]: {url}")
                result = await AutoHuntOrchestrator._process_single_job(url, profile)
                job_data["results"].append(result)
                job_data["jobs_processed"] = index

            job_data["status"] = "COMPLETED"
            job_data["logs"].append("Auto-Hunt complete! All discovered jobs processed.")

        except Exception as e:
            job_data["status"] = "FAILED"
            job_data["logs"].append(f"Fatal error in hunt pipeline: {str(e)}")

    @staticmethod
    async def _process_single_job(url: str, profile: ParsedCandidateProfile) -> Dict[str, Any]:
        result_summary = {"url": url, "status": "UNKNOWN", "score": 0}
        candidate_dict = profile.model_dump()

        try:
            job_text = await ScraperService.scrape_job_details(url)
            context = {"job_description": job_text, "candidate_profile": candidate_dict}

            match_eval = LLMGateway.execute_llm_task(
                task_type=TaskType.EVALUATE_MATCH,
                context=context,
                response_schema=MatchEvaluation
            )
            result_summary["score"] = match_eval.match_score

            if match_eval.match_score < settings.min_match_score:
                result_summary["status"] = f"SKIPPED (Score {match_eval.match_score} < {settings.min_match_score})"
                return result_summary

            resume_res = LLMGateway.execute_llm_task(TaskType.GENERATE_RESUME, context, ResumeOutput)
            cover_res = LLMGateway.execute_llm_task(TaskType.GENERATE_COVER_LETTER, context, CoverLetterOutput)
            
            pdf_id = str(uuid.uuid4())[:6]
            resume_pdf = DocumentEngine.compile_latex_to_pdf(resume_res.resume_tex, f"resume_{pdf_id}.pdf")
            cover_pdf = DocumentEngine.compile_latex_to_pdf(cover_res.cover_letter_tex, f"cover_{pdf_id}.pdf")

            hr_eval = LLMGateway.execute_llm_task(TaskType.EXTRACT_HR_EMAIL, context, HREmailOutput)
            
            if hr_eval.email and settings.smtp_username and settings.smtp_password:
                EmailAdapter.send_application_email(
                    recipient_email=hr_eval.email,
                    candidate_name=profile.name,
                    job_title="Position",
                    cover_letter_text="Please find attached my tailored CV and Cover Letter.",
                    attachments=[resume_pdf, cover_pdf]
                )
                result_summary["status"] = f"APPLIED via Email ({hr_eval.email})"
            else:
                adapter = PlaywrightATSAdapter()
                success = await adapter.fill_and_submit(
                    job_url=url,
                    candidate_data={"name": profile.name, "email": profile.email, "phone": profile.phone},
                    resume_path=resume_pdf,
                    cover_letter_path=cover_pdf
                )
                result_summary["status"] = "APPLIED via Browser Automation" if success else "ATS_AUTOMATION_FAILED"

        except Exception as e:
            result_summary["status"] = f"ERROR: {str(e)}"

        return result_summary