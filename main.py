from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import requests
import re

app = FastAPI()

# Allowed CORS origins
origins = ["https://uniplace.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resume parser
def parse_resume(text: str):
    email = re.findall(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", text)
    phone = re.findall(r"\b\d{10}\b", text)
    skills_list = ['python', 'java', 'c++', 'html', 'css',
                   'javascript', 'react', 'node.js', 'sql', 'mongodb']
    text = text.lower()
    found_skills = [skill for skill in skills_list if skill in text]

    return {
        "email": email[0] if email else None,
        "phone": phone[0] if phone else None,
        "skills": found_skills
    }

# API endpoint
@app.get("/api/parse-resume")
def parse_resume_from_url(pdf_url: str = Query(..., description="Public PDF resume URL")):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()

        doc = fitz.open(stream=response.content, filetype="pdf")
        text = "".join(page.get_text() for page in doc)
        doc.close()

        return {
            "status": "success",
            "parsed_data": parse_resume(text)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Local dev runner
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
