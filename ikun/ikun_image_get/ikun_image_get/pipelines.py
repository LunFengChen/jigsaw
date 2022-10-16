# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy

from scrapy.pipelines.images import ImagesPipeline


class IkunImageGetPipeline:
    def process_item(self, item, spider):
        img_src = item['img_src']
        return item


class MyIKunPipeline(ImagesPipeline):  # 使用MyTuPipeline需要安装pillow
    # 图片存储需要到settings配置IMAGES_STORE
    # 1.发送请求
    def get_media_requests(self, item, info):
        url = item['img_src']

        yield scrapy.Request(url=url, meta={'sss': url})  # 直接返回一个请求对象就行，不同于爬虫中的scrapy.Request()中有很多参数

    # 2.图片的存储路径
    def file_path(self, request, response=None, info=None, *, item=None):
        # 准备文件夹，文件名字
        img_path = './ikun_image'
        # 或者 file_name = response.url  # 可能会报错
        # 或者file_name = item['img_src'].spilt('/')[-1] # 这样和下面这样都行
        file_name = request.meta['sss'].split('/')[-1]

        file_path = img_path + '/' + file_name
        return file_path

    # 3，可能对item进行更新
    # 比如把图片的路径存到item中
    def item_completed(self, results, item, info):
        # print(results)
        # print(results[0][1]['path'])

        # 去items里设置好数据结构
        item['path'] = results[0][1]['path']
        print(item)
        return item
