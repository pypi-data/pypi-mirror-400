"""
통합 문서 클래스
"""

import os
from pathlib import Path
from typing import Union, Optional, Literal, List, Any, TYPE_CHECKING, Callable
from enum import Enum
import logging

JPYPE_AVAILABLE = False
jpype = None

try:
    import jpype

    JPYPE_AVAILABLE = True
except ImportError:
    pass

if JPYPE_AVAILABLE:
    from .core import initialize_jvm, ensure_jvm_running
    from .hwp import (
        HWPReader as HWPJavaReader,
        HWPWriter,
        HWPTextExtractor,
        HWPTextExtractMethod,
        HWPFieldFinder,
        HWPControlFinder,
        HWPTableManager,
        HWPCreator,
        HWPImageInserter,
        HWPHyperlinkInserter,
        HWPCommentManager,
    )
    from .hwpx import (
        HWPXReader as HWPXJavaReader,
        HWPXWriter,
        HWPXTextExtractor,
        HWPXTextExtractMethod,
        HWPXTextMarks,
        HWPXCreator,
        HWPXObjectFinder,
        HWPXMemosManager,
        HWPXTableManager,
        HWPXTextReplacer,
    )

from hwp_hwpx_parser import (
    HWP5Reader,
    HWPXReader,
    ExtractOptions,
    TableStyle,
    ImageMarkerStyle,
    NoteData,
    HyperlinkData,
    ExtractResult,
    MemoData,
)

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """문서 타입"""

    HWP = "hwp"
    HWPX = "hwpx"


