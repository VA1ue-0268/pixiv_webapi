from os import kill
from flask import Flask, jsonify
from flask import request, make_response
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
        #self.author_today = {"day":[], "week":[], "month":[], "day_male":[], "day_female":[], "week_original":[], "week_rookie":[], "day_r18":[], "day_male_r18":[], "day_female_r18":[], "week_r18":[], "week_r18g":[], "day_manga":[], "week_manga":[], "month_manga":[], "week_rookie_manga":[], "day_r18_manga":[], "week_r18_manga":[], "week_r18g_manga":[]}
    
    #检查地址是否有效
    def check_url(self, url):
        proxies = {'https': 'http://127.0.0.1:1080'}
        headers = {'referer': 'https://www.pixiv.net'}
        result = requests.get(url, proxies=proxies, headers=headers)
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
    
    """
    搜索API: tag 榜单 画师(未改)

    统一返回值
    -> [(author, pic_url)]
    
    """
    
    #搜索tag 支持随机n张
    async def search(self, tag, search_type, k=3):
        search_target = {
            1:'partial_match_for_tags',
            2:'exact_match_for_tags',
            3:'title_and_caption'
        }

        await self.login()
        result = await self.aapi.search_illust(tag, search_target[search_type])
        result_list = []
        
        for res_ in result.illusts:
            pic_url = (self.large_to_original(res_['image_urls']['large']))
            author = (res_['user']['name'])
            result_list.append((author, pic_url))

        assert len(result_list) > 0
        if k > len(result_list):
            k = len(result_list)
        # 返回随机的 元组list
        return random.choices(result_list, k=k)


    #随机日榜
    async def random_pic(self, typ='day', num=1):

        if len(self.pic_today[typ])==0 or self.today != self.date():
            # 更新缓存
            if self.today != self.date():
                print('day changed, caching new data')
                print('%s to %s'%(self.today, self.date()))
                self.today = self.date()
            await self.login()
            
            result = await self.aapi.illust_ranking(typ, date=self.date())
            for i in result.illusts:
                try:
                    pic_url = (self.large_to_original(i['image_urls']['large']))
                    author = (i['user']['name'])
                    if (author, pic_url) not in self.pic_today[typ]:
                        self.pic_today[typ].append((author, pic_url))
                except:
                    pass
            # # 翻页
            # while result.next_url:
            #     next_qs = self.aapi.parse_qs(result.next_url)
            #     result = await self.aapi.illust_ranking(**next_qs)
            #     for i in result.illusts:
            #         try:
            #             pic_url = (self.large_to_original(i['image_urls']['large']))
            #             author = (i['user']['name'])
            #             if (author, pic_url) not in self.pic_today[typ]:
            #                 self.pic_today[typ].append((author, pic_url))
            #         except:
            #             pass


        if num > len(self.pic_today[typ]):
            num = len(self.pic_today[typ])
        return random.choices(self.pic_today[typ], k=num)


pixiv_api = pixiv()


async def func(session, url):
  fin = bytes()
  proxy = 'http://127.0.0.1:1080'
  #分块存入数据
  async with session.get(url, verify_ssl=False, proxy=proxy) as res:
    while True:
      data = await res.content.read(1048576)
      fin = fin + data
      if not data:
        break
    
    return fin

async def get_pic(url):
  async with aiohttp.ClientSession(headers=header) as s:
    done = await func(s, url)
    return done
    
def pic2b64(pic):
    return base64.b64encode(pic).decode()


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


async def get_data(request):
    if request.method == 'GET':
        data = []
        num = request.args.get("num", type=int ,default=1)
        type =  request.args.get("type", type=str ,default="rank")
        typ = request.args.get("rank_type",type=str ,default="day")
        search_type = request.args.get("search_type",type=int ,default=1)
        tag = request.args.get("tag", "")

        if type == 'search':
            print('search')
            res_ = await pixiv_api.search(tag, search_type, num)
            for author, url in res_:
                url = pixiv_api.check_url(url)
                url = "".join(url)
                pic = await get_pic(url)
                data.append((author, pic))
        else:
            
            res_ = await pixiv_api.random_pic(typ, num)
            for author, url in res_:
                url = pixiv_api.check_url(url)   
                url = "".join(url)
                pic = await get_pic(url)
                data.append((author, pic))
    
        return data


app = Flask(__name__)
@app.route("/b64", methods=['GET', 'POST'])
async def get_b64(): 
        data = await get_data(request)  
        data_ = {}
        for index, (author, b64) in enumerate(data):
            data_[index] = {
                "author":author,
                "base64":str(b64)
            }
        return jsonify(data_)

@app.route("/image", methods=['GET', 'POST'])
async def get_image(): 
        data = await get_data(request)  
        _, url = random.choice(data)
        respose = make_response(url)
        respose.headers['Content-Type'] = 'image/jpg'
        return (respose) 


app.run(port=6000)