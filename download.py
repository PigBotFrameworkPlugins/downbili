import json, requests, re, sys
from fake_useragent import UserAgent
sys.path.append("../..")
import go

# 自动最大分辨率 -> 0, 1080p -> 1, 720p -> 2, 480p -> 3, 360p -> 4 ,1080+ -> 5
type = 0
# 编码格式 avc -> 0, hev -> 1
codecs = 0
#cookie
cookie = ''
# 下载大小(Byte为单位，None为全部)
byte = None
# byte = '0-9999'

url1='https://api.bilibili.com/pgc/player/web/playurl?fnval=80&cid={c}'
url2='https://api.bilibili.com/x/player/playurl?fnval=80&avid={a}&cid={c}'

class VideoList:

    headers={
        'User-Agent': '',
        'referer': '',
        'cookie': cookie
    }

    def __init__(self, url, uid, gid, part=[0]):
        self.url=url
        self.uid = uid
        self.gid = gid
        self.part=part
        
    def download(self):
        self.headers['User-Agent'] = str(UserAgent().random)
        try:
            self.html = requests.get(self.url,self.headers).text
        except Exception:
            go.send(self.uid, '链接失败', self.gid)
            return None

        if re.findall(r'\.bilibili\.com/video/BV',self.url) != [] or re.findall(r'\.bilibili\.com/video/av',self.url) != []:
            return self.video()
        elif re.findall(r'\.bilibili\.com/bangumi/play/',self.url) != []:
            return self.bangumi()
        else:
            go.send(self.uid, 'url无效', self.gid)
            return None

    def bangumi(self):
        json_ = json.loads('{'+re.search(r'"epList":\[.+?\]',self.html).group()+'}')
        self.headers['referer']=self.url

        for i in self.part:
            try:
                cid = json_['epList'][i]['cid']
            except Exception:
                go.send(self.uid, '分p不存在', self.gid)
                break
            self.headers['User-Agent'] = str(UserAgent().random)
            js = json.loads(requests.get(url1.format(c=cid),headers=self.headers).text)
            js['referer'] = self.url
            js['part'] = i
            yield js

    def video(self):
        json_ = json.loads('{'+re.search(r'"aid":\d+',self.html).group()+'}')
        aid = json_['aid']
        json_ = json.loads('{'+re.search(r'"pages":\[.+?\]',self.html).group()+'}')
        self.headers['referer']=self.url

        for i in self.part:
            try:
                cid = json_['pages'][i]['cid']
            except Exception:
                go.send(self.uid, '分p不存在', self.gid)
                break
            self.headers['User-Agent'] = str(UserAgent().random)
            js = json.loads(requests.get(url2.format(a=aid,c=cid),headers=self.headers).text)
            js['referer'] = self.url
            js['part'] = i
            yield js
        

class Download:

    headers={
        'User-Agent': '',
        'referer': '',
        'cookie': cookie
    }

    def __init__(self,js, uid, gid):
        self.uid = uid
        self.gid = gid
        self.js=js

    def download(self,path,type = 0,codecs = 0,byte = None):
        self.headers['User-Agent'] = str(UserAgent().random)
        self.headers['referer'] = self.js['referer']
        p = str(self.js['part'])

        if 'data' in self.js:
            self.js=self.js['data']
        else:
            self.js=self.js['result']

        id = self.js['dash']['video'][0]['id']
        if type == 1:
            id = 80
        elif type == 2:
            id = 64
        elif type == 3:
            id = 32
        elif type == 4:
            id = 16
        elif type == 5:
            id = 112
        elif type != 0:
            go.send(self.uid, 'type参数错误', self.gid)
            return None
        code = 'avc'
        if codecs == 1:
            code = 'hev'
        elif codecs != 0:
            go.send(self.uid, 'codecs参数错误', self.gid)
            return None

        js_movie = None
        for i in self.js['dash']['video']:
            if i['id'] == id and re.findall(code,i['codecs']) != []:
                js_movie = i
                break
        js_audio = self.js['dash']['audio'][0]
        if js_movie == None:
            go.send(self.uid, '指定元素相关视频不存在', self.gid)
            return None

        if byte!=None:
            self.headers['range'] = 'bytes='+byte

        vid = self.headers['referer'].split('/')[-1]
        with open(path+vid+'_'+p+'.mp4','wb+') as file1, open(path+vid+'_'+p+'.mp3','wb+') as file2:
            go.send(self.uid, '[CQ:face,id=189] 下载中\n网址:'+vid+'  分p:'+p, self.gid)
            file1.write(requests.get(js_movie['base_url'],headers=self.headers).content)
            file2.write(requests.get(js_audio['base_url'],headers=self.headers).content)
            go.send(self.uid, '[CQ:face,id=161] 下载成功', self.gid)
            videourl = 'https://xzy.center/qqbot/bilivideo/'+str(vid)+'_'+str(p)+'.mp4'
            videopath = '/www/wwwroot/xzydwz/qqbot/bilivideo/'+str(vid)+'_'+str(p)+'.mp4'
            videomessage = '[CQ:video,file='+videourl+']'
            print(videomessage)
            go.send(self.uid, videomessage, self.gid)
            go.send(self.uid, '[CQ:face,id=151] 若视频发送失败请前往：'+videourl, self.gid)