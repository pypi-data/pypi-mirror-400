import logging

import couchdb

from whee import Interface, ensure_hex_key

logg = logging.getLogger('whee.couchdb')


class CouchDBStore(Interface):
    """Implements whee.Interface for Apache CouchDB
    """

    dbname_prefix = 'whee-'

    def __init__(self, dbname, passphrase, user='admin', host='localhost', port=5984, ssl=False):
        self.dbname = self.dbname_prefix + dbname
        connstr = 'http'
        if ssl:
            connstr += 's'
        connstr += '://'
        connstr += '{}:{}@{}:{}/'.format(user, passphrase, host, port)
        self.conn = couchdb.Server(connstr)
        try:
            self.db = self.conn.create(self.dbname)
        except couchdb.http.PreconditionFailed:
            self.db = self.conn[self.dbname]


    def get(self, k):
        #try:
        #    self.db.find('selector': {'type': 'wheekv'},
        pass
