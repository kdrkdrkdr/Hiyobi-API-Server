# ㄹㅇ 생각없이 만든 히요비 api ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ
# 진짜 왜 만든거지 ㅋㅋㅋ


from flask import Flask, jsonify, request
from requests.adapters import HTTPAdapter
from requests import Session, exceptions
from urllib.parse import urlparse
from queue import Queue
from threading import Thread
from bs4 import BeautifulSoup


class _Enable_SNI_Adapter(HTTPAdapter):

    def send(self, request, **kwargs):
        connection_pool_kwargs = self.poolmanager.connection_pool_kw
        result = urlparse(request.url)
        DNSADDR = '1.1.1.1'
        
        if result.scheme == 'https' and DNSADDR:
            request.url = request.url.replace(
                'https://' + result.hostname,
                'https://' + DNSADDR,
            )

            connection_pool_kwargs['server_hostname'] = result.hostname 
            connection_pool_kwargs['assert_hostname'] = result.hostname
            request.headers['Host'] = result.hostname

        else:
            connection_pool_kwargs.pop('server_hostname', None)
            connection_pool_kwargs.pop('assert_hostname', None)

        return super(_Enable_SNI_Adapter, self).send(request, **kwargs)



baseURL = 'https://hiyobi.me'

s = Session()

s.mount('https://', _Enable_SNI_Adapter())

hParser = 'html.parser'

header = {
    'User-agent' : 'Mozilla/5.0',
    'Referer' : baseURL,
}

def GetSoup(queue, url):
    while True:
        try:
            html = s.get(url, headers=header).text
            soup = BeautifulSoup(html, hParser)
            break
        except (exceptions.ChunkedEncodingError, exceptions.SSLError, exceptions.Timeout, exceptions.ConnectionError):
            pass
    queue.put(soup)



def FastGetSoup(url):

    q = Queue()
    t = Thread(target=GetSoup, args=(q, url, ))
    t.start()

    soupObj = q.get()
    t.join()

    t._stop()

    return soupObj



def GetIMGsURL(g_num):
    jsonURL = baseURL + f'/data/json/{g_num}_list.json'
    imgURL = baseURL + f'/data/{g_num}/'
    
    while True:
        try: reqObj = s.get(jsonURL, headers=header, ).json(); break
        except: pass

    ListOfIMGsURL = [imgURL + i['name'] for i in reqObj]
    return str(ListOfIMGsURL)


def cleanStr(string, delList=[]):
    for d in delList:
        string = string.replace(d, '')

    return string


def GetGalleryInfo(g_num):
    infoURL = baseURL + f"/info/{g_num}"
    infoJson = {}
    soup = FastGetSoup(infoURL)

    infoString = "\n"
    infoContainer = soup.find('div', {'class':'gallery-content row'})
    galleryInfos = infoContainer.find_all('tr')
    
    title = infoContainer.find('h5').text

    for gInfo in galleryInfos:
        info = gInfo.find_all('td')
        infoJson[cleanStr(info[0].text, delList=[':', ' '])] = info[1].text

    return infoJson


def GetSearchResult(kWord, page):
    soup = FastGetSoup(f"https://hiyobi.me/search/{kWord}/{page}")
    mainContainer = soup.find('main', {'class':'container'}).find_all('h5')
    sResult = {}

    if mainContainer == []:
        return "검색 결과가 없습니다."
    else:
        for i in mainContainer:
            sTitle = i.a.text
            sLink = i.a['href']
            sResult[sTitle] = sLink

        return sResult 
        


app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False


@app.route('/', methods=['GET'])
def index():
    return '히요비(hiyobi.me) API 서버입니다. 제작자 : kdr (https://github.com/kdrkdrkdr/Hiyobi-API-Server)'
        

@app.route('/hiyobi/galleries/<int:g_num>', methods=['GET'])
def GalleriesInfo(g_num):
    return jsonify(
        {
            'gallery_info' : GetGalleryInfo(g_num=g_num),
            'images_url' : GetIMGsURL(g_num=g_num),
        }
    )


@app.route('/hiyobi/search/<string:kWord>/<int:page>', methods=['GET'])
def GallerySearch(kWord, page):
    return jsonify(
        {
            'search_result' : GetSearchResult(kWord, page)
        }
    )


if __name__ == '__main__':
    print('\nMade by 김경민\n\n')
    print('\n갤러리 정보 : http://127.0.0.1/hiyobi/galleries/히요비_갤러리_번호')
    print('\n갤러리 찾기 : http://127.0.0.1/hiyobi/search/검색어/페이지\n\n')
    app.run()