import random
import threading
from flask import Flask, render_template, jsonify, request, url_for
from werkzeug.utils import redirect
from PFU_scraper import PFUScraper
from google_feeder import GoogleSheetEditor
import WTForm_settings
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

exporting_threads = {}

app = Flask(__name__)
app.debug = True
bootstrap = Bootstrap(app)

# SECRET KEY SETUP
app.config["SECRET_KEY"] = 'pobycr4ter2iudyrdgdxxdindo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class SyncCheck(db.Model):
    __tablename__ = 'sync_check'
    id = db.Column(db.Integer, primary_key=True)
    is_syncing = db.Column(db.Boolean)
    sync_date = db.Column(db.DateTime)


class CategoryURLs(db.Model):
    __tablename__ = 'category_URLs'
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String)
    locale = db.Column(db.String)
    currency = db.Column(db.String)
    URL = db.Column(db.String)


class SheetyEndpoints(db.Model):
    __tablename__ = 'sheety_endpoints'
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String)
    sheety_URL = db.Column(db.String)
    sheety_authorisation = db.Column(db.String)


def end_point_dict():
    scansnap = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'scansnap').first()
    fujitsu = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'fujitsu').first()
    realforce = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'realforce').first()
    hhkb = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'hhkb').first()
    scansnap_uk = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'scansnap_uk').first()
    realforce_uk = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'realforce_uk').first()
    hhkb_uk = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'hhkb_uk').first()
    fujitsu_uk = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'fujitsu_uk').first()

    sheety_endpoints = dict(
        scansnap=dict(url=scansnap.sheety_URL, header=dict(Authorization=f'Bearer {scansnap.sheety_authorisation}')),
        fujitsu=dict(url=fujitsu.sheety_URL, header=dict(Authorization=f'Bearer {fujitsu.sheety_authorisation}')),
        realforce=dict(url=realforce.sheety_URL, header=dict(Authorization=f'Bearer {realforce.sheety_authorisation}')),
        hhkb=dict(url=hhkb.sheety_URL, header=dict(Authorization=f'Bearer {hhkb.sheety_authorisation}')),
        scansnap_uk=dict(url=scansnap_uk.sheety_URL,
                         header=dict(Authorization=f'Bearer {scansnap_uk.sheety_authorisation}')),
        realforce_uk=dict(url=realforce_uk.sheety_URL,
                          header=dict(Authorization=f'Bearer {realforce_uk.sheety_authorisation}')),
        hhkb_uk=dict(url=hhkb_uk.sheety_URL, header=dict(Authorization=f'Bearer {hhkb_uk.sheety_authorisation}')),
        fujitsu_uk=dict(url=fujitsu_uk.sheety_URL,
                        header=dict(Authorization=f'Bearer {fujitsu_uk.sheety_authorisation}'))
    )

    return sheety_endpoints


def category_URL_dict():
    categories = CategoryURLs.query.all()

    category_URLs = dict()

    for cat in categories:
        category_URLs[f'{cat.brand}_{cat.locale}'] = dict(URL=cat.URL, currency=cat.currency)

    return category_URLs


