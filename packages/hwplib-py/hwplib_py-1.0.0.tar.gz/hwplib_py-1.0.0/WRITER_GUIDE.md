# HWP Writer Implementation Guide

Implementing **Write (Creation/Save)** support for HWP files is a complex task that requires reversing the parsing process. This document outlines the architectural roadmap for adding write capabilities to `hwplib-py`.

## Architectural Roadmap

### Phase 1: Record Serialization (`to_bytes()`)
Currently, classes like `ParaHeader` or `CharShape` parse bytes *into* integers. You must implement the reverse: packing integers *into* bytes.

- **Task**: Add `to_bytes(self) -> bytes` methods to all Core Objects.
- **Example (ParaHeader)**:
  ```python
  def to_bytes(self):
      return struct.pack('<IIHBBHHI', 
          self.text_len, self.control_mask, self.para_shape_id, ...
      )
  ```

### Phase 2: Stream Assembly
HWP files are collections of "Streams" (Virtual Files). You need to construct these streams from your objects.

1.  **FileHeader**: Create a fixed 256-byte header with the key "HWP Document File" signature.
2.  **DocInfo**:
    - Serialize all `FaceNames` into a list of records.
    - Serialize all `CharShapes`, `ParaShapes`, etc.
    - **Challenge**: ID Management. Paragraphs reference Shape IDs (e.g., `para_shape_id=3`). You must ensure `DocInfo.para_shapes[3]` exists and matches the intent.
3.  **BodyText**:
    - Iterate sections.
    - For each section, serialize paragraphs into a continuous binary buffer.
    - **Tags**: Every object must be wrapped in a Record Header (`Tag | Level | Size`).
    - **Compression**: The final buffer must be compressed using `zlib` (deflate).

### Phase 3: OLE2 Container Writing
Once you have the raw byte streams (e.g., the compressed BodyText blob), you need to save them into an OLE2 container (`.hwp` file).

- **Tools**: Use `olefile` (write mode support is limited/beta) or a specialized Compound File writer.
- **Structure**:
  ```text
  root
   ├── FileHeader
   ├── DocInfo
   ├── BodyText
   │   ├── Section0
   │   └── Section1
   ├── BinData
   │   ├── BIN0001.jpg
   │   └── ...
   └── PrvText (Preview)
  ```

### Phase 4: Integration
Create a `save(doc, filename)` API.

```python
def save(doc, filename):
    # 1. Update/Normalize IDs in DocInfo based on usage in BodyText
    # 2. Serialize Streams
    # 3. Write OLE2/Storage
```

## Difficulty Assessment
- **High**: Correctly generating `ParaHeader` control masks and `CharShape` bitmasks. Use the provided `docs/` spec carefully.
- **Critical**: If offsets or sizes are off by 1 byte, the HWP Viewer will crash or show a blank document.

## Recommendation
Start by implementing a **"Passthrough"** test:
1. `load("test.hwp")` -> `doc`
2. `save(doc, "output.hwp")`
3. Verify `output.hwp` opens in Hancom Office.

Once Passthrough works, you can start modifying `doc` properties safely.
