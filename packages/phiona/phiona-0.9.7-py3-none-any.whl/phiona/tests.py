import time
import datetime as dt
from core import (
    get_refresh_token,
    get_new_access_token,
    get_file_status,
    generate_playlist_raw,
    generate_playlist_from_songs,
    generate_playlist_presets,
    get_similar_songs,
    add_new_file,
    edit_song,
    edit_user_playlist,
    delete_song,
    delete_user_playlist,
    delete_generated_playlist,
    create_new_playlist,
    add_song_to_playlist,
    load_user_playlist_songs,
    load_generated_playlists,
    load_generated_playlist_songs,
    load_user_playlists,
    get_artists,
    get_similar_artists,
    multi_target_playlist_creation,
    get_account_tokens,
    save_user_preset,
    duplicate_user_playlist,
)

# generate access and refresh token
username = 'testaccount1'
password = '76UiSPukuf9eNXO'
# refresh token lasts for 1 week
refresh_token = get_refresh_token(username, password)
print(refresh_token)
# access token lasts for 4 hours
access_token = get_new_access_token(refresh_token)
print('access')
print(access_token)

# # feed the access token to the api call

# track_id = add_new_file(access_token, r"C:\Users\Carl\Downloads\drive-download-20250603T085118Z-1-001\Beautiful Day - U2.mp3", 'u2', 'test', '', '', '')
# print(f"Process song time: {process_time:.2f} seconds")


# Test get_file_status with new parameters (search, order_by)
start_time = time.time()
file_result = get_file_status(access_token, page_n=1)
print(f"Files page 1: {len(file_result.get('song_info', []))} songs, {file_result.get('n_pages', 0)} pages")
if file_result.get('song_info'):
    print(f"First song: {file_result['song_info'][0]['song_title']}")

# Test with search
file_result_search = get_file_status(access_token, page_n=1, search='pop')
print(f"Search 'pop': {len(file_result_search.get('song_info', []))} songs found")

# Test with emotion search
file_result_emotion = get_file_status(access_token, page_n=1, search='happy;calm')
print(f"Search 'happy;calm': {len(file_result_emotion.get('song_info', []))} songs found")

# Test with order_by
file_result_ordered = get_file_status(access_token, page_n=1, order_by='-tempo')
print(f"Ordered by -tempo: {len(file_result_ordered.get('song_info', []))} songs")
status_time = time.time() - start_time
print(f"Get file status time: {status_time:.2f} seconds")

# # get the file status but sorted
# start_time = time.time()
# song_info = get_file_status(access_token, page_n=2, sorting_mechanism=['-friendship_love', 'frustration'])
# status_time = time.time() - start_time
# print(f"Get file status time: {status_time:.2f} seconds")


# # generate a playlist 
# # single hybrid
# targets1 = [
#     {
#         'genre': 'Dance Pop',
#         'target_circumplex': [0.5, 0.3],
#         'target_fingerprint': [0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89],
#         'weighting': '100', 
#         'avg_date': '2018-12-12',
#     },
# ]
# # multi hybrid
# targets2 = [
#     {
#         'genre': 'Dance Pop',
#         'target_circumplex': [0.5, 0.3],
#         'target_fingerprint': [0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89],
#         'weighting': '60', 
#         'avg_date': '2018-12-12',
#     },
#     {
#         'genre': 'House',
#         'target_circumplex': [0.5, 0.3],
#         'target_fingerprint': [0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89],
#         'weighting': '40', 
#         'avg_date': '2022-12-12',
#     },
# ]

# start_time = time.time()
# playlist_info = generate_playlist_raw(access_token, targets1)
# status_time = time.time() - start_time
# print(f"Get playlist status time: {status_time:.2f} seconds")

# start_time = time.time()
# playlist_info2 = generate_playlist_presets(access_token, 'fitness-pop')
# status_time = time.time() - start_time
# print(f"Get playlist status time: {status_time:.2f} seconds")

# song_ids = [53, 54, 55, 56, 57]

# start_time = time.time()
# playlist_info = generate_playlist_from_songs(access_token, song_ids)
# status_time = time.time() - start_time
# print(f"Get playlist status time: {status_time:.2f} seconds")


# song_ids = [56]

# start_time = time.time()
# playlist_info = generate_playlist_from_songs(access_token, song_ids)
# status_time = time.time() - start_time
# print(f"Get playlist status time: {status_time:.2f} seconds")


song_id = 56

# Test get_similar_songs with new parameters (genre, page)
start_time = time.time()
similar_songs_result = get_similar_songs(access_token, song_id)
print(f"Similar songs: {len(similar_songs_result.get('similar_songs', []))} songs")
print(f"Available genres: {similar_songs_result.get('available_genres', [])[:5]}...")
print(f"Page info: page {similar_songs_result.get('page', 1)}/{similar_songs_result.get('total_pages', 1)}")

# Test with genre filter
similar_songs_genre = get_similar_songs(access_token, song_id, genre='Pop')
print(f"Similar songs (Pop genre): {len(similar_songs_genre.get('similar_songs', []))} songs")

# Test with pagination
similar_songs_page2 = get_similar_songs(access_token, song_id, page=2)
print(f"Similar songs page 2: {len(similar_songs_page2.get('similar_songs', []))} songs")
status_time = time.time() - start_time
print(f"Get similar songs time: {status_time:.2f} seconds")

# Test load_user_playlists with new parameters (page_n, search)
out = load_user_playlists(access_token)
print(f"User playlists: {len(out.get('playlists_info', []))} playlists, {out.get('n_pages', 0)} pages")

