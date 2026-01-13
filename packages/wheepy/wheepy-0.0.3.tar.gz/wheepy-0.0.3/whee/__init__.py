from .base import Interface


def ensure_hex_key(v):
    """Return hex for bytes, or verify valid hex.

    :param v: Value to check or convert.
    :type v: bytes or str
    :raises: ValueError if invalid hexadecimal value (and not bytes).
    :returns: Corresponding hexadecimal data.
    :rtype: str
    """
    if isinstance(v, bytes):
        return v.hex()
    bytes.fromhex(v)
    return v


def ensure_bytes_key(v): 
    """Return bytes key if hex is given.

    :param v: Value to check or convert.
    :type v: bytes or str
    :returns: Corresponding bytes data
    :rtype: bytes
    """
    if isinstance(v, bytes):
        return v
    return bytes.fromhex(v)
