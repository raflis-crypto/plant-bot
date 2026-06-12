import os
from groq import AsyncGroq

MODEL = "llama-3.3-70b-versatile"


def _client() -> AsyncGroq:
    return AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

DISCLAIMER = (
    "\n\n⚠️ Информация носит справочный характер. "
    "Перед применением проконсультируйтесь со специалистом."
)


async def get_info(name: str) -> str:
    prompt = (
        f"Напиши краткую справку о растении «{name}»: "
        "описание, ареал, польза и возможная опасность. "
        "Ответ — 3-4 абзаца на русском языке."
    )
    chat = await _client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=800,
    )
    return chat.choices[0].message.content + DISCLAIMER


async def get_recipe(name: str, condition: str) -> str:
    prompt = (
        f"Составь народный рецепт на основе растения «{name}» "
        f"при состоянии: {condition}. "
        "Укажи ингредиенты, способ приготовления и дозировку. "
        "Ответ — на русском языке."
    )
    chat = await _client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=600,
    )
    return chat.choices[0].message.content + DISCLAIMER
