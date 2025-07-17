import streamlit as st
import requests
import json

st.subheader("🛡️ Cyber Quiz: Spot the Phish!")

# Question & options
q = "This email says you won a prize. Click here to claim. What do you do?"
options = ["Click the link", "Report as phishing", "Forward to a friend"]
answer = st.radio(q, options)

if st.button("Submit"):
    is_correct = answer == "Report as phishing"

    # Local feedback
    if is_correct:
        st.success("✅ Correct! Stay safe.")
    else:
        st.warning("⚠️ Oops! That could be a phishing attempt.")

    # Webhook to n8n (replace with your actual URL)
    webhook_url = "https://kanthimathinathan77.app.n8n.cloud/webhook-test/ask cyber-coach"

    payload = {
        "question": q,
        "answer": answer,
        "correct": is_correct
    }

    try:
        response = requests.post(webhook_url, json=payload)

        if response.status_code == 200:
            try:
                data = response.json()

                # If wrapped in a list, extract the first item
                if isinstance(data, list):
                    data = data[0]

                # ✅ Case 1: Clean Gemini response
                if 'question' in data:
                    parsed = data

                # ✅ Case 2: Gemini returned raw string with code block
                elif "raw" in data and "output" in data["raw"]:
                    raw_output = data["raw"]["output"]
                    clean_json_str = raw_output.replace("```json", "").replace("```", "").strip()
                    parsed = json.loads(clean_json_str)
                else:
                    st.error("❌ Unexpected response format from Gemini or webhook.")
                    parsed = None

                # ✅ Final Display – Only the clean output shown
                if parsed:
                    st.markdown("### 🔍 Gemini 2.0 Evaluation (Recovered)")
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

            except Exception as parse_error:
                st.error(f"❌ Failed to parse Gemini response: {parse_error}")
        else:
            st.error(f"❌ Failed to get response from n8n. Status code: {response.status_code}")

    except Exception as e:
        st.error(f"❌ Error contacting webhook: {e}")
