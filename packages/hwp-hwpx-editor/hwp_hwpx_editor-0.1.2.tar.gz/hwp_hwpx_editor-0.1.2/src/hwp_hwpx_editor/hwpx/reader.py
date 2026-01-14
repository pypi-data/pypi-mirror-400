"""
HWPX 파일 읽기 모듈
"""

import jpype
from pathlib import Path
from typing import Optional, Union
import logging

from ..core import ensure_jvm_running, HWPXLibError, FileNotFoundError, ParsingError

logger = logging.getLogger(__name__)


class HWPXReader:
    """HWPX 파일 읽기 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._HWPXReader = jpype.JClass("kr.dogfoot.hwpxlib.reader.HWPXReader")
            self._HWPXFile = jpype.JClass("kr.dogfoot.hwpxlib.object.HWPXFile")
        except Exception as e:
            raise HWPXLibError(f"Failed to import HWPX classes: {e}")

    def read_file(self, file_path: Union[str, Path]) -> 'jpype.JObject':
        """
        HWPX 파일을 읽어 HWPXFile 객체를 반환합니다.

        Args:
            file_path: HWPX 파일 경로

        Returns:
            HWPXFile 객체

        Raises:
            FileNotFoundError: 파일을 찾을 수 없는 경우
            ParsingError: 파일 파싱 중 오류가 발생한 경우
            HWPXLibError: hwpxlib 관련 오류
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"HWPX file not found: {file_path}")

        try:
            logger.debug(f"Reading HWPX file: {file_path}")
            hwpx_file = self._HWPXReader.fromFilepath(str(file_path))

            if hwpx_file is None:
                raise ParsingError(f"Failed to parse HWPX file: {file_path}")

            logger.debug(f"Successfully read HWPX file: {file_path}")
            return hwpx_file

        except jpype.JException as e:
            raise ParsingError(f"Failed to parse HWPX file {file_path}: {e}")
        except Exception as e:
            raise HWPXLibError(f"Unexpected error reading HWPX file {file_path}: {e}")
