from typing import BinaryIO

class Hwp3Parser:
    """
    Parser for Legacy HWP 3.0 Binary format.
    """
    SIGNATURE = b"HWP Document File V3.00"

    def __init__(self, stream: BinaryIO):
        self.stream = stream

    def is_valid(self) -> bool:
        """
        Checks if the stream is a valid HWP 3.0 file.
        """
        start_pos = self.stream.tell()
        sig = self.stream.read(len(self.SIGNATURE))
        self.stream.seek(start_pos)
        return sig == self.SIGNATURE

    def parse(self):
        if not self.is_valid():
            raise ValueError("Invalid HWP 3.0 Signature")
        
        # 1. Read Header (Signature + 30 bytes reserved + etc)
        self.stream.read(len(self.SIGNATURE))
        
        # TODO: Implement 3.0 specific parsing logic
        # - Info Blocks
        # - Font Blocks
        # - Spec Blocks
        # - Body Text (1-byte control codes)
        pass
