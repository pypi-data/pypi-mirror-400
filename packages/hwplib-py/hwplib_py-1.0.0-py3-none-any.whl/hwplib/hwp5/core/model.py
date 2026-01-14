from .file_header import HwpFileHeader
from .doc_info import DocInfo
from .body_text import Section
from typing import List

class HwpDocument:
    """
    Represents a complete HWP Document.
    """
    def __init__(self):
        self.header = HwpFileHeader()
        self.doc_info = DocInfo()
        self.sections: List[Section] = []

    def get_text(self) -> str:
        """
        Extracts plain text from the document.
        """
        text_lines = []
        for section in self.sections:
            for para in section.paragraphs:
                # Basic text
                text_lines.append(para.text)
                
                # Check controls (e.g. Table)
                for ctrl in para.controls:
                    if hasattr(ctrl, 'get_text'):
                         # If control supports text extraction, add it
                         text_lines.append(ctrl.get_text())
        
        return "\n".join(text_lines)

    def __repr__(self):
        return f"<HwpDocument v{self.header.version_str} Sections={len(self.sections)}>"
