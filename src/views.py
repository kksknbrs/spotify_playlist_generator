import sys
from src import app
from requests_oauthlib import OAuth2Session
from flask import redirect, request, session, url_for
import json
from src.models import AccessToken
import time

@app.route('/')
# DBにアクセストークンが格納されているか確認
# 格納されているアクセストークンは失効していないか確認
def checkStoredAccessToken():
    user_id = session.get("user_id")
    # cookieにユーザーIDの値が格納されてなければ認可を行う
    if user_id == "None":
        authorization_url = getAuthorizationUrl()
        return redirect(authorization_url)

    # 何らかの原因でDBからユーザーIDに対応するレコードがなければ
    # 認可を行う
    query = AccessToken.select() \
                       .where(AccessToken.user_id == user_id) \
                       .limit(1)
    if query.count() == 0:
        authorization_url = getAuthorizationUrl()
        return redirect(authorization_url)

    # 該当するレコードが一件以上ある場合はgetで取得する方が扱いが楽なのでそうする
    token_record = AccessToken.get(AccessToken.user_id == user_id)
    
    # アクセストークンの有効期限が切れていればリフレッシュする
    expires_at = token_record.expires_at
    if expires_at < time.time():
        token = getRefreshToen(token_record.refresh_token)
        token_record.access_token = token["access_token"]
        token_record.refresh_token = token["refresh_token"]
        token_record.expires_at = token["expires_at"]
        token_record.save()
    
    return redirect(url_for("getMyProfile"))
    
# リフレッシュトークンを取得する
def getRefreshToen(refresh_token):
    print(refresh_token, file=sys.stdout)
    oauth = OAuth2Session(client_id=app.config["CLIENT_ID"])
                        
    token = oauth.refresh_token(
        token_url=app.config["REQUEST_ACCESS_TOKEN_URI"], \
        refresh_token=refresh_token, \
        client_id=app.config["CLIENT_ID"], \
        client_secret=app.config["CLIENT_SECRET"])

    return token 

# 認可ページのURLを返す
def getAuthorizationUrl():
    oauth = OAuth2Session(
        client_id=app.config['CLIENT_ID'],
        redirect_uri=app.config['REDIRECT_URI'])
    authorization_url, state = oauth.authorization_url(
        app.config['REQUEST_AUTHORIZATION_URI'])

    return authorization_url

@app.route('/auth/spotify')
# アクセストークンを送り、DBに格納する。
def requestAccessToken():
    code = request.args.get("code")
    oauth = OAuth2Session(client_id=app.config['CLIENT_ID'],
                            redirect_uri=app.config['REDIRECT_URI'])
    # TODO: キャンセルされた時の処理を追加しよう

    # アクセストークンを取得
    token = oauth.fetch_token(
        token_url=app.config['REQUEST_ACCESS_TOKEN_URI'],
        code=code,
        client_secret=app.config["CLIENT_SECRET"]
    )

    # プロフィールを取得する(useridを手に入れたいので)
    profile_raw = oauth.request("GET", app.config["USER_PROFILE_URI"])
    profile = json.loads(profile_raw.text)
    
    # cookieへuseridの値を格納 この値をkeyとしてアクセストークン、リフレッシュトークンを
    # 取得したりする
    session['user_id'] = profile["id"]

    # DBヘ格納
    access_token_record = AccessToken(user_id=profile["id"]
                                    , access_token=token["access_token"]
                                    , refresh_token=token["refresh_token"]
                                    , expires_at=token["expires_at"])
    access_token_record.save()

    return redirect(url_for("getMyProfile"))

@app.route('/profile')
def getMyProfile():
    access_token = getAccessToken(session.get("user_id"))
    d = {}
    d["access_token"] = access_token

    oauth2 = OAuth2Session(token=d)

    me = oauth2.request("GET", "https://api.spotify.com/v1/me")
    text = me.text
    return text

def getAccessToken(user_id):
    query = AccessToken.select() \
                       .where(AccessToken.user_id == user_id) \
                       .limit(1)
    if query.count() == 0:
        return None

    return query[0].access_token

# デバッグ用。コンソールにprintする。
def printStdOut(a):
    print(a, file=sys.stdout)
