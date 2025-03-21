import streamlit as st
import database
import hashlib
import re
from datetime import datetime

# Function to hash passwords (using MD5 for compatibility with admin user)
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Function to validate email format
def is_valid_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

# Function to display login page
def login_page():
    st.title("Sign In")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            if not username or not password:
                st.error("Please enter both username and password")
                return
            
            # Hash the password
            hashed_password = hash_password(password)
            
            # Check user credentials
            user = database.check_user_credentials(username, hashed_password)
            
            if user:
                if user["status"] != "approved":
                    st.error("Your account is pending approval. Please wait for admin confirmation.")
                else:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_role = user["role"]
                    st.session_state.is_admin = (user["role"] == "admin")
                    st.session_state.page = "dashboard"
                    
                    # Log the login
                    database.log_user_activity(username, "login")
                    st.success("Login successful!")
                    st.rerun()
            else:
                st.error("Invalid username or password")
        
        if st.button("Back to Welcome Page", use_container_width=True):
            st.session_state.page = "welcome"
            st.rerun()

# Function to display signup page
def signup_page():
    st.title("Sign Up")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        username = st.text_input("Username", key="signup_username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        # Field selection dropdown
        industry_field = st.selectbox(
            "Select your industry field",
            ["Oil and Gas", "Food and Beverage", "Pharmaceutical", "Other"]
        )
        
        # Initialize other_field with a default value
        other_field = ""
        if industry_field == "Other":
            other_field = st.text_input("Please specify your industry field")
        
        if st.button("Create Account", use_container_width=True):
            if not username or not email or not password or not confirm_password:
                st.error("Please fill in all fields")
                return
            
            if not is_valid_email(email):
                st.error("Please enter a valid email address")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            if len(password) < 8:
                st.error("Password must be at least 8 characters long")
                return
                
            if industry_field == "Other" and not other_field:
                st.error("Please specify your industry field")
                return
            
            # Check if username already exists
            if database.check_username_exists(username):
                st.error("Username already exists. Please choose another one.")
                return
            
            # Hash the password
            hashed_password = hash_password(password)
            
            # Prepare user data
            field = other_field if industry_field == "Other" else industry_field
            
            # Register the user
            success = database.register_user(username, email, hashed_password, field)
            
            if success:
                st.success("Account created successfully! Please wait for admin approval before logging in.")
                # Redirect to login page after a brief pause
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error("Error creating account. Please try again.")
        
        if st.button("Back to Welcome Page", use_container_width=True):
            st.session_state.page = "welcome"
            st.rerun()
