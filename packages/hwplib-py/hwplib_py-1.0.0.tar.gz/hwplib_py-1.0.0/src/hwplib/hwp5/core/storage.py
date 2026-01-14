import zlib
import io
from typing import BinaryIO, Optional

# Try importing olefile, but handle failure gracefully
try:
    import olefile
except ImportError:
    olefile = None

class StorageReader:
    """
    Abstracts the OLE2 storage and Zlib decompression.
    """
    def __init__(self, filename_or_stream):
        self._ole = None
        if olefile:
            try:
                self._ole = olefile.OleFileIO(filename_or_stream)
            except:
                pass # Not an OLE file or error opening
        
        # If not OLE, maybe it's a raw stream for testing?
        # In production, HWP 5.0 is strictly OLE.

    def is_ole(self) -> bool:
        return self._ole is not None

    def list_streams(self):
        if self._ole:
            return self._ole.listdir()
        return []

    def get_stream_data(self, stream_name: str, decompress: bool = False) -> bytes:
        """
        Reads a stream.
        """
        if not self._ole:
            raise NotImplementedError("OLE support requires 'olefile' library or a valid OLE file.")
        
        if not self._ole.exists(stream_name):
            raise FileNotFoundError(f"Stream {stream_name} not found in container.")
        
        with self._ole.openstream(stream_name) as f:
            data = f.read()
        
        if decompress:
            # HWP compression is raw Deflate (zlib without header usually, or standard zlib)
            # -15 for raw deflate is common in zip, HWP uses standard zlib?
            # Creating a decompress object to handle potential stream issues.
            try:
                return zlib.decompress(data, -15) # Raw inflation
            except zlib.error:
                try:
                    return zlib.decompress(data) # Standard zlib
                except zlib.error:
                    return data # Fallback?
        return data

    def close(self):
        if self._ole:
            self._ole.close()
