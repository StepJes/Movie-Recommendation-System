import streamlit as st
from pymongo import MongoClient
import subprocess

# Function to create a MongoDB connection
def create_connection():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["MovieReg"]
        return db
    except Exception as err:
        st.error(f"Error: {err}")
        return None

# Function to authenticate a user
def authenticate_user(users_collection, username, password):
    user = users_collection.find_one({"username": username, "password": password})
    return user is not None

# Streamlit login page
def login_page():
    st.title("User Login")

    # Input fields
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    # Providing unique keys to the st.button widgets
    login_button_key = "login_button"

    if st.button("Login", key=login_button_key):
        db = create_connection()

        if db is not None:
            users_collection = db["users"]

            if authenticate_user(users_collection, username, password):
                st.success(f"Welcome, {username}!")
                st.balloons()

                # Run the other Python script using subprocess
                subprocess.run(["streamlit", "run", "m1.py"])

                # Optionally, you can close the current Streamlit app
                st.stop()
            else:
                st.error("Invalid username or password. Please try again.")
        else:
            st.error("Failed to connect to the database.")

# Run the login page
if __name__ == "__main__":
    login_page()
