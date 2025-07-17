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
    st.session_state.answers = []
    st.session_state.answered = False
    st.session_state.selected = None

q_index = st.session_state.current_q

# If still questions left
if q_index < len(questions):
    current = questions[q_index]

    if not st.session_state.answered:
        # Show the question and options
        st.session_state.selected = st.radio(
            current["question"],
            current["options"],
            key=f"q{q_index}"
        )

        if st.button("Submit"):
            is_correct = st.session_state.selected == current["correct"]
            st.session_state.answers.append({
                "question": current["question"],
                "answer": st.session_state.selected,
                "correct": is_correct
            })

            if is_correct:
                st.session_state.score += 1
                st.success("✅ Correct! Stay safe.")
            else:
                st.warning("⚠️ Oops! That could be a phishing attempt.")

            # Webhook integration
            webhook_url = "https://kanthimathinathan77.app.n8n.cloud/webhook-test/ask cyber-coach"
            payload = {
                "question": current["question"],
                "answer": st.session_state.selected,
                "correct": is_correct
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
                            if raw_output.startswith("```json") or raw_output.startswith("```"):
                                clean_json_str = raw_output.replace("```json", "").replace("```", "").strip()
                                if clean_json_str:
                                    parsed = json.loads(clean_json_str)
                                else:
                                    st.warning("⚠️ Gemini returned an empty JSON code block.")
                            else:
                                st.warning("⚠️ Gemini response did not contain JSON format.")
                        else:
                            st.warning("⚠️ Gemini response missing expected fields.")

                        if parsed:
                            st.markdown("### 🔍 Gemini 2.0 Evaluation (Recovered)")
                            if parsed.get("fallback"):
                                st.info(f"💬 Gemini Tip: {parsed.get('tip', 'No additional info')}")
                            else:
                                st.write(f"**Question:** {parsed.get('question')}")
                                st.write(f"**Your Answer:** {parsed.get('answer')}")
                                st.write(f"**Correct:** {'✅ Yes' if parsed.get('correct', False) else '❌ No'}")
                                if parsed.get("threat_type"):
                                    st.write(f"**Threat Type:** 🛑 {parsed['threat_type']}")
                                if parsed.get("risk_level"):
                                    st.write(f"**Risk Level:** ⚠️ {parsed['risk_level']}")
                                if parsed.get("tip"):
                                    st.info(f"💡 Tip: {parsed['tip']}")
                                if parsed.get("action"):
                                    st.warning(f"📚 Action: {parsed['action']}")
                        else:
                            if is_correct:
                                st.info("✅ Correct answer submitted. No threat details needed.")
                            else:
                                st.warning("⚠️ Incorrect answer, but no detailed response from Gemini.")
                    except Exception as parse_error:
                        st.error(f"❌ Failed to parse Gemini response: {parse_error}")
                else:
                    st.error(f"❌ Failed to get response from n8n. Status code: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Error contacting webhook: {e}")

            # Mark question as answered
            st.session_state.answered = True

    else:
        st.info("Click below to go to the next question.")
        if st.button("Next Question"):
            st.session_state.current_q += 1
            st.session_state.answered = False
            st.session_state.selected = None
            # Use modern st.query_params to force rerun
            st.query_params.update(refresh=str(st.session_state.current_q))

else:
    # Quiz complete
    st.success("🎉 Quiz Completed!")
    total = len(questions)
    score = st.session_state.score
    percent = round((score / total) * 100)
    st.markdown(f"### 🧮 Your Score: **{score} / {total}** ({percent}%)")

    # Show summary
    st.markdown("#### 📝 Review Your Answers:")
    for i, entry in enumerate(st.session_state.answers, 1):
        st.write(f"**Q{i}:** {entry['question']}")
        st.write(f"Your Answer: {entry['answer']} - {'✅ Correct' if entry['correct'] else '❌ Incorrect'}")
        st.write("---")
