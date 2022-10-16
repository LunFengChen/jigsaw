import scrapy
from scrapy.http.response.html import HtmlResponse
from ikun_image_get.items import IkunImageGetItem
from tqdm import tqdm


class IkunSpider(scrapy.Spider):
    name = 'ikun'
    allowed_domains = ['remeins.com']
    start_urls = ['https://remeins.com/index/resimg/bqb/ikun/1']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, resp: HtmlResponse, **kwargs):
        href_list = resp.xpath('//div[@class="col-xs-12 page"]/a/@href').extract()

        for href in href_list:
            href = resp.urljoin(href)
            yield scrapy.Request(
                url=href,
                callback=self.parse
            )

        image_href = resp.xpath("//div[@class='indexlist']/div/div/img/@src").extract()

        for src in image_href:
            img = IkunImageGetItem()
            img['img_src'] = resp.urljoin(src)

            yield img
