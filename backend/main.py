import csv
import json
from datetime import datetime
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
import os
from dotenv import load_dotenv



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key = GEMINI_API_KEY)
chat = client.aio.chats.create(model = "gemini-2.5-pro-exp-03-25")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MenuRequest(BaseModel):
    dietary_restrictions: list[str]
    day: str
    meal_time: str
    max_calories: int | None = None

class MenuResponse(BaseModel):
    menu_items: list[dict]
    recommendations: str
    date: str
    total_calories: int

def read_menu_csv(path: str = "menu2.csv") -> dict:
    """
    Load the CSV that the scraper produced and return a nested
    dict  →  {day → {meal_time → recipe_dict}}
    """
    try:
        logger.info("Reading menu from CSV…")
        menu_data: dict[str, dict[str, dict]] = {}

        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for row in reader:
                day        = row["Day"].strip()
                meal_time  = row["Meal Time"].strip().title()
                recipes    = json.loads(row["Recipe Dict"])

                # 2.  build {day → {meal_time → recipes}}
                menu_data.setdefault(day, {})[meal_time] = recipes

        logger.info("Loaded %d days from %s", len(menu_data), path)
        return menu_data

    except Exception as exc:
        logger.exception("Error reading menu CSV")
        raise HTTPException(status_code=400,
                            detail=f"Error reading menu CSV: {exc}")

@app.post("/analyze-menu", response_model=MenuResponse)
async def analyze_menu(request: MenuRequest):
    try:
        logger.info(f"Received request with dietary restrictions: {request.dietary_restrictions}")
        logger.info(f"Selected day: {request.day}")
        logger.info(f"Selected meal time: {request.meal_time}")
        logger.info(f"Max calories: {request.max_calories}")

        menu_data = read_menu_csv()
        
        if not menu_data:
            logger.error("No menu data found")
            raise HTTPException(status_code=400, detail="No menu data found")
 
        if request.day not in menu_data or request.meal_time not in menu_data[request.day]:
            raise HTTPException(status_code=400, detail=f"No menu data found for {request.day} {request.meal_time}")
            
        menu_items = menu_data[request.day][request.meal_time]
        
        menu_content = "\n".join([
            f"Item: {item_name}\n"
            f"Description: {item_desc}\n"
            for item_name, item_desc in menu_items.items()
        ])

        calorie_instruction = ""
        if request.max_calories:
            calorie_instruction = f"\nMaximum calories allowed: {request.max_calories}\nPlease ensure the sum of the calories of the recommended items do not exceed this limit."

        prompt = f"""Given the following menu items and dietary restrictions, analyze each item and list only the items that are safe to eat.
Consider both common dietary restrictions and any specific custom restrictions provided.

Menu Items:
{menu_content}

Dietary Restrictions:
{', '.join(request.dietary_restrictions)}
{calorie_instruction}

Please analyze each menu item considering:
1. Common dietary restrictions (vegetarian, vegan, gluten-free, etc.)
2. Allergens and ingredients
3. Any specific custom restrictions provided
4. Caloric content and limits

For each safe item, provide only the item name and its caloric content.
Format your response as:
Item Name (Calories: X)

Only include items that are safe to eat based on ALL the provided restrictions.
Before sending the response, make sure to check if the total calories of the recommended items do not exceed the maximum calories allowed.
If they do, construct a new response that contains all the important food nutrient that humans needs and does NOT exceed the maximum calories allowed. 
Also return the response in above format only do not add any more text or comments."""


        
        response = await chat.send_message(prompt)

        if not response or not response.text:
            logger.error("No response from Gemini")
            raise HTTPException(status_code=500, detail="No response from Gemini")
        response_text = response.text
        logger.info(f"Response from Gemini: {response_text}")
        
        safe_items = [
            {"name": line.strip()}
            for line in response_text.split('\n')
            if line.strip()
        ]
        
        return MenuResponse(
            menu_items=safe_items,
            recommendations=response_text,
            date=request.day,
            total_calories=0
        )
        
    except Exception as e:
        logger.error(f"Error analyzing menu: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/available-days")
async def get_available_days():
    try:
        menu_data = read_menu_csv()
        days = sorted(list(menu_data.keys()))
        return {"days": days}
    except Exception as e:
        logger.error(f"Error getting available days: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 