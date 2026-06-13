import pickle
import streamlit as st
import requests

# ---------------- Page Settings ----------------
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');

/* Animations */
@keyframes fadeIn {
    0% { opacity: 0; transform: translateY(30px) scale(0.95); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 15px rgba(229, 9, 20, 0.4); }
    50% { box-shadow: 0 0 30px rgba(229, 9, 20, 0.8), 0 0 10px rgba(255, 65, 108, 0.6); }
    100% { box-shadow: 0 0 15px rgba(229, 9, 20, 0.4); }
}

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(-45deg, #0d0d0c, #1a0505, #000000, #260a0a);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: #e0e0e0;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

h1 {
    text-align: center;
    font-size: 3.5rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #ff416c, #ff4b2b, #E50914, #ff416c);
    background-size: 300% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientBG 5s ease infinite;
    margin-bottom: 30px !important;
    text-shadow: 0px 5px 15px rgba(229, 9, 20, 0.3);
}

/* Movie Card */
.movie-card {
    display: flex;
    background: rgba(20, 20, 20, 0.85);
    border-radius: 15px;
    margin-bottom: 25px;
    overflow: hidden;
    border: 1px solid rgba(229, 9, 20, 0.1);
    box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    backdrop-filter: blur(10px);
    animation: fadeIn 0.8s ease-out forwards;
}

.movie-card:hover {
    transform: scale(1.03) translateY(-10px);
    box-shadow: 0 20px 40px rgba(229, 9, 20, 0.4);
    border: 1px solid rgba(229, 9, 20, 0.5);
}

.movie-poster {
    width: 200px;
    object-fit: cover;
    transition: transform 0.5s ease;
}

.movie-card:hover .movie-poster {
    transform: scale(1.08); /* slight zoom on the image itself */
}

.movie-details {
    padding: 20px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.movie-title {
    font-size: 26px;
    font-weight: 700;
    color: #ffffff !important;
    margin-bottom: 10px;
    transition: color 0.3s ease;
}

.movie-card:hover .movie-title {
    color: #ff4b2b !important;
}

.movie-info {
    font-size: 14px;
    color: #E50914 !important;
    font-weight: 600;
    margin-top: 5px;
    letter-spacing: 0.5px;
}

.movie-overview {
    font-size: 15px;
    margin-top: 15px;
    margin-bottom: 15px;
    color: #cccccc !important;
    line-height: 1.6;
}

.movie-cast {
    font-size: 14px;
    color: #aaaaaa !important;
    margin-top: 5px;
}

.movie-cast strong {
    color: #ffffff !important;
}

/* Button */
.stButton {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}

.stButton>button {
    background: linear-gradient(90deg, #E50914, #ff4b2b, #E50914);
    background-size: 200% auto;
    animation: gradientBG 3s linear infinite, pulseGlow 2s infinite;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    height: 3.5em !important;
    width: 280px !important;
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    transition: all 0.3s ease !important;
}

.stButton>button:hover {
    transform: translateY(-3px) scale(1.05);
    animation: gradientBG 1.5s linear infinite, pulseGlow 1s infinite;
}

@media (max-width: 768px) {
    .movie-card {
        flex-direction: column;
        align-items: center;
    }
    .movie-poster {
        width: 100%;
        max-width: 300px;
    }
    .movie-details {
        text-align: center;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------- Load Data ----------------
@st.cache_data
def load_data():
    movies = pickle.load(open('movie_list.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    movie_similarity_cf = pickle.load(open('movie_similarity_cf.pkl', 'rb'))
    return movies, similarity, movie_similarity_cf

movies, similarity, movie_similarity_cf = load_data()

# ---------------- Fetch Movie Details ----------------
def fetch_details(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()

        poster_path = data.get("poster_path")

        poster_path = data.get("poster_path")
        if poster_path:
            poster = "https://image.tmdb.org/t/p/w342/" + poster_path
        else:
            poster = "https://via.placeholder.com/500x750?text=No+Poster"
        # Genres
        genres_list = [genre.get('name') for genre in data.get('genres', []) if genre.get('name')]
        genre_str = ", ".join(genres_list) if genres_list else "N/A"

        # Keywords
        keywords_url = f"https://api.themoviedb.org/3/movie/{movie_id}/keywords?api_key=8265bd1679663a7ea12ac168da84d2e8"
        keywords_data = requests.get(keywords_url).json()
        keywords_list = [kw.get('name') for kw in keywords_data.get('keywords', []) if kw.get('name')][:10]
        keywords_str = ", ".join(keywords_list) if keywords_list else "N/A"

        # Cast + Crew
        credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        credits_data = requests.get(credits_url).json()

        cast = [actor.get('name') for actor in credits_data.get('cast', [])[:5] if actor.get('name')]
        cast_str = ", ".join(cast) if cast else "N/A"

        crew_members = credits_data.get('crew', [])
        crew_items = []
        for role in ['Director', 'Producer', 'Writer']:
            person = next((c.get('name') for c in crew_members if c.get('job') == role and c.get('name')), None)
            if person:
                crew_items.append(f"{role}: {person}")
        crew_str = ", ".join(crew_items) if crew_items else "N/A"

        return {
            "poster": poster,
            "rating": data.get("vote_average", "N/A"),
            "year": data.get("release_date", "N/A")[:4] if data.get("release_date") else "N/A",
            "language": data.get("original_language", "N/A").upper(),
            "overview": data.get("overview", "No description available"),
            "cast": cast_str,
            "crew": crew_str,
            "genres": genre_str,
            "keywords": keywords_str
        }
    except:
        return {
            "poster": "https://via.placeholder.com/500x750?text=No+Image",
            "rating": "N/A",
            "year": "N/A",
            "language": "N/A",
            "overview": "No description",
            "cast": "N/A",
            "crew": "N/A",
            "genres": "N/A",
            "keywords": "N/A"
        }

# ---------------- Display Movie ----------------
def display_movie(title, details):
    st.markdown(f"""
    <div class="movie-card">
        <img class="movie-poster" src="{details['poster']}">
        <div class="movie-details">
            <div class="movie-title">{title}</div>
            <div class="movie-info">⭐ {details['rating']} | 🌐 {details['language']} | 📅 {details['year']}</div>
            <div class="movie-overview">{details['overview'][:200]}...</div>
            <div class="movie-info">🎬 Genres: {details.get('genres', 'N/A')}</div>
            <div class="movie-info">🔑 Keywords: {details.get('keywords', 'N/A')}</div>
            <div class="movie-cast"><strong>Cast:</strong> {details.get('cast', 'N/A')}</div>
            <div class="movie-cast"><strong>Crew:</strong> {details.get('crew', 'N/A')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- Show Selected Movie ----------------
def show_selected(movie):
    movie_id = movies[movies['title'] == movie]['id'].values[0]
    details = fetch_details(movie_id)

    st.subheader("Selected Movie")
    display_movie(movie, details)

# ---------------- Content Based ----------------
def recommend_content(movie):
    index = movies[movies['title'] == movie].index[0]

    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    results = []

    for i in distances:
        movie_id = movies.iloc[i[0]].id
        title = movies.iloc[i[0]].title
        details = fetch_details(movie_id)
        results.append((title, details))

    return results

# ---------------- Collaborative Filtering ----------------
def recommend_cf(movie):
    results = []

    movie_data = movies[movies['title'] == movie]
    if movie_data.empty:
        return results

    movie_id = movie_data['id'].values[0]
    movie_title = movie_data['title'].values[0]

    target_id = None

    if movie_id in movie_similarity_cf.columns:
        target_id = movie_id
    elif str(movie_id) in movie_similarity_cf.columns:
        target_id = str(movie_id)
    elif movie_title in movie_similarity_cf.columns:
        target_id = movie_title

    if target_id is None:
        return results

    similar_movies = movie_similarity_cf[target_id].sort_values(ascending=False)[1:6]

    for mid in similar_movies.index:
        movie_match = movies[(movies['id'] == mid) | (movies['title'] == mid)]

        if not movie_match.empty:
            title = movie_match['title'].values[0]
            fetch_id = movie_match['id'].values[0]
            details = fetch_details(fetch_id)
            results.append((title, details))

    return results

# ---------------- Emotion Based ----------------
def recommend_by_emotion(emotion):
    # 🎯 Emotion → keyword mapping
    emotion_map = {
        "Happy": ["comedy", "fun", "family", "feel good", "animation"],
        "Sad": ["drama", "emotional", "tragedy", "loss"],
        "Excited": ["action", "thriller", "adventure", "sci-fi"],
        "Romantic": ["romance", "love", "relationship"],
        "Adventure": ["adventure", "fantasy", "journey", "epic"]
    }

    keywords = emotion_map.get(emotion, [])

    # 🔍 Match ANY keyword in tags
    emotion_movies = movies[
        movies['tags'].apply(
            lambda x: any(word in x.lower() for word in keywords) if isinstance(x, str) else False
        )
    ]

    # ⚠️ Fallback if nothing found
    if emotion_movies.empty:
        emotion_movies = movies.sample(5)

    results = []

    for i in emotion_movies.head(5).index:
        movie_id = movies.iloc[i].id
        title = movies.iloc[i].title
        details = fetch_details(movie_id)
        results.append((title, details))

    return results

# ---------------- UI ----------------
st.markdown("<h1>Movie Recommender System</h1>", unsafe_allow_html=True)

selected_movie = st.selectbox("Select a Movie", movies['title'].values)

emotion = st.selectbox(
    "Select your Mood",
    ["Happy", "Sad", "Excited", "Romantic", "Adventure"]
)

# ---------------- BUTTON ----------------
if st.button("Show Recommendation"):
    import time
    with st.spinner("Analyzing movies & finding the best matches for you..."):
        time.sleep(1.5)
        
        # 🎬 Selected Movie
        show_selected(selected_movie)
        st.markdown("---")

        # 🎥 Content Based
        st.subheader("Content Based")
        for title, details in recommend_content(selected_movie):
            display_movie(title, details)

        # 👥 Collaborative Filtering (silent fallback)
        st.subheader("👥 Collaborative Filtering")
        cf_results = recommend_cf(selected_movie)

        if len(cf_results) == 0:
            index = movies[movies['title'] == selected_movie].index[0]
            fallback = sorted(
                list(enumerate(similarity[index])),
                reverse=True,
                key=lambda x: x[1]
            )[6:11]

            for i in fallback:
                movie_id = movies.iloc[i[0]].id
                title = movies.iloc[i[0]].title
                details = fetch_details(movie_id)
                display_movie(title, details)
        else:
            for title, details in cf_results:
                display_movie(title, details)

        # 🎭 Emotion Based
        st.subheader(f"🎭 {emotion} Mood")
        for title, details in recommend_by_emotion(emotion):
            display_movie(title, details)