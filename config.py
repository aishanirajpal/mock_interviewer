import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Gemini Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Speech Recognition Settings
SPEECH_CONFIG = {
    "language": "en-US",
    "timeout": 5,
    "phrase_time_limit": 30
}
