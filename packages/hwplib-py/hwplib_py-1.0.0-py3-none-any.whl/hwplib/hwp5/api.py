"""
API for HWP Library.

본 제품은 (주)한글과컴퓨터의 한글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다.
"""

import io
from .core.storage import StorageReader
from .core.model import HwpDocument
from .core.file_header import HwpFileHeader
from .core.doc_info import DocInfo
from .core.body_text import Section
from .distribute.distribute_handler import DistributeDocParser, HWPTAG_DISTRIBUTE_DOC_DATA

def load(filename: str) -> HwpDocument:
    """
    Loads an HWP 5.0 file.
    """
    storage = StorageReader(filename)
    doc = HwpDocument()
    
    # 1. FileHeader
    # Usually in stream 'FileHeader'
    try:
        header_data = storage.get_stream_data('FileHeader', decompress=False)
        doc.header.parse(header_data)
    except FileNotFoundError:
        # Maybe HWP 3.0 or invalid
        raise ValueError("FileHeader stream not found. Might be HWP 3.0 or invalid file.")

    # Check for Distribution Document
    is_dist = False
    dist_parser = None
    
    # Check tags in DocInfo if mapped? 
    # Or usually distribution data is in a stream?
    # Spec says it's inside DocInfo or separate?
    # Actually encryption is often handled via 'FileHeader' flags + 'ViewText'.
    
    # 2. DocInfo
    # Stream 'DocInfo' is compressed zlib
    if doc.header.is_compressed:
        doc_info_data = storage.get_stream_data('DocInfo', decompress=True)
    else:
        doc_info_data = storage.get_stream_data('DocInfo', decompress=False)
        
    doc.doc_info.parse(io.BytesIO(doc_info_data))

    # 3. BodyText
    # Streams are named 'BodyText/Section0', 'BodyText/Section1', ...
    # Or just 'BodyText' in some ancient ones. HWP 5.0 uses Section index.
    # Logic: list streams, find those starting with 'BodyText/Section'
    
    streams = storage.list_streams() 
    # storage.list_streams() return list of list of parts e.g. [['BodyText', 'Section0'], ...]
    # Adaptation needed for olefile output format
    
    # Simplified approach: Try reading Section0, Section1... until fail
    idx = 0
    while True:
        section_name = f'BodyText/Section{idx}'
        try:
            if doc.header.is_compressed:
                sec_data = storage.get_stream_data(section_name, decompress=True)
            else:
                sec_data = storage.get_stream_data(section_name, decompress=False)
            
            section = Section()
            section.parse(io.BytesIO(sec_data))
            doc.sections.append(section)
            idx += 1
        except FileNotFoundError:
            break
            
    storage.close()
    return doc
