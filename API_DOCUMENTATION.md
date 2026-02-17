# Thinki Question Generator API Documentation

## Overview

The Thinki Question Generator API is a FastAPI-based service that generates educational questions using Google's Gemini LLM. It supports generating questions for English and Math subjects with flexible context fields and custom templates.

**Base URL:** http://localhost:8000

**API Version:** 1.0.0

---

## Routes

### 1. Generate English Questions

**Endpoint:** POST /api/english/generate

**Description:** Generates English questions for students based on their context and requirements.

**Request Body Structure:**

```json
{
  "action": "generate",
  "year_band": "string",
  "subject": "English",
  "count": integer,
  "ema": float,
  "context": {
    "age": integer,
    "onboarding_english_score": integer (optional),
    "onboarding_math_score": integer (optional),
    "language": "string",
    // Additional fields can be added dynamically
  },
  "template": "string (optional)"
}
```

**Request Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| action | string | Yes | Must be "generate" |
| year_band | string | Yes | Year band identifier (e.g., "Y5", "Y6") |
| subject | string | Yes | Must be "English" for this endpoint |
| count | integer | Yes | Number of questions to generate (1 or more) |
| ema | float | Yes | Expected Mastery Average (0.0 to 1.0) |
| context | object | Yes | Student context object (see Context Structure below) |
| template | string | No | Optional custom question template with placeholders |

**Response Structure:**

**Status Code:** 200 OK

```json
{
  "success": true,
  "questions": [
    {
      "id": "string",
      "question": "string",
      "type": "string",
      "options": ["string"] | null,
      "correct_answer": "string",
      "difficulty": "string",
      "explanation": "string"
    }
  ],
  "message": "string"
}
```

**Response Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always true for successful responses |
| questions | array | Array of question objects |
| message | string | Success message (e.g., "Successfully generated 3 English questions") |

**Question Object Structure:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique identifier for the question |
| question | string | Yes | The question text |
| type | string | Yes | Question type (e.g., "multiple_choice", "fill_in_blank", "comprehension") |
| options | array of strings | null | Conditional | Answer options (required for multiple choice, null for others) |
| correct_answer | string | Yes | The correct answer |
| difficulty | string | Yes | Difficulty level (e.g., "easy", "medium", "hard") |
| explanation | string | Yes | Brief explanation of the answer |

**Error Responses:**

**400 Bad Request - Invalid Action:**
```json
{
  "detail": "Action must be 'generate'"
}
```

**400 Bad Request - Wrong Subject:**
```json
{
  "detail": "Subject must be 'English' for this endpoint"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error generating questions: <error message>"
}
```

---

### 2. Generate Math Questions

**Endpoint:** POST /api/math/generate

**Description:** Generates Math questions for students based on their context and requirements.

**Request Body Structure:**

```json
{
  "action": "generate",
  "year_band": "string",
  "subject": "Math",
  "count": integer,
  "ema": float,
  "context": {
    "age": integer,
    "onboarding_english_score": integer (optional),
    "onboarding_math_score": integer (optional),
    "language": "string",
    // Additional fields can be added dynamically
  },
  "template": "string (optional)"
}
```

**Request Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| action | string | Yes | Must be "generate" |
| year_band | string | Yes | Year band identifier (e.g., "Y5", "Y6") |
| subject | string | Yes | Must be "Math" for this endpoint |
| count | integer | Yes | Number of questions to generate (1 or more) |
| ema | float | Yes | Expected Mastery Average (0.0 to 1.0) |
| context | object | Yes | Student context object (see Context Structure below) |
| template | string | No | Optional custom question template with placeholders |

**Response Structure:**

**Status Code:** 200 OK

```json
{
  "success": true,
  "questions": [
    {
      "id": "string",
      "question": "string",
      "type": "string",
      "options": ["string"] | null,
      "correct_answer": "string",
      "difficulty": "string",
      "explanation": "string"
    }
  ],
  "message": "string"
}
```

**Response Field Descriptions:**

Same as English endpoint (see above).

**Error Responses:**

**400 Bad Request - Invalid Action:**
```json
{
  "detail": "Action must be 'generate'"
}
```

**400 Bad Request - Wrong Subject:**
```json
{
  "detail": "Subject must be 'Math' for this endpoint"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error generating questions: <error message>"
}
```

---

