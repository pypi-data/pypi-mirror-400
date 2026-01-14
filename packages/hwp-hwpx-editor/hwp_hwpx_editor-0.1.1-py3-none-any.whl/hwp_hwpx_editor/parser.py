"""
메인 파서 클래스
"""

from pathlib import Path
from typing import Union, Optional

from .document import Document, DocumentType
from .core import initialize_jvm


class HWPParser:
    """
    HWP 파일 파서

    HWP와 HWPX 파일을 읽고 쓸 수 있는 통합 인터페이스를 제공합니다.

    Rust hwp-rs의 libhwp을 참고하여 간단하고 직관적인 API를 제공합니다.
    """

    def __init__(self):
        """파서를 초기화합니다."""
        initialize_jvm()

    def __call__(self, file_path: Union[str, Path]) -> Document:
        """
        파일을 읽어 Document 객체를 반환합니다. (Rust 스타일)

        Args:
            file_path: 파일 경로

        Returns:
            Document 객체

        Example:
            parser = HWPParser()
            doc = parser('document.hwp')  # Rust 스타일 호출
        """
        return self.read(file_path)

    def read(self, file_path: Union[str, Path], doc_type: Optional[DocumentType] = None) -> Document:
        """
        파일을 읽어 Document 객체를 반환합니다.

        Args:
            file_path: 파일 경로
            doc_type: 문서 타입 (지정하지 않으면 자동 판별)

        Returns:
            Document 객체
        """
        return Document(file_path, doc_type)

    def create_blank(self, doc_type: DocumentType = DocumentType.HWPX) -> Document:
        """
        빈 문서를 생성합니다.

        Args:
            doc_type: 문서 타입

        Returns:
            Document 객체
        """
        return Document(doc_type=doc_type)
