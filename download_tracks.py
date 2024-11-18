import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor
from separate_stems import process_with_demucs  # Import the processing function

API_KEY = '98a51d8e'
BASE_URL = 'https://api.jamendo.com/v3.0/tracks'

def download_and_process_track(track):
    track_title = track['name']
    download_url = track['audio']  # Direct download link
    track_id = track['id']

    # Create a folder to store downloaded tracks
    download_dir = 'downloaded_songs'
    os.makedirs(download_dir, exist_ok=True)

    # Construct the file path
    file_path = os.path.join(download_dir, f"{track_id}_{track_title}.mp3")

    # Check if the track is already downloaded
    if os.path.exists(file_path):
        print(f"{track_title} is already downloaded, skipping...")
        return
    else:
        # Download the track file
        response = requests.get(download_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded {track_title}")

            # Separate stems immediately after downloading
            process_with_demucs(file_path, output_dir='downloaded_songs')

            time.sleep(1)  # Avoid rate limits
        else:
            print(f"Failed to download {track_title}")

def download_tracks(genre, limit=10):
    # Set up API parameters
    params = {
        'client_id': API_KEY,
        'format': 'json',
        'limit': limit,
        'tags': genre,
        'order': 'popularity_total',  # or 'latest' for recent tracks
    }

    # Fetch track data from Jamendo
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    # Use ThreadPoolExecutor to download and process tracks concurrently
    with ThreadPoolExecutor() as executor:
        executor.map(download_and_process_track, data['results'])

# Example usage
if __name__ == "__main__":
    download_tracks(genre="rnb", limit=15)  # Change genre and limit as needed