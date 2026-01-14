"""
HWPX 파일 텍스트 추출 모듈
"""

import jpype
from enum import Enum
from typing import Optional
import logging

from ..core import ensure_jvm_running, HWPXLibError, ParsingError

logger = logging.getLogger(__name__)


class HWPXTextExtractMethod(Enum):
    APPEND_CONTROL_TEXT_AFTER_PARAGRAPH_TEXT = "AppendControlTextAfterParagraphText"
    INSERT_CONTROL_TEXT_BETWEEN_PARAGRAPH_TEXT = "InsertControlTextBetweenParagraphText"


class HWPXTextMarks:
    def __init__(self):
        ensure_jvm_running()

        try:
            self._TextMarks = jpype.JClass(
                "kr.dogfoot.hwpxlib.tool.textextractor.TextMarks"
            )
            self._marks = self._TextMarks()
        except Exception as e:
            raise HWPXLibError(f"Failed to import TextMarks class: {e}")

    def line_break_and(self, text: str) -> "HWPXTextMarks":
        """줄바꿈 텍스트 설정"""
        self._marks.lineBreakAnd(text)
        return self

    def para_separator_and(self, text: str) -> "HWPXTextMarks":
        """문단 구분 텍스트 설정"""
        self._marks.paraSeparatorAnd(text)
        return self

    def get_java_object(self) -> "jpype.JObject":
        """Java 객체 반환"""
        return self._marks


class HWPXTextExtractor:
    """HWPX 파일 텍스트 추출 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._TextExtractor = jpype.JClass(
                "kr.dogfoot.hwpxlib.tool.textextractor.TextExtractor"
            )
            self._TextExtractMethod = jpype.JClass(
                "kr.dogfoot.hwpxlib.tool.textextractor.TextExtractMethod"
            )
        except Exception as e:
            raise HWPXLibError(f"Failed to import text extractor classes: {e}")

    def extract_text(
        self,
        hwpx_file: "jpype.JObject",
        method: HWPXTextExtractMethod = HWPXTextExtractMethod.APPEND_CONTROL_TEXT_AFTER_PARAGRAPH_TEXT,
        include_hidden_paragraph: bool = False,
        text_marks: Optional[HWPXTextMarks] = None,
    ) -> str:
        """
        HWPX 파일에서 텍스트를 추출합니다.

        Args:
            hwpx_file: HWPXFile 객체
            method: 텍스트 추출 방법
            include_hidden_paragraph: 숨겨진 문단 포함 여부
            text_marks: 텍스트 마크 설정

        Returns:
            추출된 텍스트

        Raises:
            ParsingError: 텍스트 추출 중 오류가 발생한 경우
            HWPXLibError: hwpxlib 관련 오류
        """
        try:
            logger.debug(f"Extracting text with method: {method.value}")

            # 기본 HWPXTextMarks 사용
            if text_marks is None:
                text_marks = (
                    HWPXTextMarks().line_break_and("\n").para_separator_and("\n")
                )

            # 텍스트 추출
            extracted_text = self._TextExtractor.extract(
                hwpx_file,
                getattr(self._TextExtractMethod, method.value),
                include_hidden_paragraph,
                text_marks.get_java_object(),
            )

            logger.debug(
                f"Successfully extracted text ({len(extracted_text)} characters)"
            )
            return str(extracted_text)

        except jpype.JException as e:
            raise ParsingError(f"Failed to extract text: {e}")
        except Exception as e:
            raise HWPXLibError(f"Unexpected error extracting text: {e}")
