import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from xacbank.items import Article


class xacbankSpider(scrapy.Spider):
    name = 'xacbank'
    start_urls = ['https://www.xacbank.mn/news/news']

    def parse(self, response):
        articles = response.xpath('//div[@class="news-item"]')
        for article in articles:
            link = article.xpath('.//h4/a/@href').get()
            date = article.xpath('.//span/text()').get()
            if date:
                date = " ".join(date.split())

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@rel="next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h3[@class="text-orange text-semibold"]/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="maintext fr-view news-detail"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
