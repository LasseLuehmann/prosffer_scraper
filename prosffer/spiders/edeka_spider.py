from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import SupermarketScraperItem
from scrapy.loader import ItemLoader


class EdekaSpider(CrawlSpider):
    name = "edeka"
    allowed_domains = ["edeka24.de"]
    start_urls = ['https://www.edeka24.de/Lebensmittel/Kaffee-Tee/'] #,'https://www.edeka24.de/Lebensmittel/Getraenke/']

    rules = (
        # Rule(LinkExtractor(allow=(r'/Lebensmittel/Kaffee-Tee/')),),
        # Rule(LinkExtractor(allow=(r'/Lebensmittel/Getraenke/')),),
        # Rule(LinkExtractor(allow=(r'/Lebensmittel/Backen-Desserts/')),),
        # Rule(LinkExtractor(allow=(r'/Lebensmittel/Fruehstueck-Snacks/')),),
        # Rule(LinkExtractor(allow=(r'/Lebensmittel/Wuerzmittel-Bruehen/')),),
        # Rule(LinkExtractor(allow=(r'/Lebensmittel/Sossen/')),),
        # Rule(LinkExtractor(allow=(r'/Lebensmittel/Beilagen/')),),
        # Rule(LinkExtractor(allow=(r'/Lebensmittel/Konserven/')),),
        # Rule(LinkExtractor(allow=(r'/Lebensmittel/Suess-Salzig/')),),
        # Rule(LinkExtractor(allow=(r'/Lebensmittel/Fertiggerichte/')),),

        #Rule(LinkExtractor(allow=r'[A-Za-z]+-*[A-Za-z]*-*[A-Za-z]*')),
        Rule(LinkExtractor(allow=r'/Kaffee-ganze-Bohnen/')),


        Rule(LinkExtractor(allow=r'[A-Za-z0-9-]+/*[A-Za-z0-9-]*\.html'),
             callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        l = ItemLoader(item=SupermarketScraperItem(), response=response)

        name = response.css('h1::text').get().strip()
        l.add_value('name', name)

        price_str = response.css('div.price::text').get().strip()

        if price_str:
            # Remove the currency symbol and replace the comma with a dot
            price_clean = price_str.replace('€', '').replace(',', '.').strip()
            price_float = float(price_clean)  # Convert to float
            l.add_value('price', price_float)

            currency = ''.join([char for char in price_str if not char.isdigit() and char != ',' and char != '.']).strip()
            l.add_value('currency', currency)

        category = response.css('ul li:nth-child(n+2) a::text').get()
        l.add_value("category", category)

        description = response.css('div.listing::text').get().strip()
        l.add_value('description', description)

        image_url = response.css('div.detail-image img::attr(src)').get()
        l.add_value('image', image_url)

        l.add_value("link", response.url)

        return l.load_item()