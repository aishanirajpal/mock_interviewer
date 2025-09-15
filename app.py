import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEY
from ui import welcome_screen, loading_screen, interview_screen, results_screen
from styles import STYLES

# Configure APIs
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

def init_session_state():
    """Initialize session state variables."""
    if 'stage' not in st.session_state:
        st.session_state.stage = 'welcome'
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'years_of_experience' not in st.session_state:
        st.session_state.years_of_experience = 0
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = []
    if 'interview_questions' not in st.session_state:
        st.session_state.interview_questions = []
    if 'start_recording' not in st.session_state:
        st.session_state.start_recording = False

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="AI Excel Mock Interviewer",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.markdown(STYLES, unsafe_allow_html=True)
    
    init_session_state()

    # Navigation based on stage
    if st.session_state.stage == 'welcome':
        welcome_screen()
    elif st.session_state.stage == 'loading_questions':
        loading_screen()
    elif st.session_state.stage == 'interview':
        interview_screen()
    elif st.session_state.stage == 'results':
        results_screen()

if __name__ == "__main__":
    main()
