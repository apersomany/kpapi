import requests
import json
import html
import pickle

def loadAccounts():
    return pickle.load(open('accounts', 'rb'))

def saveAccounts(accounts):
    pickle.dump(accounts, open('accounts', 'wb'))
    
def createAccountsFile():
    accounts = {}
    saveAccounts(accounts)

def loadAccount(accounts, account):
    session = requests.Session()
    session.cookies.update(accounts[account]['cookies'])
    return session

def load(input):
    with open(input + '.cjar', 'rb') as f:
        sessions.cookies.update(pickle.load(f))

def getImg(url):
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

def getSingle(singleid, session):
    return requests.get(
        "https://api2-page.kakao.com/api/v1/inven/get_download_data/web",
        data = {
            'productid' : singleid,
            'deviceid' : deviceid
        }
    ).json()

def useTicket(seriesid, singleid, session):
    print(session.post(
        "https://api2-page.kakao.com/api/v6/store/use/ticket",
        data = {
            'seriesid' : seriesid,
            'singleid' : singleid,
            'deviceId' : '5284e8b6574185351c9af6bffed9bdb9'
        }
    ).json())

def jsonPrint(data):
    print(json.dumps(data, indent=4, sort_keys=True))

#print(html.unescape(search('4000년')[0]['title']) + ' : ' + html.unescape(search('4000년')[0]['category']))

