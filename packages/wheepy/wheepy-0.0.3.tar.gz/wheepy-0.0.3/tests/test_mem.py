import logging
import unittest

from whee.mem import MemStore

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()


class TestMem(unittest.TestCase):

    def setUp(self):
        self.store = MemStore()


    def test_get_put(self):
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
