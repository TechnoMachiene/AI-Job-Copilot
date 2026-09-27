import io
from pypdf import PdfReader

class CVParserService:
    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        """Extracts plain text content from uploaded PDF bytes."""
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        
        if not extracted_text.strip():
            raise ValueError("Could not extract any readable text from the uploaded PDF CV.")
            
        return extracted_text.strip()