from PFU_scraper import PFUScraper
from google_feeder import GoogleSheetEditor

sheety_endpoints = dict(fujitsu=dict(url='https://api.sheety.co/41c3cf738c4f0093959c15c5a2c4a68d/fujitsuAutomatedFeed/sheet1', header=dict(Authorization=f'Bearer 97e83126b7e32byne71d312r')))

category_URLs = dict(
    fujitsu_de=dict(URL='https://www.pfuemea.com/de-de/dr_product_category/fujitsu', currency='EUR'))

brand = 'fujitsu'
scraper = PFUScraper('https://www.pfuemea.com/de-de/dr_product_category/fujitsu')
for job in scraper.scrape_products('EUR'):
    progress = job
    print(progress)
print(scraper.id_list)
uploader = GoogleSheetEditor().add_data(scraper.id_list, 'https://api.sheety.co/41c3cf738c4f0093959c15c5a2c4a68d/fujitsuAutomatedFeed/sheet1',
                                            dict(Authorization=f'Bearer 97e83126b7e32byne71d312r'))
for job in uploader:
    progress = job
    print(progress)


# for URL in category_URLs.items():
#     brand = URL[1]['URL'].split('/')[-1]
#     scraper = PFUScraper(URL[1]['URL'])
#     for job in scraper.scrape_products(URL[1]['currency']):
#         progress = job
#         print(progress)
#     print(scraper)
#     uploader = GoogleSheetEditor().add_data(scraper.id_list, sheety_endpoints[brand]['url'],
#                                             sheety_endpoints[brand]['header'])
#     for job in uploader:
#         progress = job
#         print(progress)



