# This program uses the Spotipy library to generate a Spotify playlist 
# based the popular tracks of the artists of a provided playlist.
# Made by Jacob Chunn

# Imports
import spotipy
import numpy as np
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException

# SpotifyOAuth inputs
client_id = "" # Enter client id
client_secret = "" # Enter client secret
redirect_uri = "https://www.google.com/"
scope = "playlist-modify-public playlist-modify-private playlist-read-private"

# Spotify Client Authorization Code Flow
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

# Returns the name of a track with a provided id
def get_track_name_from_id(id):
	return sp.track(id)["name"]

# Prints the track names when given an array of track ids
def print_track_names(tracks):
	for i in tracks:
		if i == "0": continue
		print("" + get_track_name_from_id(i) + "\n")

# Returns a numpy array of track names, given an array of track ids
def map_track_names_from_id_list(ids):
	return np.array(get_track_name_from_id(ids))

# Creates a new playlist and adds a list of tracks
def create_new_playlist(playlist_name, track_ids):
	sp.user_playlist_create(sp.current_user()["id"], \
		playlist_name, \
		public=True, \
		description="Tracks based on: " + playlist_link + " | Coded using spotipy | Made by Jake Chunn")
	new_playlist = sp.current_user_playlists(limit=1)["items"][0]
	if new_playlist["name"] != playlist_name: raise Exception("The playlist \"" + playlist_name + "\" was not found in User's playlists")
	if track_ids.size == 0: return
	track_ids = [i for i in list(track_ids) if i != "0"]
	sp.playlist_add_items(new_playlist["id"], track_ids)

# Gets all of the tracks of the playlist
# Playlist to test handling of local tracks:
#https://open.spotify.com/playlist/3yXCOWDRZz9QgUnZqg5bwU?si=5e1bdc9521bc4a69
# Playlist to test handling of large track amounts:
#https://open.spotify.com/playlist/7B0kSnc5JgV8ljvBAgsKD8?si=b21ea82b2d12441a
def get_tracks():
	try:
		playlist_link = str(input("Enter a valid spotify playlist link or playlist ID: "))
		if "/" in playlist_link and "?" in playlist_link:
			playlist_id = playlist_link.split("/")[-1].split("?")[0]
		else:
			playlist_id = playlist_link
		playlist_tracks = sp.playlist_tracks(playlist_id, fields="items(track)", limit=100)
		return playlist_tracks, playlist_link
	except SpotifyException:
		print("Invalid Spotify Playlist Link")
		return get_tracks()

# Store playlist track and link information 
playlist_tracks, playlist_link = get_tracks()

# Get track ids and names
track_ids = np.array([x["track"]["id"] for x in playlist_tracks["items"]])
track_names = np.array([x["track"]["name"] for x in playlist_tracks["items"]])

# Get artist uris
artist_uris = [x["track"]["artists"][0]["uri"] if x["track"]["is_local"] != True else "0" for x in playlist_tracks["items"]]

# Get each artists' top ten tracks starting with their most popular
artist_top_tracks = [sp.artist_top_tracks(artist_uris[i]) if artist_uris[i] != "0" else ["0"] for i in range(len(artist_uris))]

# Get the ids and names for each artists' top ten tracks
top_track_ids = [[artist_top_tracks[i]["tracks"][j]["id"] \
	for j in range(len(artist_top_tracks[i]["tracks"]))] \
		if artist_top_tracks[i] != ["0"] else ["0"] \
			for i in range(len(artist_top_tracks))]
top_track_names = [[artist_top_tracks[i]["tracks"][j]["name"] \
	for j in range(len(artist_top_tracks[i]["tracks"]))] \
		if artist_top_tracks[i] != ["0"] else ["0"] \
			for i in range(len(artist_top_tracks))]

# Pad each artist' top song ids and names with None objects so each artist has ten elements in their list
top_track_ids = [top_track_ids[i] + ["0"] * (10 - len(top_track_ids[i])) for i in range(len(top_track_ids))]
top_track_names = [top_track_names[i] + ["0"] * (10 - len(top_track_names[i])) for i in range(len(top_track_names))]

# Convert top track ids and names into a numpy array
top_track_ids = np.array(top_track_ids)
top_track_names = np.array(top_track_names)

# Create empty arrays to store names and ids of the generated playlist
tracks_for_new_playlist = np.empty(len(track_ids), dtype=object)
tracks_for_new_playlist.fill("0")
new_playlist_track_names = np.empty(len(track_ids), dtype=object)
new_playlist_track_names.fill("0")

# Gather non-duplicate and existing track-ids
for i in range(track_ids.size):
	for j in range(top_track_ids[i].size):
		if (top_track_ids[i][j] not in track_ids) and \
				(top_track_ids[i][j] not in tracks_for_new_playlist) and \
				(top_track_names[i][j] not in track_names) and \
				(top_track_names[i][j] not in new_playlist_track_names):
			if top_track_names[i][j] == "0": break
			tracks_for_new_playlist[i] = top_track_ids[i][j]
			new_playlist_track_names[i] = get_track_name_from_id(top_track_ids[i][j])
			break

# Get playlist name and create new playlist
playlist_name = str(input("Enter the name of the generated playlist: "))
create_new_playlist(playlist_name, tracks_for_new_playlist)