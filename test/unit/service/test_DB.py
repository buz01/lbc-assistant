from unittest import TestCase

__author__ = 'buzz'
from service.db import DB


class TestDB(TestCase):
    def test_find_search_by_id(self):
        my_search_id = 1
        db = DB()
        search = db.find_search_by_id(my_search_id)
        if search is not None:
            self.assertEquals(search.search_id, my_search_id)
        else:
            self.fail()
