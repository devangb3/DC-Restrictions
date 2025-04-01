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
import pathlib


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
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

class MenuResponse(BaseModel):
    menu_items: list[dict]
    recommendations: str
    date: str

def read_menu_csv():
    try:
        logger.info("Reading menu from CSV...")
        menu_data = {}
        
        with open('backend/menu.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                day = row['Day']
                meal_time = row['Meal Time']
                recipe_dict = json.loads(row['Recipe Dict'])
                
                if day not in menu_data:
                    menu_data[day] = {}
                menu_data[day][meal_time] = recipe_dict
                
        logger.info(f"Successfully read menu data for {len(menu_data)} days")
        return menu_data
        
    except Exception as e:
        logger.error(f"Error reading menu CSV: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Error reading menu CSV: {str(e)}")

@app.post("/analyze-menu", response_model=MenuResponse)
async def analyze_menu(request: MenuRequest):
    try:
        logger.info(f"Received request with dietary restrictions: {request.dietary_restrictions}")
        logger.info(f"Selected day: {request.day}")
        logger.info(f"Selected meal time: {request.meal_time}")
        
        # Read menu data
        menu_data = read_menu_csv()
        
        if not menu_data:
            logger.error("No menu data found")
            raise HTTPException(status_code=400, detail="No menu data found")
        
        # Get menu items for selected day and meal time
        if request.day not in menu_data or request.meal_time not in menu_data[request.day]:
            raise HTTPException(status_code=400, detail=f"No menu data found for {request.day} {request.meal_time}")
            
        menu_items = menu_data[request.day][request.meal_time]
        
        # Prepare menu content for Gemini
        menu_content = "\n".join([
            f"Item: {item_name}\n"
            f"Description: {item_desc}\n"
            for item_name, item_desc in menu_items.items()
        ])
        
        # Prepare prompt for Gemini
        prompt = f"""Given the following menu items and dietary restrictions, list only the items that are safe to eat.

Menu Items:
{menu_content}

Dietary Restrictions:
{', '.join(request.dietary_restrictions)}

Please list only the names of the safe items, one per line."""

        # Get response from Gemini
        response = await chat.send_message(prompt)
        response_text = response.text
        logger.info(f"Response from Gemini: {response_text}")
        # Parse the response into a list of safe items
        safe_items = [{"name": item.strip()} for item in response_text.split('\n') if item.strip()]
        
        return MenuResponse(
            menu_items=safe_items,
            recommendations=response_text,
            date=request.day
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