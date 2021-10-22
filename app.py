from os import kill
from flask import Flask
from flask import request
from pixivpy_async import AppPixivAPI, PixivAPI
from datetime import timedelta, datetime
import requests
import json
import random
import re
import aiohttp
import asyncio
import base64
header = {
  'Referer': 'https://www.pixiv.net',
  }



app = Flask(__name__)

#token自己搞
_TOKEN = "o-HYGiZqb_azny7RSwX7y2uy0Z0JVOu6WHUD9He9Vgk"

# windows系统 去掉注释
# policy = asyncio.WindowsSelectorEventLoopPolicy()
# asyncio.set_event_loop_policy(policy)

class pixiv:
    def __init__(self):
        self.aapi = AppPixivAPI(proxy="http://127.0.0.1:1080")
        self.today = ''
        self.pic_id = []
        self.pic_user_id = []
        self.pic_user_works = []
        self.pic_user_name = []
        self.pic_today = {"day":[], "week":[], "month":[], "day_male":[], "day_female":[], "week_original":[], "week_rookie":[], "day_r18":[], "day_male_r18":[], "day_female_r18":[], "week_r18":[], "week_r18g":[], "day_manga":[], "week_manga":[], "month_manga":[], "week_rookie_manga":[], "day_r18_manga":[], "week_r18_manga":[], "week_r18g_manga":[]}
        self.author_today = {"day":[], "week":[], "month":[], "day_male":[], "day_female":[], "week_original":[], "week_rookie":[], "day_r18":[], "day_male_r18":[], "day_female_r18":[], "week_r18":[], "week_r18g":[], "day_manga":[], "week_manga":[], "month_manga":[], "week_rookie_manga":[], "day_r18_manga":[], "week_r18_manga":[], "week_r18g_manga":[]}
    
    #检查地址是否有效
    def check_url(self, url):
        proxies = {'https': 'http://127.0.0.1:1080'}
        headers = {'referer': 'https://www.pixiv.net'}
        result = requests.get(url, proxies=proxies, headers=headers)
        print(result.status_code)
        if(result.status_code != 200):
            url = re.sub('.jpg', '_master1200.jpg', re.sub('img-original/', 'img-master/', url, count=0, flags=0), count=0, flags=0)
        return url

    #将转换链接为原图
    def large_to_original (self, url):
        result = re.sub('_master1200', '', re.sub('c/600x1200_90_webp/img-master/', 'img-original/', url, count=0, flags=0), count=0, flags=0)
        return result

    #登录
    async def login(self): 
        await self.aapi.login(refresh_token=_TOKEN)

    #获取日期
    def date(self):
        yesterday = datetime.today() + timedelta(-2)
        yesterday_format = yesterday.strftime('%Y-%m-%d')
        return yesterday_format
    
    #搜索tag
    async def search(self, tag, search_type, t):
        if search_type == 1:
            search_target = 'partial_match_for_tags'
        if search_type == 2:
            search_target = 'exact_match_for_tags'
        if search_type == 3:
            search_target = 'title_and_caption'
        await self.login()
        result = await self.aapi.search_illust(tag, search_target)
        pic = []
        author = []
        pic_fin = []
        author_fin = []
        total = 0
        for i in result.illusts:
            pic.append(self.large_to_original(i['image_urls']['large']))
            author.append(i['user']['name'])
            total += 1
        try:
            if t == -1:
                t = random.randint(1,total-1)
            pic_fin.append(pic[t])
            author_fin.append(author[t])
        except:
            pass
        return pic_fin, author_fin

    #搜索画师作品
    async def search_user(self, user_id, a, b):
        pic = []
        author = []
        pic_fin = []
        author_fin = []
        if user_id != self.pic_user_id:
            self.pic_user_id = user_id
            await self.login()
            result = await self.aapi.user_illusts(user_id)
            print(result)
            for i in result.illusts:
                try:
                    pic.append(self.large_to_original(i['image_urls']['large']))
                except:
                    try:
                        pic.append(i['image_urls']['medium'])
                    except:
                        pass
                author.append(i['user']['name'])
            while result.next_url:
                next_qs = self.aapi.parse_qs(result.next_url)
                result = await self.aapi.user_illusts(**next_qs)
                for i in result.illusts:
                    try:
                        pic.append(self.large_to_original(i['image_urls']['large']))
                    except:
                        try:
                            pic.append(i['image_urls']['medium'])
                        except:
                            pass
                    author.append(i['user']['name'])
            print(len(pic))
            self.pic_user_works = pic
            self.pic_user_name = author
            pic_fin = self.pic_user_works[a:b]
            author_fin = self.pic_user_name[a:b]
        else:
            pic_fin = self.pic_user_works[a:b]
            author_fin = self.pic_user_name[a:b]
        return pic_fin, author_fin, len(self.pic_user_works)

    #随机日榜
    async def random(self, typ='day', num=1):
        pic = []
        author = []
        pic_fin = []
        author_fin = []
        k = 0
        if self.pic_today[typ] and self.today == self.date():
            while k < num:
                i = random.randint(0,len(self.pic_today[typ])-1)
                url = self.check_url(self.pic_today[typ][i])
                if url not in pic_fin:
                    pic_fin.append(url)
                    author_fin.append(self.author_today[typ][i])
                    k += 1
        else:
            if self.today != self.date():
                print('day changed, caching new data')
                print('%s to %s'%(self.today, self.date()))
                self.today = self.date()
            await self.login()
            result = await self.aapi.illust_ranking(typ, date=self.date())
            for i in result.illusts:
                try:
                    pic.append(self.large_to_original(i['image_urls']['large']))
                except:
                    try:
                        pic.append(i['image_urls']['medium'])
                    except:
                        pass
                author.append(i['user']['name'])
            while result.next_url:
                next_qs = self.aapi.parse_qs(result.next_url)
                result = await self.aapi.illust_ranking(**next_qs)
                for i in result.illusts:
                    try:
                        pic.append(self.large_to_original(i['image_urls']['large']))
                    except:
                        try:
                            pic.append(i['image_urls']['medium'])
                        except:
                            pass
                    author.append(i['user']['name'])
            print(len(pic))
            self.pic_today[typ] = pic
            self.author_today[typ] = author
            while k < num:
                i = random.randint(0,len(self.pic_today[typ])-1)
                url = self.check_url(self.pic_today[typ][i])
                if url not in pic_fin:
                    pic_fin.append(url)
                    author_fin.append(self.author_today[typ][i])
                    k += 1
        return pic_fin, author_fin


