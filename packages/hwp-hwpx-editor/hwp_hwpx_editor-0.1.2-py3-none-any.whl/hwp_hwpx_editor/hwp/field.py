"""
HWP 필드 조작 모듈
"""

from typing import List, Optional, Union
from enum import Enum
import jpype
import logging

from ..core import ensure_jvm_running, HWPLibError

logger = logging.getLogger(__name__)


class HWPFieldControlType(Enum):
    FIELD_CLICKHERE = "FIELD_CLICKHERE"
    FIELD_UNKNOWN = "FIELD_UNKNOWN"


class HWPFieldTextExtractMethod(Enum):
    ONLY_MAIN_PARAGRAPH = "OnlyMainParagraph"
    INSERT_CONTROL_TEXT_BETWEEN_PARAGRAPH_TEXT = "InsertControlTextBetweenParagraphText"
    APPEND_CONTROL_TEXT_AFTER_PARAGRAPH_TEXT = "AppendControlTextAfterParagraphText"


class HWPSetFieldResult(Enum):
    SUCCESS = "SUCCESS"
    FIELD_NOT_FOUND = "FIELD_NOT_FOUND"
    INVALID_TEXT_LIST = "INVALID_TEXT_LIST"


class HWPFieldFinder:
    """HWP 필드 찾기 및 조작 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._FieldFinder = jpype.JClass(
                "kr.dogfoot.hwplib.tool.objectfinder.FieldFinder"
            )
            self._HWPFieldControlType = jpype.JClass(
                "kr.dogfoot.hwplib.object.bodytext.control.HWPFieldControlType"
            )
            self._HWPFieldTextExtractMethod = jpype.JClass(
                "kr.dogfoot.hwplib.tool.textextractor.HWPFieldTextExtractMethod"
            )
            self._HWPSetFieldResult = jpype.JClass(
                "kr.dogfoot.hwplib.tool.objectfinder.HWPSetFieldResult"
            )
        except Exception as e:
            raise HWPLibError(f"Failed to import field finder classes: {e}")

    def get_click_here_text(
        self,
        hwp_file: "jpype.JObject",
        field_name: str,
        extract_method: HWPFieldTextExtractMethod = HWPFieldTextExtractMethod.ONLY_MAIN_PARAGRAPH,
    ) -> Optional[str]:
        """
        누름틀 필드의 텍스트를 가져옵니다.

        Args:
            hwp_file: HWPFile 객체
            field_name: 필드 이름
            extract_method: 텍스트 추출 방법

        Returns:
            필드 텍스트 또는 None (필드가 없는 경우)
        """
        try:
            result = self._FieldFinder.getClickHereText(
                hwp_file,
                field_name,
                getattr(self._HWPFieldTextExtractMethod, extract_method.value),
            )
            return str(result) if result is not None else None
        except Exception as e:
            logger.error(f"Failed to get click here text for field '{field_name}': {e}")
            return None

    def get_all_click_here_text(
        self,
        hwp_file: "jpype.JObject",
        field_name: str,
        extract_method: HWPFieldTextExtractMethod = HWPFieldTextExtractMethod.ONLY_MAIN_PARAGRAPH,
    ) -> List[str]:
        """
        동일한 이름의 모든 누름틀 필드의 텍스트를 가져옵니다.

        Args:
            hwp_file: HWPFile 객체
            field_name: 필드 이름
            extract_method: 텍스트 추출 방법

        Returns:
            필드 텍스트 리스트
        """
        try:
            java_list = self._FieldFinder.getAllClickHereText(
                hwp_file,
                field_name,
                getattr(self._HWPFieldTextExtractMethod, extract_method.value),
            )

            # Java ArrayList를 Python 리스트로 변환
            result = []
            if java_list is not None:
                for i in range(java_list.size()):
                    result.append(str(java_list.get(i)))

            return result
        except Exception as e:
            logger.error(
                f"Failed to get all click here text for field '{field_name}': {e}"
            )
            return []

    def get_all_field_text(
        self,
        hwp_file: "jpype.JObject",
        control_type: HWPFieldControlType,
        field_name: str,
        extract_method: HWPFieldTextExtractMethod = HWPFieldTextExtractMethod.ONLY_MAIN_PARAGRAPH,
    ) -> List[str]:
        """
        동일한 이름의 모든 필드 컨트롤의 텍스트를 가져옵니다.

        Args:
            hwp_file: HWPFile 객체
            control_type: 컨트롤 타입
            field_name: 필드 이름
            extract_method: 텍스트 추출 방법

        Returns:
            필드 텍스트 리스트
        """
        try:
            java_list = self._FieldFinder.getAllFieldText(
                hwp_file,
                getattr(self._HWPFieldControlType, control_type.value),
                field_name,
                getattr(self._HWPFieldTextExtractMethod, extract_method.value),
            )

            # Java ArrayList를 Python 리스트로 변환
            result = []
            if java_list is not None:
                for i in range(java_list.size()):
                    result.append(str(java_list.get(i)))

            return result
        except Exception as e:
            logger.error(f"Failed to get all field text for field '{field_name}': {e}")
            return []

    def set_field_text(
        self,
        hwp_file: "jpype.JObject",
        control_type: HWPFieldControlType,
        field_name: str,
        text_list: List[str],
    ) -> HWPSetFieldResult:
        """
        필드 컨트롤의 텍스트를 설정합니다.

        Args:
            hwp_file: HWPFile 객체
            control_type: 컨트롤 타입
            field_name: 필드 이름
            text_list: 설정할 텍스트 리스트

        Returns:
            설정 결과
        """
        try:
            # Python 리스트를 Java ArrayList로 변환
            java_array_list = jpype.JClass("java.util.ArrayList")()
            for text in text_list:
                java_array_list.add(text)

            result = self._FieldFinder.setFieldText(
                hwp_file,
                getattr(self._HWPFieldControlType, control_type.value),
                field_name,
                java_array_list,
            )

            # Java HWPSetFieldResult를 Python Enum으로 변환
            if result == self._HWPSetFieldResult.SUCCESS:
                return HWPSetFieldResult.SUCCESS
            elif result == self._HWPSetFieldResult.FIELD_NOT_FOUND:
                return HWPSetFieldResult.FIELD_NOT_FOUND
            elif result == self._HWPSetFieldResult.INVALID_TEXT_LIST:
                return HWPSetFieldResult.INVALID_TEXT_LIST
            else:
                return HWPSetFieldResult.FIELD_NOT_FOUND

        except Exception as e:
            logger.error(f"Failed to set field text for field '{field_name}': {e}")
            return HWPSetFieldResult.FIELD_NOT_FOUND
