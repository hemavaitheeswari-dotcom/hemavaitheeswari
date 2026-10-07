import os
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google import genai
from dotenv import load_dotenv

# Automatically load environment variables from the local .env file
load_dotenv()

app = FastAPI(title="EduGenie: Learning Assistant")

# Configure Static files and Templates directories
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Warning: GEMINI_API_KEY environment variable not found in your .env file.")

def generate_gemini_content(prompt: str) -> str:
    """Helper function to run inference via Google Gemini API."""
    if not os.getenv("GEMINI_API_KEY"):
        return "Error: Gemini API Key is missing. Please check your `.env` configuration file."
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while communicating with the AI: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None, "mode": None, "input_text": None})

@app.post("/action", response_class=HTMLResponse)
async def handle_action(
    request: Request, 
    mode: str = Form(...), 
    input_text: str = Form(...)
):
    prompt = ""
    
    if mode == "ask":
        prompt = f"Answer the following educational question in a smart, concise, and clear manner:\n\n{input_text}"
    elif mode == "simplify":
        prompt = f"Explain the following complex concept in very simple terms suitable for a student laying out foundational intuitive steps:\n\n{input_text}"
    elif mode == "quiz":
        prompt = f"Generate a short multi-question educational quiz with answers based on the following topic or text to test user understanding:\n\n{input_text}"
    elif mode == "recommend":
        prompt = f"Act as an educational advisor. Generate a highly structured learning path with beginner to advanced topics, timelines, and study suggestions for:\n\n{input_text}"
    elif mode == "summarize":
        prompt = f"Provide a comprehensive yet concise summary of the following educational passage highlighting key takeaways:\n\n{input_text}"
    else:
        raise HTTPException(status_code=400, detail="Invalid operation mode selected.")

    ai_response = generate_gemini_content(prompt)
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "result": ai_response, 
        "mode": mode,
        "input_text": input_text
    })
