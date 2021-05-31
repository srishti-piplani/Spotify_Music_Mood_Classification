import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
import seaborn as sns
import numpy as np
from scipy import stats
from termcolor import colored

def init_credentials():
    client_id = 'YOUR_CLIENT_ID'
    client_secret = 'YOUR_CLIENT_SECRET'
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_track_info(id, mood):
    client_id = 'YOUR_CLIENT_ID'
    client_secret = 'YOUR_CLIENT_SECRET'
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    meta = sp.track(id)
    #print(meta)
    track_title = meta['name']
    #print(track_title)
    album_name = meta['album']['name']
    #print(album_name)
    release_year = meta['album']['release_date']
    #print(release_year)
    song_length_ms = meta['duration_ms']
    #print(song_length_ms)
    popularity = meta['popularity']
    #print(popularity)
    artist = meta['album']['artists'][0]['name']
    features = sp.audio_features(id)
    #print(features)
    
    #Fetching Audio features of a track
    acousticness = features[0]['acousticness']
    danceability = features[0]['danceability']
    energy = features[0]['energy']
    instrumentalness = features[0]['instrumentalness']
    liveness = features[0]['liveness']
    loudness = features[0]['loudness']
    speechiness = features[0]['speechiness']
    valence = features[0]['valence']
    tempo = features[0]['tempo']
    time_signature = features[0]['time_signature']
    
    song_complete_features = [track_title, album_name, artist, release_year, song_length_ms,
                              popularity,danceability, acousticness, danceability, energy,
                              instrumentalness, liveness, loudness, speechiness, valence,
                              tempo, time_signature, mood]
    #print(song_complete_features)
    return pd.DataFrame([song_complete_features], columns = ['track_title', 'album_name', 'artist', 
                                                             'release_year', 'song_length_ms',
                              'popularity','danceability', 'acousticness', 'danceability', 'energy',
                              'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence',
                              'tempo', 'time_signature', 'Mood'])

def predict_new_song(id, model_type, scaler):
    df_song = get_track_info(id, 'Any')
    df_song = df_song.loc[:,~df_song.columns.duplicated()]
    song_name = df_song.loc[:,'track_title'][0]
    feature_arr = df_song.loc[:, 'danceability':'valence']
    tfmd = scaler.transform(feature_arr)
    res = model_type.predict(tfmd)
    #0 Happy 1 Sad 2 Energetic
    if res == 0:
        print(f' {song_name} is a HAPPY song')
    elif res == 1:
        print(f' {song_name} is a SAD song')
    else:
        print(f' {song_name} is an ENERGETIC song')

def predict_playlist_mood(playlist_url, model_type, scaler):
    client_id = 'YOUR_CLIENT_ID'
    client_secret = 'YOUR_CLIENT_SECRET'
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    tracks_list = []
    tracks_info_list = []
    new_playlist_df = track_features_from_url_list(playlist_url,
                                                   tracks_list,
                                                   tracks_info_list,
                                                   'Any')
    new_playlist_df = new_playlist_df.loc[:,~new_playlist_df.columns.duplicated()]
    feature_arr = new_playlist_df.loc[:, 'danceability':'valence']
    tfmd = scaler.transform(feature_arr)
    predicted_vals = model_type.predict(tfmd)
    #Predict the mode as the mood of the playlist
    pl_mood = stats.mode(predicted_vals)[0][0]
    if pl_mood == 0:
        print(f' The playlist is a HAPPY playlist')
    elif pl_mood == 1:
        print(f' The playlist is a SAD playlist')
    else:
        print(f' The playlist is an ENERGETIC playlist')

def track_features_from_url_list(url_list, tracks_list_name, tracks_info_list_name, mood):
    for song_url in url_list:
        populate_mood_playlist(song_url, tracks_list_name)
    for song_id in tracks_list_name:
        tracks_info_list_name.append(get_track_info(song_id, mood))
    songs_list_dataframe = pd.concat(tracks_info_list_name, ignore_index=True)
    return songs_list_dataframe

#function to fetch songs from a single playlist and add to the corresponding mood playlist
def populate_mood_playlist(playlist_url, tracks_list_name):
    client_id = 'YOUR_CLIENT_ID'
    client_secret = 'YOUR_CLIENT_SECRET'
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    #Fetching playlist data from the URL
    current_playlist = sp.playlist(playlist_url)
    #Fetching ID's of all tracks as ID's can be used to get audio features of a particular song
    for item in current_playlist['tracks']['items']:
        tracks_list_name.append(item['track']['id'])

def predict_new_song_flask(id, model_type, scaler):
    df_song = get_track_info(id, 'Any')
    df_song = df_song.loc[:,~df_song.columns.duplicated()]
    song_name = df_song.loc[:,'track_title'][0]
    feature_arr = df_song.loc[:, 'danceability':'valence']
    tfmd = scaler.transform(feature_arr)
    res = model_type.predict(tfmd)
    #0 Happy 1 Sad 2 Energetic
    if res == 0:
        return [song_name, 'HAPPY']
    elif res == 1:
        return [song_name, 'SAD']
    else:
        return [song_name, 'ENERGETIC']

def get_track_image(id):
    #track['album']['images'][0]['url']
    client_id = 'YOUR_CLIENT_ID'
    client_secret = 'YOUR_CLIENT_SECRET'
    client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    meta = sp.track(id)
    return meta['album']['images'][0]['url']

def populate_mood_values_df(df, model_type, scaler):
    df = df.loc[:,~df.columns.duplicated()]
    feature_arr = df.loc[:, 'danceability':'valence']
    tfmd = scaler.transform(feature_arr)
    predicted_vals = model_type.predict(tfmd)
    df['Mood'] = predicted_vals
    return df