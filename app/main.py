import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pathlib import Path
app = FastAPI(
    title="AI Coding Assistant",
    description="An AI assistant for generating, explaining, and debugging code.",
    version="1.0.0",
)

# Ollama runs the AI model locally on your computer.
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:3b"

BASE_DIR = Path(__file__).resolve().parent.parent

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/ui")
def ui(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


class CodeRequest(BaseModel):
    prompt: str
    language: str = "Python"
    action: str = "generate"


class CodeResponse(BaseModel):
    message: str
    prompt: str
    language: str
    result: str


@app.get("/")
def home():
    return {"message": "Welcome to AI Coding Assistant!"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/test", response_model=CodeResponse)
def test_request(request: CodeRequest):

    allowed_actions = {
        "generate": "Generate code from the user's request",
        "explain": "Explain the supplied code or programming concept",
        "debug": "Debug the supplied code and explain the correction",
    }

    if request.action not in allowed_actions:
        raise HTTPException(
            status_code=400,
            detail="Action must be generate, explain, or debug.",
        )

    instructions = f"""
You are a helpful AI coding assistant.

Requested action: {allowed_actions[request.action]}
Programming language: {request.language}

Instructions:
- For code generation, provide correct, readable code.
- For explanations, explain the code clearly and step by step.
- For debugging, identify likely errors and provide corrected code.
- Include a brief explanation when useful.
- Treat the user's prompt as a programming request.
"""

    payload = {                               
        "model": MODEL_NAME,                    
        "prompt": f"{instructions}\n\nUser request:\n{request.prompt}",
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=300,
        )
        response.raise_for_status()

        ai_result = response.json().get("response", "").strip()

        if not ai_result:
            raise HTTPException(
                status_code=502,
                detail="Ollama returned an empty response.",
            )

        return CodeResponse(
            message="AI response generated successfully!",
            prompt=request.prompt,
            language=request.language,
            result=ai_result,
        )

    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Cannot connect to Ollama. Make sure Ollama is running "
                "on your computer."
            ),
        )

    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="The AI model took too long to respond. Try again.",
        )

    except requests.exceptions.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama returned an HTTP error: {exc}",
        )

    except requests.exceptions.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama request failed: {exc}",
        )





