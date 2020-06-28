"""
    select.py
    ・楽曲名とアーティスト名でspotifyに検索をさせる
    ・検索結果を表示する
    ・検索結果の中からプレイリストに入れたい楽曲を選択する
    ・もし希望の楽曲がない場合、楽曲名、アーティスト名を変更し、再度検索させる
"""

from src import app, utils
from flask import request, session, jsonify
from src.api import auth
import requests
from urllib.parse import quote
import json

@app.route('/search', methods=["GET"])
def getSearchResult():
    """
    アーティスト名と曲名でspotifyに検索をさせ、 検索結果を返す
    """
    artist = request.args.get("artist")
    track = request.args.get("track")

    oauth2 = auth.getOAuth2Session(session.get("user_id"))
    params_str = "q=artist:" + artist + " track:" + track + "&type=track"
    response_raw = oauth2.get(app.config["SEARCH_URI"], params=params_str)

    if response_raw.status_code == 401:
        # unauthorized
        # TODO: 認証を行う
        pass

    response = response_raw.json()

    # アーティスト名、トラック名、アルバム名を取り出して詰め直す
    result = dict()
    result["tracks"] = []

    if len(response["tracks"]) == 0:
        # 検索結果0件
        return jsonify(result)
    
    items = response["tracks"]["items"]
    for item in items:
        track = dict()
        track["artists_name"] = list(map(lambda artist: artist["name"], item["artists"]))
        track["track_name"] = item["name"]
        track["album_name"] = item["album"]["name"]
        result["tracks"].append(track)

    return jsonify(result)

@app.route('/playlist', methods=["GET"])
def createAndAddPlayList():
    """
    プレイリストを作成し、選択した曲を作成したプレイリストに追加
    プレイリストのURL,IDを返す
    """
    # TODO: POSTにして、下記の二変数をbodyから受け取るようにする
    playlist_name = "test4"
    track_uris = ["spotify:track:4iV5W9uYEdYUVa79Axb7Rh","spotify:track:1301WleyT98MSxVHPZCA6M", "spotify:episode:512ojhOuo1ktJprKbVcKyQ"]

    oauth2 = auth.getOAuth2Session(session.get("user_id"))

    # 登録しようとしているプレイリストの名前がダブっていたら
    # TODO: 何かする?(警告でも返す?)
    if isDoubledPlaylistName(oauth2, playlist_name):
        pass

    # プレイリストを作成
    external_url, playlist_id = createPlaylist(oauth2, playlist_name)

    # プレイリストにトラックを追加
    addToPlaylist(oauth2, playlist_id, track_uris)

    return jsonify({"external_url":external_url, "playlist_id": playlist_id})

def addToPlaylist(oauth2, playlist_id,track_uris):
    """
    プレイリストにトラックを追加する
    track_urisはsptify uriのリスト
    成功したら(201)、Trueを返す
    """
    ADD_PLAYLIST_URI = app.config["ADD_PLAYLIST_URI1"] \
                        + playlist_id \
                        + app.config["ADD_PLAYLIST_URI2"]
    
    data = {"uris": track_uris}
    response_raw = oauth2.post(ADD_PLAYLIST_URI, data=json.dumps(data))

    if response_raw.status_code == "201": # created
        return True
    else:
        return False

def createPlaylist(oauth2,playlist_name):
    """
    プレイリストを作成
    プレイリストのURLとidを返す
    """
    CREATE_PLAYLIST_URI = app.config["CREATE_PLAYLIST_URI1"] \
                        + session.get("user_id") \
                        + app.config["CREATE_PLAYLIST_URI2"]

    data = {"name": playlist_name, "public": "false"}
    headers = {'content-type': 'application/json'}
    response_raw = oauth2.post(CREATE_PLAYLIST_URI, data=json.dumps(data), headers=headers)
    response = response_raw.json()

    return response["external_urls"]["spotify"], response["id"]

def isDoubledPlaylistName(oauth2, playlist_name):
    """
    playlistNameと同じ名前を持ったプレイリストが既に存在するかどうか
    """
    return playlist_name in getPlaylistNames(oauth2)

def getPlaylistNames(oauth2):
    """
    存在するプレイリストの名前のリストを返す
    """
    response_raw = oauth2.get(app.config['GET_MY_PLAYLIST_URI'])
    response = response_raw.json()
    items = response["items"]
    existing_playlist_names = list(map(lambda item: item["name"], items))

    return existing_playlist_names


