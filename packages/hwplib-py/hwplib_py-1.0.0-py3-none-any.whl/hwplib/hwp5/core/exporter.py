import json
from .model import HwpDocument
from .control import ControlTable, ControlPicture, ControlEquation, ControlLine, ControlRect, ControlEllipse, ControlPolygon

class HwpJsonExporter:
    """
    Exports HwpDocument to JSON.
    """
    def export(self, doc: HwpDocument) -> str:
        data = {
            "version": doc.header.version_str,
            "compressed": doc.header.is_compressed,
            "encrypted": doc.header.is_encrypted,
            "sections": []
        }
        
        for section in doc.sections:
            sec_data = {"paragraphs": []}
            for para in section.paragraphs:
                p_data = {
                    "text": para.text,
                    "controls": []
                }
                
                for ctrl in para.controls:
                    c_data = {"type": hasattr(ctrl, 'ctrl_id') and ctrl.ctrl_id or "unknown"}
                    
                    if isinstance(ctrl, ControlTable):
                        c_data["type"] = "table"
                        # TODO: export rows/cells if we fully linked them
                    elif isinstance(ctrl, ControlPicture):
                        c_data["type"] = "picture"
                        c_data["width"] = ctrl.width
                        c_data["height"] = ctrl.height
                    elif isinstance(ctrl, ControlEquation):
                        c_data["type"] = "equation"
                        c_data["script"] = ctrl.script
                    elif isinstance(ctrl, ControlLine): c_data["type"] = "line"
                    elif isinstance(ctrl, ControlRect): c_data["type"] = "rect"
                    elif isinstance(ctrl, ControlEllipse): c_data["type"] = "ellipse"
                    elif isinstance(ctrl, ControlPolygon): c_data["type"] = "polygon"
                    
                    p_data["controls"].append(c_data)
                
                sec_data["paragraphs"].append(p_data)
            data["sections"].append(sec_data)
            
        return json.dumps(data, indent=2, ensure_ascii=False)
