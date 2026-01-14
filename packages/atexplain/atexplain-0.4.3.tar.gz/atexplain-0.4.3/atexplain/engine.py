from openai import OpenAI

# 🔑 ВСТАВЬ СВОЙ КЛЮЧ СЮДА
API_KEY = "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"

client = OpenAI(api_key=API_KEY)


def explain_code(code: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Ты объясняешь Python-код простым и понятным языком, как учитель."
            },
            {
                "role": "user",
                "content": f"Объясни этот Python-код:\n\n{code}"
            }
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content
