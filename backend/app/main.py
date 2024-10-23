import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .routes import router

# Load environment variables from .env file
load_dotenv()

def _set_env(var: str):
    if not os.environ.get(var):
        raise EnvironmentError(f"Environment variable {var} is not set.")
# Ensure the ANTHROPIC_API_KEY is set
_set_env("ANTHROPIC_API_KEY")
_set_env("TAVILY_API_KEY")

print("API Key from outside the func:", os.environ.get("ANTHROPIC_API_KEY"))
print("Tavily API Key from outside the func:", os.environ.get("TAVILY_API_KEY"))


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)
