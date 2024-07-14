import streamlit as st
import pandas as pd
import requests
import pickle
from datetime import datetime

movie_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movie_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

genres = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy', 'Foreign', 'History', 'Horror', 'Music', 'Mystery', 'Romance', 'ScienceFiction', 'TVMovie', 'Thriller', 'War', 'Western']

emotions = ['Happy', 'Sad', 'Exciting', 'Scary', 'Romantic']

if 'release_date' in movies.columns:
    movies['release_date'] = pd.to_datetime(movies['release_date'], format='%d-%m-%Y', errors='coerce')

# Streamlit App
st.title('Movie :blue[Recommender] :movie_camera:') 

def fetch_img(movie_id):
    api_key = "e792017cec91c6964e70f3e510ebb445"
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=US'
    response = requests.get(url)
    data = response.json()
    poster_path = data.get('poster_path')
    return "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else None

def recommend(shortlist):
    if not shortlist.empty:
        movie = shortlist.sample(1).iloc[0]['title']
        try:
            movie_index = movies[movies['title'] == movie].index[0]
        except IndexError:
            print(f"Movie '{movie}' not found in the data.")
            return None, None
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        recommended_movies = [movies.iloc[i[0]].title for i in movies_list]
        rec_movieIMG = [fetch_img(movies.iloc[i[0]].movie_id) for i in movies_list]
        return recommended_movies, rec_movieIMG
    else:
        print("No movies remaining in the shortlist.")
        return None, None

if 'sidebar_visible' not in st.session_state:
    st.session_state.sidebar_visible = False

# Toggle sidebar visibility
if st.button('Chatbot'):
    st.session_state.sidebar_visible = not st.session_state.sidebar_visible

# Function to maintain a shortlist of movies based on user choices
def update_shortlist(shortlist, genre_choices, release_period):
    shortlist = shortlist.copy()

    if genre_choices and genre_choices != "All":
        shortlist = shortlist[shortlist['genres'].apply(lambda x: all(genre in x for genre in genre_choices))]
    
    if release_period and 'release_date' in shortlist.columns:
        start_year, end_year = release_period
        # Extract the start and end dates with year format from the selected release period
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        # Filter the shortlist based on the extracted year range
        shortlist = shortlist[(shortlist['release_date'].dt.year >= start_date.year) & (shortlist['release_date'].dt.year <= end_date.year)]
    return shortlist

# Initial shortlist containing all movies
shortlist = movies.copy()

# Track the number of questions asked
question_count = 0
genre_choices = []
release_period = (2000, 2017)
emotions_choice = []

if st.session_state.sidebar_visible:
    with st.sidebar:
        st.write("### Chatbot Interaction")
        with st.chat_message("user"):
            st.write("Hello User👋")
        st.sidebar.title('Specific Recommendation')
        while question_count < 3 and len(shortlist) > 1:
            with st.sidebar:
                if question_count == 0:
                    genre_choices = st.multiselect(f"Question {question_count+1}: Which genre(s) are you interested in?", genres, key=f"genre_choice_{question_count+1}")
                elif question_count == 1:
                    release_period = st.slider(f"Question {question_count+1}: Select the release period", 1916, 2017, (2000, 2017), key=f"release_period_{question_count+1}")
                question_count += 1

        shortlist = update_shortlist(movies, genre_choices, release_period)
        st.sidebar.write(f"Based on your choices, there are approximately {len(shortlist)} movies remaining. Click below to see your top 5 picks")

Selected = st.selectbox(
    "Search Movies Here :point_down:",
    movies['title'].values,
    placeholder="Movies...",
)

