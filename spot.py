import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import time

def main():
    client_id = 'id'  # Substitute with your actual client ID
    client_secret = 'id'  # Substitute with your actual client secret
    credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=credentials_manager)

    track_ids = set()

    try:
        with open('tamil_tracks.csv', 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            line_number = 2  # Start from line 2 because the header is line 1
            for row in reader:
                if not row or len(row) < 1:  # Check if the row is empty or does not have enough columns
                    print(f"Skipping empty or incomplete row at line {line_number}")
                else:
                    track_id = row[0]  # Assuming the track ID is in the first column
                    track_ids.add(track_id)
                line_number += 1  # Increment line number with each iteration
    except FileNotFoundError:
        print(f"File not found")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    print(f"Loaded track IDs count: {len(track_ids)}")

    # Open a CSV file to write
    with open('tamil_tracks.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        #writer.writerow(['Track ID', 'Track Name', 'Artist Name', 'Year', 'Scale', 'BPM', 'Artwork URL'])  # Write header if starting new file

        # Pagination setup
        offset = 0
        limit = 50
        more_tracks = True
        artist ="BTS"
        x=0
        while more_tracks:
            results = sp.search(q='year:2013 artist:'+artist, type='track', limit=limit, offset=offset)
            tracks = results['tracks']['items']

            if not tracks:
                more_tracks = False  # Break loop if no more tracks are found
                continue

            for track in tracks:
                track_id = track['id']
                track_name = track['name']
                artist_name = ', '.join(artist['name'] for artist in track['artists'])  # Join all artist names
                release_year = track['album']['release_date'][:4]
                artwork_url = track['album']['images'][0]['url'] if track['album']['images'] else 'No artwork available'

                # Retrieve audio features
                # if x==0:
                #     audio_features = sp.audio_features(track_id)[0]
                #     x=1

                # if audio_features:
                #     bpm = audio_features['tempo']
                #     scale = audio_features['key']  # Convert scale to note name if necessary
                #     scale_note = convert_scale_to_note(scale)  # Assuming convert_scale_to_note is defined
                # else:
                #     bpm = 'N/A'
                #     scale_note = 'N/A'
                # and ("Adele," in artist_name or len(artist_name)==len(artist))

                # Append data to CSV
                if track['id'] not in track_ids and (len(artist_name)==len(artist))  :        
                    writer.writerow([track_id, track_name, artist_name, release_year,track['popularity'],artwork_url,track['album']['name']]+[''] * 14)
                track_ids.add(track['id'])
                # time.sleep(1)

            offset += limit  # Move to the next page

def convert_scale_to_note(scale):
    scale_notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return scale_notes[scale] if 0 <= scale <= 11 else "Invalid scale"

if __name__ == "__main__":
    main()
