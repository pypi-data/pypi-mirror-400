import logging

from whee import Interface, ensure_hex_key

logg = logging.getLogger('memstore')


class MemStore(Interface):
    """Memstore implements the whee.Interface for python dicts in in-process memory.
    """

    def __init__(self):
        self.v = {}
        self.__to_store_key = ensure_hex_key


    def have(self, k):
        k = self.__to_store_key(k)
        return bool(self.v.get(k))


    def get(self, k):
        k = self.__to_store_key(k)
        r = self.v.get(k)
        if r == None:
            raise FileNotFoundError()
        logg.debug('memstore get {} -> {}'.format(k, r))
        return r


    def put(self, k, v, exist_ok=False):
        k = self.__to_store_key(k)
        if self.have(k):
            if not exist_ok:
                raise FileExistsError()
            logg.debug('memstore put (replace) {} <- {}'.format(k, v))
        else:
            logg.debug('memstore put {} <- {}'.format(k, v))
        self.v[k] = v


    def delete(self, k):
        k = self.__to_store_key(k)
        if not self.have(k):
            raise FileNotFoundError
        logg.debug('memstore delete {}'.format(k))
        del self.v[k]


    def start(self):
        raise PermissionError()


    def stop(self):
        raise PermissionError()