class ScraperThread(threading.Thread):
    def __init__(self, category_URLs, sheety_endpoints):
        self.progress = ''
        self.category_URLs = category_URLs
        self.sheety_endpoints = sheety_endpoints
        super().__init__()

    def run(self):
        self.progress = 'Deleting ScanSnap Rows'
        delete_scansnap_data = GoogleSheetEditor().delete_rows(google_sheet=self.sheety_endpoints['scansnap']['url'],
                                                               google_authorisation=self.sheety_endpoints['scansnap']
                                                               ['header'])
        self.progress = 'Deleting RealForce Rows'
        delete_realforce_data = GoogleSheetEditor().delete_rows(google_sheet=self.sheety_endpoints['realforce']['url'],
                                                                google_authorisation=self.sheety_endpoints['realforce']
                                                                ['header'])
        self.progress = 'Deleting HHKB Rows'
        delete_hhkb_data = GoogleSheetEditor().delete_rows(google_sheet=self.sheety_endpoints['hhkb']['url'],
                                                           google_authorisation=self.sheety_endpoints['hhkb']
                                                           ['header'])
        self.progress = 'Deleting Fujitsu Rows'
        delete_fujitsu_data = GoogleSheetEditor().delete_rows(google_sheet=self.sheety_endpoints['fujitsu']['url'],
                                                              google_authorisation=self.sheety_endpoints['fujitsu']
                                                              ['header']),
        self.progress = 'Deleting ScanSnap UK Rows'
        delete_scansnap_uk_data = GoogleSheetEditor().delete_rows(
            google_sheet=self.sheety_endpoints['scansnap_uk']['url'],
            google_authorisation=self.sheety_endpoints['scansnap_uk']
            ['header'])

        self.progress = 'Deleting RealForce UK Rows'
        delete_realforce_uk_data = GoogleSheetEditor().delete_rows(
            google_sheet=self.sheety_endpoints['realforce_uk']['url'],
            google_authorisation=self.sheety_endpoints['realforce_uk']
            ['header'])

        self.progress = 'Deleting HHKB UK Rows'
        delete_hhkb_uk_data = GoogleSheetEditor().delete_rows(google_sheet=self.sheety_endpoints['hhkb_uk']['url'],
                                                              google_authorisation=self.sheety_endpoints['hhkb_uk']
                                                              ['header'])

        self.progress = 'Deleting Fujitsu UK Rows'
        delete_fujitsu_uk_data = GoogleSheetEditor().delete_rows(
            google_sheet=self.sheety_endpoints['fujitsu_uk']['url'],
            google_authorisation=self.sheety_endpoints['fujitsu_uk']
            ['header'])

        try:
            for URL in self.category_URLs.items():
                brand = URL[1]['URL'].split('/')[-1]
                country = URL[1]['URL'].split('/')[-3]
                if country == 'en-gb':
                    brand += '_uk'
                scraper = PFUScraper(URL[1]['URL'])
                for job in scraper.scrape_products(URL[1]['currency']):
                    self.progress = job
                uploader = GoogleSheetEditor().add_data(product_data=scraper.id_list,
                                                        google_sheet=self.sheety_endpoints[brand]['url'],
                                                        google_authorisation=self.sheety_endpoints[brand]['header'])
                for job in uploader:
                    self.progress = job
        except TimeoutError:
            self.progress = 'Cannot Connect to Website. Go back and try again'


def locale_dict_maker(query_result):
    locale_dict = []
    for locale in query_result:
        key_name = f'{locale.brand}_{locale.locale}'
        locale_dict.append(dict(brand=locale.brand, locale=locale.locale, currency=locale.currency, URL=locale.URL))
    return locale_dict


