import openai
import instructor
from pydantic import BaseModel
from typing import List

# Patch OpenAI client to use instructor
client = instructor.from_openai(openai.OpenAI())

class ColoringIdeas(BaseModel):
    ideas: List[str]

def generate_coloring_ideas(topic: str, count: int, api_key: str) -> List[str]:
    openai.api_key = api_key

    prompt = (
        f"Generate a list of {count} fun and creative ideas for a children's coloring book. "
        f"The theme is '{topic}'. Each idea should be a short phrase describing a scene or object, "
        f"suitable for a coloring book (e.g., 'A monkey swinging on vines'). Keep the language simple and fun."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_model=ColoringIdeas,
    )

    return response.ideas