if st.button('Recommend', key="recommend_button_selected"):
    selected_df = pd.DataFrame({'title': [Selected]})
    names, posters = recommend(selected_df)
    if names:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.image(posters[0])
            #st.write(names[0])
        with col2:
            st.image(posters[1])
            #st.write(names[1])

        with col3:
            st.image(posters[2])
            #st.write(names[2])
        with col4:
            st.image(posters[3])
            #st.write(names[3])
        with col5:
            st.image(posters[4])
            #st.write(names[4])
        for i in range(5):
            movie_id = movies[movies['title'] == names[i]].iloc[0]["movie_id"]
            with st.expander(f"{names[i]} - Watch Now", expanded=False):
                if posters[i]:
                    st.image(posters[i])
                else:
                    st.write(f"No image available for {names[i]}")
                # HTML links to streaming platforms that open in a new tab
                tmdb_link = f'<a href="https://www.themoviedb.org/movie/{movie_id}" target="_blank">TMDB - {names[i]}</a>'
                st.markdown(tmdb_link, unsafe_allow_html=True)

                netflix_link = f'<a href="https://www.netflix.com/in/title/{names[i]}" target="_blank">Netflix - {names[i]}</a>'
                st.markdown(netflix_link, unsafe_allow_html=True)

                hotstar_link = f'<a href="https://www.hotstar.com/in/explore?search_query={names[i]}" target="_blank">Hotstar - {names[i]}</a>'
                st.markdown(hotstar_link, unsafe_allow_html=True)

                prime_link = f'<a href="https://www.primevideo.com/search/ref=atv_sr_sug_nb_sb_ss_i_5_10?phrase={names[i]}" target="_blank">Prime Video - {names[i]}</a>'
                st.markdown(prime_link, unsafe_allow_html=True)

                soap2day_link = f'<a href="https://ww8.soap2dayhd.co/search/?q={names[i]}" target="_blank">Soap2Day - {names[i]}</a>'
                st.markdown(soap2day_link, unsafe_allow_html=True)

# Display recommendations
if st.session_state.sidebar_visible:
    #with st.sidebar:
    if st.sidebar.button("Recommend based on current selection", key="recommend_button"):
        recommended_movies, rec_movieIMG = recommend(shortlist)
        if recommended_movies:
            st.subheader("Recommended Movies based on selection:")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.image(rec_movieIMG[0])
            with col2:
                st.image(rec_movieIMG[1])
            with col3:
                st.image(rec_movieIMG[2])
            with col4:
                st.image(rec_movieIMG[3])
            with col5:
                st.image(rec_movieIMG[4])
            for i in range(len(recommended_movies)):
                movie_id = movies[movies['title'] == recommended_movies[i]].iloc[0]["movie_id"]
                with st.expander(f"{recommended_movies[i]} - Watch Now", expanded=False):
                    if rec_movieIMG[i]:
                        st.image(rec_movieIMG[i])
                    else:
                        st.write(f"No image available for {recommended_movies[i]}")
                    # Streaming platforms links
                    tmdb_link = f'<a href="https://www.themoviedb.org/movie/{movie_id}" target="_blank">TMDB - {recommended_movies[i]}</a>'
                    st.markdown(tmdb_link, unsafe_allow_html=True)
    
                    netflix_link = f'<a href="https://www.netflix.com/in/title/{recommended_movies[i]}" target="_blank">Netflix - {recommended_movies[i]}</a>'
                    st.markdown(netflix_link, unsafe_allow_html=True)
    
                    hotstar_link = f'<a href="https://www.hotstar.com/in/explore?search_query={recommended_movies[i]}" target="_blank">Hotstar - {recommended_movies[i]}</a>'
                    st.markdown(hotstar_link, unsafe_allow_html=True)
    
                    prime_link = f'<a href="https://www.primevideo.com/search/ref=atv_sr_sug_nb_sb_ss_i_5_10?phrase={recommended_movies[i]}" target="_blank">Prime Video - {recommended_movies[i]}</a>'
                    st.markdown(prime_link, unsafe_allow_html=True)
    
                    soap2day_link = f'<a href="https://ww8.soap2dayhd.co/search/?q={recommended_movies[i]}" target="_blank">Soap2Day - {recommended_movies[i]}</a>'
                    st.markdown(soap2day_link, unsafe_allow_html=True)
        else:
            st.sidebar.write("No movies to recommend based on the current selection.")