import json
import librosa
import numpy as np
import requests


def calculate_features(song_path, sr=22050, chunk_size=256000):

    mono_data, sr = librosa.load(song_path, mono=True, sr=sr)
    # Smooth the whole song using a moving average filter
    window_size = int(sr * 0.05)  # 50 ms window
    if window_size < 1:
        window_size = 1
    # Downsample the smoothed waveform to reduce the number of values
    smoothed_waveform = np.convolve(mono_data, np.ones(window_size)/window_size, mode='same')
    # Determine reduction factor based on the length of mono_data
    if len(mono_data) > 6615000:
        reduction_factor = round(100 * (len(mono_data) / 6615000))
    else:
        reduction_factor = 100
    smoothed_waveform = smoothed_waveform[::reduction_factor]
    # Ensure the smoothed waveform amplitude is relative to the original
    # (i.e., scale the smoothed waveform so its max absolute value matches the original's)
    original_max = np.max(np.abs(mono_data))
    smoothed_max = np.max(np.abs(smoothed_waveform))
    if smoothed_max > 0:
        smoothed_waveform = smoothed_waveform * (original_max / smoothed_max)

    # Convert the smoothed waveform to 16-bit integer format
    smoothed_waveform_int8 = np.int8(smoothed_waveform / np.max(np.abs(smoothed_waveform)) * 127)

    # make sure the song is 22500 sr
    num_chunks = int(np.ceil(len(mono_data) / chunk_size))

    mel_chunks = []
    chroma_chunks = []
    choma_filter = librosa.filters.chroma(sr=sr, n_fft=2048)
    for i in range(num_chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, len(mono_data))
        if i > 0:
            chunk = mono_data[start-(2048-512):end]
        else:
            chunk = mono_data[start:end]
        if i == (num_chunks - 1):
            chunk = np.pad(chunk, (0, 512*2), 'constant')
        # Perform STFT
        if i == 0:
            stft_result = librosa.stft(chunk, hop_length=512, n_fft=2048)
            mel_result = librosa.feature.melspectrogram(S=np.abs(stft_result) ** 2, n_fft=2048,
                                                            hop_length=512, window='hann', center=True,
                                                            pad_mode='constant', power=2.0, n_mels=128)
            chroma_result = np.dot(choma_filter, np.abs(stft_result))
            mel_chunks.append(mel_result[:, :-2])
            chroma_chunks.append(chroma_result[:, :-2])

        else:
            stft_result = librosa.stft(chunk, hop_length=512, n_fft=2048, center=False)
            mel_result = librosa.feature.melspectrogram(S=np.abs(stft_result) ** 2, n_fft=2048,
                                                            hop_length=512, window='hann', center=False,
                                                            pad_mode='constant', power=2.0, n_mels=128)
            chroma_result = np.dot(choma_filter, np.abs(stft_result))
            mel_chunks.append(mel_result)
            chroma_chunks.append(chroma_result)
            
    merged_mel_spec = np.hstack(mel_chunks)
    merged_chroma_spec = np.hstack(chroma_chunks)
    # INSERT_YOUR_CODE
    merged_chroma_spec = merged_chroma_spec / np.max(merged_chroma_spec, axis=0, keepdims=True)
    # Normalize each row so the max is 1, but if the max is 0, leave the row unchanged;
    mean_chroma = np.mean(merged_chroma_spec, axis=1)

    # pitches in 12 tone equal temperament 
    pitches = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']


    # select the most dominate pitch
    pitch_id = np.argmax(mean_chroma)
    pitch = pitches[pitch_id]

    min_third_id = (pitch_id+3)%12
    maj_third_id = (pitch_id+4)%12

    #check if the musical 3rd is major or minor
    if mean_chroma[min_third_id] < mean_chroma[maj_third_id]:
        third = 'major'
    else:
        third = 'minor'

    estimated_key = pitch + ' ' + third

    return merged_mel_spec, estimated_key, smoothed_waveform_int8


def upload_to_gbp(merged_mel_spec, npy_url):

    # Upload the NPY file to the signed URL
    headers = {'Content-Type': 'application/octet-stream'}
    response2 = requests.put(npy_url, data=merged_mel_spec.tobytes(), headers=headers)
    # Check if the upload was successful
    if not response2.status_code == 200:
        raise Exception(f'Failed to upload features: {response2.status_code} {response2.text}. Please try again.')


