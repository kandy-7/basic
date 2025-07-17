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

                parsed = None

                # ✅ Case 1: Direct Gemini-like output
                if 'question' in data:
                    parsed = data

                # ✅ Case 2: Raw Gemini JSON embedded in code block
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

                # ✅ Display clean output
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
                    # Fallback: No detailed explanation returned, but correct
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
