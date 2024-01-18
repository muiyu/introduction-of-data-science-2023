import scrapy


class DangdangSpider(scrapy.Spider):
    name = 'DangDangs'
    start_urls = ['https://book.dangdang.com/01.54.htm']

    def parse(self, response):
        for DangDang in response.xpath('//ul[@class="product_ul"]/li'):
            new_book_price_sign = DangDang.xpath('.//p[@class="price"]/span/span[@class="sign"]/text()').get()
            new_book_price_num = DangDang.xpath('.//p[@class="price"]/span/span[@class="num"]/text()').get()
            new_book_price_tail = DangDang.xpath('.//p[@class="price"]/span/span[@class="tail"]/text()').get()
            new_book_price = f'{new_book_price_sign}{new_book_price_num}{new_book_price_tail}'
            yield{
                "书籍名称" : DangDang.xpath('.//p[@class="name"]/a/text()').get(),
                "作者" : DangDang.xpath('.//p[@class="author"]/text()').get(),
                "出版日期" : DangDang.xpath('.//p[@class="press_date"]/text()').get(),
                "折扣价" : new_book_price,
            }