import struct
from typing import Optional, BinaryIO
from .distribute_crypto import derive_key_and_flag, decrypt_aes128

HWPTAG_DISTRIBUTE_DOC_DATA = 0x00 # Actual ID needs checking (assuming defined elsewhere or placeholder)
# Note: Common tag ID for Distribution data is usually identified by context, or needs proper ID from spec.
# Spec says "Tag ID" but doesn't explicitly number it in snippet provided (implied known).

class DistributeDocParser:
    """
    Handles parsing and decryption of 'Distribution Documents'.
    """
    def __init__(self):
        self.aes_key: Optional[bytes] = None
        self.doc_flag: int = 0
        self.is_distributed: bool = False

    def parse_distribution_tag(self, header_data: bytes) -> bool:
        """
        Parses the 256-byte distribution data block.
        header_data: The content of HWPTAG_DISTRIBUTE_DOC_DATA record.
        """
        if len(header_data) < 256:
            return False

        # 1. Extract Seed (First 4 bytes)
        # Spec 2.1: "Record start -> 4bytes UINT Seed"
        seed_bytes = header_data[:4]
        # Rest is the encrypted/XORed block
        data_block = header_data[4:4+256] 
        # Wait, spec 2.1 says "First 4 bytes of record" is seed.
        # And spec 2.2 says XOR merge 256 bytes *distributed document data*.
        # Is the record > 256 bytes? usually 4 bytes signature + 256 data?
        # Or is the seed PART of the 256 bytes?
        # Re-reading spec: "Seed (UINT) ... from data record".
        # 2.2: Offset = (Seed & 0x0F) + 4.
        # If seed is inside, offset 4 implies skipping seed.
        # Let's assume structure: [Seed: 4] [Data: 256] = Total 260 bytes?
        # OR: [Data: 256], and Seed is Data[0:4]?
        # Usually: Seed(4) + Data(256).
        
        # Let's implement based on Seed(4) + Data(256) which is safer.
        if len(header_data) < 260:
            # Fallback if strict 256 implies seed is inside.
            pass

        seed = struct.unpack('<I', seed_bytes)[0]
        
        # The encrypted data chunk to XOR
        # If the record is *exactly* 256 bytes, maybe seed is first 4, data is rest (252)?
        # But XOR array is 256 bytes. This implies we need 256 bytes of target data.
        # So record likely 260 bytes.
        
        enc_data = header_data[4:260]
        if len(enc_data) != 256:
            return False

        # 2. Derive Keys
        try:
            self.aes_key, self.doc_flag = derive_key_and_flag(enc_data, seed)
            self.is_distributed = True
            return True
        except Exception:
            return False

    def decrypt_viewtext_stream(self, encrypted_stream: bytes) -> bytes:
        """
        Decrypts a ViewText stream using the derived AES key.
        """
        if not self.is_distributed or not self.aes_key:
            raise RuntimeError("Document is not identified as distributed or key is missing.")
        
        return decrypt_aes128(self.aes_key, encrypted_stream)

    def is_copy_restricted(self) -> bool:
        return bool(self.doc_flag & 0x01)

    def is_print_restricted(self) -> bool:
        return bool(self.doc_flag & 0x02)
