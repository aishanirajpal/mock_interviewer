import streamlit as st
import time
import numpy as np
import plotly.express as px
from audio_recorder_streamlit import audio_recorder
from utils import generate_questions_with_gemini, transcribe_audio, evaluate_answer_with_gemini

def welcome_screen():
    """Welcome screen with user introduction"""
    st.markdown('<div class="main-header"><h1>AI-Powered Excel Mock Interviewer</h1><p>Voice-Enabled Skills Assessment Platform</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Excel Assessment")
        st.write("This intelligent interviewer will assess your Microsoft Excel skills through voice interaction.")
        st.markdown("""
        **KEY FEATURES:**
        - **Voice Recording**: Answer questions using your microphone.
        - **AI Evaluation**: Get intelligent assessment of your responses.
        - **Detailed Feedback**: Receive immediate insights and suggestions for improvement.
        """)
        st.markdown("---")
        user_name = st.text_input("Enter your name:", placeholder="Your full name")
        years_experience = st.number_input("Enter your years of experience with Excel:", min_value=0, max_value=50, step=1)
        if st.button("Start Interview", type="primary", use_container_width=True):
            if user_name:
                st.session_state.user_name = user_name
                st.session_state.years_of_experience = years_experience
                st.session_state.stage = 'loading_questions'
                st.rerun()
            else:
                st.warning("Please enter your name to continue.")

def loading_screen():
    """Display instructions while generating questions."""
    st.markdown('<div class="main-header"><h2>Preparing Your Interview</h2></div>', unsafe_allow_html=True)
    st.info("Your questions are being generated. In the meantime, please read the instructions below.")
    st.markdown("""
    **Interview Instructions:**
    - You will be presented with a series of questions tailored to your experience level.
    - For each question, you will have a moment to prepare before recording your answer.
    - Please aim to be clear and concise in your responses. Good luck!
    """)
    with st.spinner(f"Generating questions for a candidate with {st.session_state.years_of_experience} years of experience..."):
        st.session_state.interview_questions = generate_questions_with_gemini(st.session_state.years_of_experience)
    st.session_state.stage = 'interview'
    st.rerun()

def interview_screen():
    """Main interview with voice recording"""
    st.markdown('<div class="main-header"><h2>Excel Skills Interview</h2></div>', unsafe_allow_html=True)
    questions = st.session_state.interview_questions
    if not questions:
        st.error("Could not load interview questions. Please try restarting the assessment.")
        if st.button("Restart"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()
        return
    if st.session_state.current_question < len(questions):
        progress = st.session_state.current_question / len(questions)
        st.progress(progress)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.write(f"**Question {st.session_state.current_question + 1} of {len(questions)}**")
            st.write(f"**Category:** {questions[st.session_state.current_question]['category']}")
            st.write(f"**Experience Level:** {st.session_state.years_of_experience} years")
        current_q = questions[st.session_state.current_question]
        st.markdown(f'<div class="question-card"><h3>{current_q["question"]}</h3></div>', unsafe_allow_html=True)
        if not st.session_state.start_recording:
            timer_placeholder = st.empty()
            for i in range(40, 0, -1):
                timer_placeholder.info(f"Time to prepare your answer: {i} seconds remaining.")
                time.sleep(1)
            st.session_state.start_recording = True
            st.rerun()
        else:
            st.markdown('<div class="recording-status">Voice Recording Mode</div>', unsafe_allow_html=True)
            st.info("Click the microphone to start recording, and click it again when you are finished. Please aim to keep your answer under 60 seconds.")
            audio_bytes = audio_recorder(
                text="Click to Record Your Answer",
                recording_color="#e74c3c",
                neutral_color="#4361ee",
                icon_name="microphone",
                icon_size="2x",
                pause_threshold=300.0,
                key=f"recorder_{st.session_state.current_question}"
            )
            if audio_bytes:
                answer_text = ""
                with st.spinner("Processing your answer..."):
                    answer_text = transcribe_audio(audio_bytes)
                    evaluation = evaluate_answer_with_gemini(current_q, answer_text)
                    st.session_state.answers.append({
                        "question": current_q["question"],
                        "answer": answer_text,
                        "evaluation": evaluation,
                        "category": current_q["category"]
                    })
                
                is_last_question = st.session_state.current_question == len(questions) - 1

                if not is_last_question:
                    st.success(f"Your Transcribed Answer: \"{answer_text}\"")
                    st.info("Your answer has been processed. We will now proceed to the next question.")
                    time.sleep(10)

                st.session_state.last_answer = answer_text
                st.session_state.current_question += 1
                st.session_state.start_recording = False
                st.rerun()
    else:
        # Interview complete
        if st.session_state.last_answer:
            st.success(f"Your Transcribed Answer: \"{st.session_state.last_answer}\"")
        st.info("Assessment completed. Please check your report.")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("View Results", type="primary", use_container_width=True):
                st.session_state.last_answer = ""  # Clean up state
                st.session_state.stage = 'results'
                st.rerun()

def results_screen():
    """Results and comprehensive report"""
    st.markdown('<div class="main-header"><h2>Your Excel Skills Assessment Report</h2></div>', unsafe_allow_html=True)
    if not st.session_state.answers:
        st.warning("No interview data found. Please complete the assessment first.")
        return
    tab1, tab2, tab3 = st.tabs(["Summary Report", "Detailed Analysis", "Recommendations"])
    with tab1:
        st.header("Overall Performance")
        scores = [answer["evaluation"]["score"] for answer in st.session_state.answers]
        avg_score = np.mean(scores)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="score-card"><h3>{avg_score:.0f}%</h3><p>Overall Score</p></div>', unsafe_allow_html=True)
        with col2:
            skill_level = "Expert" if avg_score >= 90 else "Advanced" if avg_score >= 75 else "Intermediate" if avg_score >= 60 else "Beginner"
            st.markdown(f'<div class="score-card"><h3>{skill_level}</h3><p>Assessed Skill Level</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="score-card"><h3>{len(st.session_state.answers)}</h3><p>Questions Answered</p></div>', unsafe_allow_html=True)
        st.header("Performance by Category")
        category_scores = {}
        for answer in st.session_state.answers:
            category = answer["category"]
            score = answer["evaluation"]["score"]
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(score)
        category_avg = {cat: np.mean(scores) for cat, scores in category_scores.items()}
        fig = px.bar(
            x=list(category_avg.keys()),
            y=list(category_avg.values()),
            labels={"x": "Category", "y": "Average Score (%)"},
            color=list(category_avg.values()),
            color_continuous_scale="viridis"
        )
        fig.update_layout(showlegend=False, height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        st.header("Detailed Question Analysis")
        for i, answer in enumerate(st.session_state.answers):
            with st.expander(f"Question {i+1}: {answer['question'][:60]}..."):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**Question:** {answer['question']}")
                    st.write(f"**Your Answer:** {answer['answer']}")
                    st.write(f"**Feedback:** {answer['evaluation']['feedback']}")
                with col2:
                    score = answer['evaluation']['score']
                    st.metric("Score", f"{score:.0f}%", f"{answer['evaluation']['matches']}/{answer['evaluation']['total_points']} points covered")
    with tab3:
        st.header("Personalized Recommendations")
        avg_score = np.mean([answer["evaluation"]["score"] for answer in st.session_state.answers])
        if avg_score >= 90:
            st.success("**Excellent Excel Skills!** You demonstrate expert-level knowledge. Consider exploring advanced topics like Power Query, VBA automation, or integrating Excel with other data analysis tools.")
        elif avg_score >= 75:
            st.info("**Strong Excel Skills!** You have a solid intermediate-to-advanced knowledge base. To advance, focus on mastering complex functions, advanced PivotTable techniques, and robust data modeling.")
        elif avg_score >= 60:
            st.warning("**Good Foundation!** You have a good grasp of the basics. Concentrate on intermediate functions like VLOOKUP/XLOOKUP, conditional formatting, and creating more complex charts and dashboards.")
        else:
            st.error("**Keep Learning!** Focus on mastering fundamental functions, cell references, and core Excel operations. A structured beginner's course could be very beneficial.")
        st.markdown("---")
        st.header("Next Steps")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Retake Assessment", use_container_width=True, type="primary"):
                for key in ['stage', 'current_question', 'answers', 'question_history', 'interview_questions']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        with col2:
            if st.button("Download Report (PDF)", use_container_width=True):
                st.info("PDF download feature would be implemented here.")
