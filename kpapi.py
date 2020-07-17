import requests
import string
import random
import uuid
import time
import os
import warnings
import contextlib
from urllib3.exceptions import InsecureRequestWarning
from pprint import pprint


old_merge_environment_settings = requests.Session.merge_environment_settings

@contextlib.contextmanager
def no_ssl_verification():
    opened_adapters = set()

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        # Verification happens only once per connection so we need to close
        # all the opened adapters once we're done. Otherwise, the effects of
        # verify=False persist beyond the end of this context manager.
        opened_adapters.add(self.get_adapter(url))

        settings = old_merge_environment_settings(self, url, proxies, stream, verify, cert)
        settings['verify'] = False

        return settings

    requests.Session.merge_environment_settings = merge_environment_settings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', InsecureRequestWarning)
            yield
    finally:
        requests.Session.merge_environment_settings = old_merge_environment_settings

        for adapter in opened_adapters:
            try:
                adapter.close()
            except:
                pass

class account:

    def __init__(self, email, password, proxies=None):
        self.session = requests.Session()
        self.deviceId = randomHashGen()
        self.auth(email, password, proxies)
            
    def auth(self, email, password, proxies):
        with no_ssl_verification():
            self.session.get(
                "https://track.tiara.kakao.com/queen/footsteps",
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
                    'password' : password,
                    'stay_signed_in' : 'true'
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

            id = self.session.get(
                'https://kapi.kakao.com/v1/user/access_token_info',
                headers = {
                    'Authorization' : 'Bearer ' + self.access_token
                }
            ).json()['id']

            self.session.post(
                'https://api2-page.kakao.com/auth/v3/web/login',
                data = {
                    'deviceId' : self.deviceId,
                    'userId' : id,
                    'accessToken' : self.access_token,
                    'refreshToken' : self.refresh_token
                }
            )

    def refresh(self):

        tokens = self.session.post(
            "https://kauth.kakao.com/oauth/token",
            data = {
                'grant_type' : 'refresh_token',
                'client_id' : '49bbb48c5fdb0199e5da1b89de359484',
                'refresh_token' : self.refresh_token
            }
        ).text

        self.access_token = tokens.split('access_token":"')[1].split('"')[0]

        try:
            self.refresh_token = tokens.split('refresh_token":"')[1].split('"')[0]
        except:
            print("Refresh Token Still OK")

        id = self.session.get(
            'https://kapi.kakao.com/v1/user/access_token_info',
            headers = {
                'Authorization' : 'Bearer ' + self.access_token
            }
        ).json()['id']

        print(self.session.post(
            'https://api2-page.kakao.com/auth/v3/web/login',
            data = {
                'deviceId' : self.deviceId,
                'userId' : id,
                'accessToken' : self.access_token,
                'refreshToken' : self.refresh_token
            }
        ).json())

    def useTicket(self, seriesid, singleid):
        request = self.session.post(
            "https://api2-page.kakao.com/api/v6/store/use/ticket",
            data = {
                'seriesid' : seriesid,
                'singleid' : singleid,
                'deviceId' : self.deviceId
            }
        ).json()
        if(request['result_code'] == 0 or request['result_code'] == 306 or request['result_code'] == -351):
            return True
        else:
            print(request['message'])
            return False

    def getDownloadData(self, singleid):
        return self.session.post(
            "https://api2-page.kakao.com/api/v1/inven/get_download_data/web",
            data = {
                'productId' : singleid,
                'deviceId' : self.deviceId
            }
        ).json()['downloadData']['members']['files']

    def getSingle(self, singleid, firstPage=1):
        downloadData = self.getDownloadData(singleid)
        single = []
        for i in range(firstPage, len(downloadData)):
            single.append(self.getImg(downloadData[i]['secureUrl'], 'page-edge'))
        return single

    def getImg(self, url, target):
        if(target == 'page-edge'): return self.session.get("https://page-edge.kakao.com/sdownload/resource?kid="+ url).content
        if(target == 'dn-img'): return self.session.get("https://dn-img-page.kakao.com/download/resource?kid="+ url).content

def createEpubStructure(title, author="aperso", coverimg=None, cachedir="cache", overwrite=True):
    os.makedirs(cachedir, exist_ok=overwrite)
    os.makedirs(cachedir + "/META-INF", exist_ok=overwrite)
    os.makedirs(cachedir + "/EPUB", exist_ok=overwrite)
    os.makedirs(cachedir + "/EPUB/singles", exist_ok=overwrite)
    id = randomIDGen()
    open(cachedir + "/mimetype", "w").write("application/epub+zip")
    open(cachedir + "/META-INF/container.xml", "w").write(
        '<?xml version="1.0" encoding="EUC-KR"?>'+
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'+
        '<rootfiles>'+
        '<rootfile full-path="EPUB/package.opf" media-type="application/oebps-package+xml" />'+
        '</rootfiles>'+
        '</container>'
    )

    if(coverimg == None):
        open(cachedir + "/EPUB/package.opf", "w").write(
            '<?xml version="1.0" encoding="EUC-KR"?>' +
            '<package version="3.0" unique-identifier="' +
            id +
            '" xmlns="http://www.idpf.org/2007/opf">' +
            '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">' +
            '<dc:identifier id="' +
            id +
            '">urn:uuid:' +
            str(uuid.uuid1()) +
            '</dc:identifier>' +
            '<dc:title>' +
            title +
            '</dc:title>' +
            '<dc:author>' +
            author +
            '</dc:author>' +
            '</metadata>' +
            '<manifest>' +
            '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav" />' +
            '</manifest>' +
            '<spine>' +
            '</spine>' +
            '</package>'
        )
    else:
        open(cachedir + "/EPUB/package.opf", "w").write(
            '<?xml version="1.0" encoding="EUC-KR"?>' +
            '<package version="3.0" unique-identifier="' +
            id +
            '" xmlns="http://www.idpf.org/2007/opf">' +
            '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">' +
            '<dc:identifier id="' +
            id +
            '">urn:uuid:' +
            str(uuid.uuid1()) +
            '</dc:identifier>' +
            '<dc:title>' +
            title +
            '</dc:title>' +
            '<dc:author>' +
            author +
            '</dc:author>' +
            '</metadata>' +
            '<manifest>' +
            '<item id="cover" href="cover.jpg" media-type="image/jpeg" properties="cover-image" />' +
            '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav" />' +
            '</manifest>' +
            '<spine>' +
            '<itemref idref="cover" />'
            '</spine>' +
            '</package>'
        )
        open(cachedir + "/EPUB/cover.jpg", "wb").write(coverimg)


    open(cachedir + "/EPUB/nav.xhtml", "w").write(
        '<?xml version="1.0" encoding="EUC-KR"?>'+
        '<!DOCTYPE html>'+
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">'+
        '<head>'+
        '<title>' + title + '</title>'+
        '</head>'+
        '<body>'+
        '<nav epub:type="toc">'+
        '<h1>"Table of Contents"</h1>'+
        '<ol>'+
        '</ol>'+
        '</nav>'+
        '</body>'+
        '</html>'
    )

def addSingleToEpub(title, single, nameinepub, cachedir="cache"):
    os.makedirs(cachedir + "/EPUB/singles/" + nameinepub, exist_ok=True)
    htmlpart = ""
    for i in range(len(single)):
        open(cachedir + "/EPUB/singles/" + nameinepub + "/" + str(i) + ".jpg", "wb").write(single[i])
        htmlpart = htmlpart + "<img src='" + str(i) + ".jpg' />"
    open(cachedir + "/EPUB/singles/" + nameinepub + "/content.xhtml", "w").write(
        '<?xml version="1.0" encoding="EUC-KR"?>'+
        '<!DOCTYPE html>'+
        '<html xmlns="http://www.w3.org/1999/xhtml">'+
        '<head>'+
        '<title>' + title + '</title>'+
        '</head>'+
        '<body>'+
        htmlpart+
        '</body>'+
        '</html>'
    )
    package = open(cachedir + "/EPUB/package.opf", "r").read().split('</manifest>')
    package[0] = package[0] + '<item id="' + nameinepub +  '" href="singles/' + nameinepub + '/content.xhtml" media-type="application/xhtml+xml" /></manifest>'
    packagespine = package[1].split('</spine>')
    packagespine[0] = packagespine[0] + '<itemref idref="' + nameinepub + '" /></spine>'
    package[1] = "".join(str(i) for i in packagespine)
    open(cachedir + "/EPUB/package.opf", "w").write("".join(str(i) for i in package))
    nav = open(cachedir + "/EPUB/nav.xhtml", "r").read().split('</ol>')
    nav[0] = nav[0] + '<li><a href="singles/' + nameinepub + '/content.xhtml">' + title + '</a></li></ol>'
    open(cachedir + "/EPUB/nav.xhtml", "w").write("".join(str(i) for i in nav))


def seriesToEPUB(accounts, seriesid, firstPage = 1, firstSingle = 0, cachedir = 'cache'):
    seriesinfo = getSeriesInfo(seriesid)
    seriessize = seriesinfo['home']['on_sale_count']
    singles = getSingles(seriesid, "asc", seriessize)['singles']
    createEpubStructure(seriesinfo['home']['title'], seriesinfo['home']['author_name'], getImg(seriesinfo['home']['image_url'], 'dn-img'), cachedir=cachedir)
    if(firstSingle == 0):
        if(seriesinfo['has_free_single'] == True):
            index = seriesinfo['free_single_count']
        else:
            index = 0
        for i in range(index):
            downloadData = getDownloadData(singles[i]['id'])
            print("Downloading " + singles[i]['title'])
            addSingleToEpub(str(singles[i]['title']), getSingle(singles[i]['id'], firstPage=firstPage), str(i), cachedir=cachedir)
    else:
        index = firstSingle

    i = 0
    while(index < len(singles) and i < len(accounts)):
        if(accounts[i].useTicket(seriesid, singles[index]['id'])):
            print("Downloading " + singles[index]['title'])
            addSingleToEpub(str(singles[index]['title']), accounts[i].getSingle(singles[index]['id'], firstPage=firstPage), str(index), cachedir=cachedir)
            index += 1
            time.sleep(1)
        else:
            i += 1

def updateEPUB(accounts, seriesid, firstPage = 1, firstSingle=0, cachedir='cache'):
    seriesinfo = getSeriesInfo(seriesid)
    seriessize = seriesinfo['home']['on_sale_count']
    singles = getSingles(seriesid, "asc", seriessize)['singles']
    if(firstSingle == 0):
        if(seriesinfo['has_free_single'] == True):
            index = seriesinfo['free_single_count']
        else:
            index = 0
        for i in range(index):
            downloadData = getDownloadData(singles[i]['id'])
            print("Downloading " + singles[i]['title'])
            addSingleToEpub(str(singles[i]['title']), getSingle(singles[i]['id'], firstPage=firstPage), str(i), cachedir=cachedir)
    else:
        index = firstSingle

    i = 0
    while(index < len(singles) and i < len(accounts)):
        if(accounts[i].useTicket(seriesid, singles[index]['id'])):
            print("Downloading " + singles[index]['title'])
            addSingleToEpub(str(singles[index]['title']), accounts[i].getSingle(singles[index]['id'], firstPage=firstPage), str(index), cachedir=cachedir)
            index += 1
            time.sleep(1)
        else:
            i += 1

def randomHashGen():
    lettersAndDigits = string.ascii_lowercase + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(32)))

def randomIDGen():
    lettersAndDigits = string.ascii_lowercase + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(6)))

def getImg(url, target):
    if (target == 'page-edge'): return requests.get("https://page-edge.kakao.com/sdownload/resource?kid=" + url).content
    if (target == 'dn-img'): return requests.get("https://dn-img-page.kakao.com/download/resource?kid=" + url).content

def search(keyword):
    return requests.post(
        "https://api2-page.kakao.com/api/v3/store/search",
        data = {
            'word' : keyword
        }
    ).json()["results"][0]["items"]

def getDownloadData(singleid):
    return requests.post(
        "https://api2-page.kakao.com/api/v1/inven/get_download_data/web",
        data={
            'productId': singleid
        }
    ).json()['downloadData']['members']['files']

def getSingle(singleid, firstPage=1):
    downloadData = getDownloadData(singleid)
    single = []
    for i in range(firstPage, len(downloadData)):
        single.append(getImg(downloadData[i]['secureUrl'], 'page-edge'))
    return single

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

def getSeriesInfo(seriesid):
    return requests.post(
        "https://api2-page.kakao.com/api/v5/store/home",
        data = {
            'seriesid' : seriesid
        }
    ).json()

