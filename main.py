import json
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import google.generativeai as genai
import requests
import os
import re
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Allowed CORS origins
origins = ["https://uniplace.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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



class Education(BaseModel):
    degree: str
    branch: Optional[str]
    institution: str
    year: str
    cgpa: str

class Experience(BaseModel):
    role: Optional[str]
    company: Optional[str]
    duration: Optional[str]
    description: Optional[str]

class Project(BaseModel):
    name: str
    description: Optional[str]
    tech: Optional[str]

class ResumeRequest(BaseModel):
    fullName: str
    email: str
    phone: str
    location: str
    education: List[Education]
    experience: Optional[List[Experience]]
    projects: Optional[List[Project]]
    skills: Optional[List[str]]




@app.post("/api/ai-resume-builder")
def ai_resume_builder(request: ResumeRequest):
        try:
            # Structure the data similar to the provided format
            updatedResumeData = {
            "fullName": request.fullName,
            "email": request.email,
            "phone": request.phone,
            "location": request.location,
            "education": [edu.dict() for edu in request.education],
            "experience": [exp.dict() for exp in request.experience] if request.experience else [],
            "projects": [proj.dict() for proj in request.projects] if request.projects else [],
            "skills": [s.strip() for s in request.skills] if request.skills else []
        }
            
            # Clean up skills by trimming whitespace
            updatedResumeData["skills"] = [s.strip() for s in updatedResumeData["skills"]]
            
            prompt = f"""
            You are an expert ATS-optimized resume writer. Create the best possible resume content that will score 100% in ATS systems.

            Resume Data:
            {json.dumps(updatedResumeData, indent=2)}

            Generate a complete ATS-optimized resume with these sections:
            1. Professional Summary (2-3 lines, keyword-rich)
            2. Technical Skills (categorized)
            3. Projects (enhanced with impact metrics, technical details)
            4. Work Experience (if provided, with quantified achievements)
            5. Education
            6. Additional sections if relevant (certifications, achievements)

            Requirements:
            - Use strong action verbs
            - Include quantified achievements where possible
            - Optimize for ATS keywords based on the provided experience and projects
            - Make each project description compelling with technical depth
            - Ensure professional formatting
            - Include relevant metrics and impact statements

            Return ONLY valid JSON format:
            {{
              "summary": "Professional summary paragraph",
              "technical_skills": {{
                "programming_languages": ["Python", "JavaScript"],
                "frameworks": ["React", "Django"],
                "tools": ["Git", "Docker"],
                "databases": ["MySQL", "MongoDB"]
              }},
              "projects": [
                {{
                  "name": "Project Name",
                  "tech_stack": ["React", "Node.js"],
                  "description": "Enhanced ATS-optimized description with metrics",
                  "highlights": ["Improved performance by 40%", "Reduced load time by 60%"]
                }}
              ],
              "experience": [
                {{
                  "company": "Company Name",
                  "position": "Job Title",
                  "duration": "Jan 2023 - Present",
                  "responsibilities": ["Responsibility with metrics", "Another achievement"]
                }}
              ],
              "education": "Enhanced education section",
              "additional_sections": {{
                "certifications": ["AWS Certified"],
                "achievements": ["Achievement 1"]
              }}
            }}
            """

            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            raw_response = response.candidates[0].content.parts[0].text

            cleaned_text = re.sub(r"```(?:json)?", "", raw_response).strip()
            
            # Extract JSON object
            match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
            if not match:
                raise ValueError("No JSON object found in AI output")

            parsed_json = json.loads(match.group(0))

            return {
                "status": "success",
                "resume_content": parsed_json,
                "input_data": updatedResumeData,
                "message": "ATS-optimized resume content generated successfully"
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def root():
    return {"message": "Resume Parser API running"}

# Local dev runner
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
