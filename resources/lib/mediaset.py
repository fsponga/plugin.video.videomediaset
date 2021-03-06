from phate89lib import rutils
import re
import math

class Mediaset(rutils.RUtils):

    USERAGENT="VideoMediaset Kodi Addon"
    
    def get_prog_root(self):
        self.log('Trying to get the program list', 4)
        url = "http://www.video.mediaset.it/programma/progr_archivio.json"
        data = self.getJson(url)
        return data["programmi"]["group"]

    def get_url_groupList(self,url):
        self.log('Trying to get the groups from program url ' + url, 4)
        if not url.startswith("http"):
          url="http://www.video.mediaset.it"+url
        url=url.replace("archivio-news.shtml","archivio-video.shtml")
        soup=self.getSoup(url)
        container=soup.find("div", class_="page brandpage")
        subparts=container.find_all('section')
        elements = []
        for subpart in subparts:
          name=subpart.find('h2', class_="title")
          if name and name.text.strip():
            elements.append({'title': name.text.strip().encode('utf-8'), 'url': url })
        return elements

    def get_prog_epList(self,url,title):
        self.log('Trying to get the episodes from group url ' + url, 4)
        totres = 0
        count = 0
        page = 1
        arrdata=[]
        maxpage = 200
       	if not url.startswith("http"):
       		url="http://www.video.mediaset.it"+url
        url=url.replace("archivio-news.shtml","archivio-video.shtml")
        soup=self.getSoup(url)
        container=soup.find("div", class_="page brandpage")
        subparts=container.find_all('section')
        elements = []
        for subpart in subparts:
          name=subpart.find('h2')
          if name and name.text.strip() == title:
            slider=subpart.find("div", class_="slider")
            if slider:
              clips=slider.find_all("div", class_="clip")
              for clip in clips:				
                data0=clip.find("div", class_="clip__info")
                data1=data0.find('a')
                data2=clip.find('img')
                data3=data0.find('p')
                arrdata.append({'id': data1['data-vid'],'title': data1['title'], 'thumbs': data2['data-lazy'].replace("310x175","640x360"), 'plot': data3.text.strip().encode('utf-8'), 'url': data1['href'] })
        return arrdata

    def get_prog_seasonList(self,url):
        self.log('Trying to get the seasons from program url ' + url, 4)
        if not url.startswith("http"):
            url="http://www.video.mediaset.it"+url
        url=url.replace("archivio-news.shtml","archivio-video.shtml")
        soup = self.getSoup(url)
        arrdata = []
        container=soup.find("li", class_="season clearfix")
        if container:
          container=container.find("ul")
          ullis=container.find_all("li")
          if ullis:
            for ulli in ullis:
              link=ulli.find("a")
              arrdata.append({"title": link.text.strip().encode('utf-8'), "url": link['href']})
        return arrdata

    def get_global_epList(self,mode,range=0):
        self.log('Trying to get episodes with mode ' + str(mode), 4)
        if mode == 0: 
            url = "http://www.video.mediaset.it/bacino/bacinostrip_1.shtml?page=all"
        elif mode == 1:
            url = "http://www.video.mediaset.it/piu_visti/piuvisti-{range}.shtml?page=all".format(range=range)
        elif mode == 2:
            url = "http://www.video.mediaset.it/bacino/bacinostrip_5.shtml?page=all"

        soup = self.getSoup(url)
        arrdata=[]
        videos = soup.find_all('div',class_='box')
        if videos:
            for video in videos:
                a = video.find('a', {'data-type': 'video'})
                img = a.find('img')
                imgurl = img['data-src']
                res = re.search("([0-9][0-9][0-9][0-9][0-9]+)",imgurl)
                if res:
                    idv = res.group(1)
                else:
                    idv = re.search("([0-9][0-9][0-9][0-9][0-9]+)",a['href']).group(1)
                p = video.find('p', class_='descr')
                arrdata.append({'id': idv,'url':a['href'],'title':img['alt'].encode("utf-8"),'tipo':video['class'],'thumbs':imgurl.replace("176x99","640x360"),'plot':p.text.strip().encode("utf-8")})
        return arrdata

    def get_canali_live(self):
        self.log('Getting the list of live channels', 4)

        url = "https://live1-mediaset-it.akamaized.net/content/hls_clr_xo/live/channel(ch{ch})/index.m3u8"

        arrdata = []

        arrdata.append({'title':"Canale 5", 'url':url.format(ch='01'),'thumbs': "Canale_5.png"})
        arrdata.append({'title':"Italia 1", 'url':url.format(ch='02'),'thumbs': "Italia_1.png"})
        arrdata.append({'title':"Rete 4", 'url':url.format(ch='03'),'thumbs': "Rete_4.png"})
        arrdata.append({'title':"Canale 20", 'url':url.format(ch='25'),'thumbs': "Canale_20.png"})
        arrdata.append({'title':"La 5", 'url':url.format(ch='04'),'thumbs': "La_5.png"})
        arrdata.append({'title':"Italia 2", 'url':url.format(ch='05'),'thumbs': "Italia_2.png"})
        arrdata.append({'title':"Mediaset Extra", 'url':url.format(ch='09'),'thumbs': "Mediaset_Extra.png"})
        arrdata.append({'title':"Top Crime", 'url':url.format(ch='07'),'thumbs': "Top_Crime.png"})
        arrdata.append({'title':"Iris", 'url':url.format(ch='06'),'thumbs': "Iris.png"})
        arrdata.append({'title':"TGCOM24", 'url':url.format(ch='10'),'thumbs': "TGCOM24.png"})
        return arrdata

    def get_stream(self, id):
        self.log('Trying to get the stream with id ' + str(id), 4)

        stream_url = "http://www.video.mediaset.it/html/metainfo.sjson?id={id}".format(id=id)

        url = "http://cdnsel01.mediaset.net/GetCdn.aspx?streamid={id}&format=json".format(id=id)

        jsn = self.getJson(stream_url)

        if "guid" in jsn["video"]:
             stream_id = jsn["video"]["guid"]
        else:
             stream_id = id

        url = "http://cdnsel01.mediaset.net/GetCdn.aspx?streamid={stream_id}&format=json".format(stream_id=stream_id)

        jsn = self.getJson(url)

        if jsn and jsn["state"]=="OK":

            stream = {}
            for vlist in jsn["videoList"]:
                self.log( "videomediaset: streams {url}".format(url=vlist))
                if ( vlist.find(".wmv") > 0): stream["wmv"] = vlist
                if ( vlist.find(".mp4") > 0): stream["mp4"] = vlist
                if ( vlist.find(".f4v") > 0): stream["f4v"] = vlist
                if ( vlist.find(".ism") > 0): stream["smoothstream"] = vlist
            return stream
        return False
