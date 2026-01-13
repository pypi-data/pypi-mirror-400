import logging
import unittest

from whee.couchdb import CouchDBStore

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

class TestCouchDB(unittest.TestCase):

    def setUp(self):
        self.store = CouchDBStore('test', 'ya0JK6)hp')


    def test_get_put(self):
        pass


if __name__ == '__main__':
    unittest.main()
