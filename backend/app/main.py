from fastapi import FastAPI

app = FastAPI(title="InsightAI")

@app.get("/")
def root():
    return {"message": "InsightAI API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}