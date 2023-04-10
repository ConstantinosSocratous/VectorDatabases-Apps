from dotenv.main import load_dotenv
import os
import spotipy
from vector_database import VectorDb
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV')

SPOTIPY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECTED_URL')
SCOPE = 'user-library-read'
CACHE = '.spotipyoauthcache'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI, scope=SCOPE))

def get_saved_tracks_ids():
    all_saved_tracks_ids = []
    results = sp.current_user_saved_tracks(limit=50)

    all_saved_tracks_ids.extend([song['track']['id'] for song in results['items']])
    while results['next']:
        results = sp.next(results)
        all_saved_tracks_ids.extend([song['track']['id'] for song in results['items']])

    return all_saved_tracks_ids

def get_audio_features_ids(track_ids):
    batches = [track_ids[i:i+100] for i in range(0, len(track_ids), 100)]
    audio_features = []
    for batch in batches:
        audio_features.extend(sp.audio_features(batch))

    return audio_features


def get_feature_vector(track):
    return [
            track['danceability'],
            track['energy'],
            track['key'],
            track['loudness'],
            track['mode'],
            track['speechiness'],
            track['acousticness'],
            track['instrumentalness'],
            track['liveness'],
            track['valence'],
            track['tempo']
        ]


def get_vectors(audio_features):
    vectors = []
    for track in audio_features:
        vec = (track['id'], get_feature_vector(track))
        vectors.append(vec)

    return vectors

track_ids = get_saved_tracks_ids()
features = get_audio_features_ids(track_ids)
vectors = get_vectors(features)
# vdb.upsert('spotify-songs', vectors) # do it once to upsert vectors in the database

random_track_position = 0
random_track = sp.track(vectors[random_track_position][0])
print(random_track['name'])
print('----------')
input_features = sp.audio_features([random_track['id']])[0]

vdb = VectorDb(PINECONE_API_KEY, PINECONE_ENV)
results = vdb.query('spotify-songs', get_feature_vector(input_features)) # get 10 'similar' tracks of the given random track

for match in results['matches']:
    name = sp.track(match['id'])['name']
    print(name)

# spotify = sp.recommendations(seed_tracks=[random_track['id']], limit=10) 
# print('----------')
# print(spotify['tracks'][0]['name'])