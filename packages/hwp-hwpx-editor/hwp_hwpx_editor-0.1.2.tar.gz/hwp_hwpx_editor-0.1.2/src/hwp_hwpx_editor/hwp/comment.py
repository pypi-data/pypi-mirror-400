"""
HWP 주석(숨은 설명) 모듈
"""

from typing import List, Optional
import jpype
import logging

from ..core import ensure_jvm_running, HWPLibError

logger = logging.getLogger(__name__)


class HWPCommentManager:
    """HWP 주석(숨은 설명) 관리 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._ControlHiddenComment = jpype.JClass("kr.dogfoot.hwplib.object.bodytext.control.ControlHiddenComment")
            self._ControlType = jpype.JClass("kr.dogfoot.hwplib.object.bodytext.control.ControlType")
        except Exception as e:
            raise HWPLibError(f"Failed to import comment classes: {e}")

    def find_comments(self, hwp_file: 'jpype.JObject') -> List['jpype.JObject']:
        """
        HWP 파일에서 모든 주석(숨은 설명)을 찾습니다.

        Args:
            hwp_file: HWPFile 객체

        Returns:
            주석 컨트롤 리스트
        """
        comments = []

        try:
            # 모든 섹션과 문단을 순회하며 주석 찾기
            section_list = hwp_file.getBodyText().getSectionList()
            for section_idx in range(section_list.size()):
                section = section_list.get(section_idx)
                paragraph_list = section.getParagraphList()

                for para_idx in range(paragraph_list.size()):
                    paragraph = paragraph_list.get(para_idx)
                    control_list = paragraph.getControlList()

                    for ctrl_idx in range(control_list.size()):
                        control = control_list.get(ctrl_idx)
                        if control.getType() == self._ControlType.HiddenComment:
                            comments.append(control)

        except Exception as e:
            logger.error(f"Failed to find comments: {e}")

        return comments

    def get_comment_text(self, comment_control: 'jpype.JObject') -> Optional[str]:
        """
        주석 컨트롤에서 텍스트를 추출합니다.

        Args:
            comment_control: ControlHiddenComment 객체

        Returns:
            주석 텍스트 또는 None
        """
        try:
            # 주석 컨트롤의 문단 리스트에서 텍스트 추출
            paragraph_list = comment_control.getParagraphList()
            if paragraph_list.size() == 0:
                return None

            texts = []
            for para_idx in range(paragraph_list.size()):
                paragraph = paragraph_list.get(para_idx)
                text = paragraph.getText()

                # 텍스트 추출 (간단한 방식)
                if text is not None:
                    # Java 문자열로 변환 시도
                    try:
                        text_str = str(text)
                        texts.append(text_str)
                    except:
                        continue

            return '\n'.join(texts) if texts else None

        except Exception as e:
            logger.error(f"Failed to get comment text: {e}")
            return None

    def create_comment_simple(
        self,
        hwp_file: 'jpype.JObject',
        section_index: int,
        paragraph_index: int,
        comment_text: str
    ) -> bool:
        """
        간단한 주석을 생성합니다. (실험적 기능)

        Args:
            hwp_file: HWPFile 객체
            section_index: 섹션 인덱스
            paragraph_index: 문단 인덱스
            comment_text: 주석 텍스트

        Returns:
            성공 여부
        """
        try:
            logger.warning("create_comment_simple is experimental and may not work correctly")
            logger.warning("For production use, please create comments using the Java API directly")

            # 섹션과 문단 가져오기
            section = hwp_file.getBodyText().getSectionList().get(section_index)
            paragraph = section.getParagraphList().get(paragraph_index)

            # 숨은 설명 컨트롤 추가
            comment_control = paragraph.addNewControl(self._ControlType.HiddenComment.getCtrlId())

            # 기본 설정 (더 자세한 설정은 Java API 직접 사용 필요)
            # 이 부분은 매우 복잡한 설정이 필요하므로 기본 구조만 생성

            logger.info(f"Added basic comment structure: '{comment_text[:50]}...'")
            return True

        except Exception as e:
            logger.error(f"Failed to create comment: {e}")
            return False

    def get_comment_info(self, comment_control: 'jpype.JObject') -> dict:
        """
        주석 컨트롤의 정보를 가져옵니다.

        Args:
            comment_control: ControlHiddenComment 객체

        Returns:
            주석 정보 딕셔너리
        """
        try:
            info = {
                'type': 'hidden_comment',
                'paragraph_count': comment_control.getParagraphList().size(),
                'text': self.get_comment_text(comment_control)
            }

            # 추가 정보들 (가능한 경우)
            try:
                list_header = comment_control.getListHeader()
                info.update({
                    'col_index': list_header.getColIndex(),
                    'row_index': list_header.getRowIndex(),
                    'width': list_header.getWidth(),
                    'height': list_header.getHeight(),
                })
            except:
                pass

            return info

        except Exception as e:
            logger.error(f"Failed to get comment info: {e}")
            return {}
