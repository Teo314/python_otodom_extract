import requests
import json
import os
from bs4 import BeautifulSoup

csv_offers_file = 'flat_offers.csv'
txt_offers_file = 'offers.txt'


class Offer:
    headers = ['ID', 'Date', 'Price', 'Currency', 'Area', 'Price per m2', 'Rooms', 'Market', 'URL', 'source']
    instances = {'csv': [], 'txt': [], 'url': []}
    IDs = {'csv': [], 'txt': [], 'url': []}

    @classmethod
    def import_offer_from_url(cls, url, source='url'):

        if not 'otodom.pl' in url:
            raise TypeError(f"Incorrect offer URL: {url}.")

        # extract json file trom url
        html = requests.get(url).text
        json_data = BeautifulSoup(html, 'html.parser').findAll(type="application/json")[0].next

        # import json
        offer_dict = json.loads(json_data)
        offer_properties = offer_dict['props']['pageProps']['ad']
        offer_location = offer_dict['props']['pageProps']['adTrackingData']

        # save offer attributes
        ID = offer_properties['id']
        date_created = offer_properties['dateCreated']
        price, currency, area, price_per_m, rooms, market = None, None, None, None, None, None
        for attr in offer_properties['characteristics']:
            if attr['key'] == 'price': price = attr['value']
            if attr['key'] == 'currency': currency = attr['value']
            if attr['key'] == 'm': area = attr['value']
            if attr['key'] == 'price_per_m': price_per_m = attr['value']
            if attr['key'] == 'rooms_num': rooms = attr['value']
            if attr['key'] == 'market': market = attr['value']

        attributes = [ID, date_created, price, currency, area, price_per_m, rooms, market, url, source]

        offer = Offer(attributes)

        return offer

    # import offers from csv file and return list of them
    @classmethod
    def import_offers_from_csv(cls, csv_file):
        with open(csv_file, 'r') as file:
            offers = []
            for line in file.readlines()[1:]:
                source = 'csv'
                offer = Offer(line.split(',') + [source])
                offers.append(offer)
            return offers

    # import offers from txt file and return list of them
    @classmethod
    def import_offers_from_txt(cls, txt_file):
        with open(txt_file, 'r') as file:
            urls = [line.strip() for line in file.readlines()]
        offers = []
        # import offer from url, delete ID from 'url' source list and add to 'txt' source list
        for url in urls:
            offer = Offer.import_offer_from_url(url, source='txt')
            offers.append(offer)
        return offers

    @classmethod
    def import_offers_from_database(cls):
        pass

    def __init__(self, attributes):
        if not len(attributes) == len(Offer.headers):
            raise ValueError(f"Wrong number of offer attributes. Correct list contains as follows: {Offer.headers}")
        else:
            ID, date_created, price, currency, area, price_per_m, rooms, market, url, source = attributes
            self.ID = ID
            self.date_created = date_created
            self.price = price
            self.currency = currency
            self.area = area
            self.price_per_m = price_per_m
            self.rooms_num = rooms
            self.market = market
            self.url = url
            self.source = source

            Offer.instances[self.source].append(self)
            Offer.IDs[self.source].append(self.ID)

    def __eq__(self, other):
        if not isinstance((other, Offer)):
            raise TypeError(f"Offer object can be compared only with another Offer object.")
        else:
            return self.ID == other.ID

    def is_exist(self, source):
        return self.ID in Offer.IDs[source]

    def export_to_csv(self, csv_file):
        if not os.path.isfile(csv_file) or os.path.getsize(csv_file) == 0:
            with open(csv_file, 'w', newline='') as file:
                file.write(','.join(Offer.headers) + '\n')
        with open(csv_file, 'a', newline='') as file:
            attributes = [self.ID, self.date_created, self.price, self.currency, self.area, self.price_per_m,
                          self.rooms_num, self.market, self.url]
            file.write(','.join(str(attr) for attr in attributes) + '\n')

    def export_to_database(self):
        pass


Offer.import_offers_from_csv(csv_offers_file)
Offer.import_offers_from_txt(txt_offers_file)

for offer in Offer.instances['txt']:
    if offer.is_exist('csv'):
        print(f'Offer ID {offer.ID} exists in csv file. Skipped.')
    else:
        offer.export_to_csv(csv_offers_file)
        print(f'Add offer ID {offer.ID} to csv file.')

