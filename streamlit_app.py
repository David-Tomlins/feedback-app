import streamlit as st
import importlib
import os
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Collapse sidebar and hide toggle
st.set_page_config(initial_sidebar_state='collapsed')

st.write(st.secrets)

def get_secret(key):
    # First, try to get the secret from st.secrets (Streamlit Cloud)
    if key in st.secrets:
        return st.secrets[key]
    # If not found, try to get it from environment variables (Codespaces)
    elif key in os.environ:
        return os.environ[key]
    else:
        raise ValueError(f"Secret {key} not found in st.secrets or environment variables.")

# Retrieve Snowflake connection parameters from environment variables
# Usage
try:
    snowflake_user = get_secret("SF_USERNAME")
    snowflake_account = get_secret("SF_ACCOUNT")
    snowflake_private_key = get_secret("SF_PRIVATE_KEY")
    # Use these secrets as needed
except ValueError as e:
    st.error(str(e))

snowflake_warehouse = "GENERAL_USE_WH"
snowflake_database = "OMETIS_APPLICATIONS"
snowflake_schema = "FEEDBACK_APP"


st.header(snowflake_user)


st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)


# URL of the Ometis logo
logo_url = "https://ometis.co.uk/hs-fs/hubfs/ometis%20orange%20transparent-1.png?width=221&height=98&name=ometis%20orange%20transparent-1.png"

# Display the Ometis logo
st.image(logo_url, width=200)

st.title("Ometis Feedback Application")

token = st.query_params.get("token")

TOKEN_ROUTES ={
    "abcd1234":"education",
    "xyz789": "services"
}

ROUTES ={
    "education": "app_pages.education_feedback" ,
    "services": "app_pages.services_feedback"
}

if token in TOKEN_ROUTES:
    module = importlib.import_module(ROUTES[TOKEN_ROUTES[token]])
    module.render()
else:
    st.header("Sorry")
    st.markdown("Thank you for taking the time to provide feedback — it really helps us improve the service we deliver. Unfortunately, something has gone wrong and it looks like there is an issue with your token. Please get in touch with your contact at Ometis, and they’ll be happy to help resolve the issue.")



