import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from typing import List

class LLM:
    def __init__(self, api_key: str = None, model_name: str = "gpt-4o"):
        self.model_name = model_name

    def chat_completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        try:
            response = client.chat.completions.create(model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature)
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error during OpenAI ChatCompletion: {str(e)}"

    def get_embedding(self, text: str, engine: str = "text-embedding-ada-002") -> List[float]:
        try:
            response = client.embeddings.create(input=[text],
            model=engine)
            embedding = response.data[0].embedding
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
