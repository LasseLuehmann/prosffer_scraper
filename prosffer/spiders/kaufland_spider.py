from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import SupermarketScraperItem
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
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
        l.default_output_processor = TakeFirst()
        l.add_css("category", "nav div:last-child a.rd-link>span.rd-link__text::text")

        description = response.css('div.rd-product-description__top-accordion-content-description p::text').get()

        if description:
            # Clean and strip whitespace
            description = description.strip()

            # Truncate the text to 150 characters or stop at the last period before 150 characters
            if len(description) > 150:
                # Find the last period before 150 characters
                last_period = description[:150].rfind('.')
                if last_period != -1:
                    # Truncate at the last period
                    truncated_description = description[:last_period + 1]
                else:
                    # Truncate at 150 characters if no period is found
                    truncated_description = description[:150]
            else:
                # Use the entire text if it's under 150 characters
                truncated_description = description

            # Add the truncated text to the item
            l.add_value('description', truncated_description)
        else:
            # Handle cases where no description was found
            self.logger.warning(f"No description found for {response.url}")

        image_urls = response.css('picture.product-picture>img::attr(src)').get()
        l.add_value('image', image_urls)

        l.add_value("link", response.url)

        return l.load_item()
