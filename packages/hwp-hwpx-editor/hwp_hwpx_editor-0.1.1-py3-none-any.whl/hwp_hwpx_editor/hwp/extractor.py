"""
HWP 파일 텍스트 추출 모듈
"""

import jpype
from enum import Enum
from typing import Optional
import logging

from ..core import ensure_jvm_running, HWPLibError, ParsingError

logger = logging.getLogger(__name__)


class HWPTextExtractMethod(Enum):
    ONLY_MAIN_PARAGRAPH = "OnlyMainParagraph"
    INSERT_CONTROL_TEXT_BETWEEN_PARAGRAPH_TEXT = "InsertControlTextBetweenParagraphText"
    APPEND_CONTROL_TEXT_AFTER_PARAGRAPH_TEXT = "AppendControlTextAfterParagraphText"


class HWPTextExtractor:
    """HWP 파일 텍스트 추출 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._TextExtractor = jpype.JClass(
                "kr.dogfoot.hwplib.tool.textextractor.TextExtractor"
            )
            self._TextExtractOption = jpype.JClass(
                "kr.dogfoot.hwplib.tool.textextractor.TextExtractOption"
            )
            self._HWPTextExtractMethod = jpype.JClass(
                "kr.dogfoot.hwplib.tool.textextractor.HWPTextExtractMethod"
            )
        except Exception as e:
            raise HWPLibError(f"Failed to import text extractor classes: {e}")

    def extract_text(
        self,
        hwp_file: "jpype.JObject",
        method: HWPTextExtractMethod = HWPTextExtractMethod.INSERT_CONTROL_TEXT_BETWEEN_PARAGRAPH_TEXT,
        with_control_char: bool = True,
        append_ending_lf: bool = True,
    ) -> str:
        """
        HWP 파일에서 텍스트를 추출합니다.

        Args:
            hwp_file: HWPFile 객체
            method: 텍스트 추출 방법
            with_control_char: 컨트롤 문자 포함 여부
            append_ending_lf: 끝에 줄바꿈 추가 여부

        Returns:
            추출된 텍스트

        Raises:
            ParsingError: 텍스트 추출 중 오류가 발생한 경우
            HWPLibError: hwplib 관련 오류
        """
        try:
            logger.debug(f"Extracting text with method: {method.value}")

            # 텍스트 추출 옵션 설정
            option = self._TextExtractOption()
            option.setMethod(getattr(self._HWPTextExtractMethod, method.value))
            option.setWithControlChar(with_control_char)
            option.setAppendEndingLF(append_ending_lf)

            # 텍스트 추출
            extracted_text = self._TextExtractor.extract(hwp_file, option)

            logger.debug(
                f"Successfully extracted text ({len(extracted_text)} characters)"
            )
            return str(extracted_text)

        except jpype.JException as e:
            raise ParsingError(f"Failed to extract text: {e}")
        except Exception as e:
            raise HWPLibError(f"Unexpected error extracting text: {e}")

    def extract_text_simple(
        self,
        hwp_file: "jpype.JObject",
        method: HWPTextExtractMethod = HWPTextExtractMethod.INSERT_CONTROL_TEXT_BETWEEN_PARAGRAPH_TEXT,
    ) -> str:
        """
        간단한 텍스트 추출 (옵션 없이).

        Args:
            hwp_file: HWPFile 객체
            method: 텍스트 추출 방법

        Returns:
            추출된 텍스트
        """
        try:
            logger.debug(f"Extracting text with simple method: {method.value}")

            # 간단한 추출 방법 사용
            extracted_text = self._TextExtractor.extract(
                hwp_file, getattr(self._HWPTextExtractMethod, method.value)
            )

            logger.debug(
                f"Successfully extracted text ({len(extracted_text)} characters)"
            )
            return str(extracted_text)

        except jpype.JException as e:
            raise ParsingError(f"Failed to extract text: {e}")
        except Exception as e:
            raise HWPLibError(f"Unexpected error extracting text: {e}")
