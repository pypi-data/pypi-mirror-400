class Interface:
    """This is Interface class abstracts transactional store operations on key-value-based backends.
    """

    def get(self, k):
        """Retrieve value for key.

        :raises: FileNotFoundError if key does not exist.
        :raises: ConnectionRefusedError if store is locked.
        :raises: IOError if key is found but read fails for any reason.
        :returns: Value
        :rtype: bytes
        """
        raise NotImplementedError()


    def put(self, k, v, exist_ok=False):
        """Retrieve value for key.

        :raises: ValueError if value is in a format that cannot be stored.
        :raises: ConnectionRefusedError if store is locked.
        :raises: FileExistsError if key already exists and exist_ok is not True.
        :raises: IOError if value is valid and key is available, but write fails for any other reason.
        :returns: Value
        :rtype: bytes
        """
        raise NotImplementedError()


    def have(self, k):
        """Check if key exists in store.

        :raises: FileNotFoundError if key does not exist.
        :raises: ConnectionRefusedError if store is locked.
        :raises: IOError if value is valid and key is available, but write fails for any other reason.
        """
        raise NotImplementedError()


    def start(self):
        """Start a store transaction.

        :raises: ConnectionError if the transaction cannot be made due to missing connection with the backend.
        :raises: ConnectionRefusedError if store is locked.
        :raises: PermissionError if a transaction is already in place, and/or the backend does not support (multiple) transactions.
        :raises: IOError if lock cannot be placed for any other reason.
        """
        raise NotImplementedError()


    def stop(self):
        """Commit and end a store transaction.

        :raises: ConnectionError if no transaction exists.
        :raises: ConnectionRefusedError if store is locked.
        :raises: ConnectionAbortedError if transaction could not be committed. After this, the transaction has been dropped.
        :raises: IOError if transaction abort fails for any reason (transaction will still be pending).
        """
        raise NotImplementedError()


    def delete(self, k):
        """Delete key and its corresponding value. This action is not reversible.

        :raises: FileNotFoundError if key does not exist.
        :raises: ConnectionRefusedError if store is locked.
        :raises: IOError if key is valid but operation fails for any other reason.
        """
        raise NotImplementedError()


    def lock(self):
        """Lock the store for any operation by any process.

        :raises: ConnectionRefusedError if store is already locked.
        :raises: IOError if lock fails for any other reason.
        """
        raise NotImplementedError()


    def abort(self):
        """Stop a store transaction without committing.

        :raises: ConnectionError if no transaction exists.
        :raises: ConnectionRefusedError if store is locked.
        :raises: IOError if transaction abort fails for any reason (transaction will still be pending).
        """
        raise NotImplementedError()


    def flush(self):
        """Write changes to store and unlock.

        :raises: IOError if write fails for any reason.
        """
        raise NotImplementedError()


    def cap(self):
        """Return bytes available for storage.

        :raises: IOError if query fails for any reason.
        """
        return 0
