import streamlit as st
import requests
import json

# Set page title and instructions
st.set_page_config(page_title="Cyber Quiz", page_icon="🛡️")
st.subheader("🛡️ Cyber Quiz: Spot the Phish!")
st.markdown("Answer all **5 questions** to test your cyber awareness. Your score will be shown at the end. Good luck! 💪")

# Quiz questions and answers
questions = [
    {
        "question": "This email says you won a prize. Click here to claim. What do you do?",
        "options": ["Click the link", "Report as phishing", "Forward to a friend"],
        "correct": "Report as phishing"
    },
    {
        "question": "You receive an email from your bank asking to confirm your password via a link. What do you do?",
        "options": ["Click and confirm", "Ignore it", "Report as phishing"],
        "correct": "Report as phishing"
    },
    {
        "question": "You get a message from a friend saying they’re stuck abroad and need money. What should you do?",
        "options": ["Send money", "Ignore the message", "Call them to confirm"],
        "correct": "Call them to confirm"
    },
    {
        "question": "You see a pop-up that says your device is infected and urges you to download an app. What do you do?",
        "options": ["Download the app", "Close the pop-up", "Restart the device"],
        "correct": "Close the pop-up"
    },
    {
        "question": "You receive a text from an unknown number claiming to be your boss asking for gift cards. What do you do?",
        "options": ["Buy the cards", "Reply for clarification", "Verify in person"],
        "correct": "Verify in person"
    }
]

# Initialize session state
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.quiz_summary = []  # <-- store all answers here
    st.session_state.answered = False
    st.session_state.selected = None
    st.session_state.gemini_response = None

q_index = st.session_state.current_q

# If still questions left
if q_index < len(questions):
    current = questions[q_index]

    if not st.session_state.answered:
        st.session_state.selected = st.radio(
            current["question"],
            current["options"],
            key=f"q{q_index}"
        )

        if st.button("Submit"):
            is_correct = st.session_state.selected == current["correct"]
            answer_record = {
                "question": current["question"],
                "answer": st.session_state.selected,
                "correct": is_correct
            }

            # Save answer to quiz_summary
            st.session_state.quiz_summary.append(answer_record)

            if is_correct:
                st.session_state.score += 1
                st.success("✅ Correct! Stay safe.")
            else:
                st.warning("⚠️ Oops! That could be a phishing attempt.")

            st.session_state.answered = True

    else:
        st.info("Click below to go to the next question.")
        if st.button("Next Question"):
            st.session_state.current_q += 1
            st.session_state.answered = False
            st.session_state.selected = None
            st.query_params.update(refresh=str(st.session_state.current_q))

# All questions answered
else:
    st.success("🎉 Quiz Completed!")
    total = len(questions)
    score = st.session_state.score
    percent = round((score / total) * 100)
    st.markdown(f"### 🧮 Your Score: **{score} / {total}** ({percent}%)")

    # Show summary
    st.markdown("#### 📝 Review Your Answers:")
    for i, entry in enumerate(st.session_state.quiz_summary, 1):
        st.write(f"**Q{i}:** {entry['question']}")
        st.write(f"Your Answer: {entry['answer']} - {'✅ Correct' if entry['correct'] else '❌ Incorrect'}")
        st.write("---")

    # Call Gemini only once after all answers
    if st.session_state.gemini_response is None:
        webhook_url = "https://kanthimathinathan77.app.n8n.cloud/webhook-test/ask cyber-coach"
        payload = {
            "quiz_summary": st.session_state.quiz_summary
        }

        try:
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        data = data[0]
                    parsed = None

                    if 'question' in data:
                        parsed = data
                    elif "raw" in data and "output" in data["raw"]:
                        raw_output = data["raw"]["output"].strip()
                        if raw_output.startswith("{") or raw_output.startswith("["):
                            clean_json_str = raw_output.replace("```json", "").replace("```", "").strip()
                            if clean_json_str:
                                parsed = json.loads(clean_json_str)
                            else:
                                st.warning("⚠️ Gemini returned an empty JSON code block.")
                        else:
                            st.warning("⚠️ Gemini response did not contain JSON format.")
                    else:
                        st.warning("⚠️ Gemini response missing expected fields.")

                    st.session_state.gemini_response = parsed

                except Exception as parse_error:
                    st.error(f"❌ Failed to parse Gemini response: {parse_error}")
            else:
                st.error(f"❌ Failed to get response from Gemini. Status: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Error contacting webhook: {e}")

    # Display Gemini Response
    if st.session_state.gemini_response:
        parsed = st.session_state.gemini_response
        st.markdown("### 🧠 Gemini Evaluation Summary")
        if isinstance(parsed, list):
            for i, entry in enumerate(parsed, 1):
                st.write(f"**Q{i}:** {entry.get('question', 'N/A')}")
                st.write(f"Your Answer: {entry.get('answer', 'N/A')} - {'✅ Correct' if entry.get('correct', False) else '❌ Incorrect'}")
                if entry.get("threat_type"):
                    st.write(f"**Threat Type:** 🛑 {entry['threat_type']}")
                if entry.get("risk_level"):
                    st.write(f"**Risk Level:** ⚠️ {entry['risk_level']}")
                if entry.get("tip"):
                    st.info(f"💡 Tip: {entry['tip']}")
                if entry.get("action"):
                    st.warning(f"📚 Action: {entry['action']}")
                st.write("---")
        else:
            st.warning("⚠️ Unexpected response format from Gemini.")
