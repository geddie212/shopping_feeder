import requests

# GC API URI structure
URL = f'https://api.digitalriver.com/v1/shoppers/me/products/'
# Params including Digital River public API key + output format
PARAMS = dict(
    apiKey='c31f1790d3914827b124fef09cb21fbd',
    format='json'
)
PARAMS = dict(
    apiKey='c31f1790d3914827b124fef09cb21fbd',
    format='json',
)
class DRAPI:

    def __init__(self, product_id, locale):
        self.product_id = product_id
        self.locale = locale
        PARAMS['locale'] = self.locale
        response = requests.get(url=URL+self.product_id, params=PARAMS)
        self.data = response.json()

    def get_sku(self):
        try:
            return self.data['product']['sku']
        except KeyError:
            return ''

    def get_price(self, currency):
        try:
            value = self.data['product']['pricing']['salePriceWithQuantity']['value']
            return f'{value} {currency}'
        except KeyError:
            return ''

    def get_gtin(self):
        try:
            gtin = self.data['product']['manufacturerPartNumber']
            return gtin
        except KeyError:
            return ''

    def get_inventory_status(self):
        try:
            response = requests.get(url=f'{URL}{self.product_id}/inventory-status', params=PARAMS)
            data = response.json()
            inventory_status = data['inventoryStatus']['productIsInStock']
            if inventory_status == 'true':
                return 'in_stock'
            else:
                return 'out_of_stock'
        except KeyError:
            return ''

