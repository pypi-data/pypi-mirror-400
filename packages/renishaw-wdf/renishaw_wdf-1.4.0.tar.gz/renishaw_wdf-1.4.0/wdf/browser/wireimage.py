from io import BytesIO
from uuid import UUID
from struct import unpack
from typing import BinaryIO
from PIL import Image
from PIL.ExifTags import Base as ExifTagsBase

CLSID_WiREImageCom = UUID('9AEBE77C-3AB7-49A8-84C3-F5E7DBDC5D21')


class WiREImageReadError(Exception):
    """Exception raise during loading of a WiREImage stream."""
    def __init__(self, message):
        super().__init__(message)


def _read_r8(stream) -> float:
    """Read a persisted COM VARIANT double"""
    vt, = unpack('<H', stream.read(2))
    if vt == 5:
        value, = unpack('<d', stream.read(8))
    else:
        raise WiREImageReadError(f'unhandled VARIANT type: {vt}')
    return value


class WiREImage:
    """Class to hold a WiREImage from a stream persistence"""

    def __init__(self, stream: BinaryIO, props: dict = None):
        self._stream = stream
        self.props = props
        self.image = Image.open(stream)
        self.thumb = self.image.resize((16, 16))

    @staticmethod
    def from_stream(stream: BinaryIO):
        """Load a WiREImage from a persisted data stream."""
        clsid = UUID(bytes_le=stream.read(16))
        if clsid != CLSID_WiREImageCom:
            raise WiREImageReadError('unrecognized clsid')

        magic, = unpack('<I', stream.read(4))
        if magic != 0x01eeffc0:
            raise WiREImageReadError('unexpected magic number')

        # TODO: version check

        props = {
            'Objective': _read_r8(stream),
            'Position': (_read_r8(stream), _read_r8(stream)),
            'FoV': (_read_r8(stream), _read_r8(stream))
        }

        type_check = stream.read(4)
        if type_check != b'wjps':
            raise WiREImageReadError('unhandled stream type')

        datalen, = unpack('<Q', stream.read(8))
        data = stream.read(datalen)
        return WiREImage(BytesIO(data), props)
