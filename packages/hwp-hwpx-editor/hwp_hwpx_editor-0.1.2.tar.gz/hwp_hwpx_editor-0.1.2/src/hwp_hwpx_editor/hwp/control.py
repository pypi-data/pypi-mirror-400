"""
HWP 컨트롤 찾기 모듈
"""

from typing import List, Callable, Protocol
from abc import ABC, abstractmethod
from enum import Enum
import jpype
import logging

from ..core import ensure_jvm_running, HWPLibError

logger = logging.getLogger(__name__)


class HWPControlFilter(Protocol):
    def is_matched(
        self,
        control: "jpype.JObject",
        paragraph: "jpype.JObject",
        section: "jpype.JObject",
    ) -> bool: ...


class HWPControlType(Enum):
    TABLE = "Table"
    PICTURE = "Gso"
    SHAPE_LINE = "ShapeLine"
    RECTANGLE = "Rectangle"
    ELLIPSE = "Ellipse"
    ARC = "Arc"
    POLYGON = "Polygon"
    CURVE = "Curve"
    CONNECT_LINE = "ConnectLine"
    TEXT_ART = "TextArt"
    OLE = "OLE"
    CONTAINER = "Container"
    FIELD_CLICKHERE = "FieldClickHere"
    FIELD_UNKNOWN = "FieldUnknown"
    HEADER_FOOTER = "Header"
    FOOTNOTE_ENDNOTE = "Footnote"
    AUTO_NUMBER = "AutoNumber"
    PAGE_HIDE = "PageHide"
    PAGE_CTB = "PageCTB"
    PAGE_NUM_POSITION = "PageNumPosition"
    INDEX_MARK = "IndexMark"
    BOOKMARK = "Bookmark"


class HWPControlFinder:
    """HWP 컨트롤 찾기 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._ControlFinder = jpype.JClass(
                "kr.dogfoot.hwplib.tool.objectfinder.ControlFinder"
            )
            self._HWPControlType = jpype.JClass(
                "kr.dogfoot.hwplib.object.bodytext.control.HWPControlType"
            )
        except Exception as e:
            raise HWPLibError(f"Failed to import control finder classes: {e}")

    def find_controls(
        self, hwp_file: "jpype.JObject", control_filter: HWPControlFilter
    ) -> List["jpype.JObject"]:
        """
        조건에 맞는 컨트롤들을 찾습니다.

        Args:
            hwp_file: HWPFile 객체
            control_filter: 컨트롤 필터 함수

        Returns:
            찾은 컨트롤 리스트
        """
        try:
            # Python 함수를 Java HWPControlFilter로 래핑
            java_filter = self._create_java_filter(control_filter)

            # 컨트롤 찾기
            java_list = self._ControlFinder.find(hwp_file, java_filter)

            # Java ArrayList를 Python 리스트로 변환
            result = []
            if java_list is not None:
                for i in range(java_list.size()):
                    result.append(java_list.get(i))

            logger.debug(f"Found {len(result)} controls")
            return result

        except Exception as e:
            logger.error(f"Failed to find controls: {e}")
            return []

    def find_controls_by_type(
        self, hwp_file: "jpype.JObject", control_type: HWPControlType
    ) -> List["jpype.JObject"]:
        """
        특정 타입의 컨트롤들을 찾습니다.

        Args:
            hwp_file: HWPFile 객체
            control_type: 컨트롤 타입

        Returns:
            찾은 컨트롤 리스트
        """

        def type_filter(control, paragraph, section):
            try:
                return control.getType() == getattr(
                    self._HWPControlType, control_type.value
                )
            except:
                return False

        return self.find_controls(hwp_file, type_filter)

    def _create_java_filter(self, python_filter: HWPControlFilter):
        """Python 필터 함수를 Java HWPControlFilter 인터페이스로 래핑합니다."""

        # Java HWPControlFilter 인터페이스 구현 클래스 생성
        class JavaHWPControlFilter:
            def __init__(self, python_filter):
                self.python_filter = python_filter

            @jpype.JImplements("kr.dogfoot.hwplib.tool.objectfinder.HWPControlFilter")
            def isMatched(self, control, paragraph, section):
                try:
                    return self.python_filter.is_matched(control, paragraph, section)
                except Exception as e:
                    logger.warning(f"Error in control filter: {e}")
                    return False

        return JavaHWPControlFilter(python_filter)
