from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Thinki Question Generator API",
    description="API for generating educational questions using Gemini LLM",
    version="1.0.0"
)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-2.5-flash')


# Request/Response Models
class Context(BaseModel):
    """Student context - accepts additional fields dynamically."""
    
    class Config:
        extra = "allow"
    
    age: int
    onboarding_english_score: Optional[int] = None
    onboarding_math_score: Optional[int] = None
    language: str = "en"


class QuestionRequest(BaseModel):
    """Question generation request - accepts additional fields dynamically."""
    
    class Config:
        extra = "allow"
    
    action: str
    year_band: str
    subject: str
    count: int
    ema: float
    context: Context
    template: Optional[str] = None  # Optional custom question template


class QuestionResponse(BaseModel):
    success: bool
    questions: list[Dict[str, Any]]
    message: Optional[str] = None


def format_context_fields(context: Context) -> str:
    """Format context fields dynamically, including any extra fields."""
    context_lines = []
    
    # Standard fields
    context_lines.append(f"- Age: {context.age}")
    
    if hasattr(context, 'onboarding_english_score') and context.onboarding_english_score is not None:
        context_lines.append(f"- Onboarding English Score: {context.onboarding_english_score}")
    
    if hasattr(context, 'onboarding_math_score') and context.onboarding_math_score is not None:
        context_lines.append(f"- Onboarding Math Score: {context.onboarding_math_score}")
    
    if hasattr(context, 'language'):
        context_lines.append(f"- Language: {context.language}")
    
    # Include any additional/extra fields
    context_dict = context.dict(exclude_none=True)
    standard_fields = {'age', 'onboarding_english_score', 'onboarding_math_score', 'language'}
    
    for key, value in context_dict.items():
        if key not in standard_fields:
            # Format the key nicely (e.g., "learning_style" -> "Learning Style")
            formatted_key = key.replace('_', ' ').title()
            context_lines.append(f"- {formatted_key}: {value}")
    
    return "\n".join(context_lines)




def generate_prompt(request: QuestionRequest) -> str:
    """Generate a prompt for the LLM based on the request."""
    # If a custom template is provided, use it
    if request.template:
        # Replace placeholders in the template with actual values
        template = request.template
        
        # Common placeholders
        replacements = {
            '{count}': str(request.count),
            '{subject}': request.subject,
            '{year_band}': str(request.year_band),
            '{ema}': str(request.ema),
            '{age}': str(request.context.age),
            '{language}': request.context.language,
            '{context}': format_context_fields(request.context),
        }
        
        # Add any additional request fields as placeholders
        request_dict = request.dict(exclude_none=True)
        for key, value in request_dict.items():
            if key not in {'action', 'year_band', 'subject', 'count', 'ema', 'context', 'template'}:
                placeholder = f'{{{key}}}'
                if placeholder not in replacements:
                    replacements[placeholder] = str(value)
        
        # Replace all placeholders
        for placeholder, value in replacements.items():
            template = template.replace(placeholder, value)
        
        return template
    
    # Otherwise, use default prompts
    subject_lower = request.subject.lower()
    context_str = format_context_fields(request.context)
    
    if subject_lower == "english":
        prompt = f"""Generate {request.count} age-appropriate English questions for a {request.context.age}-year-old student in year band {request.year_band}.

Context:
{context_str}
- EMA (Expected Mastery Average): {request.ema}

Requirements:
- Questions should be appropriate for year band {request.year_band}
- Difficulty should align with EMA score of {request.ema}
- Questions should match the student's English proficiency level
- Return questions in {request.context.language}

Return a JSON array with {request.count} questions. Each question should have:
- "id": unique identifier
- "question": the question text
- "type": question type (e.g., "multiple_choice", "fill_in_blank",
  "comprehension", etc.)
- "options": array of answer options (if applicable)
- "correct_answer": the correct answer
- "difficulty": difficulty level
- "explanation": brief explanation of the answer

Format the response as valid JSON only, no markdown formatting."""

    elif subject_lower == "math":
        prompt = f"""Generate {request.count} age-appropriate Math questions for a {request.context.age}-year-old student in year band {request.year_band}.

Context:
{context_str}
- EMA (Expected Mastery Average): {request.ema}

Requirements:
- Questions should be appropriate for year band {request.year_band}
- Difficulty should align with EMA score of {request.ema}
- Questions should match the student's math proficiency level
- Return questions in {request.context.language}

Return a JSON array with {request.count} questions. Each question should have:
- "id": unique identifier
- "question": the question text
- "type": question type (e.g., "multiple_choice", "word_problem",
  "calculation", etc.)
- "options": array of answer options (if applicable)
- "correct_answer": the correct answer
- "difficulty": difficulty level
- "explanation": brief explanation of the solution

Format the response as valid JSON only, no markdown formatting."""

    else:
        prompt = f"""Generate {request.count} age-appropriate {request.subject} questions for a {request.context.age}-year-old student in year band {request.year_band}.

Context:
{context_str}
- EMA (Expected Mastery Average): {request.ema}

Return a JSON array with {request.count} questions. Each question should have:
- "id": unique identifier
- "question": the question text
- "type": question type
- "options": array of answer options (if applicable)
- "correct_answer": the correct answer
- "difficulty": difficulty level
- "explanation": brief explanation

Format the response as valid JSON only, no markdown formatting."""

    return prompt

