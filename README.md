# 🧠 AI Resume Parser

AI Resume Parser is a FastAPI-based backend service that extracts structured work experience from resumes using advanced natural language processing. Built to serve as a microservice for the [PortFlow](https://github.com/ShawnN24/PortFlow) app, it converts uploaded resumes into a JSON format that can be consumed by frontends or other services.

---

## 🚀 Features

- 📄 Accepts resume files (`.pdf`) via POST requests  
- 🤖 Parses job titles, companies, dates, and descriptions using LLMs (Mistral AI)  
- 🧼 Handles and sanitizes messy or unstructured resume data  
- 🌐 FastAPI-based RESTful API  
- 🛡️ Handles errors gracefully with fallback responses  
- 🔐 Secure API key usage via environment variables  

---

## 🛠️ Tech Stack

- **Python**
- **FastAPI** – Web framework  
- **Uvicorn** – ASGI server    
- **Mistral AI** – For language-based parsing 
- **python-docx**, **PyMuPDF** – Resume file handling  

---

## 📦 Installation

1. **Clone the repository:**

```bash
git clone https://github.com/ShawnN24/AI-Resume-Parser.git
cd AI-Resume-Parser
```

2. **Create a virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Set up your environment variables:**

```bash
API_KEY="YOUR_OPENROUTER_API_KEY"
PROJECT_KEY="WRITE_YOUR_OWN_KEY_HERE"
```

## 🧪 Running Locally

```bash
uvicorn app.main:app --reload
```

## 📤 API Endpoint

### POST /parse

Form Data:
file: Resume file (.pdf)

Example Response (on success):
```json
{
  "name": "Example Name",
  "email": "example@gmail.com",
  "skills": [
    "javascript",
    "googlecloud",
    "python",
    "amazonwebservices",
    "github",
    "react"
  ]
}
```

### POST /extract-experience

Form Data:
file: Resume file (.pdf)

Example Response (on success):
```json
{
  "experience": [
    {
      "job_title": "Full Stack Example Intern",
      "company": "Example Inc.",
      "location": "Remote",
      "start_date": "Jan 2025",
      "end_date": "Current",
      "bullets": [
        "Developing an AI Resume Parser using python, FastAPI, Uvicorn, and Mistral AI",
        "Designed a web app to auto generate portfolio websites given a Github profile and a Resume"
      ]
    }
  ]
}
```
