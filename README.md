# AI Job Copilot (Chrome Extension + FastAPI Backend)

An automated, local ATS resume tailoring copilot.

The Chrome Extension extracts job listing details directly from active browser pages and sends the payload to a local FastAPI backend. The backend uses Groq (`openai/gpt-oss-120b`) anchored strictly to your real experience (`base_cv.txt`) to generate clean, print-ready ATS resumes.

---

## Architecture Overview

* **Frontend:** Chrome Extension (Manifest V3) — Reads active tab DOM text and triggers job processing.
* **Backend:** FastAPI (`main.py`) — Asynchronous REST server running on `http://127.0.0.1:8000`.
* **AI Engine:** Groq API (`openai/gpt-oss-120b`) — Reframes real work history against job descriptions without inventing false information.
* **Document Engine:** HTML/CSS ATS Compiler — Outputs formatted HTML documents with embedded `window.print()` PDF generation.

---

## Prerequisites

* **Python 3.10+**
* **Google Chrome**
* **Groq API Key** — [Get one here](https://console.groq.com/)

---

## Installation & Setup

### 1. Backend Setup

#### Clone or Open the Repository

```bash
cd JobAgent
```

#### Create and Activate a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Install Dependencies

```bash
pip install fastapi uvicorn groq python-dotenv pydantic
```

#### Configure Environment Variables

Create a `.env` file in the `JobAgent/` root directory:

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

#### Add Your Real Background

Create a `base_cv.txt` file in the `JobAgent/` root directory and paste your actual:

* Work experience
* Technical skills
* Projects
* Education
* Other relevant professional experience

The AI should use this file as the ground truth and must not invent experience, skills, projects, employers, or qualifications.

#### Start the FastAPI Server

```bash
python main.py
```

The server will run locally at:

`http://127.0.0.1:8000`

---

### 2. Chrome Extension Setup

1. Open Google Chrome.
2. Navigate to `chrome://extensions/`.
3. Toggle **Developer mode** ON in the top-right corner.
4. Click **Load unpacked**.
5. Select the `chrome-extension` directory inside this project.
6. Click the **Puzzle Piece** icon in the Chrome toolbar.
7. Pin **AI Job Copilot**.

---

## How to Use

1. Ensure the Python backend is running:

   ```bash
   python main.py
   ```

2. Navigate to any job posting in Google Chrome, such as:

   * LinkedIn
   * Greenhouse
   * Lever
   * Indeed

3. Click the **AI Job Copilot** icon in your Chrome toolbar.

4. Press **Tailor Resume for this Job**.

5. A new browser tab will automatically open with your tailored resume.

6. Click **Save / Download as PDF** in the top-right corner, or press `Ctrl + P`, to export the resume as a PDF.

---

## Project Structure

```text
JobAgent/
├── app/
│   ├── api.py                       # REST API endpoints (/api/tailor-resume)
│   └── services/
│       ├── document_engine.py       # Formats HTML ATS templates with print CSS
│       └── llm_gateway.py           # Groq Async Client & strict prompt engineering
│
├── chrome-extension/
│   ├── content.js                   # Injected script to extract raw page text
│   ├── manifest.json                # Extension config & permissions
│   ├── popup.html                   # Extension UI window
│   └── popup.js                     # Communication bridge between browser & FastAPI
│
├── outputs/                         # Output directory serving generated resume files
├── .env                             # API keys and environment variables
├── base_cv.txt                     # Ground-truth candidate profile
├── main.py                          # FastAPI entrypoint & static file server
└── README.md                        # Documentation
```

---

## Core Principle

The AI Job Copilot tailors the candidate's existing experience to the requirements of each job posting.

It **does not fabricate**:

* Work experience
* Job titles
* Employers
* Projects
* Technical skills
* Certifications
* Education
* Achievements
* Responsibilities

The generated resume should remain factually grounded in `base_cv.txt` while adapting wording and emphasis to the target job description.
