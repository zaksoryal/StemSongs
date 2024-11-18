import os
import librosa
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_and_extract_mfcc(audio_path):
    # Load the audio file
    y, sr = librosa.load(audio_path, sr=None)  # `sr=None` to preserve the native sample rate
    
    # Extract MFCCs
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    # Compute the mean of the MFCCs across time to get a single feature vector for the song
    mfccs_mean = np.mean(mfccs, axis=1)
    
    return mfccs_mean

def compare_audio(uploaded_audio_path, downloaded_audio_path):
    # Load and extract MFCC features from both audio files
    uploaded_mfcc = load_and_extract_mfcc(uploaded_audio_path)
    downloaded_mfcc = load_and_extract_mfcc(downloaded_audio_path)
    
    # Compute cosine similarity between the MFCC vectors
    similarity = cosine_similarity([uploaded_mfcc], [downloaded_mfcc])[0][0]
    
    return similarity

def compare_stems(uploaded_stems_dir, downloaded_songs_dir):
    print(f"Uploaded stems directory: {uploaded_stems_dir}")
    print(f"Downloaded songs directory: {downloaded_songs_dir}")

    similarity_results = []

    # Locate the uploaded stems in the `htdemucs` subfolder
    uploaded_htdemucs_path = os.path.join(uploaded_stems_dir, "htdemucs")
    if not os.path.isdir(uploaded_htdemucs_path):
        print(f"No 'htdemucs' directory found in {uploaded_stems_dir}")
        return similarity_results

    # Find the nested directory inside `htdemucs`
    uploaded_song_dir = None
    for entry in os.listdir(uploaded_htdemucs_path):
        entry_path = os.path.join(uploaded_htdemucs_path, entry)
        if os.path.isdir(entry_path):
            uploaded_song_dir = entry_path
            break

    if not uploaded_song_dir:
        print(f"No subdirectory found in 'htdemucs' for {uploaded_stems_dir}")
        return similarity_results

    # Check the uploaded stems in the nested directory
    uploaded_stems = [f for f in os.listdir(uploaded_song_dir) if os.path.isfile(os.path.join(uploaded_song_dir, f))]
    print(f"Found uploaded stems: {uploaded_stems}")

    # Function to compare a single uploaded stem with downloaded stems
    def compare_single_stem(uploaded_stem, uploaded_stem_path):
        stem_comparison_results = []
        
        # Loop through downloaded songs to find matching stems
        for song_folder in os.listdir(downloaded_songs_dir):
            song_htdemucs_dir = os.path.join(downloaded_songs_dir, song_folder, "htdemucs")
            if os.path.isdir(song_htdemucs_dir):  # Ensure the `htdemucs` folder exists
                print(f"Found htdemucs directory for song: {song_htdemucs_dir}")

                # Find the nested directory for each downloaded song's stems
                downloaded_song_dir = None
                for entry in os.listdir(song_htdemucs_dir):
                    entry_path = os.path.join(song_htdemucs_dir, entry)
                    if os.path.isdir(entry_path):
                        downloaded_song_dir = entry_path
                        break

                if not downloaded_song_dir:
                    print(f"No subdirectory found in 'htdemucs' for {song_folder}")
                    continue

                downloaded_stems = [f for f in os.listdir(downloaded_song_dir) if os.path.isfile(os.path.join(downloaded_song_dir, f))]
                print(f"Found downloaded stems: {downloaded_stems}")

                # Compare the corresponding stem (bass with bass, drums with drums, etc.)
                if uploaded_stem in downloaded_stems:
                    downloaded_stem_path = os.path.join(downloaded_song_dir, uploaded_stem)
                    print(f"Comparing {uploaded_stem_path} with {downloaded_stem_path}")

                    # Perform the actual audio comparison
                    similarity = compare_audio(uploaded_stem_path, downloaded_stem_path)

                    stem_comparison_results.append({
                        'uploaded_stem': uploaded_stem_path,
                        'downloaded_stem': downloaded_stem_path,
                        'similarity': similarity
                    })
        
        return stem_comparison_results

    # Use ThreadPoolExecutor for parallel processing of stem comparisons
    with ThreadPoolExecutor() as executor:
        # Create a future for each stem comparison
        futures = {
            executor.submit(compare_single_stem, stem, os.path.join(uploaded_song_dir, stem)): stem
            for stem in uploaded_stems
        }

        # Collect results as they complete
        for future in as_completed(futures):
            stem_results = future.result()
            similarity_results.extend(stem_results)

    return similarity_results
