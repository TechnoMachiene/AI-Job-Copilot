from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr

class TaskType(str, Enum):
    EVALUATE_MATCH = "EVALUATE_MATCH"
    GENERATE_RESUME = "GENERATE_RESUME"
    GENERATE_COVER_LETTER = "GENERATE_COVER_LETTER"
    EXTRACT_HR_EMAIL = "EXTRACT_HR_EMAIL"
    ANSWER_ATS_QUESTION = "ANSWER_ATS_QUESTION"
    PARSE_CV_PROFILE = "PARSE_CV_PROFILE"

class JobPosting(BaseModel):
    url: str
    raw_text: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None

class ApplicationContext(BaseModel):
    job_url: str
    job_description: str
    candidate_name: str
    candidate_email: str
    candidate_phone: str
    resume_pdf_path: Optional[str] = None
    cover_letter_pdf_path: Optional[str] = None
    match_score: Optional[int] = None

class ParsedCandidateProfile(BaseModel):
    name: str
    email: EmailStr
    phone: str
    summary: str
    skills: List[str]
    experience_highlights: List[str]
    education: List[str]

class MatchEvaluation(BaseModel):
    match_score: int
    strengths: List[str]
    missing_requirements: List[str]
    should_apply: bool

class ResumeOutput(BaseModel):
    resume_tex: str

class CoverLetterOutput(BaseModel):
    cover_letter_tex: str

class HREmailOutput(BaseModel):
    email: Optional[EmailStr] = None

class JobApplicationRequest(BaseModel):
    url: str

class HuntStatusResponse(BaseModel):
    hunt_id: str
    status: str
    candidate_name: Optional[str] = None
    jobs_found: int = 0
    jobs_processed: int = 0
    results: List[Dict[str, Any]] = []
    logs: List[str] = []