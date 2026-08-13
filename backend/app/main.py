from fastapi import FastAPI

from app.config import settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.groq_client import ask_groq


app = FastAPI(title="InsightAI")


@app.get("/")
def root():
    return {"message": "InsightAI API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = ask_groq(request.question)
    return {"answer": answer}