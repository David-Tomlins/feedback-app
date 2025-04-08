import streamlit as st
import json
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

nps_slider_options= ['N/A',0,1,2,3,4,5,6,7,8,9,10]
slider_options= ['N/A',0,1,2,3,4,5,]

def render(request_data: dict, conn):
    st.header("Services Feedback Form")

    # Parse the EMPLOYEES_JSON string into a Python list
    try:
        employees_raw = request_data.get("EMPLOYEES_JSON", "[]")
        consultants = json.loads(employees_raw) if isinstance(employees_raw, str) else employees_raw
    except json.JSONDecodeError:
        consultants = []

    consultant_names = ", ".join([c.get("name", "Unknown") for c in consultants])

    # Contact information
    st.subheader("Your details:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Name:** {request_data.get('NAME', 'Unknown')}")
    with col2:
        st.markdown(f"**Company:** {request_data.get('COMPANY', 'Unknown')}")
    with col3:
        st.markdown(f"**Email:** {request_data.get('EMAIL', 'Unknown')}")

    st.markdown(f"**Project:** {request_data.get('PROJECT_NAME', 'Unknown')}")
    st.markdown(f"**Project Description:** {request_data.get('PROJECT_DESC', 'Unknown')}")
    st.markdown(f"**Days Billed:** {request_data.get('DAYS_BILLED', 'Unknown')}")
    st.markdown(f"**Consultant(s):** {consultant_names or 'None'}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("Project Feedback")
    st.markdown("We sincerely appreciate your time and feedback to help us improve.")
    st.markdown("Please score us between 0 (not at all likely) and 10 (extremely likely)")

    nps = st.select_slider("Would you recommend Ometis Education and their courses to a friend or colleague in the future?", options=nps_slider_options, value=nps_slider_options[0])

    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("Optional Questions on Your Consultants")
    st.markdown("1: Poor to 5: Excellent")

    # Per-consultant feedback
    person_feedback = []
    for consultant in consultants:
        with st.expander(f"Feedback for {consultant['name']}", expanded=True):
            feedback = {
                "person_id": consultant["id"],
                "name": consultant["name"],
                "role": "consultant",
                "quality_of_work": st.select_slider("Quality of work", options=slider_options, value=slider_options[0], key=f"quality_{consultant['id']}"),
                "communication": st.select_slider("Communication", options=slider_options, value=slider_options[0], key=f"communication_{consultant['id']}"),
                "technical_capability": st.select_slider("Technical capability and advice", options=slider_options, value=slider_options[0], key=f"technical_capability_{consultant['id']}"),
                "adaptability": st.select_slider("Adaptability", options=slider_options, value=slider_options[0], key=f"adaptability_{consultant['id']}"),
                "problem_solving": st.select_slider("Problem Solving", options=slider_options, value=slider_options[0], key=f"problem_solving_{consultant['id']}"),
                "comments": st.text_area(f"Are there specific comments you want to make about {consultant['name']}? Please provide details.", key=f"comments_{consultant['id']}")
            }
            person_feedback.append(feedback)

    general_comments = st.text_area("Are there any other aspects that you would like to comment on?")

    contact_preference = st.radio(
        "By default, we send this feedback request after a piece of work has been completed. Please let us know your preference:",
        ["Yes this is fine", "I would prefer less often", "I would prefer you did not contact me again"]
    )

    # Submit feedback
    if st.button("Submit Feedback"):
        if nps == 'N/A':
            st.error("Please provide a rating for the main NPS question (0 is no response).")
        else:
            try:
                feedback_id = str(uuid.uuid4())
                submitted_at = datetime.now(ZoneInfo("Europe/London"))

                payload = {
                    "nps": nps,
                    "person_feedback": person_feedback,
                    "general_comments": general_comments,
                    "contact_preference": contact_preference
                }

                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO feedback_app.feedback (
                            feedback_id, request_id, submitted_at, nps_score,
                            person_feedback, general_comments, contact_preference, raw_payload
                        )
                        SELECT %s, %s, %s, %s,
                               PARSE_JSON(%s), %s, %s, PARSE_JSON(%s)
                    """, (
                        feedback_id,
                        request_data.get("TOKEN"),
                        submitted_at,
                        nps,
                        json.dumps(person_feedback),
                        general_comments,
                        contact_preference,
                        json.dumps(payload)
                    ))

                    cur.execute("""
                        UPDATE FEEDBACK_REQUESTS
                        SET FLAG_FEEDBACK_RECEIVED = TRUE,
                            FEEDBACK_RECEIVED_AT = CONVERT_TIMEZONE('UTC', 'Europe/London', CURRENT_TIMESTAMP())
                        WHERE TOKEN = %s
                    """, (request_data.get("TOKEN"),))

                    conn.commit()

                st.query_params.update({"page": "thanks"})
                st.rerun()

            except Exception as e:
                st.error(f"An error occurred: {e}")