pixiv_api = pixiv()


async def func(session, url):
  fin = bytes()
  print(url)
  proxy = 'http://127.0.0.1:1080'
  #分块存入数据
  async with session.get(url, verify_ssl=False, proxy=proxy) as res:
    print('res ok')
    while True:
      data = await res.content.read(1048576)
      fin = fin + data
      if not data:
        break
    print('finok')
    return fin

async def get_pic(url):
  async with aiohttp.ClientSession(headers=header) as s:
    done = await func(s, url)
    #转换成base64发送
    pic = base64.b64encode(done).decode()
    return pic
    


"""
type    指定类型（有rank和search）
num     指定数量

type=rank
    rank_type   指定排行榜类型
    | 'day'
    | 'week'
    | 'month'
    | 'day_male'
    | 'day_female'
    | 'week_original'
    | 'week_rookie'
    | 'day_r18'
    | 'day_male_r18'
    | 'day_female_r18'
    | 'week_r18'
    | 'week_r18g'
    | 'day_manga'
    | 'week_manga'
    | 'month_manga'
    | 'week_rookie_manga'
    | 'day_r18_manga'
    | 'week_r18_manga'
    | 'week_r18g_manga'

type=search
    tag         指定标签
    search_type 搜索类型（默认是3）
    | 1='partial_match_for_tags'
    | 2='exact_match_for_tags'
    | 3='title_and_caption'

"""

@app.route("/", methods=['GET', 'POST'])
async def get_data():
    if request.method == 'GET':
        data = []
        num = 1
        if request.args.get("type"):
            if request.args.get("type") == 'rank':
                typ = 'day'
                if request.args.get("rank_type"):
                    typ = request.args.get("rank_type")
                if request.args.get("num"):
                    num = int(request.args.get("num"))
                url, author = await pixiv_api.random(typ, num)
                for t, i in enumerate(url):
                    i = "".join(i)
                    pic = await get_pic(i)
                    data.append(author[t])
                    data.append(pic)
                return json.dumps(data)
            if request.args.get("type") == 'search':
                search_type = 1
                tag = request.args.get("tag")
                if request.args.get("num"):
                    num = int(request.args.get("num"))
                else:
                    num = -1
                if request.args.get("search_type"):
                    search_type = int(request.args.get("search_type"))
                url, author = await pixiv_api.search(tag, search_type, num)
                for t, i in enumerate(url):
                    i = pixiv_api.check_url(i)
                    i = "".join(i)
                    pic = await get_pic(i)
                    data.append(author[t])
                    data.append(pic)
                return json.dumps(data)
        else:
            url, author = await pixiv_api.random()
            url = "".join(url)
            pic = await get_pic(url)
            data.append(author)
            data.append(pic)
            return json.dumps(data)
