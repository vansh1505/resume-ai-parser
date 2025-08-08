import json
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import google.generativeai as genai
import requests
import os
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

load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))


# API endpoint
@app.get("/api/parse-resume")
def parse_resume_from_url(pdf_url: str = Query(..., description="Public PDF resume URL")):
    try:
        response = requests.get(pdf_url)
        response.raise_for_status()

        doc = fitz.open(stream=response.content, filetype="pdf")
        text = "".join(page.get_text() for page in doc)
        doc.close()

        prompt = f"""
            You are a resume evaluator.
            Task:
            1. Decide if the resume is appropriate for general professional use. Output only True or False.
            2. Score the resume from 0 to 100.
            3. Extract all technical skills.
            4. Rank the resume quality as: Best, Average, or Needs Improvement.
            5. Suggest 3 improvements.
            Return ONLY valid JSON, nothing else.
            Return JSON:
                {{
                  "appropriate": true or false,
                  "score": 0-100,
                  "skills": ["Python", "FastAPI", "Machine Learning" ...],
                  "rank": ["Best","Average", "Needs Improvement"],
                  "improvements": ["Add more project details", "Include a summary section", "Quantify achievements"]
                }}
            Resume text:
            {text}
            """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        raw_response = response.candidates[0].content.parts[0].text

        cleaned_text = re.sub(r"```(?:json)?", "", raw_response).strip()

        # Extract only JSON object from messy output
        match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in AI output")

        parsed_json = json.loads(match.group(0))


        return {
            "status": "success",
            "parsed_data": parsed_json,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def root():
    return {"message": "Resume Parser API running"}

# Local dev runner
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Fallback to 8000 if PORT not set
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)