def process_song(access_token, song_path, song_title, artist_name, language, genre, date_released):
    response = requests.post(
        'https://api.phiona.co.uk/api/get_new_track_upload_urls',
        json={'song_title': song_title, 'artist_name': artist_name, 'language': language, 'genre': genre, 'date_released': date_released},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    if response.status_code != 200:
        raise Exception(f"Failed to get new track upload urls: {response.status_code} {response.text}. Please try again.")
    data = json.loads(response.content)
    track_id = data['track_id']
    npy_url = data['npy_url']
    merged_mel_spec, key, smoothed_waveform_int8 = calculate_features(song_path)
    response2 = requests.post(
        'https://api.phiona.co.uk/api/save_key',
        json={'song_id': track_id, 'key': key, 'smoothed_waveform_int8': smoothed_waveform_int8.tolist()},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    if response2.status_code != 200:
        raise Exception(f"Failed to save initial features: {response2.status_code} {response2.text}. Please try again.")

    upload_to_gbp(merged_mel_spec, npy_url)
    return track_id


def generate_predictions(access_token, track_id):
    response = requests.post(
        'https://api.phiona.co.uk/api/generate_emotions',
        json={'track_id': track_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    if response.status_code != 200:
        raise Exception(f"""Failed to generate predictions: {response.status_code} {response.text}. 
        This is typically due to connection dropouts or the song being too long for us to process in one request. 
        As you have already uploaded the features then our system will process it in the background and there's no need to re upload the song.""")


def get_file_status(access_token, page_n=1, search='', order_by=None):
    """Get file/song status with pagination, search, and sorting.
    
    Args:
        access_token: The access token for authentication.
        page_n: Page number for pagination (default 1).
        search: Search string to filter results. Can include:
            - Text search: searches song_title, artists, genre, status, dates, tempo, era
            - Emotion/attribute search: use semicolon-separated values like "happy;calm"
              to filter songs with those emotions >= 0.333
        order_by: Field to sort by (e.g., '-date_added', 'song_title', '-tempo').
    
    Returns:
        dict: Contains 'song_info' list and 'n_pages' total page count.
    """
    payload = {'page_n': page_n}
    if search:
        payload['search'] = search
    if order_by:
        payload['order_by'] = order_by
    response = requests.post(
        'https://api.phiona.co.uk/api/get_files',
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def generate_playlist_raw(access_token, targets, age_window=None, required_duration=1800):
    vars = {'targets': targets, 'required_duration': required_duration}
    if age_window:
        vars['time_window'] = age_window 
    response = requests.post(
        'https://api.phiona.co.uk/api/generate_user_playlist_raw',
        json=vars,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    playlist_info = json.loads(response.content)
    
    return playlist_info


def generate_playlist_presets(access_token, preset, required_duration=1800):
    vars = {'targets': preset, 'required_duration': required_duration}
    response = requests.post(
        'https://api.phiona.co.uk/api/generate_user_playlist_presets',
        json=vars,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    playlist_info = json.loads(response.content)
    
    return playlist_info


def generate_playlist_from_songs(access_token, song_ids, age_window=None, required_duration=1800):
    vars = {'song_ids': song_ids, 'required_duration': required_duration}
    if age_window:
        vars['time_window'] = age_window 
    response = requests.post(
        'https://api.phiona.co.uk/api/generate_user_playlist_songs',
        json=vars,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    playlist_info = json.loads(response.content)
    
    return playlist_info


def get_similar_songs(access_token, song_id, genre='all', page=1):
    """Get songs similar to a given song with pagination and genre filtering.
    
    Args:
        access_token: The access token for authentication.
        song_id: The ID of the song to find similar songs for.
        genre: Filter by genre (default 'all' for no filtering).
        page: Page number for pagination (default 1, max 10 pages with 10 songs each).
    
    Returns:
        dict: Contains 'similar_songs' list, pagination info (page, total_pages, 
              has_next_page, has_previous_page), and 'available_genres' list.
    """
    payload = {'track_id': song_id, 'genre': genre, 'page': page}
    response = requests.post(
        'https://api.phiona.co.uk/api/return_similar_songs',
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def get_refresh_token(username, password):
    response = requests.post(
        'https://api.phiona.co.uk/api/token/',
        json={'username': username, 'password': password},
        headers={'Content-Type': 'application/json'}
    )
    refresh_token = json.loads(response.content)['refresh']
    
    return refresh_token


def get_new_access_token(refresh_token):
    response = requests.post(
        'https://api.phiona.co.uk/api/token/refresh/',
        json={'refresh': refresh_token},
        headers={'Content-Type': 'application/json'}
    )
    access_token = json.loads(response.content)['access']
    
    return access_token


def add_new_file(access_token, song_path, song_title, artist_name, language, genre, date_released):
    track_id = process_song(access_token, song_path, song_title, artist_name, language, genre, date_released)
    track_id = generate_predictions(access_token, track_id)
    return track_id


def edit_song(access_token, song_id, song_title, artist_name, genre, date_released):
    response = requests.post(
        'https://api.phiona.co.uk/api/edit_song',
        json={'song_id': song_id, 'song_title': song_title, 'artist_name': artist_name, 'genre': genre, 'date_released': date_released},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def edit_user_playlist(access_token, playlist_id, new_playlist_name):
    response = requests.post(
        'https://api.phiona.co.uk/api/edit_user_playlist',
        json={'playlist_id': playlist_id, 'playlist_name': new_playlist_name},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def delete_song(access_token, song_id):
    response = requests.post(
        'https://api.phiona.co.uk/api/delete_song',
        json={'song_id': song_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def delete_user_playlist(access_token, playlist_id):
    response = requests.post(
        'https://api.phiona.co.uk/api/delete_user_playlist',
        json={'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def delete_generated_playlist(access_token, playlist_id):
    response = requests.post(
        'https://api.phiona.co.uk/api/delete_generated_playlist',
        json={'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def create_new_playlist(access_token, playlist_name):
    response = requests.post(
        'https://api.phiona.co.uk/api/create_new_playlist',
        json={'playlist_name': playlist_name},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def add_song_to_playlist(access_token, playlist_id, song_id):
    response = requests.post(
        'https://api.phiona.co.uk/api/add_song_to_playlist',
        json={'song_id': song_id, 'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def load_user_playlists(access_token, page_n=1, search=''):
    """Load user playlists with pagination and search.
    
    Args:
        access_token: The access token for authentication.
        page_n: Page number for pagination (default 1, 50 playlists per page).
        search: Search string to filter playlists by name, number of songs, or date.
    
    Returns:
        dict: Contains 'playlists_info' list with id, date_added, playlist_name,
              number_of_songs, total_duration, and 'n_pages' total page count.
    """
    payload = {'page_n': page_n}
    if search:
        payload['search'] = search
    response = requests.post(
        'https://api.phiona.co.uk/api/load_user_playlists',
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def load_generated_playlists(access_token, page_n=1, search=''):
    """Load generated playlists with pagination and search.
    
    Args:
        access_token: The access token for authentication.
        page_n: Page number for pagination (default 1, 50 playlists per page).
        search: Search string to filter playlists by generation method, 
                number of songs, or date.
    
    Returns:
        dict: Contains 'generated_playlists_info' list with id, date_added, 
              generation_method, songs, user_rating, feedback, number_of_songs,
              total_duration, and 'n_pages' total page count.
    """
    payload = {'page_n': page_n}
    if search:
        payload['search'] = search
    response = requests.post(
        'https://api.phiona.co.uk/api/load_generated_playlists',
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)



def load_user_playlist_songs(access_token, playlist_id):
    response = requests.post(
        'https://api.phiona.co.uk/api/load_user_playlist_songs',
        json={'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)['song_info']


def load_generated_playlist_songs(access_token, playlist_id):
    response = requests.post(
        'https://api.phiona.co.uk/api/load_generated_playlist_songs',
        json={'playlist_id': playlist_id},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)['song_info']


def get_artists(access_token, page_n=1, search='', order_by=None):
    """Get artists with pagination, search, and sorting.
    
    Args:
        access_token: The access token for authentication.
        page_n: Page number for pagination (default 1, 50 artists per page).
        search: Search string to filter results. Can include:
            - Text search: searches artist name, genre, avg_date
            - Emotion/attribute search: use semicolon-separated values like "happy;calm"
              to filter artists with those emotions >= 0.333
        order_by: Field to sort by (e.g., '-avg_date', 'artist__name').
    
    Returns:
        dict: Contains 'artist_info' list and 'n_pages' total page count.
    """
    payload = {'page_n': page_n}
    if search:
        payload['search'] = search
    if order_by:
        payload['order_by'] = order_by
    response = requests.post(
        'https://api.phiona.co.uk/api/get_artists',
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'   
        }
    )
    return json.loads(response.content)


def get_similar_artists(access_token, artist_id, genre='all', page=1):
    """Get artists similar to a given artist with pagination and genre filtering.
    
    Args:
        access_token: The access token for authentication.
        artist_id: The ID of the artist to find similar artists for.
        genre: Filter by genre (default 'all' for no filtering).
        page: Page number for pagination (default 1, max 10 pages with 10 artists each).
    
    Returns:
        dict: Contains 'similar_artists' list with artist info including emotions
              and brand attributes, and pagination info (page, total_pages,
              has_next_page, has_previous_page), plus 'available_genres' list.
    """
    payload = {'artist_id': artist_id, 'genre': genre, 'page': page}
    response = requests.post(
        'https://api.phiona.co.uk/api/return_similar_artists',
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def multi_target_playlist_creation(access_token, targets):
    vars = {'targets': targets}
    response = requests.post(
        'https://api.phiona.co.uk/api/multi_target_playlist_creation',
        json=vars,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    playlist_info = json.loads(response.content)
    
    return playlist_info


def get_account_tokens(access_token):
    """Get the user's account token balances.
    
    Args:
        access_token: The access token for authentication.
    
    Returns:
        dict: Contains 'signature_tokens' and 'generation_tokens' counts.
    """
    response = requests.post(
        'https://api.phiona.co.uk/api/get_account_tokens',
        json={},
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def save_user_preset(access_token, preset_name, description, avg_date, genre, 
                     target_circumplex, target_fingerprint, time_length):
    """Save a new user preset for playlist generation.
    
    Args:
        access_token: The access token for authentication.
        preset_name: Name for the preset (must be unique for the user).
        description: Description of the preset.
        avg_date: Target average date for songs (format: 'YYYY-MM-DD').
        genre: Target genre for the preset.
        target_circumplex: List of 2 floats [valence, arousal] or string 
                          representation like '[0.5, 0.3]'.
        target_fingerprint: List of 31 floats for emotion fingerprint or string
                           representation. Order: allured, amazed, angst, awe, calm,
                           cynical, defiant, depressive, discouraged, doubt, empathy,
                           empowered, excitement, fearful, fiery, friendship_love,
                           frustration, grief, happy, hope, hopeless, inspired,
                           outrage, romantic_love, sad, sensual, sentimental, shame,
                           soothed, uninhibited, victorious.
        time_length: Duration in minutes for the generated playlist.
    
    Returns:
        dict: Empty dict on success, or {'error': 'message'} if preset name exists.
    """
    # Convert lists to string format if needed
    if isinstance(target_circumplex, list):
        target_circumplex = str(target_circumplex)
    if isinstance(target_fingerprint, list):
        target_fingerprint = str(target_fingerprint)
    
    payload = {
        'preset_name': preset_name,
        'description': description,
        'avg_date1': avg_date,
        'genre1': genre,
        'target_circumplex1': target_circumplex,
        'target_fingerprint1': target_fingerprint,
        'time_length': time_length,
    }
    response = requests.post(
        'https://api.phiona.co.uk/api/save_user_preset',
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)


def duplicate_user_playlist(access_token, playlist_id):
    """Duplicate a user playlist.
    
    Args:
        access_token: The access token for authentication.
        playlist_id: The ID of the playlist to duplicate.
    
    Returns:
        dict: Contains 'playlist_info' list with updated playlists after duplication,
              'n_pages' total page count, or {'error': 'message'} on failure.
    """
    payload = {'playlist_id': playlist_id}
    response = requests.post(
        'https://api.phiona.co.uk/api/duplicate_user_playlist',
        json=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return json.loads(response.content)

