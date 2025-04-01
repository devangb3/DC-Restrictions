# Restaurant Menu Dietary Restrictions Analyzer

This application helps users analyze restaurant menus based on their dietary restrictions using AI.

## Setup Instructions

### Backend Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

4. Run the backend server:
```bash
cd backend
uvicorn main:app --reload
```

### Frontend Setup
1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm start
```

## Features
- URL-based menu scraping
- Dietary restriction analysis
- AI-powered menu recommendations
- Interactive user interface 