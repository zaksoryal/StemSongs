import os
import subprocess
import time
import requests
from concurrent.futures import ThreadPoolExecutor

def process_with_demucs(file_path, output_dir):
    # Define output directory for stems
    song_output_dir = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0])
    os.makedirs(song_output_dir, exist_ok=True)

    # Run Demucs for stemming
    print(f"Processing {file_path} with Demucs...")
    
    # Use subprocess to call the Demucs command
    command = [
        'demucs',
        '-o', song_output_dir,
        file_path
    ]
    
    # Execute the Demucs command
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"Successfully separated stems for {file_path}. Stems saved in {song_output_dir}.")
    else:
        print(f"Error processing {file_path}: {result.stderr}")

    return song_output_dir


def process_tracks_concurrently(tracks, output_dir):
    # Create a ThreadPoolExecutor to process tracks concurrently
    with ThreadPoolExecutor() as executor:
        # Submit each track to be processed
        executor.map(lambda track: process_with_demucs(track['file_path'], output_dir), tracks)


# Example function that would be called after downloading tracks
def download_and_process_tracks(tracks, output_dir):
    # Assuming that tracks have been downloaded by download_threads
    # This will process the stems concurrently
    process_tracks_concurrently(tracks, output_dir)


# Example of how you might download and then process using ThreadPoolExecutor in download_tracks.py
def download_and_process_track(track, tracks_to_process):
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

            # After downloading, add the track file to a list for processing
            tracks_to_process.append({'file_path': file_path, 'track_title': track_title})

            time.sleep(1)  # Avoid rate limits
        else:
            print(f"Failed to download {track_title}")
