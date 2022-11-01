import requests
from bs4 import BeautifulSoup
from loading_bar import ProgressBar
from dr_api import DRAPI
import config

progress = config.progress


class ProductScraper:

    def __init__(self, product_URL):
        self.product_URL = product_URL
        response = requests.get(url=self.product_URL)
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def get_image_URL(self):
        div_tag = self.soup.find_all('div', {'class': 'media m-4 m-lg-0 product-image-wrapper'})
        try:
            img_link = f'''https://www.pfuemea.com{div_tag[0].img['src']}'''
        except TypeError:
            img_link = ''
        return img_link

    def get_product_attributes(self):
        try:
            div_tag = self.soup.find_all('div', {'class': 'product-details'})
            product_attributes = div_tag[0].ul.find_all('li')
            product_highlight = ''
            for att in product_attributes:
                product_highlight += f'"{att.text}",'
            return product_highlight
        except AttributeError:
            return ''

    def get_product_category(self, brand):
        if brand.lower() == 'scansnap' or brand.lower() == 'fujitsu':
            return '''Electronics > Print, Copy, Scan & Fax > Scanners'''
        elif brand.lower() == 'hhkb' or brand.lower() == 'realforce':
            return '''Electronics > Electronics Accessories > Computer Components > Input Devices > Keyboards'''

    def get_product_condition(self):
        return 'new'

    def get_sale_price(self):
        return ''

    def get_sale_price_date(self):
        return ''

    def get_shipping_info(self, locale, currency):
        return f'{locale}:::0.00 {currency}'


class PFUScraper:

    def __init__(self, category_URL):
        self.category_URL = category_URL
        response = requests.get(url=self.category_URL)
        self.soup = BeautifulSoup(response.text, 'html.parser')
        self.brand = self.category_URL.split('/')[-1]
        self.locale = self.locale_formatter()
        self.id_list = []

    def locale_formatter(self):
        locale_formatter = self.category_URL.split('.com/')
        locale_formatter = locale_formatter[1].split('/')
        locale_formatter = locale_formatter[0].split('-')
        locale_formatter = f'{locale_formatter[0]}_{locale_formatter[1]}'
        return locale_formatter

    def scrape_products(self, currency):
        global progress
        data_pid = self.soup.select('[data-pid]')
        id_list = []
        current_record = 1
        total_records = len(data_pid)
        progress = f'{total_records} total products found for the brand: {self.brand}, ' \
                   f'on PFUE ({self.locale[-2:].upper()})'
        yield progress
        loading_bar = ProgressBar(data_pid)
        for product_id in data_pid:
            URL = product_id.find('a').get('href')
            product_name = product_id.find(attrs={'class': 'title'}).text
            description = product_id.find('p').text
            brand = self.brand
            dr_id = product_id.unwrap().get('data-pid')

            dr_data = DRAPI(dr_id, f'{self.locale}')
            sku = dr_data.get_sku()
            price = dr_data.get_price(currency)
            availability = dr_data.get_inventory_status()
            gtin = dr_data.get_gtin()

            product_URL = f'''https://www.pfuemea.com{URL}'''
            product_scraper = ProductScraper(product_URL)
            product_category = product_scraper.get_product_category(brand)
            product_highlight = product_scraper.get_product_attributes()
            product_image = product_scraper.get_image_URL()
            condition = product_scraper.get_product_condition()
            sale_price = product_scraper.get_sale_price()
            sale_price_date = product_scraper.get_sale_price_date()
            shipping = product_scraper.get_shipping_info(locale=self.locale[-2:].upper(), currency=currency)

            try:
                if '.' not in price:
                    price_fixer = price.split(' ')
                    price = f'{price_fixer[0]}.00 {price_fixer[1]}'
            except IndexError:
                price = 'NA'

            progress = loading_bar.print_progress_bar(current_record, f'{brand} products downloaded from PFUE website '
                                                                      f'({self.locale[-2:].upper()})')
            yield progress
            current_record += 1
            if sku != '':
                self.id_list.append(dict(
                    product_name=product_name,
                    description=description,
                    brand=brand,
                    id=dr_id,
                    url=product_URL,
                    sku=sku,
                    price=price,
                    product_category=product_category,
                    product_highlight=product_highlight,
                    product_image=product_image,
                    condition=condition,
                    sale_price=sale_price,
                    sale_price_date=sale_price_date,
                    mpn=sku,
                    availability=availability,
                    gtin=gtin,
                    shipping=shipping
                ))
