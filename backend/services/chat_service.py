from groq import Groq
from backend.core.config import GROQ_API_KEY
from typing import List, Dict
import os
import dotenv
dotenv.load_dotenv()

text_gen_model = os.getenv('TEXT_GEN_MODEL')


class ChatService:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)

    async def generate_answer(
            self,
            context: str,
            query: str,
            model: str = text_gen_model
    ) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an advanced AI assistant designed to deliver accurate, detailed, "
                               "and well-structured responses."
                               "Your goal is to ensure clarity, precision, and relevance in every answer."
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\n"
                               f"Question:\n{query}\n\n"
                               f"Craft a comprehensive and structured response that directly addresses the question, "
                               f"fully utilizing the provided context."
                }
            ]
        )
        return response.choices[0].message.content
