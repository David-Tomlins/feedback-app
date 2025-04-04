import streamlit as st


def render(message="error message"):
    st.header("Sorry")
    st.markdown("Thank you for taking the time to provide feedback — it really helps us improve the service we deliver. Unfortunately, something has gone wrong and it looks like there is an issue. Please get in touch with your contact at Ometis, and they’ll be happy to help resolve the issue.")
    st.error(f"Further Error details: {message}")


