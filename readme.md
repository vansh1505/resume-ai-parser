Here’s a **polished, professional `README.md`** that positions your project as a strong portfolio piece while keeping it technical and impressive:

---

# AI Resume Parsing API 🚀

An **AI-powered resume analysis API** built with **FastAPI**, **PyMuPDF**, and **Google Gemini 1.5 Flash**.
This service extracts and evaluates resume content directly from a **public PDF URL**, returning **structured insights** in JSON format for easy integration into recruitment platforms, career portals, or HR automation workflows.

---

## 🔥 Key Features

* **Direct PDF Parsing** — Extracts text content from any PDF resume link.
* **AI-Powered Evaluation** — Uses **Google Generative AI (Gemini 1.5 Flash)** to analyze resumes.
* **Structured JSON Output** — Always returns clean, machine-readable JSON for easy frontend integration.
* **Resume Quality Scoring** — Rates resumes from **0 to 100** based on content strength.
* **Skill Extraction** — Automatically detects **technical skills** mentioned in the resume.
* **Quality Ranking** — Categorizes resumes as **Best**, **Average**, or **Needs Improvement**.
* **Improvement Suggestions** — Provides **3 actionable recommendations** to boost resume quality.
* **CORS Enabled** — Ready for direct use with web applications.

---

## 📦 Tech Stack

* **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/)
* **PDF Parsing:** [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/)
* **AI Model:** [Google Generative AI (Gemini 1.5 Flash)](https://ai.google.dev/)
* **Environment Config:** [python-dotenv](https://pypi.org/project/python-dotenv/)
* **HTTP Requests:** [Requests](https://pypi.org/project/requests/)

---

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ai-resume-parser.git
cd ai-resume-parser

# Install dependencies
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root and add your **Google Generative AI API key**:

```
API_KEY=your_google_genai_api_key
```

Get your API key from: [Google AI Studio](https://makersuite.google.com/).

---

## 🚀 Running Locally

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at:

```
http://localhost:8000
```

---

## 📡 API Usage

**Endpoint:**

```
GET /api/parse-resume?pdf_url=<PUBLIC_PDF_LINK>
```

**Example Request:**

```bash
curl "http://localhost:8000/api/parse-resume?pdf_url=https://example.com/resume.pdf"
```

**Example Response:**

```json
{
  "status": "success",
  "parsed_data": {
    "appropriate": true,
    "score": 87,
    "skills": ["Python", "FastAPI", "Machine Learning"],
    "rank": "Best",
    "improvements": [
      "Add quantified achievements",
      "Include a professional summary",
      "Expand project details"
    ]
  }
}
```

---

## 🎯 Ideal Use Cases

* **Job Portals** – Automate resume screening before human review.
* **HR Tools** – Integrate structured resume data directly into applicant tracking systems.
* **Career Services** – Give students AI feedback on resumes.