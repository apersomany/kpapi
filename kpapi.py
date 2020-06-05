import requests
import string
import random
import uuid
import time
import os

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

    def useTicket(self, seriesid, singleid):
        request = self.session.post(
            "https://api2-page.kakao.com/api/v6/store/use/ticket",
            data = {
                'seriesid' : seriesid,
                'singleid' : singleid,
                'deviceId' : self.deviceId
            }
        ).json()
        if(request['result_code'] == 0 or request['result_code'] == 306):
            return True
        else:
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
            single.append(self.getImg(downloadData[i]['secureUrl']), downloadData[i]['target'])
        return single

    def getImg(self, url, target):
        if(target == 'page-edge'): return self.session.get("https://page-edge.kakao.com/sdownload/resource?kid="+ url).content
        if(target == 'dn-img'): return self.session.get("https://dn-img-page.kakao.com/sdownload/resource?kid="+ url).content

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


def singleToEPUB(accounts, seriesid, firstPage = 1, firstSingle = 0):
    seriesinfo = getSeriesInfo(seriesid)
    seriessize = seriesinfo['home']['on_sale_count']
    singles = getSingles(seriesid, "asc", seriessize)['singles']
    createEpubStructure(seriesinfo['home']['title'], seriesinfo['home']['author_name'], getThumbnail(seriesinfo['home']['image_url']))
    if(firstSingle == 0):
        if(seriesinfo['has_free_single'] == True):
            index = seriesinfo['free_single_count']
        else:
            index = 0
        for i in range(index):
            downloadData = getDownloadData(singles[i]['id'])
            print("Downloading " + singles[i]['title'])
            addSingleToEpub(str(singles[i]['title']), getSingle(singles[i]['id']), str(i))
    else:
        index = firstSingle

    i = 0
    while(index < len(singles) and i < len(accounts)):
        if(accounts[i].useTicket(seriesid, singles[index]['id'])):
            print("Downloading " + singles[index]['title'])
            addSingleToEpub(str(singles[index]['title']), accounts[i].getSingle(singles[index]['id']), str(index))
            index += 1
            time.sleep(1)
        else:
            i += 1

def updateEPUB(accounts, seriesid, firstPage = 1, firstSingle=0):
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
            addSingleToEpub(str(singles[i]['title']), getSingle(singles[i]['id']), str(i))
    else:
        index = firstSingle

    i = 0
    while(index < len(singles) and i < len(accounts)):
        if(accounts[i].useTicket(seriesid, singles[index]['id'])):
            print("Downloading " + singles[index]['title'])
            addSingleToEpub(str(singles[index]['title']), accounts[i].getSingle(singles[index]['id']), str(index))
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
    if (target == 'dn-img'): return requests.get("https://dn-img-page.kakao.com/sdownload/resource?kid=" + url).content

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
        single.append(getImg(downloadData[i]['secureUrl']), downloadData[i]['target'])
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

