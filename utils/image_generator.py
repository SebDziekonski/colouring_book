import openai
from typing import List

def generate_images(ideas: List[str], api_key: str) -> List[str]:
    openai.api_key = api_key
    image_urls = []

    for idea in ideas:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=f"{idea}, black and white, line art, coloring book style",
            n=1,
            size="1024x1024",
            quality="standard",  # or "hd" if available in your plan
            response_format="url"
        )
        image_url = response.data[0].url
        image_urls.append(image_url)

    return image_urls
