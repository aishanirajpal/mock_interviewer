# AI-Powered Excel Mock Interviewer

This Streamlit application provides a sophisticated, voice-enabled mock interview experience for candidates preparing for roles that require Microsoft Excel skills. The application leverages Google's Gemini API to dynamically generate questions and evaluate answers based on the candidate's self-reported years of experience, offering a highly personalized and intelligent assessment.

## Key Features

- **Dynamic Question Generation**: Utilizes the Gemini API to curate 10 unique interview questions tailored to the candidate's experience level.
- **AI-Powered Evaluation**: Employs the Gemini API to perform a nuanced evaluation of the candidate's recorded answers, providing a score and constructive feedback.
- **Voice-First Interface**: The primary mode of interaction is through voice, using a streamlined recording interface.
- **Structured Interview Flow**: A clean, timed process guides the user through preparation and answering phases for each question.
- **Comprehensive Feedback**: At the end of the interview, a detailed report is provided with an overall score, a category-based performance breakdown, and personalized recommendations.
- **Modern, Modular UI**: A sleek, dark-themed user interface built with a modular structure for easy maintenance and future development.

## Project Structure

The application is organized into a clean, modular structure to separate concerns and improve readability:

```
.
├── app.py                  # Main Streamlit application entry point
├── ui.py                   # UI components and screen layouts
├── utils.py                # Helper functions (Gemini API, audio transcription)
├── styles.py               # CSS styles for the application
├── config.py               # Configuration settings (API keys)
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (for API keys)
```

## Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Create a Virtual Environment

It is recommended to use a virtual environment to manage the project's dependencies.

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 2. Install Dependencies

Install all the required Python packages using pip.

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

The application requires a Google Gemini API key. Create a `.env` file in the root of the project directory and add your key:

```
GOOGLE_API_KEY="your_gemini_api_key_here"
```

### 4. Run the Application

Launch the Streamlit application by running the `app.py` file.

```bash
streamlit run app.py
```

The application will open in your default web browser.

## Usage

1.  **Welcome Screen**: Enter your name and years of experience with Excel.
2.  **Instructions**: Review the interview instructions while the AI generates your personalized questions.
3.  **Interview**: For each of the 10 questions:
    *   You will have 5 seconds to read the question and prepare.
    *   You will then be prompted to record your answer. Click the microphone to start and stop the recording.
    *   After recording, your answer will be transcribed and displayed for 10 seconds before automatically moving to the next question.
4.  **Results**: After the final question, your comprehensive results report will be displayed, including your overall score, performance by category, and personalized recommendations.
