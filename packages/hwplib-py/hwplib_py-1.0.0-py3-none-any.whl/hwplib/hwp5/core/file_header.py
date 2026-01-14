import struct
from .defs import HwpTag

class HwpFileHeader:
    """
    Represents the HWP File Header (256 bytes).
    """
    SIGNATURE = b"HWP Document File"
    
    def __init__(self):
        self.version_mm = 0
        self.version_nn = 0
        self.version_pp = 0
        self.version_rr = 0
        self.flags = 0
        self.is_compressed = False
        self.is_encrypted = False
        self.is_distributed = False
        self.is_drm = False

    def parse(self, data: bytes):
        if len(data) < 256:
            raise ValueError("FileHeader must be at least 256 bytes")

        # 1. Signature (32 bytes)
        sig_data = data[:32]
        if not sig_data.startswith(self.SIGNATURE):
            raise ValueError("Invalid HWP Signature")

        # 2. Version (4 bytes: DWORD) -> MM nn PP rr
        # Struct unpack <I reads little endian.
        # 0xMMnnPPrr ? Spec says: "M.n.P.r"
        # Example: 5.0.1.0
        version_val = struct.unpack('<I', data[32:36])[0]
        self.version_rr = (version_val >> 0) & 0xFF
        self.version_pp = (version_val >> 8) & 0xFF
        self.version_nn = (version_val >> 16) & 0xFF
        self.version_mm = (version_val >> 24) & 0xFF

        # 3. Flags (4 bytes: DWORD) at offset 36
        self.flags = struct.unpack('<I', data[36:40])[0]
        
        # Parse Flags
        self.is_compressed = bool(self.flags & 0x00000001)
        self.is_encrypted = bool(self.flags & 0x00000002)
        self.is_distributed = bool(self.flags & 0x00000004)
        self.is_drm = bool(self.flags & 0x00000010) # check bit pos in spec
    
    @property
    def version_str(self) -> str:
        return f"{self.version_mm}.{self.version_nn}.{self.version_pp}.{self.version_rr}"

    def __repr__(self):
        return f"<HwpFileHeader v{self.version_str} Flags={hex(self.flags)}>"
