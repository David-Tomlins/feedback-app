import streamlit as st

consultants = [
    {"id": 1, "name": "Consultant A"},
    {"id": 2, "name": "Consultant B"}
    # Add more consultants as needed
]

feedback_data = {}

def render():
    st.header("Services Feedback Form")

    # Feedback form fields
    name = st.text_input("Your Name", value="Name Surname", disabled=True)
    company = st.text_input("Company", value="A Company", disabled=True)
    email = st.text_input("Your Email", value="name.surname@company.com" ,disabled=True)
    project = st.text_input("Project", value="Migrate Qlik Apps from PowerBI", disabled=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("Project feedback")
    st.markdown("We sincerely appreciate you taking the time to provide us with your valuable feedback. Your insights are crucial in helping us enhance our services and better meet your needs. Thank you for contributing to our continuous improvement.")
    st.markdown("Please score us between 1-10 (0 = no response)")
    nps = st.slider("Would you recommend Ometis Consulting Services to a friend or colleague in the future?", 0, 10)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("Optional questions on your consultants")
    
    st.subheader("Please rate your consultant(s):")
    st.markdown("1: Very poor to 5: Excellent  (0 = no response)")
    for consultant in consultants:
        with st.expander(f"Feedback for:", expanded=True):
            feedback = {}
            st.subheader(f"{consultant['name']}")
            feedback['quality'] = st.slider("Quality of work", 0, 5, key=f"quality_{consultant['id']}")
            feedback['communication'] = st.slider("Communication", 0, 5, key=f"communication_{consultant['id']}")
            feedback['technical'] = st.slider("Technical capability and advice", 0, 5, key=f"technical_{consultant['id']}")
            feedback['adaptaility'] = st.slider("Adaptability", 0, 5, key=f"adaptability_{consultant['id']}")
            feedback['problemSolving'] = st.slider("Problem Solving", 0, 5, key=f"problem solving_{consultant['id']}")
            feedback['comment'] = st.text_area(f"Are there specific comments you want to make about {consultant['name']}? Please provide details.", key=f"comments_{consultant['id']}")
            feedback_data[consultant['id']] = feedback
   


    comments = st.text_area("Are there any other aspects that you believe could be improved? Please provide details.")

    if st.button("Submit Feedback"):
        if nps == 0:
            st.error("Please provide a rating for the question ""Would you recommend Ometis Consulting Services to a friend or colleague in the future?"" (0 is no response)")
        else:
            st.success("Thank you for your feedback!")



