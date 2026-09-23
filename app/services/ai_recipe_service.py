import json
import google as genai
from google.genai import types
from app.schemas.recipe_schema import RecipeCreate
from app.core.config import settings

# API KEY
client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def generate_recipe_from_ai(ingredients: list[str]) -> RecipeCreate:
    ingredients_str = ", ".join(ingredients)
    
    # prompt = f"""
    #     당신은 전문 요리사입니다. 다음 제공된 식재료({ingredients_str})를 가장 잘 활용할 수 있는 레시피를 하나 추천해주세요.
    #     반드시 아래 JSON 형식의 키값에 맞추어 응답해야 하며, 설명이나 마크다운 기호(```json)는 절대 포함하지 마세요.
    #     {{
    #         "title": "레시피 이름",
    #         "description": "간단한 요리 설명",
    #         "instructions": "1. 첫번째 순서\n2. 두번째 순서",
    #         "cooking_time": 30,
    #         "difficulty": "보통"
    #     }}
    # """
    
    prompt = f"""
    {{
        "title": "Recipe Name",
        "description": "Explain Simple Cook",
        "instructions": "1. first step\n 2. second step",
        "cooking_time": 30,
        "difficulty": "moderate"
    }}
    """

    # call async
    response = await client.aio.models.generate_content(
        model='genemi-1.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.7,
        )
    )
    
    recipe_dict = json.load(response.text)
    
    return RecipeCreate(**recipe_dict)