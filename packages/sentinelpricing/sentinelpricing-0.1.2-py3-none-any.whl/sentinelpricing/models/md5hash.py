import hashlib


class MD5Hash:
    md5 = None
    filename = None

    def __init__(self, file, chunking=False):

        _md5 = hashlib.md5()

        if chunking:

            while byte_block := file.read(4096):
                _md5.update(byte_block)
        else:
            _md5.update(file.read())

        self.md5 = _md5.hexdigest()

    def __eq__(self, other):
        if isinstance(other, MD5Hash):
            return self.md5 == other.md5
        elif isinstance(other, str):
            return self.md5 == other
        return NotImplemented