class Document:
    """
    통합 문서 클래스

    HWP와 HWPX 파일을 동일한 인터페이스로 다룰 수 있습니다.
    """

    def __init__(
        self,
        file_path: Optional[Union[str, Path]] = None,
        doc_type: Optional[DocumentType] = None,
        fast_mode: bool = False,
    ):
        """
        문서 객체를 초기화합니다.

        Args:
            file_path: 파일 경로 (지정하지 않으면 빈 문서 생성)
            doc_type: 문서 타입 (지정하지 않으면 파일 확장자로 자동 판별)
            fast_mode: True면 JVM 없이 Fast Layer만 사용 (텍스트 추출만 가능)
        """
        self._fast_mode = fast_mode
        self._file_path = Path(file_path) if file_path else None
        self._doc_type = doc_type
        self._java_object = None
        self._is_modified = False

        if file_path:
            self._doc_type = self._detect_doc_type(Path(file_path))

        if not fast_mode:
            if not JPYPE_AVAILABLE:
                raise ImportError(
                    "JVM 모드를 사용하려면 jpype가 필요합니다. "
                    "fast_mode=True를 사용하거나 pip install JPype1을 실행하세요."
                )
            initialize_jvm()
            if file_path:
                self._validate_and_load_file(file_path, doc_type)
            else:
                self._doc_type = DocumentType.HWPX
                self._create_blank()

    def _detect_doc_type(self, file_path: Path) -> DocumentType:
        suffix = file_path.suffix.lower()
        if suffix == ".hwp":
            return DocumentType.HWP
        elif suffix == ".hwpx":
            return DocumentType.HWPX
        raise ValueError(f"지원하지 않는 파일 형식: {suffix}")

    def _validate_and_load_file(
        self, file_path: Union[str, Path], doc_type: Optional[DocumentType]
    ):
        """파일 검증 후 로드 (extract-hwp 스타일)"""
        file_path = Path(file_path)

        # 1. 파일 존재 확인
        if not file_path.exists():
            raise FileNotFoundError(
                f"파일을 찾을 수 없습니다: {file_path}", str(file_path)
            )

        # 2. 파일 권한 확인
        if not file_path.is_file():
            raise ValueError(f"유효한 파일이 아닙니다: {file_path}")

        if not os.access(file_path, os.R_OK):
            raise PermissionError(
                f"파일 읽기 권한이 없습니다: {file_path}", str(file_path)
            )

        # 3. 파일 크기 확인 (너무 큰 파일 제외)
        file_size = file_path.stat().st_size
        if file_size == 0:
            raise EmptyFileError(f"빈 파일입니다: {file_path}", str(file_path))
        if file_size > 100 * 1024 * 1024:  # 100MB 제한
            raise FileTooLargeError(
                f"파일이 너무 큽니다 (100MB 초과): {file_path}", str(file_path)
            )

        # 4. 암호화 파일 확인 (간단 버전)
        if self._is_file_encrypted(file_path):
            raise EncryptedFileError(
                f"암호로 보호된 파일입니다: {file_path}", str(file_path)
            )

        logger.info(f"파일 검증 완료: {file_path} ({file_size} bytes)")

        # 5. 파일 로드
        self._load_from_file(file_path, doc_type)

    def _is_file_encrypted(self, file_path: Path) -> bool:
        """파일이 암호화되었는지 간단히 확인"""
        try:
            # HWPX 파일의 경우
            if file_path.suffix.lower() == ".hwpx":
                import zipfile
                import xml.etree.ElementTree as ET

                with zipfile.ZipFile(file_path, "r") as zip_file:
                    manifest_path = "META-INF/manifest.xml"
                    if manifest_path in zip_file.namelist():
                        with zip_file.open(manifest_path) as manifest_file:
                            manifest_content = manifest_file.read()
                            root = ET.fromstring(manifest_content)
                            for elem in root.iter():
                                if "encryption-data" in elem.tag:
                                    return True
            # HWP 파일의 경우 - Java 라이브러리에 의존
            # 현재는 간단한 체크만 수행

        except Exception:
            # 암호화 확인 실패 시 안전하게 False 반환
            pass

        return False

    def _load_from_file(
        self, file_path: Union[str, Path], doc_type: Optional[DocumentType] = None
    ):
        """파일에서 문서를 로드합니다."""
        file_path = Path(file_path)

        # 문서 타입 판별
        if doc_type is None:
            if file_path.suffix.lower() == ".hwp":
                self._doc_type = DocumentType.HWP
            elif file_path.suffix.lower() == ".hwpx":
                self._doc_type = DocumentType.HWPX
            else:
                raise ValueError(f"Unsupported file extension: {file_path.suffix}")

        if self._doc_type == DocumentType.HWP:
            reader = HWPJavaReader()
            self._java_object = reader.read_file(file_path)
        elif self._doc_type == DocumentType.HWPX:
            reader = HWPXJavaReader()
            self._java_object = reader.read_file(file_path)

        logger.info(f"Loaded {self._doc_type.value} document: {file_path}")

    def _create_blank(self):
        """빈 문서를 생성합니다."""
        if self._doc_type == DocumentType.HWP:
            creator = HWPCreator()
            self._java_object = creator.create_blank_file()
            self._is_modified = True
            logger.info("Created blank HWP document")
        elif self._doc_type == DocumentType.HWPX:
            creator = HWPXCreator()
            self._java_object = creator.create_blank_file()
            self._is_modified = True
            logger.info("Created blank HWPX document")
        else:
            raise ValueError(f"Unsupported document type: {self._doc_type}")

    @property
    def document_type(self) -> DocumentType:
        """문서 타입을 반환합니다."""
        return self._doc_type

    @property
    def file_path(self) -> Optional[Path]:
        """파일 경로를 반환합니다."""
        return self._file_path

    @property
    def is_modified(self) -> bool:
        """문서가 수정되었는지 여부를 반환합니다."""
        return self._is_modified

    @property
    def version(self):
        """문서 버전 정보를 반환합니다."""
        if self._java_object is None:
            return None
        try:
            if self._doc_type == DocumentType.HWP:
                file_header = self._java_object.getFileHeader()
                if file_header:
                    return str(file_header.getVersion())
            elif self._doc_type == DocumentType.HWPX:
                # HWPX는 버전 정보가 다르게 저장됨
                return "HWPX"
        except Exception as e:
            logger.debug(f"Failed to get version: {e}")
        return None

    @property
    def sections(self):
        """문서의 섹션 리스트를 반환합니다."""
        if self._java_object is None:
            return []
        try:
            if self._doc_type == DocumentType.HWP:
                body_text = self._java_object.getBodyText()
                if body_text:
                    section_list = body_text.getSectionList()
                    if section_list:
                        return [section_list.get(i) for i in range(section_list.size())]
            elif self._doc_type == DocumentType.HWPX:
                # HWPX 섹션 접근 방식 (추후 구현)
                pass
        except Exception as e:
            logger.debug(f"Failed to get sections: {e}")
        return []

    @property
    def bin_data(self):
        """문서에 포함된 바이너리 데이터 파일들을 반환합니다."""
        if self._java_object is None:
            return []
        try:
            if self._doc_type == DocumentType.HWP:
                bin_data_list = self._java_object.getBinData()
                if bin_data_list:
                    result = []
                    for bin_data in bin_data_list:
                        try:
                            result.append(
                                {
                                    "name": str(bin_data.getNameOfStorage()),
                                    "data": bytes(bin_data.getBinaryDataInStorage()),
                                }
                            )
                        except:
                            continue
                    return result
        except Exception as e:
            logger.debug(f"Failed to get bin_data: {e}")
        return []

    def find_all(self, tag: str, **kwargs):
        """
        문서에서 지정된 태그의 모든 객체를 찾습니다.

        Rust hwp-rs의 find_all 메소드를 참고하여 구현했습니다.

        Args:
            tag: 찾을 객체 타입 ('paragraph', 'table', 'image', 'comment' 등)
            **kwargs: 추가 옵션들

        Returns:
            찾은 객체 리스트
        """
        if self._java_object is None:
            return []

        recursive = kwargs.get("recursive", True)

        if self._doc_type == DocumentType.HWP:
            return self._find_all_hwp(tag, recursive, **kwargs)
        elif self._doc_type == DocumentType.HWPX:
            return self._find_all_hwpx(tag, recursive, **kwargs)

        return []

    def _find_all_hwp(self, tag: str, recursive: bool, **kwargs):
        """HWP 문서에서 객체 찾기"""
        results = []

        try:
            sections = self.sections

            for section in sections:
                if tag == "paragraph":
                    # 문단 찾기
                    para_list = section.getParagraphList()
                    if para_list:
                        for i in range(para_list.size()):
                            para = para_list.get(i)
                            results.append(para)
                            if recursive:
                                # 문단 내 컨트롤들도 포함
                                results.extend(
                                    self._find_controls_in_paragraph(para, tag)
                                )

                elif tag in ["table", "image", "comment"]:
                    # 특정 컨트롤 타입 찾기
                    results.extend(self.find_controls_by_type(tag))

                elif tag == "section":
                    results.append(section)

        except Exception as e:
            logger.debug(f"Error in find_all for HWP: {e}")

        return results

    def _find_all_hwpx(self, tag: str, recursive: bool, **kwargs):
        """HWPX 문서에서 객체 찾기"""
        finder = HWPXObjectFinder()

        try:
            if tag == "paragraph":
                return finder.find_paragraphs(self._java_object)
            elif tag == "table":
                return finder.find_tables(self._java_object)
            elif tag == "image":
                return finder.find_images(self._java_object)
            elif tag == "memo":
                return finder.find_memo_properties(self._java_object)
        except Exception as e:
            logger.debug(f"Error in find_all for HWPX: {e}")

        return []

    def _find_controls_in_paragraph(self, paragraph, tag: str):
        """문단 내의 컨트롤 찾기"""
        results = []
        try:
            control_list = paragraph.getControlList()
            if control_list:
                for i in range(control_list.size()):
                    control = control_list.get(i)
                    control_type = str(control.getType()).lower()

                    # 태그에 따라 필터링
                    if tag == "table" and "table" in control_type:
                        results.append(control)
                    elif tag == "image" and (
                        "picture" in control_type or "gso" in control_type
                    ):
                        results.append(control)
                    elif tag == "comment" and "hiddencomment" in control_type:
                        results.append(control)

        except Exception as e:
            logger.debug(f"Error finding controls in paragraph: {e}")

        return results

    def extract_text(
        self,
        method: Optional[Union[HWPTextExtractMethod, HWPXTextExtractMethod]] = None,
        **kwargs,
    ) -> str:
        """
        문서에서 텍스트를 추출합니다.

        Args:
            method: 텍스트 추출 방법
            **kwargs: 추가 옵션들

        Returns:
            추출된 텍스트
        """
        if self._java_object is None:
            raise RuntimeError("Document not loaded")

        if self._doc_type == DocumentType.HWP:
            extractor = HWPTextExtractor()
            if method is None:
                method = HWPTextExtractMethod.INSERT_CONTROL_TEXT_BETWEEN_PARAGRAPH_TEXT
            return extractor.extract_text(self._java_object, method, **kwargs)

        elif self._doc_type == DocumentType.HWPX:
            extractor = HWPXTextExtractor()
            if method is None:
                method = HWPXTextExtractMethod.APPEND_CONTROL_TEXT_AFTER_PARAGRAPH_TEXT
            return extractor.extract_text(self._java_object, method, **kwargs)

    def extract_text_fast(
        self,
        options: Optional[ExtractOptions] = None,
        table_style: Optional[TableStyle] = None,
        image_marker: Optional[ImageMarkerStyle] = None,
    ) -> str:
        """
        Fast Layer로 텍스트를 추출합니다 (JVM 불필요).

        표는 Markdown 형식으로, 이미지는 [IMAGE] 마커로 출력됩니다.
        JVM 없이 순수 Python으로 동작하여 빠릅니다.

        Args:
            options: ExtractOptions 객체 (세부 옵션 직접 지정시)
            table_style: 표 출력 스타일 (MARKDOWN, CSV, INLINE)
            image_marker: 이미지 마커 스타일 (SIMPLE, WITH_NAME, NONE)

        Returns:
            추출된 텍스트 (표: Markdown, 이미지: [IMAGE] 마커)

        Example:
            >>> doc = Document("sample.hwpx")
            >>> text = doc.extract_text_fast()
            >>> text = doc.extract_text_fast(table_style=TableStyle.CSV)
        """
        if self._file_path is None:
            raise RuntimeError("파일 경로가 지정되지 않았습니다")

        if options is None:
            options = ExtractOptions()

        if table_style is not None:
            options.table_style = table_style
        if image_marker is not None:
            options.image_marker = image_marker

        if self._doc_type == DocumentType.HWP:
            with HWP5Reader(str(self._file_path)) as reader:
                return reader.extract_text(options)
        elif self._doc_type == DocumentType.HWPX:
            with HWPXReader(str(self._file_path)) as reader:
                return reader.extract_text(options)
        else:
            raise ValueError(f"지원하지 않는 문서 타입: {self._doc_type}")

    def get_tables_fast(
        self,
        style: TableStyle = TableStyle.MARKDOWN,
    ) -> List[str]:
        """
        Fast Layer로 모든 표를 추출합니다 (JVM 불필요).

        Args:
            style: 표 출력 스타일 (기본: MARKDOWN)

        Returns:
            표 문자열 리스트
        """
        if self._file_path is None:
            raise RuntimeError("파일 경로가 지정되지 않았습니다")

        options = ExtractOptions(table_style=style)

        if self._doc_type == DocumentType.HWP:
            with HWP5Reader(str(self._file_path)) as reader:
                tables = reader.get_tables(options)
                return [t.format(style) for t in tables]
        elif self._doc_type == DocumentType.HWPX:
            with HWPXReader(str(self._file_path)) as reader:
                tables = reader.get_tables(options)
                return [t.format(style) for t in tables]
        else:
            raise ValueError(f"지원하지 않는 문서 타입: {self._doc_type}")

    def extract_text_with_notes_fast(
        self,
        options: Optional[ExtractOptions] = None,
    ) -> ExtractResult:
        """
        Fast Layer로 텍스트와 각주/미주/하이퍼링크를 함께 추출합니다 (JVM 불필요).

        각주는 [^N], 미주는 [^eN] 형식의 마커로 본문에 표시되며,
        실제 내용은 ExtractResult의 footnotes, endnotes, hyperlinks에서 조회 가능합니다.

        Args:
            options: ExtractOptions 객체 (세부 옵션 직접 지정시)

        Returns:
            ExtractResult 객체 (text, footnotes, endnotes, hyperlinks 포함)

        Example:
            >>> doc = Document("sample.hwp", fast_mode=True)
            >>> result = doc.extract_text_with_notes_fast()
            >>> print(result.text)  # 본문 ([^1] 마커 포함)
            >>> for fn in result.footnotes:
            ...     print(f"각주 {fn.number}: {fn.text}")
        """
        if self._file_path is None:
            raise RuntimeError("파일 경로가 지정되지 않았습니다")

        if options is None:
            options = ExtractOptions()

        if self._doc_type == DocumentType.HWP:
            with HWP5Reader(str(self._file_path)) as reader:
                return reader.extract_text_with_notes(options)
        elif self._doc_type == DocumentType.HWPX:
            with HWPXReader(str(self._file_path)) as reader:
                return reader.extract_text_with_notes(options)
        else:
            raise ValueError(f"지원하지 않는 문서 타입: {self._doc_type}")

    def get_footnotes_fast(self) -> List[NoteData]:
        """
        Fast Layer로 모든 각주를 추출합니다 (JVM 불필요).

        Returns:
            각주 NoteData 리스트
        """
        result = self.extract_text_with_notes_fast()
        return result.footnotes

    def get_endnotes_fast(self) -> List[NoteData]:
        """
        Fast Layer로 모든 미주를 추출합니다 (JVM 불필요).

        Returns:
            미주 NoteData 리스트
        """
        result = self.extract_text_with_notes_fast()
        return result.endnotes

    def get_hyperlinks_fast(self) -> List[tuple]:
        """
        Fast Layer로 모든 하이퍼링크를 추출합니다 (JVM 불필요).

        Returns:
            하이퍼링크 (텍스트, URL) 튜플 리스트
        """
        result = self.extract_text_with_notes_fast()
        return result.hyperlinks

    def get_memos_fast(self) -> List[MemoData]:
        """
        Fast Layer로 메모를 추출합니다 (JVM 불필요).

        Returns:
            MemoData 리스트
        """
        if self._file_path is None:
            raise RuntimeError("파일 경로가 지정되지 않았습니다")

        if self._doc_type == DocumentType.HWP:
            with HWP5Reader(str(self._file_path)) as reader:
                return reader.get_memos()
        elif self._doc_type == DocumentType.HWPX:
            with HWPXReader(str(self._file_path)) as reader:
                return reader.get_memos()
        return []

    # HWP 전용 기능들
    def get_field_text(self, field_name: str) -> Optional[str]:
        """
        HWP 필드의 텍스트를 가져옵니다.

        Args:
            field_name: 필드 이름

        Returns:
            필드 텍스트 또는 None
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                "Field operations are only supported for HWP documents"
            )

        finder = HWPFieldFinder()
        return finder.get_click_here_text(self._java_object, field_name)

    def set_field_text(self, field_name: str, text: str) -> bool:
        """
        HWP 필드의 텍스트를 설정합니다.

        Args:
            field_name: 필드 이름
            text: 설정할 텍스트

        Returns:
            성공 여부
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                "Field operations are only supported for HWP documents"
            )

        finder = HWPFieldFinder()
        result = finder.set_field_text(
            self._java_object, finder._ControlType.FIELD_CLICKHERE, field_name, [text]
        )
        return result == finder._SetFieldResult.SUCCESS

    def find_controls(self, control_filter):
        """
        HWP 문서에서 조건에 맞는 컨트롤들을 찾습니다.

        Args:
            control_filter: 컨트롤 필터 함수

        Returns:
            찾은 컨트롤 리스트
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                "Control finding is only supported for HWP documents"
            )

        finder = HWPControlFinder()
        return finder.find_controls(self._java_object, control_filter)

    def get_tables(self):
        """
        HWP 문서에서 모든 표 컨트롤을 찾습니다.

        Returns:
            표 컨트롤 리스트
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                "Table operations are only supported for HWP documents"
            )

        finder = HWPControlFinder()
        return finder.find_controls_by_type(
            self._java_object, finder._ControlType.TABLE
        )

    def merge_table_cells(
        self, table_control, start_row: int, start_col: int, end_row: int, end_col: int
    ) -> bool:
        """
        HWP 표의 셀들을 병합합니다.

        Args:
            table_control: 표 컨트롤 객체
            start_row: 시작 행 인덱스
            start_col: 시작 열 인덱스
            end_row: 끝 행 인덱스
            end_col: 끝 열 인덱스

        Returns:
            성공 여부
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                "Table operations are only supported for HWP documents"
            )

        manager = HWPTableManager()
        return manager.merge_cells(
            table_control, start_row, start_col, end_row, end_col
        )

    def remove_table_row(self, table_control, row_index: int) -> bool:
        """
        HWP 표의 행을 삭제합니다.

        Args:
            table_control: 표 컨트롤 객체
            row_index: 삭제할 행 인덱스

        Returns:
            성공 여부
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                "Table operations are only supported for HWP documents"
            )

        manager = HWPTableManager()
        return manager.remove_row(table_control, row_index)

    def extract_table_text(self, table_control: "jpype.JObject") -> List[List[str]]:
        """
        표에서 셀별 텍스트를 추출합니다.

        Args:
            table_control: 표 컨트롤 객체 (HWP 파일에서만 지원)

        Returns:
            2차원 리스트: [[셀1, 셀2, ...], [셀1, 셀2, ...], ...]

        Raises:
            NotImplementedError: HWPX 파일인 경우
            ValueError: 잘못된 표 컨트롤 객체
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                f"표 텍스트 추출은 HWP 파일에서만 지원됩니다. "
                f"현재 파일 형식: {self._doc_type.value}"
            )

        if table_control is None:
            raise ValueError("표 컨트롤 객체가 None입니다")

        manager = HWPTableManager()
        return manager.extract_table_text(table_control)

    def get_table_as_markdown(self, table_control: "jpype.JObject") -> str:
        """
        표를 마크다운 형식으로 변환합니다.

        Args:
            table_control: 표 컨트롤 객체 (HWP 파일에서만 지원)
            delimiter: 구분자 (기본값: ",")

        Returns:
            마크다운 형식의 표 문자열

        Raises:
            NotImplementedError: HWPX 파일인 경우
            ValueError: 잘못된 표 컨트롤 객체
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                f"표 마크다운 변환은 HWP 파일에서만 지원됩니다. "
                f"현재 파일 형식: {self._doc_type.value}"
            )

        if table_control is None:
            raise ValueError("표 컨트롤 객체가 None입니다")

        manager = HWPTableManager()
        return manager.get_table_as_markdown(table_control)

    def get_table_as_csv(
        self, table_control: "jpype.JObject", delimiter: str = ","
    ) -> str:
        """
        표를 CSV 형식으로 변환합니다.

        Args:
            table_control: 표 컨트롤 객체 (HWP 파일에서만 지원)
            delimiter: 구분자 (기본값: ",")

        Returns:
            CSV 형식의 표 문자열

        Raises:
            NotImplementedError: HWPX 파일인 경우
            ValueError: 잘못된 표 컨트롤 객체 또는 구분자
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                f"표 CSV 변환은 HWP 파일에서만 지원됩니다. "
                f"현재 파일 형식: {self._doc_type.value}"
            )

        if table_control is None:
            raise ValueError("표 컨트롤 객체가 None입니다")

        if not delimiter or len(delimiter) == 0:
            raise ValueError("구분자는 빈 문자열일 수 없습니다")

        manager = HWPTableManager()
        return manager.get_table_as_csv(table_control, delimiter)

    def get_table_info(self, table_control) -> dict:
        """
        HWP 표의 정보를 가져옵니다.

        Args:
            table_control: 표 컨트롤 객체

        Returns:
            표 정보 딕셔너리
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                "Table operations are only supported for HWP documents"
            )

        manager = HWPTableManager()
        return manager.get_table_info(table_control)

    def insert_image(
        self,
        section_index: int,
        paragraph_index: int,
        image_path: str,
        width: Optional[float] = None,
        height: Optional[float] = None,
    ) -> bool:
        """
        HWP 문서에 이미지를 삽입합니다.

        Args:
            section_index: 섹션 인덱스
            paragraph_index: 문단 인덱스
            image_path: 이미지 파일 경로
            width: 이미지 너비 (mm, 옵션)
            height: 이미지 높이 (mm, 옵션)

        Returns:
            성공 여부
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                "Image insertion is only supported for HWP documents"
            )

        inserter = HWPImageInserter()
        success = inserter.insert_image_simple(
            self._java_object, section_index, paragraph_index, image_path, width, height
        )
        if success:
            self._is_modified = True
        return success

    def insert_hyperlink(
        self, section_index: int, paragraph_index: int, link_text: str, url: str
    ) -> bool:
        """
        HWP 문서에 하이퍼링크를 삽입합니다.

        Args:
            section_index: 섹션 인덱스
            paragraph_index: 문단 인덱스
            link_text: 링크 텍스트
            url: 하이퍼링크 URL

        Returns:
            성공 여부
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                "Hyperlink insertion is only supported for HWP documents"
            )

        inserter = HWPHyperlinkInserter()
        success = inserter.insert_hyperlink_simple(
            self._java_object, section_index, paragraph_index, link_text, url
        )
        if success:
            self._is_modified = True
        return success

    # HWPX 전용 기능들
    def find_objects(self, object_filter):
        """
        HWPX 문서에서 조건에 맞는 객체들을 찾습니다.

        Args:
            object_filter: 객체 필터 함수

        Returns:
            찾은 객체 리스트
        """
        if self._doc_type != DocumentType.HWPX:
            raise NotImplementedError(
                "Object finding is only supported for HWPX documents"
            )

        finder = HWPXObjectFinder()
        return finder.find_objects(self._java_object, object_filter)

    def find_tables(self):
        """
        HWPX 문서에서 모든 표 객체를 찾습니다.

        Returns:
            표 객체 리스트
        """
        if self._doc_type != DocumentType.HWPX:
            raise NotImplementedError(
                "Table finding is only supported for HWPX documents"
            )

        finder = HWPXObjectFinder()
        return finder.find_tables(self._java_object)

    def find_images(self):
        """
        HWPX 문서에서 모든 이미지 객체를 찾습니다.

        Returns:
            이미지 객체 리스트
        """
        if self._doc_type != DocumentType.HWPX:
            raise NotImplementedError(
                "Image finding is only supported for HWPX documents"
            )

        finder = HWPXObjectFinder()
        return finder.find_images(self._java_object)

    def find_paragraphs(self):
        """
        HWPX 문서에서 모든 문단 객체를 찾습니다.

        Returns:
            문단 객체 리스트
        """
        if self._doc_type != DocumentType.HWPX:
            raise NotImplementedError(
                "Paragraph finding is only supported for HWPX documents"
            )

        finder = HWPXObjectFinder()
        return finder.find_paragraphs(self._java_object)

    # HWPX 메모 기능들
    def find_memo_properties(self):
        """
        HWPX 문서에서 모든 메모 속성을 찾습니다.

        Returns:
            메모 속성 리스트
        """
        if self._doc_type != DocumentType.HWPX:
            raise NotImplementedError(
                "Memo operations are only supported for HWPX documents"
            )

        finder = HWPXObjectFinder()
        return finder.find_memo_properties(self._java_object)

    def get_memo_info(self, memo_property):
        """
        메모 속성의 정보를 가져옵니다.

        Args:
            memo_property: MemoPr 객체

        Returns:
            메모 정보 딕셔너리
        """
        if self._doc_type != DocumentType.HWPX:
            raise NotImplementedError(
                "Memo operations are only supported for HWPX documents"
            )

        manager = HWPXMemosManager()
        return manager.get_memo_info(memo_property)

    def create_memo_property(
        self,
        memo_id: str = "memo1",
        width: int = 200,
        line_color: str = "#000000",
        fill_color: str = "#FFFF00",
        active_color: str = "#FF0000",
    ) -> bool:
        """
        HWPX 문서에 메모 속성을 생성합니다.

        Args:
            memo_id: 메모 ID
            width: 메모 너비
            line_color: 선 색상 (HEX)
            fill_color: 채우기 색상 (HEX)
            active_color: 활성 색상 (HEX)

        Returns:
            성공 여부
        """
        if self._doc_type != DocumentType.HWPX:
            raise NotImplementedError(
                "Memo operations are only supported for HWPX documents"
            )

        manager = HWPXMemosManager()
        success = manager.create_memo_property(
            self._java_object, memo_id, width, line_color, fill_color, active_color
        )
        if success:
            self._is_modified = True
        return success

    def set_memo_shape_reference(self, section_index: int, memo_shape_id: str) -> bool:
        """
        섹션에 메모 모양 ID를 설정합니다.

        Args:
            section_index: 섹션 인덱스
            memo_shape_id: 메모 모양 ID

        Returns:
            성공 여부
        """
        if self._doc_type != DocumentType.HWPX:
            raise NotImplementedError(
                "Memo operations are only supported for HWPX documents"
            )

        manager = HWPXMemosManager()
        success = manager.set_memo_shape_id_ref(
            self._java_object, section_index, memo_shape_id
        )
        if success:
            self._is_modified = True
        return success

    def find_memos_in_content(self):
        """
        HWPX 문서 내용에서 메모 관련 요소들을 찾습니다.

        Returns:
            메모 정보 리스트
        """
        if self._doc_type != DocumentType.HWPX:
            raise NotImplementedError(
                "Memo operations are only supported for HWPX documents"
            )

        manager = HWPXMemosManager()
        return manager.find_memos_in_content(self._java_object)

    # HWP 주석 기능들
    def find_comments(self):
        """
        HWP 문서에서 모든 주석(숨은 설명)을 찾습니다.

        Returns:
            주석 컨트롤 리스트
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                "Comment operations are only supported for HWP documents"
            )

        manager = HWPCommentManager()
        return manager.find_comments(self._java_object)

    def get_comment_text(self, comment_control):
        """
        주석 컨트롤에서 텍스트를 추출합니다.

        Args:
            comment_control: ControlHiddenComment 객체

        Returns:
            주석 텍스트
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                "Comment operations are only supported for HWP documents"
            )

        manager = HWPCommentManager()
        return manager.get_comment_text(comment_control)

    def create_comment(
        self, section_index: int, paragraph_index: int, comment_text: str
    ) -> bool:
        """
        HWP 문서에 주석(숨은 설명)을 추가합니다.

        Args:
            section_index: 섹션 인덱스
            paragraph_index: 문단 인덱스
            comment_text: 주석 텍스트

        Returns:
            성공 여부
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                "Comment operations are only supported for HWP documents"
            )

        manager = HWPCommentManager()
        success = manager.create_comment_simple(
            self._java_object, section_index, paragraph_index, comment_text
        )
        if success:
            self._is_modified = True
        return success

    def get_comment_info(self, comment_control) -> dict:
        """
        주석 컨트롤의 정보를 가져옵니다.

        Args:
            comment_control: ControlHiddenComment 객체

        Returns:
            주석 정보 딕셔너리
        """
        if self._doc_type != DocumentType.HWP:
            raise NotImplementedError(
                "Comment operations are only supported for HWP documents"
            )

        manager = HWPCommentManager()
        return manager.get_comment_info(comment_control)

    def replace_all_texts(
        self,
        replacer: Callable[[str], str],
        locations: Optional[List[str]] = None,
    ) -> int:
        """
        문서의 텍스트를 일괄 교체합니다 (HWPX만 지원).

        본문, 표, 각주, 미주, 메모 등 모든 위치의 텍스트를 교체할 수 있습니다.
        중첩된 표(표 안의 표)의 텍스트도 자동으로 처리됩니다.

        Args:
            replacer: 텍스트 변환 함수 (old_text) -> new_text
            locations: 교체할 위치 리스트. None이면 모든 위치.
                      가능한 값: ["body", "table", "footnote", "endnote", "memo"]

        Returns:
            교체된 텍스트 요소 수

        Example:
            >>> doc = editor("sample.hwpx")
            >>>
            >>> # 모든 텍스트를 대문자로
            >>> count = doc.replace_all_texts(str.upper)
            >>>
            >>> # 표 텍스트만 교체
            >>> count = doc.replace_all_texts(my_func, locations=["table"])
            >>>
            >>> # 본문과 표만 교체 (각주, 미주, 메모 제외)
            >>> count = doc.replace_all_texts(my_func, locations=["body", "table"])
            >>>
            >>> doc.save("output.hwpx")
        """
        if self._doc_type != DocumentType.HWPX:
            raise NotImplementedError(
                "Text replacement is currently only supported for HWPX documents"
            )

        text_replacer = HWPXTextReplacer(self._java_object)
        count = text_replacer.replace_by_location(replacer, locations)

        if count > 0:
            self._is_modified = True

        return count

    def replace_table_texts(self, replacer: Callable[[str], str]) -> int:
        """
        문서의 모든 표 텍스트를 교체합니다 (HWPX만 지원).

        중첩된 표(표 안의 표)의 텍스트도 자동으로 처리됩니다.

        Args:
            replacer: 텍스트 변환 함수

        Returns:
            교체된 텍스트 요소 수
        """
        return self.replace_all_texts(replacer, locations=["table"])

    def get_hwpx_table_manager(self) -> "HWPXTableManager":
        """
        HWPX 표 관리자를 반환합니다.

        더 세밀한 표 조작이 필요한 경우 사용합니다.

        Returns:
            HWPXTableManager 인스턴스
        """
        if self._doc_type != DocumentType.HWPX:
            raise NotImplementedError(
                "HWPXTableManager is only available for HWPX documents"
            )

        return HWPXTableManager(self._java_object)

    def save(self, file_path: Optional[Union[str, Path]] = None) -> None:
        """
        문서를 파일로 저장합니다.

        Args:
            file_path: 저장할 파일 경로 (지정하지 않으면 원본 파일 경로 사용)
        """
        if self._java_object is None:
            raise RuntimeError("Document not loaded")

        save_path = Path(file_path) if file_path else self._file_path
        if save_path is None:
            raise ValueError("File path must be specified for new documents")

        # 확장자에 따라 적절한 라이터 선택
        if save_path.suffix.lower() == ".hwp":
            writer = HWPWriter()
            writer.write_file(self._java_object, save_path)
        elif save_path.suffix.lower() == ".hwpx":
            writer = HWPXWriter()
            writer.write_file(self._java_object, save_path)
        else:
            raise ValueError(f"Unsupported file extension: {save_path.suffix}")

        self._file_path = save_path
        self._is_modified = False
        logger.info(f"Saved document: {save_path}")

    def save_as_bytes(self) -> bytes:
        """
        문서를 바이트 데이터로 반환합니다.

        Returns:
            문서 데이터 바이트
        """
        if self._java_object is None:
            raise RuntimeError("Document not loaded")

        if self._doc_type == DocumentType.HWP:
            writer = HWPWriter()
            return writer.write_stream(self._java_object)
        else:
            raise NotImplementedError("HWPX byte stream writing is not yet implemented")

    def close(self) -> None:
        """문서를 닫고 리소스를 해제합니다."""
        if self._java_object is not None:
            # Java 객체 참조 해제
            self._java_object = None
            logger.debug("Document closed")

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()

    def __repr__(self) -> str:
        status = "modified" if self._is_modified else "unmodified"
        path = str(self._file_path) if self._file_path else "new document"
        return f"Document(type={self._doc_type.value}, path={path}, status={status})"
