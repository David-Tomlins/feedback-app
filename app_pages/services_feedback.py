import streamlit as st
import json
import uuid
import datetime

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
    st.markdown("We sincerely appreciate you taking the time to provide us with your valuable feedback.")
    st.markdown("Please score us between 1-10 (0 = no response)")

    # Mandatory NPS question
    nps = st.slider("Would you recommend Ometis Consulting Services to a friend or colleague in the future?", 0, 10)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("Optional Questions on Your Consultants")
    st.markdown("1: Very poor to 5: Excellent (0 = no response)")

    # Per-consultant feedback
    person_feedback = []
    for consultant in consultants:
        with st.expander(f"Feedback for {consultant['name']}", expanded=True):
            feedback = {
                "person_id": consultant["id"],
                "name": consultant["name"],
                "role": "consultant",
                "quality_of_work": st.slider("Quality of work", 0, 5, key=f"quality_{consultant['id']}"),
                "communication": st.slider("Communication", 0, 5, key=f"communication_{consultant['id']}"),
                "technical_capability": st.slider("Technical capability and advice", 0, 5, key=f"technical_{consultant['id']}"),
                "adaptability": st.slider("Adaptability", 0, 5, key=f"adaptability_{consultant['id']}"),
                "problem_solving": st.slider("Problem Solving", 0, 5, key=f"problem_solving_{consultant['id']}"),
                "comments": st.text_area(f"Are there specific comments you want to make about {consultant['name']}? Please provide details.", key=f"comments_{consultant['id']}")
            }
            person_feedback.append(feedback)

    general_comments = st.text_area("Are there any other aspects that you believe could be improved?")

    contact_preference = st.radio(
        "By default, we send this feedback form after a piece of work has been completed. Please let us know your preference:",
        ["Yes this is fine", "I would prefer less often", "I would prefer you did not contact me again"]
    )

    # Submit feedback
    if st.button("Submit Feedback"):
        if nps == 0:
            st.error("Please provide a rating for the main NPS question (0 is no response).")
        else:
            try:
                feedback_id = str(uuid.uuid4())
                submitted_at = datetime.datetime.utcnow()

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
                            FEEDBACK_RECEIVED_AT = CURRENT_TIMESTAMP()
                        WHERE TOKEN = %s
                    """, (request_data.get("TOKEN"),))

                    conn.commit()

                st.query_params.update({"page": "thanks"})
                st.rerun()

            except Exception as e:
                st.error(f"An error occurred: {e}")
