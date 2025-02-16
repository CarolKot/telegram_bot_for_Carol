# generate.py

from openai import AsyncOpenAI
from config import AI_TOKEN
client = AsyncOpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key= AI_TOKEN,
)

history = {}

async def ai_generate(text:str):
 completion = await client.chat.completions.create(
   model="deepseek/deepseek-chat",
   messages=[
     {
       "role": "user",
       "content": text
     }
   ]
 )
 print(completion)
 return completion.choices[0].message.content

async def ai_genetate(user_id: int, text: str):
  if user_id not in history:
    history[user_id] = []

  history[user_id].append({"role": "user", "content": text})

  completion = await client.chat.completions.create(
        model="deepseek/deepseek-chat",
        messages=history[user_id]
    )

  response_text = completion.choices[0].message.content
  history[user_id].append({"role": "assistant", "content": response_text})

  return response_text