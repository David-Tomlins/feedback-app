import streamlit as st


# URL of the Ometis logo
logo_url = "https://ometis.co.uk/hs-fs/hubfs/ometis%20orange%20transparent-1.png?width=221&height=98&name=ometis%20orange%20transparent-1.png"

# Display the Ometis logo
st.image(logo_url, width=200)

st.title("Education Feedback Form")

# Feedback form fields
name = st.text_input("Your Name")
email = st.text_input("Your Email")
course = st.selectbox("Course Attended", ["Course 1", "Course 2", "Course 3"])
st.markdown("<hr>", unsafe_allow_html=True)
st.header("Mandatory question")
nps = st.slider("Would you recommend Ometis Education to a friend or colleague in the future?", 0, 10)
st.markdown("<hr>", unsafe_allow_html=True)
st.header("Optional questions")
overall = st.slider("Considering content, delivery, and materials, how would you rate the training overall?", 0, 10)
objectives = st.slider("Did the training meet your expected objectives?", 0, 10)
materials = st.slider("Did the training materials effectively support your learning?", 0, 10)
balance = st.slider("Was the balance between instructor-led activities and exercises appropriate?", 0, 10)
knowledge = st.slider("Was the instructor was knowledgeable on the subject?", 0, 10)
manner = st.slider("Did the instructor deliver the training in a clear and engaging manner?", 0, 10)
pace = st.slider("Was the pace of the training was suitable?", 0, 10)
questions = st.slider("Was there adequate time allocated for questions and discussions?", 0, 10)


comments = st.text_area("Are there specific aspects of the training you believe could be improved? Please provide details.")

if st.button("Submit Feedback"):
    if nps == 0:
        st.error("Please provide a rating for the mandatory question between 1 and 10 (0 is no response)")
    else:
        st.success("Thank you for your feedback!")



