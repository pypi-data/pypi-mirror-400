import xml.etree.ElementTree as ET
from typing import List, Optional

class HwpmlElem:
    """
    Base class for HWPML Elements.
    """
    TAG = ""

    def to_xml(self) -> ET.Element:
        return ET.Element(self.TAG)

    @classmethod
    def from_xml(cls, element: ET.Element):
        return cls()

class HwpmlHead(HwpmlElem):
    TAG = "HEAD"
    # Contains DOCSUMMARY, DOCSETTING, etc.

class HwpmlBody(HwpmlElem):
    TAG = "BODY"
    # Contains SECTIONS

class HwpmlRoot(HwpmlElem):
    """
    Root <HWPML> element.
    """
    TAG = "HWPML"
    
    def __init__(self):
        self.head = HwpmlHead()
        self.body = HwpmlBody()
        self.version = "1.2" # or target version

    def to_xml(self) -> ET.Element:
        root = ET.Element(self.TAG)
        root.set("Version", self.version)
        root.append(self.head.to_xml())
        root.append(self.body.to_xml())
        return root
