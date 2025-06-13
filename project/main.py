import streamlit as st
from pages.about_us_page import about_us
from pages.faq_page import faq
from pages.your_datasets_page import your_datasets
from pages.selected_datasets_page import selected_datasets
from pages.search_dataset_page import search_datasets
from pages.your_model_page import your_model
from database.database import get_db
from database.db_operations import create_user, get_user_by_email
import time


def handle_user_login():
    """Handle user login and database creation if needed."""
    try:
        # Get database session
        db = next(get_db())
        
        # Check if user exists in database
        user = get_user_by_email(db, st.user.email)
        
        if not user:
            # Create new user if they don't exist
            user = create_user(
                db=db,
                username=st.user.email.split('@')[0],  # Use email prefix as username
                email=st.user.email,
                password_hash="oauth_user",  # OAuth users don't need password
                first_name=st.user.first_name if hasattr(st.user, 'first_name') else None,
                last_name=st.user.last_name if hasattr(st.user, 'last_name') else None
            )
            
    except Exception as e:
        st.error(f"Error handling user login: {str(e)}")
    finally:
        if 'db' in locals():
            db.close()

def user_login():
    st.login("google")

# st.page_link("data_consumer_dashboard.py", label="Page 1", icon="1️⃣")
# st.page_link("oauth.py", label="Page 2", icon="2️⃣")
# st.page_link("http://www.google.com", label="Google", icon="🌎")


pages_signed_user = {
    "model": [
        st.Page(your_model, title="Your uploaded models", icon="📦"),
    ],
    "datasets": [
        st.Page(your_datasets, title="Your uploaded datasets", icon="📦"),
        st.Page(selected_datasets, title="Selected datasets", icon="📦"),
        st.Page(search_datasets, title="Search datasets", icon="🔍"),
    ],
    "resources": [
        st.Page(about_us, title="About us", icon="ℹ️"),
        st.Page(faq, title="FAQs", icon="❓"),
    ],
}

pages_unsigned_user = {
    "resources": [
        st.Page(about_us, title="About us", icon="ℹ️"),
        st.Page(faq, title="FAQs", icon="❓"),
    ],
}

# if st.user: 
if st.user.is_logged_in:
    # Handle user database entry after successful login
        handle_user_login()
        pg = st.navigation(pages_signed_user)
    # else :
    #     pg = st.navigation(pages_unsigned_user)
else:
    pg = st.navigation(pages_unsigned_user)
    

pg.run()

with st.sidebar:
        if st.user.is_logged_in:
            st.button("logout",
                      on_click=st.logout)
        else:
            st.button(
            "login", 
            help="login using google",
            on_click=st.login,
            args=("google",)
            )

st.write(f"user login status: {st.user.is_logged_in}")

if st.user is not None:
    st.write(f"Welcome, {st.user}!")