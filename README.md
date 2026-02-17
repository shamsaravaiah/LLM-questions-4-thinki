# LLM-questions-4-thinki

FastAPI server for generating educational questions using Google's Gemini LLM for the Thinki educational application.

## Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

4. **Get a Gemini API Key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file

## Running the Server

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The server will start on `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /health` - Check if the server is running

### Generate English Questions
- `POST /api/english/generate`
- Request body:
  ```json
  {
    "action": "generate",
    "year_band": "Y5",
    "subject": "English",
    "count": 3,
    "ema": 0.65,
    "context": {
      "age": 10,
      "onboarding_english_score": 75,
      "language": "en"
    }
  }
  ```

### Generate Math Questions
- `POST /api/math/generate`
- Request body:
  ```json
  {
    "action": "generate",
    "year_band": "Y5",
    "subject": "Math",
    "count": 3,
    "ema": 0.65,
    "context": {
      "age": 10,
      "onboarding_math_score": 75,
      "language": "en"
    }
  }
  ```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Response

```json
{
  "success": true,
  "questions": [
    {
      "id": "1",
      "question": "What is the capital of France?",
      "type": "multiple_choice",
      "options": ["London", "Paris", "Berlin", "Madrid"],
      "correct_answer": "Paris",
      "difficulty": "medium",
      "explanation": "Paris is the capital city of France."
    }
  ],
  "message": "Successfully generated 3 English questions"
}
```
