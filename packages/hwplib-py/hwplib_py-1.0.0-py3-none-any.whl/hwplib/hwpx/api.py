import zipfile
from .model import HwpxDocument

def load(filename: str) -> HwpxDocument:
    """
    Loads an OWPML (HWPX) file (Zip container).
    """
    doc = HwpxDocument()
    
    try:
        with zipfile.ZipFile(filename, 'r') as zf:
            # Basic validation: check for version.xml or Content folder
            names = zf.namelist()
            
            # Read unique OWPML files
            if 'version.xml' in names:
                with zf.open('version.xml') as f:
                    doc.version_xml = f.read().decode('utf-8')
            
            # TODO: Parse 'Contents/header.xml', 'Contents/section0.xml'
            
    except zipfile.BadZipFile:
        raise ValueError("Not a valid HWPX (Zip) file.")
        
    return doc