def parse_llm_response(response_text: str) -> list[Dict[str, Any]]:
    """Parse the LLM response and extract JSON."""
    import json
    import re

    # Try to extract JSON from the response
    # Remove markdown code blocks if present
    response_text = re.sub(r'```json\n?', '', response_text)
    response_text = re.sub(r'```\n?', '', response_text)
    response_text = response_text.strip()

    try:
        questions = json.loads(response_text)
        if isinstance(questions, list):
            return questions
        elif isinstance(questions, dict) and "questions" in questions:
            return questions["questions"]
        else:
            return [questions]
    except json.JSONDecodeError:
        # If parsing fails, try to find JSON array in the text
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # Fallback: return error message
        raise ValueError("Failed to parse LLM response as JSON")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Thinki Question Generator API",
        "version": "1.0.0",
        "endpoints": {
            "english": "/api/english/generate",
            "math": "/api/math/generate"
        },
        "features": {
            "flexible_context": "Context accepts additional fields dynamically",
            "custom_templates": "Support for custom question templates via 'template' field",
            "template_placeholders": "Use {count}, {subject}, {year_band}, {ema}, {age}, {language}, {context}, or any request field name"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/english/generate", response_model=QuestionResponse)
async def generate_english_questions(request: QuestionRequest):
    """
    Generate English questions for Thinki educational application.
    
    Supports:
    - Additional context fields (e.g., learning_style, interests, etc.)
    - Custom question templates via the 'template' field
    - Template placeholders: {count}, {subject}, {year_band}, {ema}, {age}, {language}, {context}, or any request field

    - **action**: Should be "generate"
    - **year_band**: Year band (e.g., "Y5")
    - **subject**: Should be "English"
    - **count**: Number of questions to generate
    - **ema**: Expected Mastery Average (0.0-1.0)
    - **context**: Student context (accepts additional fields)
    - **template**: Optional custom question template string
    """
    if request.action != "generate":
        raise HTTPException(
            status_code=400, detail="Action must be 'generate'"
        )

    if request.subject.lower() != "english":
        raise HTTPException(
            status_code=400,
            detail="Subject must be 'English' for this endpoint"
        )

    try:
        # Generate prompt
        prompt = generate_prompt(request)
        
        # Call Gemini API
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Parse response
        questions = parse_llm_response(response_text)
        
        # Limit to requested count
        questions = questions[:request.count]
        
        return QuestionResponse(
            success=True,
            questions=questions,
            message=f"Successfully generated {len(questions)} English questions"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating questions: {str(e)}"
        )


@app.post("/api/math/generate", response_model=QuestionResponse)
async def generate_math_questions(request: QuestionRequest):
    """
    Generate Math questions for Thinki educational application.
    
    Supports:
    - Additional context fields (e.g., learning_style, interests, etc.)
    - Custom question templates via the 'template' field
    - Template placeholders: {count}, {subject}, {year_band}, {ema}, {age}, {language}, {context}, or any request field

    - **action**: Should be "generate"
    - **year_band**: Year band (e.g., "Y5")
    - **subject**: Should be "Math"
    - **count**: Number of questions to generate
    - **ema**: Expected Mastery Average (0.0-1.0)
    - **context**: Student context (accepts additional fields)
    - **template**: Optional custom question template string
    """
    if request.action != "generate":
        raise HTTPException(
            status_code=400, detail="Action must be 'generate'"
        )

    if request.subject.lower() != "math":
        raise HTTPException(
            status_code=400,
            detail="Subject must be 'Math' for this endpoint"
        )

    try:
        # Generate prompt
        prompt = generate_prompt(request)
        
        # Call Gemini API
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Parse response
        questions = parse_llm_response(response_text)
        
        # Limit to requested count
        questions = questions[:request.count]
        
        return QuestionResponse(
            success=True,
            questions=questions,
            message=f"Successfully generated {len(questions)} Math questions"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating questions: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