## Context Structure

The context object accepts standard fields and any additional fields dynamically.

**Standard Context Fields:**

```json
{
  "age": integer,
  "onboarding_english_score": integer (optional),
  "onboarding_math_score": integer (optional),
  "language": "string"
}
```

**Context Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| age | integer | Yes | Student's age |
| onboarding_english_score | integer | No | Student's English proficiency score (0-100) |
| onboarding_math_score | integer | No | Student's Math proficiency score (0-100) |
| language | string | No | Language code (default: "en") |
| * | any | No | Any additional fields are accepted and included in the prompt |

**Example with Additional Fields:**

```json
{
  "age": 10,
  "onboarding_english_score": 75,
  "language": "en",
  "learning_style": "visual",
  "interests": "animals, space",
  "attention_span": "short"
}
```

---

## Template Placeholders

When using the template field, you can use the following placeholders:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| {count} | Number of questions to generate | 3 |
| {subject} | Subject name | English or Math |
| {year_band} | Year band | Y5 |
| {ema} | Expected Mastery Average | 0.65 |
| {age} | Student's age | 10 |
| {language} | Language code | en |
| {context} | Formatted context fields | - Age: 10\n- Language: en\n... |
| {<field_name>} | Any additional request field | Custom fields are supported |

---

## Additional Endpoints

### Health Check

**Endpoint:** GET /health

**Description:** Check if the API server is running.

**Response:**

**Status Code:** 200 OK

```json
{
  "status": "healthy"
}
```

---

### Root Endpoint

**Endpoint:** GET /

**Description:** Get API information and available endpoints.

**Response:**

**Status Code:** 200 OK

```json
{
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
```

---

## Request Examples

### Example 1: Basic English Question Request

```bash
curl -X POST "http://localhost:8000/api/english/generate" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Example 2: Math Question with Extra Context Fields

```bash
curl -X POST "http://localhost:8000/api/math/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "generate",
    "year_band": "Y5",
    "subject": "Math",
    "count": 2,
    "ema": 0.65,
    "context": {
      "age": 10,
      "onboarding_math_score": 75,
      "language": "en",
      "learning_style": "visual",
      "interests": "animals, space"
    }
  }'
```

### Example 3: Custom Template Request

```bash
curl -X POST "http://localhost:8000/api/english/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "generate",
    "year_band": "Y5",
    "subject": "English",
    "count": 2,
    "ema": 0.65,
    "context": {
      "age": 10,
      "onboarding_english_score": 75,
      "language": "en"
    },
    "template": "Create {count} fun {subject} questions for a {age}-year-old. Context: {context}. Return JSON array."
  }'
```

---

## Response Examples

### Success Response Example

```json
{
  "success": true,
  "questions": [
    {
      "id": "1",
      "question": "Which word is a noun in the sentence: 'The quick brown fox jumps'?",
      "type": "multiple_choice",
      "options": ["quick", "fox", "jumps", "brown"],
      "correct_answer": "fox",
      "difficulty": "medium",
      "explanation": "A noun is a person, place, thing, or idea. 'Fox' is a thing (animal)."
    },
    {
      "id": "2",
      "question": "What is the past tense of 'run'?",
      "type": "fill_in_blank",
      "options": null,
      "correct_answer": "ran",
      "difficulty": "easy",
      "explanation": "The past tense of 'run' is 'ran'."
    }
  ],
  "message": "Successfully generated 2 English questions"
}
```

### Error Response Examples

**400 Bad Request:**
```json
{
  "detail": "Action must be 'generate'"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error generating questions: Failed to parse LLM response as JSON"
}
```

---

## Notes

1. **Flexible Context Fields:** The context object accepts any additional fields beyond the standard ones. These will be automatically included in the prompt sent to the LLM.

2. **Custom Templates:** When a template is provided, it takes precedence over the default prompts. Use placeholders to inject dynamic values.

3. **Question Count:** The API will return up to the requested count of questions. If the LLM generates fewer questions, all available questions will be returned.

4. **Question Structure:** The exact structure of question objects may vary slightly based on the LLM's response, but will always include the core fields: id, question, type, correct_answer, difficulty, and explanation.

5. **Error Handling:** All errors return a JSON object with a detail field containing the error message.

---

## Interactive API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

These provide interactive testing interfaces and detailed schema information.
