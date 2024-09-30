from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import SupermarketScraperItem
from scrapy.loader import ItemLoader


class AldiSuedSpider(CrawlSpider):
    name = "aldi_sued"
    allowed_domains = ["aldi-sued.de"]
    start_urls = ['https://www.aldi-sued.de/de/produkte.html']


    rules = (
        Rule(LinkExtractor(allow=(r'/produktsortiment/',))),


        Rule(LinkExtractor(allow=r'https://www\.aldi-sued\.de/de/p\.[a-z0-9-]+\.([0-9]+)\.html'),
             callback='parse_item'),
    )

    def parse_item(self, response):
        l = ItemLoader(item=SupermarketScraperItem(), response=response)

        l.add_css("name","h1::text")

        price = response.css("span.pdp_price__now::attr(data-price)").get()
        try:
            price = float(price)
        except ValueError:
            price = None
        l.add_value("price", price)

        l.add_css("currency", "span.pdp_price__now::attr(data-currency)")

        l.add_css("category", "ol.breadcrumb li:last-child a::text")

        description = response.css("div.infobox ul li::text").getall()
        description_cleaned = [item.strip().replace('\xa0', '') for item in description if item.strip()]
        l.add_value("description", description_cleaned)

        image_urls = response.css('img::attr(src)').getall()
        l.add_value('image', image_urls)

        l.add_value("link", response.url)

        return l.load_item()