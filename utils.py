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

def generate_questions_with_gemini(years_of_experience: int) -> List[Dict[str, Any]]:
    """Generate interview questions using Gemini AI"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Generate 10 interview questions for an Excel position for a candidate with '{years_of_experience}' years of experience.
        The questions should cover a range of relevant topics, from basic to advanced, appropriate for that experience level.
        Provide the output in a clean JSON array format. Each object in the array should have the following keys:
        - "question": The interview question.
        - "category": A relevant category for the question (e.g., "Data Analysis", "Lookup Functions").
        - "expected_points": A list of 3-4 key points or concepts expected in a good answer.
        - "voice_hints": A short hint for the user on what to mention in their voice answer.

        Example format:
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
        
        json_response = response.text.strip()
        if json_response.startswith("```json"):
            json_response = json_response[7:]
        if json_response.endswith("```"):
            json_response = json_response[:-3]
        
        questions = json.loads(json_response)
        return questions
    except Exception as e:
        st.error(f"Failed to generate questions using Gemini: {e}")
        return []

def evaluate_answer_with_gemini(question_data: Dict[str, Any], user_answer: str) -> Dict[str, Any]:
    """Evaluate the user's answer using Gemini AI"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are an expert Excel interview evaluator. Your task is to evaluate a candidate's answer to an interview question.

        Here is the context:
        - Interview Question: "{question_data['question']}"
        - Key points expected in the answer: {question_data['expected_points']}

        Here is the candidate's answer:
        - Candidate's Answer: "{user_answer}"

        Based on the provided context, please evaluate the candidate's answer and provide the following in a clean JSON format:
        1. "score": An integer score from 0 to 100, representing the quality of the answer.
        2. "rating": A string rating, one of "excellent", "good", "fair", or "poor".
        3. "feedback": A constructive feedback string for the candidate.
        4. "matches": The number of key points covered by the user.
        5. "total_points": The total number of key points.

        Example JSON output format:
        {{
            "score": 85,
            "rating": "good",
            "feedback": "Very good! You understand the main concepts well, but you could have explained one of the points in more detail.",
            "matches": 3,
            "total_points": 4
        }}
        """
        
        response = model.generate_content(prompt)
        
        json_response = response.text.strip()
        if json_response.startswith("```json"):
            json_response = json_response[7:]
        if json_response.endswith("```"):
            json_response = json_response[:-3]
            
        evaluation = json.loads(json_response)
        return evaluation
        
    except Exception as e:
        st.error(f"Failed to evaluate answer using Gemini: {e}")
        return {
            "score": 0,
            "rating": "poor",
            "feedback": "Could not evaluate the answer due to an error.",
            "matches": 0,
            "total_points": len(question_data.get('expected_points', []))
        }
