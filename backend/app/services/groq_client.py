from groq import Groq
from app.config import settings


def ask_groq(question: str) -> str:
    client = Groq(api_key=settings.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content or ""