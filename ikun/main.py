"""
    1. 爬取kun的照片
    2. 利用jigsaw项目合成想要的图片
"""

import requests


url = "https://cn.bing.com/images/search?q=%E8%94%A1%E5%BE%90%E5%9D%A4%E5%9B%BE%E7%89%87&go=%E6%90%9C%E7%B4%A2&qs=ds&form=QBIR&first=1&tsc=ImageHoverTitle"

headers = {

}
resp = requests.get(url, headers=headers)
