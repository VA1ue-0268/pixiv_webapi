### 用flask实现的获取pixiv图片链接的api，还在完善中，目前直接访问能获得一个随机日榜图。
#### bot使用方法
```
from base64 import b64decode
from io import BytesIO
#测试用的，最好自己搭建
url ="https://future-world.net:438"
r = requests.get(url)
b64 = b64decode(r.json()[1])

from PIL import Image
pic = Image.open(BytesIO((b64)))
pic.show()
# await bot.send(event, message = MessageSegment.image(f'base64://{b64}'))
```