@app.route('/', methods=['GET', 'POST'])
def index():
    scansnap_sheety_form = WTForm_settings.SheetyEndPointForm()
    realforce_sheety_form = WTForm_settings.SheetyEndPointForm()
    hhkb_sheety_form = WTForm_settings.SheetyEndPointForm()
    fujitsu_sheety_form = WTForm_settings.SheetyEndPointForm()
    scansnap_uk_sheety_form = WTForm_settings.SheetyEndPointForm()
    realforce_uk_sheety_form = WTForm_settings.SheetyEndPointForm()
    hhkb_uk_sheety_form = WTForm_settings.SheetyEndPointForm()
    fujitsu_uk_sheety_form = WTForm_settings.SheetyEndPointForm()

    scansnap_locale_query = CategoryURLs.query.filter(CategoryURLs.brand == 'scansnap').all()
    scansnap_locale_dict = locale_dict_maker(scansnap_locale_query)

    realforce_locale_query = CategoryURLs.query.filter(CategoryURLs.brand == 'realforce').all()
    realforce_locale_dict = locale_dict_maker(realforce_locale_query)

    hhkb_locale_query = CategoryURLs.query.filter(CategoryURLs.brand == 'hhkb').all()
    hhkb_locale_dict = locale_dict_maker(hhkb_locale_query)

    fujitsu_locale_query = CategoryURLs.query.filter(CategoryURLs.brand == 'fujitsu').all()
    fujitsu_locale_dict = locale_dict_maker(fujitsu_locale_query)

    scansnap_uk_locale_query = CategoryURLs.query.filter(CategoryURLs.brand == 'scansnap_uk').all()
    scansnap_uk_locale_dict = locale_dict_maker(scansnap_uk_locale_query)

    realforce_uk_locale_query = CategoryURLs.query.filter(CategoryURLs.brand == 'realforce_uk').all()
    realforce_uk_locale_dict = locale_dict_maker(realforce_uk_locale_query)

    hhkb_uk_locale_query = CategoryURLs.query.filter(CategoryURLs.brand == 'hhkb_uk').all()
    hhkb_uk_locale_dict = locale_dict_maker(hhkb_uk_locale_query)

    fujitsu_uk_locale_query = CategoryURLs.query.filter(CategoryURLs.brand == 'fujitsu_uk').all()
    fujitsu_uk_locale_dict = locale_dict_maker(fujitsu_uk_locale_query)

    # scansnap form
    scansnap_sheety_form.end_point.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'scansnap').first().sheety_URL
    scansnap_sheety_form.auth_token.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'scansnap').first().sheety_authorisation
    # realforce form
    realforce_sheety_form.end_point.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'realforce').first().sheety_URL
    realforce_sheety_form.auth_token.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'realforce').first().sheety_authorisation
    # HHKB form
    hhkb_sheety_form.end_point.data = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'hhkb').first().sheety_URL
    hhkb_sheety_form.auth_token.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'hhkb').first().sheety_authorisation
    # fujitsu form
    fujitsu_sheety_form.end_point.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'fujitsu').first().sheety_URL
    fujitsu_sheety_form.auth_token.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'fujitsu').first().sheety_authorisation
    # scansnap uk form
    scansnap_uk_sheety_form.end_point.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'scansnap_uk').first().sheety_URL
    scansnap_uk_sheety_form.auth_token.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'scansnap_uk').first().sheety_authorisation
    # realforce uk form
    realforce_uk_sheety_form.end_point.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'realforce_uk').first().sheety_URL
    realforce_uk_sheety_form.auth_token.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'realforce_uk').first().sheety_authorisation
    # HHKB uk form
    hhkb_uk_sheety_form.end_point.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'hhkb_uk').first().sheety_URL
    hhkb_uk_sheety_form.auth_token.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'hhkb_uk').first().sheety_authorisation
    # fujitsu uk form
    fujitsu_uk_sheety_form.end_point.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'fujitsu_uk').first().sheety_URL
    fujitsu_uk_sheety_form.auth_token.data = SheetyEndpoints.query.filter(
        SheetyEndpoints.brand == 'fujitsu_uk').first().sheety_authorisation

    return render_template('index.html', scan_snap_sheety_form=scansnap_sheety_form,
                           scansnap_locale_dict=scansnap_locale_dict, real_force_sheety_form=realforce_sheety_form,
                           hhkb_sheety_form=hhkb_sheety_form, fujitsu_sheety_form=fujitsu_sheety_form,
                           realforce_locale_dict=realforce_locale_dict, hhkb_locale_dict=hhkb_locale_dict,
                           fujitsu_locale_dict=fujitsu_locale_dict, scansnap_uk_locale_dict=scansnap_uk_locale_dict,
                           scansnap_uk_sheety_form=scansnap_uk_sheety_form,
                           realforce_uk_locale_dict=realforce_uk_locale_dict,
                           realforce_uk_sheety_form=realforce_uk_sheety_form, hhkb_uk_sheety_form=hhkb_uk_sheety_form,
                           hhkb_uk_locale_dict=hhkb_uk_locale_dict, fujitsu_uk_sheety_form=fujitsu_uk_sheety_form,
                           fujitsu_uk_locale_dict=fujitsu_uk_locale_dict)


