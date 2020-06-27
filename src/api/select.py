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
def createPlayList():
    oauth2 = auth.getOAuth2Session(session.get("user_id"))
    CREATE_PLAYLIST_URI = app.config["CREATE_PLAYLIST_URI1"] \
                        + session.get("user_id") \
                        + app.config["CREATE_PLAYLIST_URI2"]

    data = {"name": "test", "public": "false"}
    headers = {'content-type': 'application/json'}
    response_raw = oauth2.post(CREATE_PLAYLIST_URI, data=json.dumps(data), headers=headers)

    # TODO: 同じ名前のプレイリストが既に存在していれば、プレイリストを作らせない

    return response_raw.text
