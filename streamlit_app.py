import streamlit as st
import importlib
import os
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Set up the Streamlit page with the sidebar collapsed
st.set_page_config(initial_sidebar_state='collapsed')

# Hide sidebar and toggle controls
st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# Function to retrieve secrets from either Streamlit Cloud or environment variables
def get_secret(key):
    if key in st.secrets:
        return st.secrets[key]
    elif key in os.environ:
        return os.environ[key]
    else:
        raise ValueError(f"Secret {key} not found.")

# Attempt to retrieve the required Snowflake connection details
try:
    snowflake_user = get_secret("SF_USERNAME")
    snowflake_account = get_secret("SF_ACCOUNT")
    snowflake_private_key = get_secret("SF_PRIVATE_KEY")
except ValueError as e:
    st.error(str(e))

# Convert the PEM-encoded private key string into a usable private key object
private_key = serialization.load_pem_private_key(
    snowflake_private_key.encode(),
    password=None,
    backend=default_backend()
)

# Establish the Snowflake connection using key-pair authentication
conn = snowflake.connector.connect(
    account=snowflake_account,
    user=snowflake_user,
    private_key=private_key,
    warehouse='GENERAL_USE_WH',
    database='OMETIS_APPLICATIONS',
    schema='FEEDBACK_APP'
)

# Display the Ometis logo at the top of the app
logo_url = "https://ometis.co.uk/hs-fs/hubfs/ometis%20orange%20transparent-1.png?width=221&height=98&name=ometis%20orange%20transparent-1.png"
st.image(logo_url, width=200)

# App title
st.title("Ometis Feedback Application")

# Get the token passed in the URL query parameters
token = st.query_params.get("token")

# Define available feedback types and their corresponding modules
ROUTES = {
    "education": "app_pages.education_feedback",
    "services": "app_pages.services_feedback"
}

# Fallback module for error handling and thanks
ISSUE_PAGE = "app_pages.issues"
THANKYOU_PAGE = "app_pages.thankyou"

# If a token was provided, proceed to validate and route
if st.query_params.get("page") == "thanks":
    thanks = importlib.import_module(THANKYOU_PAGE)
    thanks.render()
    st.stop()
elif token:
    with st.spinner("Validating your feedback link..."):
        try:
            # Query the feedback request associated with the token
            cur = conn.cursor()
            cur.execute("SELECT * FROM FEEDBACK_REQUESTS WHERE TOKEN = %s AND FLAG_FEEDBACK_RECEIVED=FALSE", (token,))
            feedback_record = cur.fetchone()
            col_names = [desc[0] for desc in cur.description]  # Extract column names from cursor metadata

            if feedback_record:
                # Create a dictionary of column names and values
                request_data = dict(zip(col_names, feedback_record))
                feedback_type = request_data.get("FEEDBACK_TYPE", "").lower()

                # Route to the appropriate feedback form
                if feedback_type in ROUTES:
                    module = importlib.import_module(ROUTES[feedback_type])
                    module.render(request_data, conn)  # Pass request data and DB connection
                else:
                    issues = importlib.import_module(ISSUE_PAGE)
                    issues.render("Unknown feedback type. Please contact Ometis.")
            else:
                # Token was not found in the table
                issues = importlib.import_module(ISSUE_PAGE)
                issues.render("Invalid or expired token. Please check your link.")

            cur.close()  # Close the cursor after use

        except Exception as e:
            # Generic error handling for any issues during the process
            issues = importlib.import_module(ISSUE_PAGE)
            issues.render(f"Database error: {e}")
else:
    # If no token was provided, show an error page
    issues = importlib.import_module(ISSUE_PAGE)
    issues.render("No token provided. Please check your feedback link.")