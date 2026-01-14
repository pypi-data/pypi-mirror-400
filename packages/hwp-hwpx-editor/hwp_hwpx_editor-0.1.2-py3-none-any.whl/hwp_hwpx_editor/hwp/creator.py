"""
HWP 파일 생성 모듈
"""

import jpype
import logging

from ..core import ensure_jvm_running, HWPLibError

logger = logging.getLogger(__name__)


class HWPCreator:
    """HWP 파일 생성 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._BlankFileMaker = jpype.JClass("kr.dogfoot.hwplib.tool.blankfilemaker.BlankFileMaker")
        except Exception as e:
            raise HWPLibError(f"Failed to import BlankFileMaker class: {e}")

    def create_blank_file(self) -> 'jpype.JObject':
        """
        빈 HWP 파일을 생성합니다.

        Returns:
            HWPFile 객체

        Raises:
            HWPLibError: 파일 생성 중 오류가 발생한 경우
        """
        try:
            logger.debug("Creating blank HWP file")
            hwp_file = self._BlankFileMaker.make()

            if hwp_file is None:
                raise HWPLibError("Failed to create blank HWP file")

            logger.debug("Successfully created blank HWP file")
            return hwp_file

        except jpype.JException as e:
            raise HWPLibError(f"Failed to create blank HWP file: {e}")
        except Exception as e:
            raise HWPLibError(f"Unexpected error creating blank HWP file: {e}")
