import pandas as pd
import requests
import time

# Load the CSV file
file_path = 'tamil_tracks.csv'
data = pd.read_csv(file_path)

def search_spotify_track(track_name, access_token):
    search_url = 'https://api.spotify.com/v1/search'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'q': track_name,
        'type': 'track',
        'limit': 10  # You can adjust the limit or add more parameters like market
    }
    response = requests.get(search_url, headers=headers, params=params)
    search_results = response.json()
    tracks = search_results['tracks']['items']
    track_details = [{'name': track['name'], 'id': track['id'], 'artists': [artist['name'] for artist in track['artists']]} for track in tracks]
    return track_details


def uri_to_url(spotify_uri):
    # Split the URI into its parts [spotify, type, id]
    parts = spotify_uri.split(':')
    if len(parts) == 3 and parts[0] == 'spotify':
        # Construct the URL
        return f"https://open.spotify.com/{parts[1]}/{parts[2]}"
    else:
        # Return None or raise an exception if the URI format is incorrect
        return None

def get_spotify_token(client_id, client_secret):
    # Spotify URL for obtaining the access token
    auth_url = "https://accounts.spotify.com/api/token"

    # Parameters for the POST request
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })

    # Convert the response to JSON
    auth_response_data = auth_response.json()

    # Access token from the response
    return auth_response_data['access_token']

def fetch_track_audio_features(track_id, access_token, count,index):
    endpoint = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    for attempt in range(5):  # Retry up to 5 times
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            features = response.json()
            # Extract desired features and the URI
            desired_features = {
                "acousticness": features['acousticness'],
                "danceability": features['danceability'],
                "duration_ms": features['duration_ms'],
                "energy": features['energy'],
                "instrumentalness": features['instrumentalness'],
                "key": features['key'],
                "liveness": features['liveness'],
                "loudness": features['loudness'],
                "mode": features['mode'],
                "speechiness": features['speechiness'],
                "tempo": features['tempo'],
                "time_signature": features['time_signature'],
                "valence": features['valence'],
                "uri": features['uri']  # Include the URI of the track
            }
            print(f"Updated Features {count}")
            return desired_features
        elif response.status_code == 429:
            # Handle rate limiting
            retry_after = int(response.headers.get("Retry-After", 1))
            print(f"Rate limit exceeded, retrying after {retry_after} seconds...")
            # time.sleep(retry_after)
            print(f"Skipping {count}")
            return 0
        else:
            print(f"Failed to fetch for {track_id}: Status {response.status_code} line {index}")
            return None
    return None  # Return None if all attempts fail

# Function to fetch album details using Spotify API
def fetch_album_details(track_id, access_token,count):
    endpoint = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    for attempt in range(5):  # Retry up to 5 times
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            track_data = response.json()
            duration = track_data['duration_ms']
            url = track_data['external_urls']['spotify']
            print(f"Updated {count}")
            return duration,url
        elif response.status_code == 429:
            # Extract how many seconds to wait from the headers and wait
            retry_after = int(response.headers.get("Retry-After", 1))
            print(f"Rate limit exceeded, retrying after {retry_after} seconds...")
            time.sleep(retry_after)
        else:
            print(f"Failed to fetch for {track_id}: Status {response.status_code}")
            return None
    return None  # Return None if all attempts fail

# Update the DataFrame with the fetched album names
def update_album_names(data, access_token):
    count = 0
    for index, row in data.iterrows():
        if pd.isna(row['duration_ms']) and not(pd.isna(row['acousticness']))  and count < 20:
            duration,url = fetch_album_details(row['track_id'], access_token,count)
            if duration:
                data.at[index, 'duration_ms'] = duration
            if url:
                data.at[index, 'track_url'] = url
                count += 1
            
    return data

def update_track_features(data, access_token):
    count = 0
    for index, row in data.iterrows():
        if pd.isna(row['acousticness']) and count < 1000:  # Assuming 'Audio Features' is a placeholder for any feature
            features = fetch_track_audio_features(row['track_id'], access_token, count,index)
            if features==0:
                break
            if features:
                # Update each feature in the DataFrame
                for feature in ['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'speechiness', 'tempo', 'time_signature', 'valence']:
                    data.at[index, feature] = features[feature]
                
                # Convert URI to URL and update
                data.at[index, 'track_url'] = uri_to_url(features['uri'])
                
                count += 1

    return data
#6srj5VAeLXSSTYcfbNYO8h
tok=get_spotify_token("151a89e56fe14a879110c42278ad8698","2b9c220642104c5987528454125ed099")
# Run the update function with your access token
updated_data = update_album_names(data, tok)
updated_data1 = update_track_features(updated_data, tok)

# Overwrite the original CSV file with the updated DataFrame
updated_data1.to_csv(file_path, index=False)

print("Update complete. Original CSV has been updated.")
