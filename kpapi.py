import requests
import string
import random
import json

class account:
    def __init__(self, email, password, proxies=None):
        self.session = requests.Session()
        self.deviceId = randomHashGen()
        self.auth(email, password, proxies)
            
    def auth(self, email, password, proxies):
        self.session.get(
            "https://track.tiara.kakao.com/queen/footsteps",
            proxies=proxies
        )
    
        self.session.get(
            "https://accounts.kakao.com/login",
            proxies=proxies
        )

        self.session.post(
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
        code = self.session.get(
            "https://kauth.kakao.com/oauth/authorize",
            params = {
                'redirect_uri' : 'kakaojs',
                'response_type' : 'code',
                'client_id' : '49bbb48c5fdb0199e5da1b89de359484'
            },
            proxies=proxies
        ).text.split("code: '")[1].split("'")[0]

        tokens = self.session.post(
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

        self.access_token = tokens.text.split('access_token":"')[1].split('"')[0]

        self.refresh_token = tokens.text.split('refresh_token":"')[1].split('"')[0]

        uid = self.session.get(
            "https://kapi.kakao.com/v2/user/me",
            headers = {
                'authorization' : 'bearer ' + self.access_token
            },
            proxies=proxies
        ).text.split('id":')[1].split(',')[0]

        self.session.get(
            "https://page.kakao.com/main",
            params = {
                'loginHash' : self.deviceId,
                'uid' : uid, 'at' : self.access_token,
                'rt' : self.refresh_token
            },
            headers = {
                'referer' : 'https://page.kakao.com/main'
            },
            proxies=proxies
        )

    def refresh(self):
        tokens = self.session.post(
            "https://kauth.kakao.com/oauth/token",
            headers = {
                'referer' : 'https://kauth.kakao.com',
                'content-type' : 'application/x-www-form-urlencoded'
            },
            data = {
                'grant_type' : 'refresh_token',
                'client_id' : '49bbb48c5fdb0199e5da1b89de359484',
                'refresh_token' : self.refresh_token
            }
        ).json()
        
        self.access_token = tokens['access_token']
        if 'refresh_token' in tokens:
            self.refresh_token = tokens['refresh_token']

        uid = self.session.get(
            "https://kapi.kakao.com/v2/user/me",
            headers = {
                'authorization' : 'bearer ' + self.access_token
            }
        ).text.split('id":')[1].split(',')[0]

        self.session.get(
            "https://page.kakao.com/main",
            params = {
                'loginHash' : self.deviceId,
                'uid' : uid, 'at' : self.access_token,
                'rt' : self.refresh_token
            },
            headers = {
                'referer' : 'https://page.kakao.com/main'
            }
        )

    def useTicket(self, seriesid, singleid):
        return self.session.post(
            "https://api2-page.kakao.com/api/v6/store/use/ticket",
            data = {
                'seriesid' : seriesid,
                'singleid' : singleid,
                'deviceId' : self.deviceId
            }
        ).json()

    def getSingle(self, singleid):
        return self.session.post(
            "https://api2-page.kakao.com/api/v1/inven/get_download_data/web",
            data = {
                'productId' : '53192467',
                'deviceId' : self.deviceId
            }
        ).json()['downloadData']['members']['files']
    
    def getImg(self, url):
        return self.session.get("https://page-edge.kakao.com/sdownload/resource?kid="+ url).content

def jsonPrint(data):
    print(json.dumps(data, indent=4, sort_keys=True))
    
def randomHashGen():
    lettersAndDigits = string.ascii_lowercase + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(32)))

def getImg(self, url):
    return requests.get("https://page-edge.kakao.com/sdownload/resource?kid="+ url).content
def getThumbnail(url):
    return requests.get("https://dn-img-page.kakao.com/download/resource?kid=" + url).content

def search(keyword):
    return requests.post(
        "https://api2-page.kakao.com/api/v3/store/search",
        data = {
            'word' : keyword
        }
    ).json()["results"][0]["items"]

def getSingle(self, singleid):
    return requests.post(
        "https://api2-page.kakao.com/api/v1/inven/get_download_data/web",
        data = {
        'productId' : '53192467',
        'deviceId' : self.deviceId
        }
    ).json()['downloadData']['members']['files']

def getSingles(seriesid, order="asc", pagesize="20", page="0"):
    return requests.post(
        "https://api2-page.kakao.com/api/v5/store/singles",
        data = {
            'seriesid' : seriesid,
            'page' : page,
            'page_size' : pagesize,
            'direction' : order
        }
    ).json()
