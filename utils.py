import streamlit as st
import json
import speech_recognition as sr
import io
from typing import Dict, List, Any
import google.generativeai as genai

def transcribe_audio(audio_bytes):
    """Transcribe audio using speech recognition"""
    try:
        r = sr.Recognizer()
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)
            text = r.recognize_google(audio)
            return text
    except sr.UnknownValueError:
        return "Could not understand the audio. Please try speaking more clearly."
    except sr.RequestError as e:
        return f"Error with speech recognition service: {e}"
    except Exception as e:
        return f"Error processing audio: {e}"

def _clean_json_response(response_text: str) -> str:
    """Clean the JSON response from Gemini."""
    text = response_text.strip()
    
    # Remove markdown code blocks
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    
    if text.endswith("```"):
        text = text[:-3]
    
    text = text.strip()
    
    # Find JSON array or object boundaries
    # Try to extract JSON if there's text before/after it
    if '[' in text and ']' in text:
        start = text.find('[')
        end = text.rfind(']') + 1
        text = text[start:end]
    elif '{' in text and '}' in text:
        start = text.find('{')
        end = text.rfind('}') + 1
        text = text[start:end]
    
    return text.strip()

def generate_questions_with_gemini(years_of_experience: int) -> List[Dict[str, Any]]:
    """Generate interview questions using Gemini AI"""
    try:
        # Configure safety settings to be more permissive
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        
        # Configure generation parameters
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            safety_settings=safety_settings,
            generation_config=generation_config
        )
        
        prompt = f"""
        Generate 10 interview questions for an Excel position for a candidate with {years_of_experience} years of experience.
        The questions should cover a range of relevant topics, from basic to advanced, appropriate for that experience level.
        
        IMPORTANT: Return ONLY a valid JSON array. Do not include any markdown formatting, code blocks, or explanatory text.
        
        Each object in the array should have these exact keys:
        - "question": The interview question (string)
        - "category": A relevant category (string, e.g., "Data Analysis", "Lookup Functions")
        - "expected_points": A list of 3-4 key points expected in a good answer (array of strings)
        - "voice_hints": A short hint for what to mention (string)

        Return format (no code blocks, just the JSON):
        [
            {{
                "question": "How do you create a basic SUM formula in Excel?",
                "category": "Basic Functions",
                "expected_points": [
                    "Use =SUM(range) syntax",
                    "Specify cell range like A1:A10",
                    "Can add individual cells with commas"
                ],
                "voice_hints": "Mention the equals sign, include cell references, explain the syntax"
            }}
        ]
        """
        
        response = model.generate_content(prompt)
        
        # Check if response was blocked
        if not response.text:
            st.error("The Gemini API returned an empty response. This might be due to safety filters or API issues.")
            if hasattr(response, 'prompt_feedback'):
                st.error(f"Prompt feedback: {response.prompt_feedback}")
            return []
        
        json_response = _clean_json_response(response.text)
        
        questions = json.loads(json_response)
        
        # Validate the structure
        if not isinstance(questions, list) or len(questions) == 0:
            st.error("Invalid response format: Expected a non-empty list of questions.")
            return []
        
        # Validate each question has required fields
        required_fields = ["question", "category", "expected_points", "voice_hints"]
        for i, q in enumerate(questions):
            for field in required_fields:
                if field not in q:
                    st.error(f"Question {i+1} is missing required field: {field}")
                    return []
        
        return questions
        
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON response from Gemini: {e}")
        st.error(f"Response text was: {response.text[:500]}...")  # Show first 500 chars
        return []
    except Exception as e:
        st.error(f"Failed to generate questions using Gemini: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        return []

def evaluate_answer_with_gemini(question_data: Dict[str, Any], user_answer: str) -> Dict[str, Any]:
    """Evaluate the user's answer using Gemini AI"""
    try:
        # Configure safety settings to be more permissive
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]
        
        # Configure generation parameters
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            safety_settings=safety_settings,
            generation_config=generation_config
        )
        
        prompt = f"""
        You are an expert Excel interview evaluator. Your task is to evaluate a candidate's answer to an interview question.

        Here is the context:
        - Interview Question: "{question_data['question']}"
        - Key points expected in the answer: {question_data['expected_points']}

        Here is the candidate's answer:
        - Candidate's Answer: "{user_answer}"

        IMPORTANT: Return ONLY a valid JSON object. Do not include any markdown formatting, code blocks, or explanatory text.

        Evaluate the answer and provide:
        1. "score": An integer score from 0 to 100
        2. "rating": A string rating: "excellent", "good", "fair", or "poor"
        3. "feedback": A constructive feedback string
        4. "matches": The number of key points covered (integer)
        5. "total_points": The total number of key points (integer)

        Return format (no code blocks, just the JSON):
        {{
            "score": 85,
            "rating": "good",
            "feedback": "Very good! You understand the main concepts well, but you could have explained one of the points in more detail.",
            "matches": 3,
            "total_points": 4
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Check if response was blocked
        if not response.text:
            st.warning("The Gemini API returned an empty response during evaluation.")
            return {
                "score": 0,
                "rating": "poor",
                "feedback": "Could not evaluate the answer due to an API error.",
                "matches": 0,
                "total_points": len(question_data.get('expected_points', []))
            }
        
        json_response = _clean_json_response(response.text)
            
        evaluation = json.loads(json_response)
        
        # Validate required fields
        required_fields = ["score", "rating", "feedback", "matches", "total_points"]
        for field in required_fields:
            if field not in evaluation:
                st.warning(f"Evaluation response missing field: {field}")
                evaluation[field] = 0 if field in ["score", "matches", "total_points"] else "N/A"
        
        return evaluation
        
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse evaluation JSON: {e}")
        return {
            "score": 0,
            "rating": "poor",
            "feedback": "Could not evaluate the answer due to a JSON parsing error.",
            "matches": 0,
            "total_points": len(question_data.get('expected_points', []))
        }
    except Exception as e:
        st.error(f"Failed to evaluate answer using Gemini: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        return {
            "score": 0,
            "rating": "poor",
            "feedback": "Could not evaluate the answer due to an error.",
            "matches": 0,
            "total_points": len(question_data.get('expected_points', []))
        }
