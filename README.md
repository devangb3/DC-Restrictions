# DC-Restrictions: Dining Commons Menu Analyzer

A web application that helps UC Davis students analyze Tercero Dining Commons menu items based on their dietary restrictions and preferences. The application uses AI to provide personalized menu recommendations while considering dietary restrictions, allergies, and caloric requirements.

## Features

- **Menu Analysis**: Analyzes dining commons menu items based on user-specified dietary restrictions
- **Customizable Dietary Preferences**: Supports common restrictions (vegetarian, vegan, gluten-free, etc.) and custom restrictions
- **Calorie Tracking**: Option to set maximum calorie limits for meal recommendations
- **Day and Meal Selection**: Browse menu items by specific days and meal times (Breakfast, Lunch, Dinner)
- **AI-Powered Recommendations**: Uses Google's Gemini AI to analyze menu items and provide safe recommendations
- **Real-time Analysis**: Instant feedback on safe menu items based on your restrictions
- **Interactive UI**: User-friendly interface built with React and Material-UI

## Tech Stack

### Backend
- FastAPI (Python web framework)
- Google Gemini AI API for menu analysis
- BeautifulSoup4 for menu data extraction
- uvicorn ASGI server

### Frontend
- React.js
- Material-UI components
- Axios for API communication

## Installation

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- npm (Node Package Manager)
- Google Gemini API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file in the backend directory:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

5. Start the backend server:
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install frontend dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will be available at http://localhost:3000

## Usage

1. Select a day and meal time (Breakfast, Lunch, or Dinner)
2. Choose your dietary restrictions from the predefined options
3. Add any custom dietary restrictions if needed
4. Optionally set a maximum calorie limit
5. Click "Analyze Menu" to get personalized recommendations
6. View the safe menu items based on your preferences

## API Endpoints

### GET /available-days
- Returns a list of available days with menu data

### POST /analyze-menu
- Analyzes menu items based on provided restrictions
- Request body:
  ```json
  {
    "dietary_restrictions": ["string"],
    "day": "string",
    "meal_time": "string",
    "max_calories": "number" (optional)
  }
  ```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- UC Davis Dining Services for menu data
- Google Gemini AI for menu analysis capabilities
- Material-UI for the component library