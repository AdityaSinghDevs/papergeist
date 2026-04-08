from groq import Groq
from utils.env_loader import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def summarize(text):
    prompt = f"""
Summarize this research paper in 3 concise bullet points:
{text[:1500]}
"""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a research assistant who summarizes papers clearly and concisely."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        print("Groq error:", e)
        return "Summary unavailable"