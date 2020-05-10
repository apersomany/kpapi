import requests
import json
import random
import string
from utils import *

def randomHashGen():
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(32)))

def auth(email, password, accounts, account, proxies=None):
    loginHash = randomHashGen()
    a = requests.Session()
    a.get(
        "https://track.tiara.kakao.com/queen/footsteps",
        proxies=proxies
    )

    a.get(
        "https://accounts.kakao.com/login",
        proxies=proxies
    )

    a.post(
        "https://accounts.kakao.com/weblogin/authenticate.json",
        headers = {
            'referer' : 'https://accounts.kakao.com',
            'content-type' : 'application/x-www-form-urlencoded'
        },
        data = {
            'email' : email,
            'password' : password
        },
        proxies=proxies
    )

    code = a.get(
        "https://kauth.kakao.com/oauth/authorize",
        params = {
            'redirect_uri' : 'kakaojs',
            'response_type' : 'code',
            'client_id' : '49bbb48c5fdb0199e5da1b89de359484'
        },
        proxies=proxies
    ).text.split("code: '")[1].split("'")[0]
    
    tokens = a.post(
        "https://kauth.kakao.com/oauth/token",
        headers = {
            'referer' : 'https://kauth.kakao.com',
            'content-type' : 'application/x-www-form-urlencoded'
        },
        data = {
            'grant_type' : 'authorization_code',
            'client_id' : '49bbb48c5fdb0199e5da1b89de359484',
            'code' : code
        },
        proxies=proxies
    )

    access_token = tokens.text.split('access_token":"')[1].split('"')[0]

    refresh_token = tokens.text.split('refresh_token":"')[1].split('"')[0]

    uid = a.get(
        "https://kapi.kakao.com/v2/user/me",
        headers = {
            'authorization' : 'bearer ' + access_token
        },
        proxies=proxies
    ).text.split('id":')[1].split(',')[0]

    a.get(
        "https://page.kakao.com/main",
        params = {
            'loginHash' : loginHash,
            'uid' : uid, 'at' : access_token,
            'rt' : refresh_token
        },
        headers = {
            'referer' : 'https://page.kakao.com/main'
        },
        proxies=proxies
    )

    accounts[account] = {
        'cookies' : a.cookies,
        'refresh_token' : refresh_token,
        'deviceId' : loginHash
    }

    
    
def refresh(accounts, account):
    a = requests.Session()
    
    a.cookies.update(accounts[account]['cookies'])

    refresh_token = accounts[account]['refresh_token']
    
    tokens = a.post(
        "https://kauth.kakao.com/oauth/token",
        headers = {
            'referer' : 'https://kauth.kakao.com',
            'content-type' : 'application/x-www-form-urlencoded'
        },
        data = {
            'grant_type' : 'refresh_token',
            'client_id' : '49bbb48c5fdb0199e5da1b89de359484',
            'refresh_token' : refresh_token
        }
    ).json()
    
    access_token = tokens['access_token']
    if 'refresh_token' in tokens:
        refresh_token = tokens['refresh_token']

    uid = a.get(
        "https://kapi.kakao.com/v2/user/me",
        headers = {
            'authorization' : 'bearer ' + access_token
        }
    ).text.split('id":')[1].split(',')[0]

    a.get(
        "https://page.kakao.com/main",
        params = {
            'loginHash' : accounts[account]['deviceId'],
            'uid' : uid, 'at' : access_token,
            'rt' : refresh_token
        },
        headers = {
            'referer' : 'https://page.kakao.com/main'
        }
    )

    accounts[account] = {
        'cookies' : a.cookies,
        'refresh_token' : refresh_token,
        'deviceId' : accounts[account]['deviceId']
        
    }
accounts = {}
auth('page030@aperso.iptime.org', '1q2w3e4r', accounts, 30)
print(accounts)
saveAccounts(accounts)
