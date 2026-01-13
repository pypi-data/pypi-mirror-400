import logging

import valkey

from whee import Interface, ensure_bytes_key

logg = logging.getLogger('whee.valkey')


class ValkeyStore(Interface):
    """Implements whee.Interface for Valkey
    """

    dbno_default = 0

    def __init__(self, passphrase, user=None, host='localhost', port=6379, dbno=None):
        if dbno == None:
            dbno = self.dbno_default
        self.db = valkey.Valkey(host=host, port=port, db=dbno)
        if user != None:
            self.db.auth(user, passphrase)
        self.db.ping()


    def have(self, k):
        k = ensure_bytes_key(k)
        return bool(self.db.get(k))


    def get(self, k):
        k = ensure_bytes_key(k)
        r = self.db.get(k)
        if r == None:
            raise FileNotFoundError()
        logg.debug('valkeystore get {} -> {}'.format(k, r))
        return r


    def put(self, k, v, exist_ok=False):
        k = ensure_bytes_key(k)
        if self.have(k):
            if not exist_ok:
                raise FileExistsError()
            logg.debug('valkeystore put (replace) {} <- {}'.format(k, v))
        else:
            logg.debug('valkeystore put {} <- {}'.format(k, v))
        self.db.set(k, v)


    def delete(self, k):
        k = ensure_bytes_key(k)
        if not self.have(k):
            raise FileNotFoundError
        logg.debug('valkeystore delete {}'.format(k))
        self.db.delete(k)
