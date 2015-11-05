from unittest import TestCase
from processor import Processor
from search import Search
from datetime import datetime,date,timedelta
import locale

__author__ = 'buzz'


class TestProcessor(TestCase):
    def test_extract_item_id(self):
        # General case
        self.assertEquals(Processor.extract_item_id('http://www.leboncoin.fr/vetements/874884613.htm'), "874884613")
        # We must keep leading 0's
        self.assertEquals(Processor.extract_item_id('http://www.leboncoin.fr/vetements/004884613.htm'), "004884613")
        # Only digits (may evolve one day)
        self.assertIsNone(Processor.extract_item_id('http://www.leboncoin.fr/vetements/00488XXX3.htm'))

    def test_get_item_list_1(self):
        """ Test the process to get 1 page """
        s = Search(search_id=999, label="Test Search",
                   url="http://www.leboncoin.fr/vetements/offres/ile_de_france/occasions/?", )
        p = Processor(s)

        nb_page = 1
        l = p.get_item_list(stop_item=None, max_page=nb_page)
        self.assertIsNotNone(l)
        self.assertEquals(len(l), Processor.nb_ad_per_page * nb_page)

        nb_page = 2
        l = p.get_item_list(stop_item=None, max_page=nb_page)
        self.assertIsNotNone(l)
        self.assertEquals(len(l), Processor.nb_ad_per_page * nb_page)

    def test_get_item_list_2(self):
        s = Search(search_id=999, label="Test Search",
                   url="http://www.leboncoin.fr/materiel_medical/offres/ile_de_france/occasions/?f=a&th=1&location=Blois%2041000")
        p = Processor(s)

        nb_page = 1
        l = p.get_item_list(stop_item=None, max_page=nb_page)
        self.assertIsNotNone(l)
        stop_item = l[20]

        nb_page = 2
        l = p.get_item_list(stop_item=stop_item, max_page=nb_page)
        self.assertIsNotNone(l)
        self.assertEquals(len(l), 20)


class TestProcessor(TestCase):
    def test_parse_date(self):
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        print (date.today().strftime('%e %b %Y'))
        for i in range(30,360,30):
            print (date.today() - timedelta(i)).strftime('%e %b %Y')

        self.assertEquals(Processor.parse_date('28 Oct', '11:00'), datetime.strptime(date.today().strftime('%Y')+'/10/28 11:00',"%Y/%m/%d %H:%M"))
        self.assertEquals(Processor.parse_date('1 oct', '14:27'), datetime.strptime(date.today().strftime('%Y')+'/10/01 14:27',"%Y/%m/%d %H:%M"))
        self.assertEquals(Processor.parse_date('13 sept', '08:15'), datetime.strptime(date.today().strftime('%Y')+'/09/13 08:15',"%Y/%m/%d %H:%M"))

