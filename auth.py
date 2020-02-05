import requests, pickle
def auth(email, password, output):
    a = requests.Session()

    a.get("https://track.tiara.kakao.com/queen/footsteps")

    a.get("https://accounts.kakao.com/login")

    a.post("https://accounts.kakao.com/weblogin/authenticate.json", headers={'referer' : 'https://accounts.kakao.com', 'content-type' : 'application/x-www-form-urlencoded'}, data={'email' : email, 'password' : password})

    code = a.get("https://kauth.kakao.com/oauth/authorize", params={'redirect_uri' : 'kakaojs', 'response_type' : 'code', 'client_id' : '49bbb48c5fdb0199e5da1b89de359484'}).text.split("code: '")[1].split("'")[0]

    tokens = a.post("https://kauth.kakao.com/oauth/token", headers={'referer' : 'https://kauth.kakao.com', 'content-type' : 'application/x-www-form-urlencoded'}, data={'grant_type' : 'authorization_code', 'client_id' : '49bbb48c5fdb0199e5da1b89de359484', 'code' : code})

    access_token = tokens.text.split('access_token":"')[1].split('"')[0]

    refresh_token = tokens.text.split('refresh_token":"')[1].split('"')[0]

    uid = a.get("https://kapi.kakao.com/v2/user/me", headers={'authorization' : 'bearer ' + access_token}).text.split('id":')[1].split(',')[0]

    a.get("https://page.kakao.com/main", params={'loginHash' : '5284e8b6574185351c9af6bffed9bdb9', 'uid' : uid, 'at' : access_token, 'rt' : refresh_token}, headers={'referer' : 'https://page.kakao.com/main'})

    with open(output+".cjar", 'wb') as f:
        pickle.dump(a.cookies, f)
    tokenfile = open(output+".rtoken", 'w')
    tokenfile.write(refresh_token)
