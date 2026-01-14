"""
HWP-HWPX Editor - JVM 기반 한글 문서 편집 라이브러리

hwp-hwpx-parser의 확장 패키지로, JVM(Java)을 사용하여 문서 편집 기능을 제공합니다.

기본 사용법:
    >>> from hwp_hwpx_editor import HWPEditor, Document
    >>>
    >>> editor = HWPEditor()
    >>> doc = editor('document.hwp')
    >>> text = doc.extract_text()
    >>> doc.save('output.hwp')

필수 요구사항:
    - Java Runtime Environment (JRE) 8+
    - hwp-hwpx-parser (자동 설치)
"""

__version__ = "0.1.0"

from .parser import HWPParser as HWPEditor
from .document import Document, DocumentType
from .core import (
    initialize_jvm,
    JVMManager,
    get_jvm_manager,
    shutdown_jvm,
    is_jvm_running,
)
from .core.exceptions import (
    HWPParserError,
    JVMNotStartedError,
    UnsupportedFileFormatError,
    ParsingError,
    WritingError,
    HWPLibError,
    HWPXLibError,
)
from .simple import (
    extract_text_from_hwp,
    extract_text_from_hwpx,
    extract_text_from_hwp5,
    extract_text_from_hwp_fast,
    is_hwp_file_password_protected,
    is_hwpx_password_protected,
    is_hwp5_password_protected,
)

from .hwp import (
    HWPReader,
    HWPWriter,
    HWPTextExtractor,
    HWPTextExtractMethod,
    HWPFieldFinder,
    HWPFieldControlType,
    HWPFieldTextExtractMethod,
    HWPSetFieldResult,
    HWPControlFinder,
    HWPControlType,
    HWPControlFilter,
    HWPTableManager,
    HWPCreator,
    HWPImageInserter,
    HWPHyperlinkInserter,
    HWPCommentManager,
)

from .hwpx import (
    HWPXReader,
    HWPXWriter,
    HWPXTextExtractor,
    HWPXTextExtractMethod,
    HWPXTextMarks,
    HWPXCreator,
    HWPXObjectFinder,
    HWPXObjectFilter,
    HWPXMemosManager,
    HWPXTableManager,
    HWPXTextIterator,
    HWPXTextReplacer,
)

from hwp_hwpx_parser import (
    HWP5Reader,
    HWPXReader as HWPXPureReader,
    Reader,
    ExtractOptions,
    TableData,
    TableStyle,
    ImageMarkerStyle,
    NoteData,
    HyperlinkData,
    MemoData,
    ExtractResult,
    read,
    extract_hwp5,
    extract_hwpx,
)

HWPParser = HWPEditor

__all__ = [
    "HWPEditor",
    "HWPParser",
    "Document",
    "DocumentType",
    "initialize_jvm",
    "JVMManager",
    "get_jvm_manager",
    "shutdown_jvm",
    "is_jvm_running",
    "HWPParserError",
    "JVMNotStartedError",
    "UnsupportedFileFormatError",
    "ParsingError",
    "WritingError",
    "HWPLibError",
    "HWPXLibError",
    "extract_text_from_hwp",
    "extract_text_from_hwpx",
    "extract_text_from_hwp5",
    "extract_text_from_hwp_fast",
    "is_hwp_file_password_protected",
    "is_hwpx_password_protected",
    "is_hwp5_password_protected",
    "HWPReader",
    "HWPWriter",
    "HWPTextExtractor",
    "HWPTextExtractMethod",
    "HWPFieldFinder",
    "HWPFieldControlType",
    "HWPFieldTextExtractMethod",
    "HWPSetFieldResult",
    "HWPControlFinder",
    "HWPControlType",
    "HWPControlFilter",
    "HWPTableManager",
    "HWPCreator",
    "HWPImageInserter",
    "HWPHyperlinkInserter",
    "HWPCommentManager",
    "HWPXReader",
    "HWPXWriter",
    "HWPXTextExtractor",
    "HWPXTextExtractMethod",
    "HWPXTextMarks",
    "HWPXCreator",
    "HWPXObjectFinder",
    "HWPXObjectFilter",
    "HWPXMemosManager",
    "HWPXTableManager",
    "HWPXTextIterator",
    "HWPXTextReplacer",
    "HWP5Reader",
    "HWPXPureReader",
    "Reader",
    "ExtractOptions",
    "TableData",
    "TableStyle",
    "ImageMarkerStyle",
    "NoteData",
    "HyperlinkData",
    "MemoData",
    "ExtractResult",
    "read",
    "extract_hwp5",
    "extract_hwpx",
]
