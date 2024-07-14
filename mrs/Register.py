import streamlit as st
from pymongo import MongoClient

# Function to create a MongoDB connection
def create_connection():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["MovieReg"]
        return db
    except Exception as err:
        st.error(f"Error: {err}")
        return None

# Function to insert a new user into the database
def insert_user(users_collection, username, password):
    users_collection.insert_one({"username": username, "password": password})
    st.success("User registered successfully!")
    st.balloons()

# Function to check if a username already exists
def username_exists(users_collection, username):
    return users_collection.find_one({"username": username}) is not None

# Streamlit registration page
def registration_page():
    st.title("User Registration")

    # Input fields
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")
    confirm_password = st.text_input("Confirm Password:", type="password")

    # Providing unique keys to the st.button widgets
    register_button_key = "register_button"

    if st.button("Register", key=register_button_key):
        if password == confirm_password:
            db = create_connection()

            if db is not None:
                users_collection = db["users"]

                if not username_exists(users_collection, username):
                    insert_user(users_collection, username, password)
                else:
                    st.error("Username already exists. Please choose a different one.")
            else:
                st.error("Failed to connect to the database.")
        else:
            st.error("Passwords do not match. Please try again.")

# Run the registration page
if __name__ == "__main__":
    registration_page()
