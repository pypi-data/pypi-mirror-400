import logging
import unittest

from whee.valkey import ValkeyStore

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

class TestValkey(unittest.TestCase):

    def setUp(self):
        self.store = ValkeyStore(124)

    def test_get_put(self):
        # remove the initial delete once we are creating temporary test dbs 
        try:
            self.store.delete(b'foo')
        except:
            pass
        r = self.store.have(b'foo')
        self.assertFalse(r)
        self.store.put(b'foo', b'bar')
        r = self.store.have(b'foo')
        self.assertTrue(r)
        r = self.store.get(b'foo')
        self.assertEqual(r, b'bar')
        r = self.store.get(b'foo'.hex())
        self.assertEqual(r, b'bar')
        with self.assertRaises(FileExistsError):
            self.store.put(b'foo', b'baz')
        self.store.put(b'foo', b'baz', exist_ok=True)
        self.store.delete(b'foo')
        with self.assertRaises(FileNotFoundError):
            self.store.delete(b'foo')


if __name__ == '__main__':
    unittest.main()
