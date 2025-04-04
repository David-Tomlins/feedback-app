import streamlit as st
import json
import uuid
import datetime

def render(request_data: dict, conn):
    st.header("Education Feedback Form")

    # Parse the EMPLOYEES_JSON field (instructors) into a list
    try:
        employees_raw = request_data.get("EMPLOYEES_JSON", "[]")
        instructors = json.loads(employees_raw) if isinstance(employees_raw, str) else employees_raw
    except json.JSONDecodeError:
        instructors = []

    instructor_names = ", ".join([i.get("name", "Unknown") for i in instructors])

    # Display attendee and course info
    st.subheader("Your details:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Name:** {request_data.get('NAME', 'Unknown')}")
    with col2:
        st.markdown(f"**Company:** {request_data.get('COMPANY', 'Unknown')}")
    with col3:
        st.markdown(f"**Email:** {request_data.get('EMAIL', 'Unknown')}")

    st.markdown(f"**Course:** {request_data.get('COURSE_NAME', 'Unknown')}")
    st.markdown(f"**Course Completed:** {request_data.get('COURSE_DATE', 'Unknown')}")
    st.markdown(f"**Educator(s):** {instructor_names or 'None'}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("Education Feedback")
    st.markdown("We sincerely appreciate your time and feedback to help us improve.")
    st.markdown("Please score us between 1-10 (0 = no response)")

    nps = st.slider("Would you recommend Ometis Education and their courses to a friend or colleague in the future?", 0, 10)

    # Optional course-specific feedback
    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("Course Feedback")
    course_feedback = {
        "overall": st.slider("Overall training quality", 0, 10),
        "objectives": st.slider("Training met your objectives", 0, 10),
        "materials": st.slider("Materials supported your learning", 0, 10),
        "balance": st.slider("Instructor-led vs exercises balance", 0, 10),
        "knowledge": st.slider("Instructor knowledge", 0, 10),
        "manner": st.slider("Instructor delivery quality", 0, 10),
        "pace": st.slider("Training pace", 0, 10),
        "questions": st.slider("Time for questions and discussion", 0, 10)
    }

    comments = st.text_area("Are there specific aspects of the training you believe could be improved?")

    person_feedback = []
    for instructor in instructors:
        with st.expander(f"Feedback for {instructor['name']}", expanded=True):
            person_feedback.append({
                "person_id": instructor.get("id"),
                "name": instructor.get("name"),
                "role": "instructor",
                "comments": st.text_area(f"Comments about {instructor['name']}:", key=f"comments_{instructor['id']}")
            })

    if st.button("Submit Feedback"):
        if nps == 0:
            st.error("Please provide a rating for the mandatory NPS question.")
        else:
            try:
                feedback_id = str(uuid.uuid4())
                submitted_at = datetime.datetime.utcnow()

                payload = {
                    "nps": nps,
                    "course_feedback": course_feedback,
                    "person_feedback": person_feedback,
                    "general_comments": comments,
                    "contact_preference": "N/A"
                }

                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO feedback_app.feedback (
                            feedback_id, request_id, submitted_at, nps_score,
                            person_feedback, course_feedback, general_comments, contact_preference, raw_payload
                        )
                        SELECT %s, %s, %s, %s,
                               PARSE_JSON(%s), PARSE_JSON(%s), %s, %s, PARSE_JSON(%s)
                    """, (
                        feedback_id,
                        request_data.get("TOKEN"),
                        submitted_at,
                        nps,
                        json.dumps(person_feedback),
                        json.dumps(course_feedback),
                        comments,
                        "N/A",
                        json.dumps(payload)
                    ))

                    cur.execute("""
                        UPDATE FEEDBACK_REQUESTS
                        SET FLAG_FEEDBACK_RECEIVED = TRUE,
                            FEEDBACK_RECEIVED_AT = CURRENT_TIMESTAMP()
                        WHERE TOKEN = %s
                    """, (request_data.get("TOKEN"),))

                    conn.commit()

                st.query_params.clear()
                st.query_params.update({"page": "thanks"})
                st.rerun()

            except Exception as e:
                st.error(f"An error occurred: {e}")
