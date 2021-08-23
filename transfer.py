import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import oauth2
from YM_to_Spotify_transfer import get_my_playlists, get_liked_playlists, get_albums, get_liked_on_radio


def authorization():
    client_id = '2dc3faf3fe9a4fb1ae0741d5889100e3'
    client_secret = '1fc127a6a9f5430e951afa86bcb47d07'

    scope = ('user-library-read,' +
             ' playlist-read-private,' +
             ' playlist-modify-private,' +
             ' playlist-modify-public,' +
             ' user-read-private,' +
             ' user-library-modify,' +
             ' user-library-read')

    redirect_uri = 'http://localhost:8888/callback/' # redirect here after auth

    sp_oauth = oauth2.SpotifyOAuth(client_id, client_secret,
                                   redirect_uri, scope=scope)
    code = sp_oauth.get_auth_response(open_browser=True)

    token = sp_oauth.get_access_token(code,as_dict=False)  # get token
    sp = spotipy.Spotify(auth=token)

    username = sp.current_user()['id']

    return sp, username

def get_album_id(query, sp):
    # album data from spotify search
    album_id = sp.search(q=query, limit=1, type='album')
    # split() – делает список, состоящий из одной строчки для метода current_user_saved_albums_add()
    return album_id['albums']['items'][0]['id'].split()


def transfer_albums(yandex_username, albums_for_spotify):
    sp, username = authorization()
    # albums_for_spotify – альбомы для переноса из Яндекс.Музыки
    # содержит название трека и имя исполнитель
    for album_id in albums_for_spotify:
        try:
            # get album name
            album_title = albums_for_spotify[album_id]['album_title']
            # get artist name
            artist_name = albums_for_spotify[album_id]['artist_name']
            # get search query
            query = ' '.join([artist_name,  album_title])
            # get spotify album id
            album_id = get_album_id(query, sp)
            # add album to user s spotify
            sp.current_user_saved_albums_add(album_id)

        except:
            pass


def get_track_id(query, sp):

    track_id = sp.search(q=query, limit=1, type='track')  # get first spotify track id
    return  track_id['tracks']['items'][0]['id'].split()

def transfer_playlists(yandex_username, playlists_for_spotify):  # transfer playlists from yandex music to spotify

    sp, username = authorization()

    for playlist_name in playlists_for_spotify:  # playlist_for_spotify['playlist_name']['track_name']

        create_spotify_playlist = sp.user_playlist_create(username, playlist_name)  # create 'playlist_name' playlist in spotify
        new_spotify_playlist_id = create_spotify_playlist['id']

        tracks_ids = playlists_for_spotify[playlist_name].keys()

        new_spotify_playlist = {}

        for i in tracks_ids:  #  get tracks' id
            try:
                artist_name = playlists_for_spotify[playlist_name][i]['artist_name']
                track_name = playlists_for_spotify[playlist_name][i]['track_name']

                query = artist_name + ' ' + track_name
                spotify_track_id = get_track_id(query, sp)

                new_spotify_playlist[spotify_track_id[0]] = new_spotify_playlist_id

            except:
                pass

        if all(query == '' for query in new_spotify_playlist.values()):
            sp.user_playlist_unfollow(username, new_spotify_playlist_id)
            continue

        else:
            for new_spotify_playlist_id, track_id in new_spotify_playlist.items():
                sp.playlist_add_items(track_id, new_spotify_playlist_id.split())



def main(yandex_username):

    transfer_playlists(yandex_username, get_liked_on_radio(yandex_username))

if __name__ == '__main__':
    yandex_username = "anton.mel"
    main(yandex_username)

