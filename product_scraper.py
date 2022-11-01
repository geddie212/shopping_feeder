import requests
from bs4 import BeautifulSoup


class ProductScraper:

    def __init__(self, product_URL):
        self.product_URL = product_URL
        response = requests.get(url=self.product_URL)
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def get_image_URL(self):
        div_tag = self.soup.find_all('div', {'class': 'media m-4 m-lg-0 product-image-wrapper'})
        img_link = f'''https://www.pfuemea.com{div_tag[0].img['src']}'''
        return img_link

    def get_product_attributes(self):
        div_tag = self.soup.find_all('div', {'class': 'product-details'})
        product_attributes = div_tag[0].ul.find_all('li')
        product_highlight = ''
        for att in product_attributes:
            product_highlight += f'"{att.text}",'
        return product_highlight

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

    def get_shipping_info(self):
        return 'GB:::0.00 GBP'


