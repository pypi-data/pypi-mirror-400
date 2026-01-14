"""
HWPX 메모/주석 모듈
"""

from typing import List, Optional, Dict
import jpype
import logging

from ..core import ensure_jvm_running, HWPXLibError

logger = logging.getLogger(__name__)


class HWPXMemosManager:
    """HWPX 메모 관리 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._MemoPr = jpype.JClass("kr.dogfoot.hwpxlib.object.content.header_xml.references.MemoPr")
            self._MemoType = jpype.JClass("kr.dogfoot.hwpxlib.object.content.header_xml.enumtype.MemoType")
            self._LineType2 = jpype.JClass("kr.dogfoot.hwpxlib.object.content.header_xml.enumtype.LineType2")
            self._LineWidth = jpype.JClass("kr.dogfoot.hwpxlib.object.content.header_xml.enumtype.LineWidth")
        except Exception as e:
            raise HWPXLibError(f"Failed to import memo classes: {e}")

    def get_memo_properties(self, hwpx_file: 'jpype.JObject') -> List['jpype.JObject']:
        """
        HWPX 파일의 메모 속성들을 가져옵니다.

        Args:
            hwpx_file: HWPXFile 객체

        Returns:
            메모 속성 리스트
        """
        try:
            ref_list = hwpx_file.refList()
            if ref_list is not None and ref_list.memoProperties() is not None:
                memo_props = ref_list.memoProperties()
                return list(memo_props.items()) if memo_props.items() else []
            return []
        except Exception as e:
            logger.error(f"Failed to get memo properties: {e}")
            return []

    def get_memo_info(self, memo_pr: 'jpype.JObject') -> Dict:
        """
        메모 속성의 정보를 가져옵니다.

        Args:
            memo_pr: MemoPr 객체

        Returns:
            메모 정보 딕셔너리
        """
        try:
            info = {
                'id': memo_pr.id(),
                'width': memo_pr.width(),
                'line_type': str(memo_pr.lineType()) if memo_pr.lineType() else None,
                'line_width': str(memo_pr.lineWidth()) if memo_pr.lineWidth() else None,
                'line_color': memo_pr.lineColor(),
                'fill_color': memo_pr.fillColor(),
                'active_color': memo_pr.activeColor(),
                'memo_type': str(memo_pr.memoType()) if memo_pr.memoType() else None,
            }
            return info
        except Exception as e:
            logger.error(f"Failed to get memo info: {e}")
            return {}

    def create_memo_property(
        self,
        hwpx_file: 'jpype.JObject',
        memo_id: str = "memo1",
        width: int = 200,
        line_color: str = "#000000",
        fill_color: str = "#FFFF00",
        active_color: str = "#FF0000"
    ) -> bool:
        """
        HWPX 파일에 메모 속성을 생성합니다.

        Args:
            hwpx_file: HWPXFile 객체
            memo_id: 메모 ID
            width: 메모 너비
            line_color: 선 색상
            fill_color: 채우기 색상
            active_color: 활성 색상

        Returns:
            성공 여부
        """
        try:
            ref_list = hwpx_file.refList()
            if ref_list is None:
                logger.warning("RefList not found in HWPX file")
                return False

            # MemoProperties가 없으면 생성
            if ref_list.memoProperties() is None:
                ref_list.createMemoProperties()

            memo_props = ref_list.memoProperties()

            # 새 메모 속성 생성
            memo_pr = self._MemoPr()
            memo_pr.idAnd(memo_id)
            memo_pr.widthAnd(width)
            memo_pr.lineTypeAnd(self._LineType2.SOLID)
            memo_pr.lineWidthAnd(self._LineWidth.MM0_5)
            memo_pr.lineColorAnd(line_color)
            memo_pr.fillColorAnd(fill_color)
            memo_pr.activeColorAnd(active_color)
            memo_pr.memoTypeAnd(self._MemoType.NORMAL)

            # 리스트에 추가
            memo_props.add(memo_pr)

            logger.info(f"Created memo property: {memo_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create memo property: {e}")
            return False

    def set_memo_shape_id_ref(
        self,
        hwpx_file: 'jpype.JObject',
        section_index: int,
        memo_shape_id: str
    ) -> bool:
        """
        섹션에 메모 모양 ID 참조를 설정합니다.

        Args:
            hwpx_file: HWPXFile 객체
            section_index: 섹션 인덱스
            memo_shape_id: 메모 모양 ID

        Returns:
            성공 여부
        """
        try:
            body = hwpx_file.body()
            if body is None:
                return False

            section = body.sectionList().get(section_index)
            if section is None:
                return False

            # 첫 번째 문단의 SecPr에 memoShapeIDRef 설정
            first_para = section.paragraphList().get(0)
            if first_para is None:
                return False

            sec_pr = first_para.secPr()
            if sec_pr is None:
                return False

            sec_pr.memoShapeIDRefAnd(memo_shape_id)

            logger.info(f"Set memo shape ID ref: {memo_shape_id} for section {section_index}")
            return True

        except Exception as e:
            logger.error(f"Failed to set memo shape ID ref: {e}")
            return False

    def find_memos_in_content(self, hwpx_file: 'jpype.JObject') -> List[Dict]:
        """
        HWPX 파일 내용에서 메모 관련 요소들을 찾습니다.

        Args:
            hwpx_file: HWPXFile 객체

        Returns:
            메모 정보 리스트
        """
        memos = []

        try:
            body = hwpx_file.body()
            if body is None:
                return memos

            # 모든 섹션과 문단을 순회하며 메모 관련 정보 수집
            section_list = body.sectionList()
            for sec_idx in range(section_list.size()):
                section = section_list.get(sec_idx)

                # 섹션의 메모 정보
                first_para = section.paragraphList().get(0)
                if first_para and first_para.secPr():
                    sec_pr = first_para.secPr()
                    memo_shape_id = sec_pr.memoShapeIDRef()
                    if memo_shape_id and memo_shape_id != "0":
                        memos.append({
                            'type': 'section_memo_ref',
                            'section_index': sec_idx,
                            'memo_shape_id': memo_shape_id
                        })

        except Exception as e:
            logger.error(f"Failed to find memos in content: {e}")

        return memos
