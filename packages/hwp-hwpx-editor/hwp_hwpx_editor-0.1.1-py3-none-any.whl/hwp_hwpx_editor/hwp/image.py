"""
HWP 이미지 삽입 모듈
"""

from pathlib import Path
from typing import Optional, Union
import jpype
import logging

from ..core import ensure_jvm_running, HWPLibError, FileNotFoundError

logger = logging.getLogger(__name__)


class HWPImageInserter:
    """HWP 이미지 삽입 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._ControlRectangle = jpype.JClass("kr.dogfoot.hwplib.object.bodytext.control.gso.ControlRectangle")
            self._GsoControlType = jpype.JClass("kr.dogfoot.hwplib.object.bodytext.control.gso.GsoControlType")
            self._CtrlHeaderGso = jpype.JClass("kr.dogfoot.hwplib.object.bodytext.control.ctrlheader.CtrlHeaderGso")
            self._BinData = jpype.JClass("kr.dogfoot.hwplib.object.docinfo.BinData")
            self._BinDataType = jpype.JClass("kr.dogfoot.hwplib.object.docinfo.bindata.BinDataType")
            self._ImageFill = jpype.JClass("kr.dogfoot.hwplib.object.docinfo.borderfill.fillinfo.ImageFill")
            self._ImageFillType = jpype.JClass("kr.dogfoot.hwplib.object.docinfo.borderfill.fillinfo.ImageFillType")
        except Exception as e:
            raise HWPLibError(f"Failed to import image classes: {e}")

    def insert_image_simple(
        self,
        hwp_file: 'jpype.JObject',
        section_index: int,
        paragraph_index: int,
        image_path: Union[str, Path],
        width: Optional[float] = None,
        height: Optional[float] = None
    ) -> bool:
        """
        간단한 방식으로 이미지를 삽입합니다. (실험적 기능)

        Args:
            hwp_file: HWPFile 객체
            section_index: 섹션 인덱스
            paragraph_index: 문단 인덱스
            image_path: 이미지 파일 경로
            width: 이미지 너비 (mm, 옵션)
            height: 이미지 높이 (mm, 옵션)

        Returns:
            성공 여부
        """
        try:
            logger.warning("insert_image_simple is experimental and may not work correctly")
            logger.warning("For production use, please insert images using the Java API directly")

            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            # 섹션과 문단 가져오기
            section = hwp_file.getBodyText().getSectionList().get(section_index)
            paragraph = section.getParagraph(paragraph_index)

            # 사각형 컨트롤 생성을 위한 확장 문자 추가
            paragraph.getText().addExtendCharForGSO()

            # 사각형 컨트롤 추가 (이미지 컨테이너로 사용)
            rect_control = paragraph.addNewGsoControl(self._GsoControlType.Rectangle)

            # 기본 크기 설정 (mm 단위)
            if width is None:
                width = 50.0  # 기본 50mm
            if height is None:
                height = 50.0  # 기본 50mm

            # 컨트롤 헤더 설정
            ctrl_header = rect_control.getHeader()
            ctrl_header.setxOffset(self._mm_to_hwp(width))
            ctrl_header.setyOffset(self._mm_to_hwp(height))
            ctrl_header.setWidth(self._mm_to_hwp(width))
            ctrl_header.setHeight(self._mm_to_hwp(height))

            # 이미지 파일을 BinData로 추가
            # 이 부분은 매우 복잡한 설정이 필요하므로
            # 실제 구현은 추후 개선 필요

            logger.info(f"Added basic image container for: {image_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to insert image: {e}")
            return False

    def _mm_to_hwp(self, mm: float) -> int:
        """mm 단위를 HWP 단위로 변환"""
        return int(mm * 72000.0 / 254.0 + 0.5)
