# hwplib-py

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

> A pure Python parser for the HWP (Hangul Word Processor) 5.0 binary file format.

This library allows you to read and extract text, metadata, and control objects (Tables, Pictures, Shapes, Equations) from HWP files without needing the official software. It is built from scratch based on the official file format specifications.

## Table of Contents

- [Background](#background)
- [Install](#install)
- [Usage](#usage)
- [Features](#features)
- [Maintainers](#maintainers)
- [Contributing](#contributing)
- [License](#license)

## Background

The HWP format is the standard word processing format in South Korea. While there are existing tools, many rely on the official ole automation or are incomplete. `hwplib-py` aims to provide a robust, cross-platform, pythonic interface to deep-dive into HWP binaries (OLE2 + Zlib structure).

## Install

```sh
pip install hwplib-py
```
*(Note: Not yet on PyPI, clone and install locally)*

```sh
git clone https://github.com/minseo0388/hwplib-py.git
cd hwplib-py
pip install .
```

## Usage

```python
from hwplib.hwp5.api import load

# Load an HWP file
doc = load("document.hwp")

# Print document metadata
print(f"Version: {doc.header.version_str}")
print(f"Compressed: {doc.header.is_compressed}")

# Extract plain text (including tables and hidden controls)
print(doc.get_text())

# Access sections and paragraphs directly
for section in doc.sections:
    for paragraph in section.paragraphs:
        print(paragraph.text)
        
        # Access embedded controls
        for ctrl in paragraph.controls:
            if ctrl.ctrl_id == 'tbl':
                print(f"Found Table with {len(ctrl.rows)} rows")
```

## Features

- **Pure Python**: Zero-dependency on Windows libraries. Uses `olefile` for OLE2 storage parsing and standard `zlib` for decompression. Cross-platform compatible.

- **Core Engine (HWP 5.0)**:
    - **Header**: Version validation, encryption flags checking.
    - **DocInfo**: Complete parsing of document metadata including:
        - *FaceNames* (Font information)
        - *Border/Fill*
        - *CharShapes* & *ParaShapes*
        - *Styles*
    - **BodyText**: Section-based parsing of Paragraphs with support for high-throughput text extraction.

- **Control Objects (The "Organs")**:
    - **Tables**: Full object model with `Row` and `Cell` structures. Supports recursive text extraction from cells (converting table layout to tab-separated text).
    - **Equations**: Parses equation controls and extracts the raw LaTeX-like script (e.g., `y = ax + b`).
    - **Shapes (GSO)**:
        - `ControlLine`: Start/End coordinates.
        - `ControlRect` & `ControlEllipse`: Width, Height, Attributes.
        - `ControlPolygon`: List of vertices.
    - **Pictures**: Meta-information parsing (Width, Height, BinData reference).

- **Specialized Modules**:
    - **Chart**: Binary parser for HWP chart objects.
    - **Distribution Document**: Detection logic for DistributeDoc (protected) files and crypto skeletons (AES-128).
    - **Legacy**: Partial support for HWP 3.0 records.

- **Export & Integration**:
    - **JSON Export**: convert the entire `HwpDocument` object graph to JSON for easy integration with web services or NoSQL databases.
    - **API**: Simple `load()` and `doc.get_text()` interface for immediate productivity.

## Maintainers

[@ Choi Minseo](https://github.com/minseo0388)

## Contributing

PRs accepted.

Small note: If editing the Readme, please conform to the [standard-readme](https://github.com/RichardLitt/standard-readme) specification.

## License

Apache-2.0 © 2026 Choi Minseo

## Legal Notice

본 제품은 (주)한글과컴퓨터의 한글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다.
