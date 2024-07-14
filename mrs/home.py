import streamlit as st
from Register import registration_page
from Login import login_page
def main():
    st.title("Movie :blue[Recommender] :movie_camera:")
    st.write("Welcome to the Movie :blue[Recommender] :pray:")

    # Add some space between the welcome message and buttons
    st.write("\n\n")

    col1, col2 = st.columns(2)  # Create two columns
    
    if col1.button("Register"):  # Button in the first column
        st.session_state.page = "register"
    
    if col2.button("Login"):  # Button in the second column
        st.session_state.page = "login"
    
    if 'page' in st.session_state:
        if st.session_state.page == "register":
            registration_page()
        elif st.session_state.page == "login":
            login_page()


if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state.page = "main"
    main()
