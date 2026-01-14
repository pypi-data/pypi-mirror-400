class HwpxDocument:
    """
    Represents an OWPML (HWPX) Document.
    Structure based on OWPML spec (Zip container).
    """
    def __init__(self):
        self.version_xml = ""
        self.content_xmls = []
        self.meta_xmls = []
    
    def __repr__(self):
        return "<HwpxDocument (OWPML)>"