playlist_id = out['playlists_info'][0]['id'] if out.get('playlists_info') else None
import random
import string

# Test load_user_playlists with search
playlists_search = load_user_playlists(access_token, search='test')
print(f"User playlists search 'test': {len(playlists_search.get('playlists_info', []))} playlists")

# Create and test playlist operations
random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
out = create_new_playlist(access_token, random_name)
print(f"Created playlist: {random_name}")

if playlist_id:
    random_name2 = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    out = edit_user_playlist(access_token, playlist_id, random_name2)
    print(f"Edited playlist {playlist_id} to: {random_name2}")
    
    out = add_song_to_playlist(access_token, playlist_id, song_id)
    print(f"Added song {song_id} to playlist")
    
    out = load_user_playlist_songs(access_token, playlist_id)
    print(f"Playlist songs: {len(out)} songs")
    
    # Test duplicate_user_playlist (new API)
    duplicate_result = duplicate_user_playlist(access_token, playlist_id)
    if duplicate_result.get('error'):
        print(f"Duplicate error: {duplicate_result['error']}")
    else:
        print(f"Duplicated playlist, now have {len(duplicate_result.get('playlist_info', []))} playlists")
    
    out = delete_user_playlist(access_token, playlist_id)
    print(f"Deleted playlist {playlist_id}")

# out = delete_song(access_token, song_id)

# Test load_generated_playlists with new parameters (page_n, search)
generated_playlists = load_generated_playlists(access_token)
print(f"Generated playlists: {len(generated_playlists.get('generated_playlists_info', []))} playlists, {generated_playlists.get('n_pages', 0)} pages")

# Test with search
generated_playlists_search = load_generated_playlists(access_token, search='fitness')
print(f"Generated playlists search 'fitness': {len(generated_playlists_search.get('generated_playlists_info', []))} playlists")

if generated_playlists.get('generated_playlists_info'):
    gen_playlist_id = generated_playlists['generated_playlists_info'][0]['id']
    out = load_generated_playlist_songs(access_token, gen_playlist_id)
    print(f"Generated playlist songs: {len(out)} songs")
    # out = delete_generated_playlist(access_token, gen_playlist_id)

# Test get_artists with new parameters (search, order_by)
artists_result = get_artists(access_token, page_n=1)
print(f"Artists: {len(artists_result.get('artist_info', []))} artists, {artists_result.get('n_pages', 0)} pages")

# Test with search
artists_search = get_artists(access_token, search='pop')
print(f"Artists search 'pop': {len(artists_search.get('artist_info', []))} artists")

# Test with emotion search
artists_emotion = get_artists(access_token, search='happy;excited')
print(f"Artists search 'happy;excited': {len(artists_emotion.get('artist_info', []))} artists")

if artists_result.get('artist_info'):
    artist_id = artists_result['artist_info'][0]['id']
    
    # Test get_similar_artists with new parameters (genre, page)
    similar_artists = get_similar_artists(access_token, artist_id)
    print(f"Similar artists: {len(similar_artists.get('similar_artists', []))} artists")
    print(f"Page info: page {similar_artists.get('page', 1)}/{similar_artists.get('total_pages', 1)}")
    
    # Test with pagination
    similar_artists_page2 = get_similar_artists(access_token, artist_id, page=2)
    print(f"Similar artists page 2: {len(similar_artists_page2.get('similar_artists', []))} artists")

# multi_targets = []

# multi_targets.append(
#     {
#         'targets':[
#             {
#                 'genre': 'Electro Pop',
#                 'target_circumplex': [0.5, 0.3],
#                 'target_fingerprint': [0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89],
#                 'weighting': '100', 
#                 'avg_date': '2010-01-01',
#             }
#         ],
#         'duration': 1800,
#     }
# )
# multi_targets.append(
#     {
#         'targets': [
#             {
#                 'genre': 'House',
#                 'target_circumplex': [0.5, 0.3],
#                 'target_fingerprint': [0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12, 0.89],
#                 'weighting': '100', 
#                 'avg_date': '2022-12-12',
#             },
#         ],
#         'duration': 1800,
#     }
# )
# multi_targets.append(
#     {
#         'targets': 'fitness-pop',
#         'duration': 1800,
#     }
# )


# out = multi_target_playlist_creation(access_token, multi_targets)

# Test get_account_tokens (new API)
print("\n=== Testing new APIs ===")
tokens = get_account_tokens(access_token)
print(f"Account tokens - Signature: {tokens.get('signature_tokens', 0)}, Generation: {tokens.get('generation_tokens', 0)}")

# Test save_user_preset (new API)
random_preset_name = 'test_preset_' + ''.join(random.choices(string.ascii_letters + string.digits, k=10))
target_circumplex = [0.5, 0.3]
target_fingerprint = [0.23, 0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 
                      0.45, 0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 
                      0.67, 0.12, 0.89, 0.34, 0.56, 0.78, 0.91, 0.23, 0.45, 0.67, 0.12]
preset_result = save_user_preset(
    access_token,
    preset_name=random_preset_name,
    description='Test preset from API',
    avg_date='2020-01-01',
    genre='Pop',
    target_circumplex=target_circumplex,
    target_fingerprint=target_fingerprint,
    time_length=30
)
if preset_result.get('error'):
    print(f"Save preset error: {preset_result['error']}")
else:
    print(f"Saved preset: {random_preset_name}")

print("\n=== All tests completed ===")

import ipdb; ipdb.set_trace()