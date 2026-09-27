from pathlib import Path

class DocumentEngine:
    def __init__(self):
        self.output_dir = Path(__file__).resolve().parent.parent.parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)

    async def compile(self, html_body: str, filename_base: str) -> str:
        filename = f"{filename_base}.html"
        file_path = self.output_dir / filename

        full_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Abdullah Tauseef - Resume</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Calibri', 'Arial', sans-serif;
            color: #111111;
            line-height: 1.4;
            background-color: #f3f4f6;
            padding: 20px 0;
        }}
        .no-print {{
            position: fixed;
            top: 15px;
            right: 20px;
            background: #2563eb;
            color: white;
            padding: 10px 18px;
            border-radius: 6px;
            cursor: pointer;
            font-family: sans-serif;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border: none;
            z-index: 1000;
        }}
        .no-print:hover {{ background: #1d4ed8; }}
        
        .page {{
            width: 210mm;
            min-height: 297mm;
            padding: 15mm 18mm;
            margin: 0 auto;
            background: #ffffff;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        
        h1 {{ font-size: 20pt; text-align: center; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; color: #000; }}
        .contact-info {{ text-align: center; font-size: 9.5pt; margin-bottom: 12px; color: #333; }}
        .contact-info a {{ color: #111; text-decoration: none; }}
        
        h2 {{ 
            font-size: 11pt; 
            text-transform: uppercase; 
            border-bottom: 1px solid #222; 
            padding-bottom: 2px; 
            margin-top: 12px; 
            margin-bottom: 6px; 
            letter-spacing: 0.5px;
            color: #000;
        }}
        
        p, li {{ font-size: 9.5pt; color: #222; }}
        ul {{ padding-left: 16px; margin-top: 3px; margin-bottom: 6px; }}
        li {{ margin-bottom: 3px; }}
        .job-header {{ display: flex; justify-content: space-between; font-weight: bold; margin-top: 6px; }}
        .job-title {{ font-style: italic; font-weight: normal; }}

        @media print {{
            body {{ background: none; padding: 0; }}
            .no-print {{ display: none !important; }}
            .page {{ box-shadow: none; margin: 0; width: 100%; padding: 10mm 12mm; }}
            @page {{ size: A4; margin: 0; }}
        }}
    </style>
</head>
<body>
    <button class="no-print" onclick="window.print()">Save / Download as PDF</button>
    <div class="page">
        {html_body}
    </div>
</body>
</html>"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_document)

        return filename