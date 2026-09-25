import json
import google as genai
from google.genai import types
from app.schemas.recipe_schema import RecipeCreate
from app.core.config import settings

# API KEY
client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def generate_recipe_ai(ingredients: list[str],
                             style: str = "home cooking",
                             diet_type: str | None = None,
                             language: str = "en",
                             creativity: float = 0.2
                             ) -> RecipeCreate:
    ingredients_str = ", ".join(ingredients)

    style_condition = f"The dish must follow this style: '{style}'." if style else ""
    diet_condition = f"The dish must strictly adhere to this diet: '{diet_type}.'" if diet_type else ""

    prompt = f"""
    You are an expert chef. Recommend exactly One recipe that best utilizes the following ingredients: {ingredients_str}.
    
    [Additional Requirements]
    {style_condition}
    {diet_condition}
    
    [Language & Output Format Requirements]
    - All JSON Keys MUST reamin in English.
    - All JSON Values (title, description, instructions, ets.) MUST be written in the language corresponding to this language code: '{language}'.
    - Do NOT include any explanations, greetings, or markdown formatting (like ```json). Return ONLY a raw JSON object.
    
    {{
        "title": "Recipe Name",
        "description": "Brief description of the dish",
        "instructions": "1. First step\n2. Second step",
        "cooking_time": 30,
        "difficulty": "Medium"
    }}
    """

    # call async
    response = await client.aio.models.generate_content(
        model='genemi-1.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=creativity, # 0~1.0 : close to 1,0, more varied and creative
        )
    )
    
    recipe_dict = json.loads(response.text)
    recipe_dict["language"] = language
    
    return RecipeCreate(**recipe_dict)