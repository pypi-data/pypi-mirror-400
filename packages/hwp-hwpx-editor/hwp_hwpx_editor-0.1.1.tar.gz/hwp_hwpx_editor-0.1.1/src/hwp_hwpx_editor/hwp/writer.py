"""
HWP 파일 쓰기 모듈
"""

import jpype
from pathlib import Path
from typing import Union
import logging

from ..core import ensure_jvm_running, HWPLibError, WritingError

logger = logging.getLogger(__name__)


class HWPWriter:
    """HWP 파일 쓰기 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._HWPWriter = jpype.JClass("kr.dogfoot.hwplib.writer.HWPWriter")
        except Exception as e:
            raise HWPLibError(f"Failed to import HWP writer classes: {e}")

    def write_file(self, hwp_file: 'jpype.JObject', file_path: Union[str, Path]) -> None:
        """
        HWPFile 객체를 파일로 저장합니다.

        Args:
            hwp_file: HWPFile 객체
            file_path: 저장할 파일 경로

        Raises:
            WritingError: 파일 쓰기 중 오류가 발생한 경우
            HWPLibError: hwplib 관련 오류
        """
        file_path = Path(file_path)

        try:
            logger.debug(f"Writing HWP file: {file_path}")
            self._HWPWriter.toFile(hwp_file, str(file_path))
            logger.debug(f"Successfully wrote HWP file: {file_path}")

        except jpype.JException as e:
            raise WritingError(f"Failed to write HWP file {file_path}: {e}")
        except Exception as e:
            raise HWPLibError(f"Unexpected error writing HWP file {file_path}: {e}")

    def write_stream(self, hwp_file: 'jpype.JObject') -> bytes:
        """
        HWPFile 객체를 바이트 스트림으로 변환합니다.

        Args:
            hwp_file: HWPFile 객체

        Returns:
            HWP 파일 데이터 바이트

        Raises:
            WritingError: 스트림 쓰기 중 오류가 발생한 경우
            HWPLibError: hwplib 관련 오류
        """
        try:
            logger.debug("Writing HWP file to stream")
            java_byte_array = self._HWPWriter.toStream(hwp_file)

            # Java 바이트 배열을 Python 바이트로 변환
            python_bytes = bytes(java_byte_array)
            logger.debug(f"Successfully wrote HWP file to stream ({len(python_bytes)} bytes)")

            return python_bytes

        except jpype.JException as e:
            raise WritingError(f"Failed to write HWP file to stream: {e}")
        except Exception as e:
            raise HWPLibError(f"Unexpected error writing HWP file to stream: {e}")
