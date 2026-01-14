"""
HWP 5.0 Engine.

본 제품은 (주)한글과컴퓨터의 한글 문서 파일(.hwp) 공개 문서를 참고하여 개발하였습니다.
"""
from .api import load
from .core.model import HwpDocument

__all__ = ['load', 'HwpDocument']