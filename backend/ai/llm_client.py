import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(context: str, question: str):

    prompt = f"""
    You are an AI platform assistant.

    Answer the user's question using the data provided.

    Be clear, concise, and actionable.

    Question:
    {question}

    Data:
    {context}

    If the question is about commits:
    → Mention author, message, and time

    If about workflows:
    → Mention status, success/failure, and link

    Provide a helpful summary.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content