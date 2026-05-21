import pickle
import streamlit as st
import requests
import pandas as pd

# Page Config
st.set_page_config(page_title="Movie Recommender", layout="wide")

# Custom CSS for Premium Design
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ff3333;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
    }
    .movie-container {
        padding: 10px;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    .reasoning-text {
        font-size: 0.8em;
        color: #888;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    try:
        data = requests.get(url)
        data.raise_for_status()
        data = data.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
    except Exception as e:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"

def get_reasoning(source_tags, target_tags):
    # Split tags into words and find common meaningful words
    source_words = set(source_tags.lower().split())
    target_words = set(target_tags.lower().split())
    
    # Common stopwords to exclude from reasoning
    stopwords = {'a', 'an', 'the', 'is', 'in', 'it', 'on', 'of', 'and', 'with', 'for', 'but', 'by', 'to', 'from', 'this', 'that'}
    
    common = source_words.intersection(target_words) - stopwords
    
    # Filter for words that look like keywords/genres (usually longer than 3 chars)
    meaningful_common = [word.capitalize() for word in common if len(word) > 3]
    
    if meaningful_common:
        return "Similar themes: " + ", ".join(meaningful_common[:3])
    return "Recommended based on overall similarity"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    source_tags = movies.iloc[index].tags
    
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    rec_data = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        overview = movies.iloc[i[0]].overview
        target_tags = movies.iloc[i[0]].tags
        
        rec_data.append({
            'title': title,
            'poster': fetch_poster(movie_id),
            'overview': overview,
            'reasoning': get_reasoning(source_tags, target_tags)
        })

    return rec_data

st.title('🎬 Movie Recommender System')

# Load main data
movies = pickle.load(open('model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

# Load overview data from CSV
try:
    movies_csv = pd.read_csv('tmdb_5000_movies.csv')
    # Merge overview into movies dataframe
    movies = movies.merge(movies_csv[['id', 'overview']], left_on='movie_id', right_on='id', how='left')
    movies['overview'] = movies['overview'].fillna("No description available.")
except Exception as e:
    st.error(f"Error loading CSV data: {e}")
    if 'overview' not in movies.columns:
        movies['overview'] = "Description not available."

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    recommendations = recommend(selected_movie)
    
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            rec = recommendations[i]
            st.image(rec['poster'])
            st.markdown(f"**{rec['title']}**")
            
            # Reasoning
            st.markdown(f"<div class='reasoning-text'>{rec['reasoning']}</div>", unsafe_allow_html=True)
            
            # Dropdown for description (Expander)
            with st.expander("Description"):
                st.write(rec['overview'])





