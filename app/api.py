import uuid
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.llm_gateway import LLMGateway
from app.services.document_engine import DocumentEngine

router = APIRouter()

class JobPayload(BaseModel):
    url: str
    description: str

def load_base_cv() -> str:
    # Look for base_cv.txt in project root
    root_dir = Path(__file__).resolve().parent.parent
    cv_path = root_dir / "base_cv.txt"
    if cv_path.exists():
        with open(cv_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    raise FileNotFoundError(f"base_cv.txt not found at path: {cv_path}")

@router.post("/tailor-resume")
async def tailor_resume(payload: JobPayload):
    try:
        base_cv = load_base_cv()
        llm = LLMGateway()
        tailored_html_body = await llm.generate_tailored_resume(payload.description, base_cv)

        doc_engine = DocumentEngine()
        filename_base = f"resume_{uuid.uuid4().hex[:8]}"
        filename = await doc_engine.compile(tailored_html_body, filename_base)

        return {
            "status": "success",
            "message": "Resume tailored successfully.",
            "filename": filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))