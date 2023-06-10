import json
import sys
import xbmc
import xbmcgui
# import web_pdb

def get_songs(artist, album=None):

    xbmc.log("Getting songs for {}...".format(artist), xbmc.LOGINFO)

    filter = {
        "field": "artist",
        "operator": "is",
        "value": artist
    }

    if album is not None:
        filter = {
            "and": [
                filter,
                {
                    "field": "album",
                    "operator": "is",
                    "value": album
                }
            ]
        }

    jsonRPC = {
        "jsonrpc": "2.0",
        "method": "AudioLibrary.GetSongs",
        "params": {
            "properties": [
                "file"           
            ],
            "filter": filter,
            "sort": {
                "method": "originaldate",
                "order": "ascending"
            }
        },
        "id": 1
    }
        
#   web_pdb.set_trace()
    query = xbmc.executeJSONRPC(json.dumps(jsonRPC))
    response = json.loads(query)
    result = response.get("result", {})

    return result.get("songs", {})

def get_playlist(songs):

    xbmc.log("Adding {} songs to playlist...".format(len(songs)), xbmc.LOGINFO)
    playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    playlist.clear()

    for song in songs:
        playlist.add(song["file"])

    return playlist

if __name__ == '__main__':

    tag = sys.listitem.getMusicInfoTag()
    artist = tag.getArtist()

    if sys.argv[1].endswith("artist"):
        songs = get_songs(artist)
    else:
        album = tag.getAlbum()
        songs = get_songs(artist, album)
    
    if len(songs) > 0:

        playlist = get_playlist(songs)

        if sys.argv[1].startswith("shuffle"):
            xbmc.log("Shuffling playlist...", xbmc.LOGINFO)
            playlist.shuffle()

        xbmc.Player().play(playlist)

    else:
        xbmcgui.Dialog().notification("Context Play", "Songs could not be found.")