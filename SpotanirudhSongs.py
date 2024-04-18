import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import time

def main():
    client_id = 'your_client_id_here'  # Substitute with your actual client ID
    client_secret = 'your_client_secret_here'  # Substitute with your actual client secret
    credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=credentials_manager)

    try:
        # Open a CSV file to write
        with open('tracks_by_anirudh_ravichander.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Track Name', 'Artist Name', 'Year', 'Scale', 'BPM', 'Artwork URL'])  # Writing the header

            # Search for Tamil tracks
            results = sp.search(q='genre:Tamil', type='track', limit=50)
            tracks = results['tracks']['items']

            for track in tracks:
                artist_names = [artist['name'] for artist in track['artists']]  # List of artist names associated with the track
                if "Anirudh Ravichander" in artist_names:  # Check if Anirudh Ravichander is one of the artists
                    track_name = track['name']
                    artist_name = "Anirudh Ravichander"  # We filter for this specific artist
                    release_year = track['album']['release_date'][:4]  # Assuming the release date is properly formatted

                    # Retrieve audio features
                    audio_features = sp.audio_features(track['id'])[0]
                    if audio_features:
                        bpm = audio_features['tempo']
                        scale = audio_features['key']
                    else:
                        bpm = 'N/A'
                        scale = 'N/A'

                    # Get artwork URL from the album associated with the track
                    artwork_url = track['album']['images'][0]['url'] if track['album']['images'] else 'No artwork available'

                    # Write data to CSV
                    writer.writerow([track_name, artist_name, release_year, scale, bpm, artwork_url])
    except spotipy.SpotifyException as e:
        if e.http_status == 429:
            retry_after = int(e.headers['Retry-After'])  # Get the value of the 'Retry-After' header
            print(f"Rate limiting detected. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)  # Pause execution for the duration specified by 'Retry-After'
            main()  # Retry the entire process

if __name__ == "__main__":
    main()
