"""
HWP 하이퍼링크 삽입 모듈
"""

from typing import Optional
import jpype
import logging

from ..core import ensure_jvm_running, HWPLibError

logger = logging.getLogger(__name__)


class HWPHyperlinkInserter:
    """HWP 하이퍼링크 삽입 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._ControlField = jpype.JClass("kr.dogfoot.hwplib.object.bodytext.control.ControlField")
            self._ControlType = jpype.JClass("kr.dogfoot.hwplib.object.bodytext.control.ControlType")
        except Exception as e:
            raise HWPLibError(f"Failed to import hyperlink classes: {e}")

    def insert_hyperlink_simple(
        self,
        hwp_file: 'jpype.JObject',
        section_index: int,
        paragraph_index: int,
        link_text: str,
        url: str
    ) -> bool:
        """
        간단한 하이퍼링크를 삽입합니다. (실험적 기능)

        Args:
            hwp_file: HWPFile 객체
            section_index: 섹션 인덱스
            paragraph_index: 문단 인덱스
            link_text: 링크 텍스트
            url: 하이퍼링크 URL

        Returns:
            성공 여부
        """
        try:
            logger.warning("insert_hyperlink_simple is experimental and may not work correctly")
            logger.warning("For production use, please insert hyperlinks using the Java API directly")

            # 섹션과 문단 가져오기
            section = hwp_file.getBodyText().getSectionList().get(section_index)
            paragraph = section.getParagraph(paragraph_index)

            # 하이퍼링크 확장 문자 추가
            paragraph.getText().addString("이것은 ")
            paragraph.getText().addExtendCharForHyperlinkStart()
            paragraph.getText().addString(link_text)
            paragraph.getText().addExtendCharForHyperlinkEnd()
            paragraph.getText().addString("로 가는 링크입니다.")

            # 하이퍼링크 컨트롤 추가
            field_control = paragraph.addNewControl(self._ControlType.FIELD_HYPERLINK.getCtrlId())

            # URL 설정 (형식: "url;1;0;0;")
            command = f"{url};1;0;0;"
            field_control.getHeader().getCommand().fromUTF16LEString(command)

            logger.info(f"Added hyperlink: {link_text} -> {url}")
            return True

        except Exception as e:
            logger.error(f"Failed to insert hyperlink: {e}")
            return False
