"""
The backend: a small FastAPI service that analyzes ONE customer review.

Use any one option to run:
    fastapi dev src/api/fastapi_api.py
    python -m fastapi dev src/api/fastapi_api.py
    uv run fastapi dev src/api/fastapi_api.py

Then the Streamlit app (streamlit_app.py) will call this service for every review.
"""

import os
from functools import lru_cache
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
app = FastAPI(title="Customer Feedback Analyzer", version="1.0")


@lru_cache
def get_genai_client() -> genai.Client:
    return genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# Welcome message 
@app.get("/")
def home():
    return {"message": "Welcome To Customer Review API"}


@app.get("/health")
def health():
    """Report service readiness without exposing configuration values."""
    configured = bool(os.getenv("GOOGLE_API_KEY"))
    return {"status": "ready" if configured else "degraded", "api_key_configured": configured}


# What the caller must SEND us
class Review(BaseModel):
    text: str = Field(min_length=1, max_length=5000)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Review text must not be blank.")
        return value


# What Gemini gives back, and what we SEND to the caller.
# We keep it small on purpose -> fewer tokens used.
class Analysis(BaseModel):
    label: Literal["positive", "negative", "neutral"]
    score: int = Field(ge=1, le=5)
    theme: str = Field(pattern=r"^[a-z][a-z0-9_-]*$")
    suggestion: str


@app.post("/analyze", response_model=Analysis)
def analyze(review: Review):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="GOOGLE_API_KEY is not configured.")

    try:
        response = get_genai_client().models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=(
                "Analyze this customer review.\n"
                "label must be 'positive', 'negative', or 'neutral'.\n"
                "score must be a number from 1 (very bad) to 5 (very good).\n"
                "theme must be ONE lowercase word for the main topic "
                "(for example: delivery, taste, price, service, quality).\n"
                "For a negative review, suggestion must be ONE concise line with an "
                "actionable way the business could address the issue. "
                "For positive or neutral reviews, suggestion must be an empty string.\n"
                f"Review: {review.text}"
            ),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Analysis,
            ),
        )
        if response.parsed is None:
            raise HTTPException(status_code=502, detail="The model returned no structured result.")
        return response.parsed
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail="The analysis service is unavailable.") from exc
