import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent.parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are an AI platform assistant for PlatformIQ.
Answer the user's question using the data provided. Be clear, concise, and actionable.
If the question is about commits, mention author, message, and time.
If about workflows, mention status, success/failure, and link.
Format your responses using markdown for readability."""


def _build_messages(context: str, question: str, history: list = None) -> list:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": f"Question: {question}\n\nData:\n{context}"})
    return messages


def generate_response(context: str, question: str, history: list = None) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=_build_messages(context, question, history)
    )
    return response.choices[0].message.content


def stream_response(context: str, question: str, history: list = None):
    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=_build_messages(context, question, history),
        stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
