from extractor import Offer
import unittest
from unittest.mock import patch

class TestOfferInicialization(unittest.TestCase):

    def test_incorrect_url_should_raise_error(self):
        self.assertRaises(TypeError, Offer.import_offer_from_url, "www.test.pl")

    def test_wrong_number_of_offer_attributes_should_raise_error(self):
        attributes = [None for _ in range(len(Offer.headers) - 1)]
        self.assertRaises(ValueError, Offer, attributes)
        attributes = [None for _ in range(len(Offer.headers) + 1)]
        self.assertRaises(ValueError, Offer, attributes)

    def test_create_offer_without_rooms_num_attribute(self):
        attributes = [100 for _ in range(len(Offer.headers))]
        for i, attr in enumerate(Offer.headers):
            if attr == 'Rooms':
                attributes[i] = None
            if attr == 'source':
                attributes[i] = 'url'
        offer = Offer(attributes)
        self.assertEqual(None, offer.rooms_num)