import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("NEBIUS_API_KEY")

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=api_key,
)

SYSTEM_PROMPT = (
    "You are a senior software engineer who analyses GitHub repositories. "
    "You return only valid JSON with no markdown formatting, no code fences, and no explanation. "
    "Your JSON must always contain exactly the fields: summary, technologies, structure."
)


def call_llm(prompt: str) -> str:

    response = client.chat.completions.create(
        model="moonshotai/Kimi-K2.5",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    return response.choices[0].message.content
