"""
HWPX 파일 쓰기 모듈
"""

import jpype
from pathlib import Path
from typing import Union
import logging

from ..core import ensure_jvm_running, HWPXLibError, WritingError

logger = logging.getLogger(__name__)


class HWPXWriter:
    """HWPX 파일 쓰기 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._HWPXWriter = jpype.JClass("kr.dogfoot.hwpxlib.writer.HWPXWriter")
        except Exception as e:
            raise HWPXLibError(f"Failed to import HWPX writer classes: {e}")

    def write_file(self, hwpx_file: 'jpype.JObject', file_path: Union[str, Path]) -> None:
        """
        HWPXFile 객체를 파일로 저장합니다.

        Args:
            hwpx_file: HWPXFile 객체
            file_path: 저장할 파일 경로

        Raises:
            WritingError: 파일 쓰기 중 오류가 발생한 경우
            HWPXLibError: hwpxlib 관련 오류
        """
        file_path = Path(file_path)

        try:
            logger.debug(f"Writing HWPX file: {file_path}")
            self._HWPXWriter.toFilepath(hwpx_file, str(file_path))
            logger.debug(f"Successfully wrote HWPX file: {file_path}")

        except jpype.JException as e:
            raise WritingError(f"Failed to write HWPX file {file_path}: {e}")
        except Exception as e:
            raise HWPXLibError(f"Unexpected error writing HWPX file {file_path}: {e}")
