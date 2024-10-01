from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import SupermarketScraperItem
from scrapy.loader import ItemLoader
import re


class KauflandSpider(CrawlSpider):
    name = "kaufland"
    allowed_domains = ["kaufland.de"]
    start_urls = ["https://www.kaufland.de/lebensmittel/"]

    rules = (
        # Rule to follow pagination links like 'c-N01/1', 'c-N01/2', etc.
        Rule(LinkExtractor(allow=(r'/nahrungsergaenzungsmittel/',))),
        Rule(LinkExtractor(allow=(r'/suessigkeiten/',))),
        Rule(LinkExtractor(allow=(r'/getraenke/',))),
        Rule(LinkExtractor(allow=(r'/haltbare-lebensmittel/',))),
        Rule(LinkExtractor(allow=(r'/oel-und-essig/',))),
        Rule(LinkExtractor(allow=(r'/gewuerze-und-saucen/',))),
        Rule(LinkExtractor(allow=(r'/backwaren/',))),
        Rule(LinkExtractor(allow=(r'/kaese-und-milchprodukte/',))),
        Rule(LinkExtractor(allow=(r'/fleisch-und-fisch/',))),
        # Rule(LinkExtractor(allow=(r'[A-Za-z0-9-]+/',))),

        # Rule to follow category URLs containing 'Content-Kachel+Spirituosen'
        Rule(LinkExtractor(allow=(r'https://www.kaufland.de/product/\d{9}/[.]*',)), callback='parse_item'),
    )

    def parse_item(self, response):
        l = ItemLoader(item=SupermarketScraperItem(), response=response)

        l.add_css("name","h1::attr(title)")

        whole_price = response.css("span.rd-price-information__price::text").get().strip()
        
        if re.search('\xa0', whole_price):
            price = whole_price.replace('\xa0€','').replace(',','.')
            price = float(price)
        else:
            price = whole_price.replace(' €','').replace(',','.')
            price = float(price)
            
        l.add_value("price", price)

        currency = whole_price[-1]

        l.add_value("currency", currency)

        #category = response.css("nav div:last-child a.rd-link>span.rd-link__text::text").get()

        l.add_css("category", "nav div:last-child a.rd-link>span.rd-link__text::text")

        description = response.css("p.rd-buybox-comparison__base-price>span::text").get().replace('\xa0','')

        l.add_value("description", description)

        image_urls = response.css('picture.product-picture>img::attr(src)').get()
        l.add_value('image', image_urls)

        l.add_value("link", response.url)

        return l.load_item()
