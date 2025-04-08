import streamlit as st
import json
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

slider_options= ['N/A',0,1,2,3,4,5,6,7,8,9,10]


def render(request_data: dict, conn):
    st.header("Education Feedback Form")
    ##submitted_at = datetime.now(ZoneInfo("Europe/London"))
    ##st.write(submitted_at)

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
    st.markdown("Please score us between 0 (not at all likely) and 10 (extremely likely)")

    nps = st.select_slider("Would you recommend Ometis Education and their courses to a friend or colleague in the future?", options=slider_options, value=slider_options[0])

    # Optional course-specific feedback
    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("Course Feedback")
    course_feedback = {
        "overall": st.select_slider("Overall training quality", options=slider_options, value=slider_options[0]),
        "objectives": st.select_slider("Training met your objectives", options=slider_options, value=slider_options[0]),
        "materials": st.select_slider("Materials supported your learning", options=slider_options, value=slider_options[0]),
        "balance": st.select_slider("Instructor-led vs exercises balance", options=slider_options, value=slider_options[0]),
        "knowledge": st.select_slider("Instructor knowledge", options=slider_options, value=slider_options[0]),
        "manner": st.select_slider("Instructor delivery quality", options=slider_options, value=slider_options[0]),
        "pace": st.select_slider("Training pace", options=slider_options, value=slider_options[0]),
        "questions": st.select_slider("Time for questions and discussion", options=slider_options, value=slider_options[0])
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
        if nps == 'N/A':
            st.error("Please provide a rating for whether you would recommend Ometis Education.")
        else:
            try:
                feedback_id = str(uuid.uuid4())
                submitted_at = datetime.now(ZoneInfo("Europe/London"))

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
                            FEEDBACK_RECEIVED_AT = CONVERT_TIMEZONE('UTC', 'Europe/London', CURRENT_TIMESTAMP())
                        WHERE TOKEN = %s
                    """, (request_data.get("TOKEN"),))

                    conn.commit()

                st.query_params.clear()
                st.query_params.update({"page": "thanks"})
                st.rerun()

            except Exception as e:
                st.error(f"An error occurred: {e}")
