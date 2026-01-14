"""
HWPX 파일 생성 모듈
"""

import jpype
import logging

from ..core import ensure_jvm_running, HWPXLibError

logger = logging.getLogger(__name__)


class HWPXCreator:
    """HWPX 파일 생성 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._BlankFileMaker = jpype.JClass("kr.dogfoot.hwpxlib.tool.blankfilemaker.BlankFileMaker")
        except Exception as e:
            raise HWPXLibError(f"Failed to import BlankFileMaker class: {e}")

    def create_blank_file(self) -> 'jpype.JObject':
        """
        빈 HWPX 파일을 생성합니다.

        Returns:
            HWPXFile 객체

        Raises:
            HWPXLibError: 파일 생성 중 오류가 발생한 경우
        """
        try:
            logger.debug("Creating blank HWPX file")
            hwpx_file = self._BlankFileMaker.make()

            if hwpx_file is None:
                raise HWPXLibError("Failed to create blank HWPX file")

            logger.debug("Successfully created blank HWPX file")
            return hwpx_file

        except jpype.JException as e:
            raise HWPXLibError(f"Failed to create blank HWPX file: {e}")
        except Exception as e:
            raise HWPXLibError(f"Unexpected error creating blank HWPX file: {e}")
