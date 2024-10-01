from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import SupermarketScraperItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


class NettoSpider(CrawlSpider):
    name = "netto"
    allowed_domains = ["netto-online.de"]
    start_urls = ['https://www.netto-online.de/lebensmittel/c-N01']


    rules = (
        # Rule to follow pagination links like 'c-N01/1', 'c-N01/2', etc.
        Rule(LinkExtractor(allow=(r'c-N01/\d+',))),

        # Rule to follow category URLs containing 'Content-Kachel+Spirituosen'
        Rule(LinkExtractor(allow=(r'Content-Kachel\+Spirituosen',)), callback='parse_item'),
    )

    def parse_item(self, response):
        l = ItemLoader(item=SupermarketScraperItem(), response=response)

        # Load name, category, and description
        l.add_css("name", "h1.tc-pdp-productname::text")

        # Extract and combine integer and fractional part of the price
        integer_part = response.css('ins.product__current-price > span.prices__ins__inner > span.prices__ins--digits-before-comma::text').get().strip()
        fractional_part = response.css('ins.product__current-price > span.prices__ins__inner > span.prices__ins--digits-before-comma > span.product__current-price--digits-after-comma::text').get()
        if fractional_part:
        # Ensure we don't add an extra dot
            if integer_part.endswith('.'):
                price = f"{integer_part}{fractional_part.strip()}"
            else:
                price = f"{integer_part}.{fractional_part.strip()}"
        else:
            price = integer_part
        price = price.rstrip('–').strip()

        # If price ends with a dot and has no fractional part, remove the dot
        if price.endswith('.'):
            price = price.rstrip('.')
        try:
            price = float(price)
        except ValueError:
            price = None

        l.add_value("price", price)

        currency = "€"
        l.add_value("currency", currency)

        l.default_output_processor = TakeFirst()
        l.add_css("category", 'li.breadcrumb__item:nth-child(3) span[itemprop="name"]::text')

        description = response.css("div.editContent.tc-product-description h2::text").get()

        if description:
            l.add_value("description", description)
        else:
            l.add_value("description", "Sorry, there is no available description for this product")

        l.add_css("image", "img.productImage::attr(src)")

        l.add_value("link", response.url)

        return l.load_item()
