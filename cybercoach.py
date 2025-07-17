import streamlit as st
import requests
import json

st.set_page_config(page_title="Cyber Quiz", page_icon="🛡️")
st.subheader("🛡️ Cyber Quiz: Spot the Phish!")
st.markdown("Answer all **5 questions** to test your cyber awareness. Score and Gemini feedback will be shown at the end.")

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
    st.session_state.gemini_feedback = []
    st.session_state.answered = False

q_index = st.session_state.current_q
total = len(questions)

if q_index < total:
    q = questions[q_index]
    st.markdown(f"### Q{q_index+1}: {q['question']}")
    answer = st.radio("Choose an option:", q["options"], key=f"radio_{q_index}")

    if not st.session_state.answered:
        if st.button("Submit Answer"):
            correct = answer == q["correct"]
            st.session_state.answers.append({
                "question": q["question"],
                "answer": answer,
                "correct": correct
            })

            if correct:
                st.session_state.score += 1
                st.success("✅ Correct!")
            else:
                st.warning("❌ Incorrect.")

            # Send to n8n
            webhook_url = "https://your-n8n-instance.app.n8n.cloud/webhook/gemini-quiz"
            payload = {
                "question": q["question"],
                "user_answer": answer,
                "is_correct": correct
            }

            try:
                response = requests.post(webhook_url, json=payload)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        st.session_state.gemini_feedback.append(data)
                    except Exception as e:
                        st.session_state.gemini_feedback.append({"error": f"Parse failed: {e}"})
                else:
                    st.session_state.gemini_feedback.append({"error": "Webhook call failed"})
            except Exception as e:
                st.session_state.gemini_feedback.append({"error": f"Request failed: {e}"})

            # Mark question as answered
            st.session_state.answered = True

    else:
        st.success("✅ Answer submitted.")
        if st.button("Next Question"):
            st.session_state.current_q += 1
            st.session_state.answered = False
            st.experimental_set_query_params()  # clean params if needed
            st.experimental_rerun()  # optional: refresh if state mismatch (can remove if unwanted)

else:
    score = st.session_state.score
    percent = round((score / total) * 100)
    st.success(f"🎉 Quiz Completed! Your score: **{score}/{total}** ({percent}%)")

    st.markdown("### 🔍 Review Your Answers & Gemini Tips")
    for i, (ans, feedback) in enumerate(zip(st.session_state.answers, st.session_state.gemini_feedback)):
        st.markdown(f"**Q{i+1}: {ans['question']}**")
        st.write(f"Your Answer: {ans['answer']} - {'✅ Correct' if ans['correct'] else '❌ Incorrect'}")
        if isinstance(feedback, dict):
            if feedback.get("tip"):
                st.info(f"💡 Gemini Tip: {feedback['tip']}")
            if feedback.get("threat_type"):
                st.write(f"Threat Type: {feedback['threat_type']}")
            if feedback.get("risk_level"):
                st.write(f"Risk Level: {feedback['risk_level']}")
            if feedback.get("action"):
                st.warning(f"Recommended Action: {feedback['action']}")
        else:
            st.warning("⚠️ No feedback received.")
        st.write("---")
