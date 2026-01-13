from core import (
    get_refresh_token,
    get_new_access_token,
    add_new_file,
)

# generate access and refresh token
username = 'testaccount1'
password = '76UiSPukuf9eNXO'
# refresh token lasts for 1 week
refresh_token = get_refresh_token(username, password)
# access token lasts for 4 hours
access_token = get_new_access_token(refresh_token)

# upload a song
# feed the access token to the api call
track_id = add_new_file(
    access_token, 
    r"C:\Users\Carl\Downloads\drive-download-20250603T085118Z-1-001\Hello - Adele.mp3", 
    'Hello', 
    'Adele', 
    '', 
    '', 
    '',
)
print(track_id)
print('Song uploaded')
