from fastapi import Depends, FastAPI, File, UploadFile, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import fitz  # PyMuPDF
import re
import json
import httpx
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = FastAPI()

# Allow CORS for testing with frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_api_key(x_api_key: str = Header(...)):
    PROJECT_KEY = os.getenv("PROJECT_KEY")
    if x_api_key != PROJECT_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

def load_skill_variants(file_path="skills.txt") -> dict:
    """
    Returns a dict where keys are canonical skill names (e.g. "aws")
    and values are lists of variations.
    """
    skill_map = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            if ':' in line:
                canonical, *variants = line.strip().split(":")
                if variants:
                    variant_list = [v.strip().lower() for v in variants[0].split(",")]
                    skill_map[canonical.strip().lower()] = variant_list
            else:
                skill = line.strip().lower()
                skill_map[skill] = [skill]
    return skill_map

def extract_skills(text: str, skill_map: dict) -> list:
    found_skills = set()
    text_lower = text.lower()

    for canonical, variants in skill_map.items():
        for variant in variants:
            # use word boundaries and escaping for special characters
            pattern = r'\b' + re.escape(variant) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(canonical)
                break  # no need to check other variants

    return list(found_skills)

# Dummy function to extract text from PDF
def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Very simple regex-based resume parser
def parse_resume(text: str) -> Dict:
    name_match = re.search(r"(?i)([A-Z][a-z]+\s[A-Z][a-z]+)", text)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    skill_map = load_skill_variants("skills.txt")
    skills = extract_skills(text, skill_map)

    return {
        "name": name_match.group() if name_match else None,
        "email": email_match.group() if email_match else None,
        "skills": list(set(skills))
    }

@app.post("/parse")
async def parse_resume_endpoint(file: UploadFile = File(...), _: str = Depends(verify_api_key)):
    contents = await file.read()
    text = extract_text_from_pdf(contents)
    parsed = parse_resume(text)
    return parsed

@app.post("/extract-experience")
async def extract_experience(file: UploadFile = File(...), _: str = Depends(verify_api_key)):
    contents = await file.read()
    text = extract_text_from_pdf(contents)
    API_KEY = os.getenv("API_KEY")
    try:
        response = httpx.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "mistralai/mistral-small-3.1-24b-instruct:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an AI resume parser that extracts and summarizes professional experience into structured JSON format. Only extract relevant experience such as job titles, companies, durations, and concise bullet points of responsibilities or achievements.\n\nOutput the result in the following JSON format:\n\n{\n\"experiences\": [\n    {\n    \"job_title\": \"\",\n    \"company\": \"\",\n    \"location\": \"\",\n    \"start_date\": \"\",\n    \"end_date\": \"\",\n    \"bullets\": [\"\", \"\", ...]\n    }\n]\n}"
                    },
                    {
                        "role": "user",
                        "content": f"Extract the experience section from this resume and format it into JSON as instructed:\n{text}"
                    }
                ],
            }),
            timeout=15.0
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logging.error(f"HTTP error: {exc.response.status_code} - {exc.response.text}")
        raise HTTPException(status_code=exc.response.status_code, detail="External API error")
    except httpx.RequestError as exc:
        logging.error(f"Request error: {str(exc)}")
        raise HTTPException(status_code=503, detail="Unable to reach the language model API")

    try:
        raw_output = response.json()["choices"][0]["message"]["content"]
        cleaned = raw_output.strip("```json\n").strip("```")
        parsed = json.loads(cleaned)
    except (KeyError, json.JSONDecodeError) as e:
        logging.warning(f"Failed to parse model output: {e}")
        return {
            "experiences": [],
            "warning": "Failed to parse structured data from the model output. Please try again later or with a different resume."
        }
    return parsed