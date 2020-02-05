import requests, pickle, json, pytesseract
from PIL import Image
from io import BytesIO

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

sessions = requests.session()

def load(input):
    with open(input + '.cjar', 'rb') as f:
        sessions.cookies.update(pickle.load(f))

def getImg(url):
    return requests.get("https://page-edge.kakao.com/sdownload/resource?kid="+ url).content

def getThumbnail(url):
    return requests.get("https://dn-img-page.kakao.com/download/resource?kid=" + url).content

def search(keyword):
    buffer = requests.post("https://api2-page.kakao.com/api/v3/store/search", data={'word' : keyword})
    return json.loads(buffer.text)["results"][0]["items"]

def getSingles(seriesid, order="asc", pagesize="20", page="0"):
    buffer = requests.post("https://api2-page.kakao.com/api/v5/store/singles", data={'seriesid' : seriesid, 'page' : page, 'page_size' : pagesize, 'direction' : order})
    return json.loads(buffer.text)

def singleToText(singleid):
    buffer = sessions.post("https://api2-page.kakao.com/api/v1/inven/get_download_data/web", headers={'content-type' : 'application/x-www-form-urlencoded'}, data={'productId' : singleid})
    buffer = json.loads(buffer.text)["downloadData"]["members"]
    for i in range(1, buffer["totalCount"]):
        return (pytesseract.image_to_string(Image.open(BytesIO(getImg(buffer["files"][i]["secureUrl"]))), lang="kor"))

def jPrint(data):
    print(json.dumps(data, indent=4, sort_keys=True))
