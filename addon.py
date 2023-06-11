import json
import sys
import xbmc
import xbmcgui
# import web_pdb

def get_artist(tag):

    artistId = get_artist_of_item(tag)

    json_rpc = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "AudioLibrary.GetArtistDetails",
        "params": {
            "artistid": artistId
        }
    }

    query = xbmc.executeJSONRPC(json.dumps(json_rpc))
    response = json.loads(query)

    result = response.get("result", {})
    result = result.get("artistdetails", {})

    return result.get("artist", {})

def get_artist_of_item(tag):

    item_id = tag.getDbId()
    item_type = tag.getMediaType()

    json_rpc = {
        "jsonrpc": "2.0",
        "method": "AudioLibrary.Get{}Details".format(item_type.title()),
        "params": {
            "properties": ["artistid"],
            item_type + "id": item_id
        },
        "id": 1
    }

    query = xbmc.executeJSONRPC(json.dumps(json_rpc))
    response = json.loads(query)

    result = response.get("result", {})
    result = result.get(item_type + "details", {})
    result = result.get("artistid")

    return result[0] if len(result) > 0 else None

def get_songs(artist, album=None):

    xbmc.log("Getting songs for {}...".format(artist), xbmc.LOGINFO)

    filter = {
        "field": "artist",
        "operator": "is",
        "value": artist
    }

    if album is not None:
        filter = add_album_filter(filter, album)

    json_rpc = {
        "id": 1,
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
        }
    }

    query = xbmc.executeJSONRPC(json.dumps(json_rpc))
    response = json.loads(query)
    result = response.get("result", {})

    return result.get("songs", {})

def add_album_filter(filter, album):

    return {
            "and": [
                filter,
                {
                    "field": "album",
                    "operator": "is",
                    "value": album
                }
            ]
    }

def get_playlist(songs):

    xbmc.log("Adding {} songs to playlist...".format(len(songs)), xbmc.LOGINFO)
    playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    playlist.clear()

    for song in songs:
        playlist.add(song["file"])

    return playlist

if __name__ == '__main__':

    tag = sys.listitem.getMusicInfoTag()

#   Does not always work: e. g. Matchbox 20 vs. Matchbox Twenty
#   artist = tag.getArtist()
#   web_pdb.set_trace()

    artist = get_artist(tag)

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
        xbmcgui.Dialog().notification(
            "Context Play", 
            "Songs could not be found.",
            xbmcgui.NOTIFICATION_WARNING)