@app.route('/update_fujitsu_UK_sheety', methods=['POST'])
def update_fujitsu_UK_sheety():
    fujitsu_sheety_form_UK = WTForm_settings.SheetyEndPointForm()

    if fujitsu_sheety_form_UK.validate_on_submit():
        fujitsu_sheety_form_UK = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'fujitsu_uk').first()
        fujitsu_sheety_form_UK.sheety_URL = fujitsu_sheety_form_UK.end_point.data
        fujitsu_sheety_form_UK.sheety_authorisation = fujitsu_sheety_form_UK.auth_token.data
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/update_hhkb_UK_sheety', methods=['POST'])
def update_hhkb_UK_sheety():
    hhkb_sheety_form_UK = WTForm_settings.SheetyEndPointForm()

    if hhkb_sheety_form_UK.validate_on_submit():
        hhkb_sheety_form_UK = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'hhkb_uk').first()
        hhkb_sheety_form_UK.sheety_URL = hhkb_sheety_form_UK.end_point.data
        hhkb_sheety_form_UK.sheety_authorisation = hhkb_sheety_form_UK.auth_token.data
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/update_realforce_UK_sheety', methods=['POST'])
def update_realforce_UK_sheety():
    realforce_sheety_form_UK = WTForm_settings.SheetyEndPointForm()

    if realforce_sheety_form_UK.validate_on_submit():
        realforce_uk_post = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'realforce_uk').first()
        realforce_uk_post.sheety_URL = realforce_uk_post.end_point.data
        realforce_uk_post.sheety_authorisation = realforce_uk_post.auth_token.data
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/update_scansnap_UK_sheety', methods=['POST'])
def update_scansnap_UK_sheety():
    scansnap_sheety_form_UK = WTForm_settings.SheetyEndPointForm()

    if scansnap_sheety_form_UK.validate_on_submit():
        scansnap_post = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'scansnap_uk').first()
        scansnap_post.sheety_URL = scansnap_sheety_form_UK.end_point.data
        scansnap_post.sheety_authorisation = scansnap_sheety_form_UK.auth_token.data
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/update_scansnap_sheety', methods=['POST'])
def update_scansnap_sheety():
    scansnap_sheety_form = WTForm_settings.SheetyEndPointForm()

    if scansnap_sheety_form.validate_on_submit():
        scansnap_post = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'scansnap').first()
        scansnap_post.sheety_URL = scansnap_sheety_form.end_point.data
        scansnap_post.sheety_authorisation = scansnap_sheety_form.auth_token.data
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/update_realforce_sheety', methods=['POST'])
def update_realforce_sheety():
    realforce_sheety_form = WTForm_settings.SheetyEndPointForm()

    if realforce_sheety_form.validate_on_submit():
        realforce_post = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'realforce').first()
        realforce_post.sheety_URL = realforce_sheety_form.end_point.data
        realforce_post.sheety_authorisation = realforce_sheety_form.auth_token.data
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/update_hhkb_sheety', methods=['POST'])
def update_hhkb_sheety():
    hhkb_sheety_form = WTForm_settings.SheetyEndPointForm()

    if hhkb_sheety_form.validate_on_submit():
        hhkb_post = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'hhkb').first()
        hhkb_post.sheety_URL = hhkb_sheety_form.end_point.data
        hhkb_post.sheety_authorisation = hhkb_sheety_form.auth_token.data
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/update_fujitsu_sheety', methods=['POST'])
def update_fujitsu_sheety():
    fujitsu_sheety_form = WTForm_settings.SheetyEndPointForm()

    if fujitsu_sheety_form.validate_on_submit():
        fujitsu_post = SheetyEndpoints.query.filter(SheetyEndpoints.brand == 'fujitsu').first()
        fujitsu_post.sheety_URL = fujitsu_sheety_form.end_point.data
        fujitsu_post.sheety_authorisation = fujitsu_sheety_form.auth_token.data
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/update_locale/<string:brand_locale>', methods=['GET', 'POST'])
def update_locale(brand_locale):
    brand = brand_locale.split('_')[0]
    locale = brand_locale.split('_')[1]
    locale_data = CategoryURLs.query.filter(CategoryURLs.brand == brand, CategoryURLs.locale == locale).first()
    form = WTForm_settings.CategoryURLForm()
    update = True

    if request.method == 'POST':
        locale_data.brand = form.brand.data
        locale_data.locale = form.locale.data
        locale_data.currency = form.currency.data
        locale_data.URL = form.URL.data
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('form-basic.html', update=update, locale_data=locale_data, form=form)


@app.route('/add_locale', methods=['GET', 'POST'])
def add_locale():
    form = WTForm_settings.CategoryURLForm()
    locale_data = []
    update = False

    if request.method == 'POST':
        new_locale = CategoryURLs(brand=form.brand.data, locale=form.locale.data, currency=form.currency.data,
                                  URL=form.URL.data)
        db.session.add(new_locale)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('form-basic.html', locale_data=locale_data, form=form, update=update)


@app.route('/delete_locale/<string:brand_locale>', methods=['GET'])
def delete_locale(brand_locale):
    brand = brand_locale.split('_')[0]
    locale = brand_locale.split('_')[1]
    locale_data = CategoryURLs.query.filter(CategoryURLs.brand == brand, CategoryURLs.locale == locale).first()
    db.session.delete(locale_data)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/scrape_products')
def scrape_products():
    global exporting_threads
    thread_id = random.randint(0, 10000)
    sheet_endpoint = end_point_dict()
    category_URL = category_URL_dict()
    exporting_threads[thread_id] = ScraperThread(category_URLs=category_URL, sheety_endpoints=sheet_endpoint)
    exporting_threads[thread_id].start()
    return render_template('fixer.html', thread_id=thread_id)


@app.route('/progress/<int:thread_id>')
def progress(thread_id):
    global exporting_threads
    try:
        return jsonify(result=str(exporting_threads[thread_id].progress))
    except KeyError:
        return jsonify(result='Products are not being pushed to Google Feeds. Go back home to start the process')


if __name__ == '__main__':
    app.run()
