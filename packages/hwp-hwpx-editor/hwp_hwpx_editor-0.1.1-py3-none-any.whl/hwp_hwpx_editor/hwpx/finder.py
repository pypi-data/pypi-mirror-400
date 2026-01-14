"""
HWPX 객체 찾기 모듈
"""

from typing import List, Callable, Protocol, Optional
from abc import ABC, abstractmethod
import jpype
import logging

from ..core import ensure_jvm_running, HWPXLibError
from .comment import HWPXMemosManager

logger = logging.getLogger(__name__)


class HWPXObjectFilter(Protocol):
    def matches(
        self, obj: "jpype.JObject", parents_path: List["jpype.JObject"]
    ) -> bool: ...


class HWPXObjectFinder:
    """HWPX 객체 찾기 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._ObjectFinder = jpype.JClass(
                "kr.dogfoot.hwpxlib.tool.finder.ObjectFinder"
            )
        except Exception as e:
            raise HWPXLibError(f"Failed to import object finder classes: {e}")

    def find_objects(
        self,
        hwpx_file: "jpype.JObject",
        object_filter: HWPXObjectFilter,
        find_first_only: bool = False,
    ) -> List["jpype.JObject"]:
        """
        조건에 맞는 객체들을 찾습니다.

        Args:
            hwpx_file: HWPXFile 객체
            object_filter: 객체 필터 함수
            find_first_only: 첫 번째 결과만 찾을지 여부

        Returns:
            찾은 객체 리스트
        """
        try:
            # Python 함수를 Java HWPXObjectFilter로 래핑
            java_filter = self._create_java_filter(object_filter)

            # 객체 찾기
            results = self._ObjectFinder.find(hwpx_file, java_filter, find_first_only)

            # Result 객체들에서 실제 객체 추출
            objects = []
            for result in results:
                objects.append(result.thisObject())

            logger.debug(f"Found {len(objects)} objects")
            return objects

        except Exception as e:
            logger.error(f"Failed to find objects: {e}")
            return []

    def find_objects_by_type(
        self,
        hwpx_file: "jpype.JObject",
        object_type_name: str,
        find_first_only: bool = False,
    ) -> List["jpype.JObject"]:
        """
        특정 타입의 객체들을 찾습니다.

        Args:
            hwpx_file: HWPXFile 객체
            object_type_name: 객체 타입 이름
            find_first_only: 첫 번째 결과만 찾을지 여부

        Returns:
            찾은 객체 리스트
        """

        def type_filter(obj, parents_path):
            try:
                return obj._objectType().name() == object_type_name
            except:
                return False

        return self.find_objects(hwpx_file, type_filter, find_first_only)

    def find_tables(self, hwpx_file: "jpype.JObject") -> List["jpype.JObject"]:
        """
        HWPX 파일에서 모든 표 객체를 찾습니다.

        Args:
            hwpx_file: HWPXFile 객체

        Returns:
            표 객체 리스트
        """
        return self.find_objects_by_type(hwpx_file, "tbl")

    def find_images(self, hwpx_file: "jpype.JObject") -> List["jpype.JObject"]:
        """
        HWPX 파일에서 모든 이미지 객체를 찾습니다.

        Args:
            hwpx_file: HWPXFile 객체

        Returns:
            이미지 객체 리스트
        """
        return self.find_objects_by_type(hwpx_file, "pic")

    def find_paragraphs(self, hwpx_file: "jpype.JObject") -> List["jpype.JObject"]:
        """
        HWPX 파일에서 모든 문단 객체를 찾습니다.

        Args:
            hwpx_file: HWPXFile 객체

        Returns:
            문단 객체 리스트
        """
        return self.find_objects_by_type(hwpx_file, "p")

    def find_memo_properties(self, hwpx_file: "jpype.JObject") -> List["jpype.JObject"]:
        """
        HWPX 파일에서 모든 메모 속성 객체를 찾습니다.

        Args:
            hwpx_file: HWPXFile 객체

        Returns:
            메모 속성 객체 리스트
        """
        memos_manager = HWPXMemosManager()
        return memos_manager.get_memo_properties(hwpx_file)

    def find_memo_styles(self, hwpx_file: "jpype.JObject") -> List["jpype.JObject"]:
        """
        HWPX 파일에서 메모 스타일을 찾습니다.

        Args:
            hwpx_file: HWPXFile 객체

        Returns:
            메모 스타일 객체 리스트
        """
        try:
            styles = []
            # 스타일 리스트에서 메모 스타일 찾기 (engName이 "Memo"인 것)
            style_list = hwpx_file.masterPage().styles()
            if style_list:
                for style in style_list.items():
                    try:
                        if hasattr(style, "engName") and style.engName() == "Memo":
                            styles.append(style)
                    except:
                        continue
            return styles
        except Exception as e:
            logger.error(f"Failed to find memo styles: {e}")
            return []

    def _create_java_filter(self, python_filter: HWPXObjectFilter):
        """Python 필터 함수를 Java HWPXObjectFilter 인터페이스로 래핑합니다."""

        @jpype.JImplements("kr.dogfoot.hwpxlib.tool.finder.comm.HWPXObjectFilter")
        class JavaHWPXObjectFilter:
            def __init__(self, py_filter):
                self.python_filter = py_filter

            @jpype.JOverride
            def isMatched(self, obj, parents_path):
                try:
                    python_parents = []
                    if parents_path is not None:
                        for i in range(parents_path.size()):
                            python_parents.append(parents_path.get(i))

                    return self.python_filter(obj, python_parents)
                except Exception as e:
                    logger.warning(f"Error in object filter: {e}")
                    return False

        return JavaHWPXObjectFilter(python_filter)
