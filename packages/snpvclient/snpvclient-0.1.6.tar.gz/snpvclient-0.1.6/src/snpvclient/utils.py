from hashlib import sha256, md5

"""Utility functions"""

def getMD5(data: str | bytes) -> str:
    """
    Returns the MD5 hash for a file.
    """

    if isinstance(data, str):
        return md5(data.encode()).hexdigest()
    elif isinstance(data, bytes):
        return md5(data).hexdigest()
    else:
        raise TypeError("Data must be string or bytes")

def getSHA256(string: str) -> str:
    """
    Returns the SHA256 hash for a string.
    """

    if isinstance(string, str):
        return sha256(string.encode()).hexdigest()
    else:
        raise TypeError("Data must be string")