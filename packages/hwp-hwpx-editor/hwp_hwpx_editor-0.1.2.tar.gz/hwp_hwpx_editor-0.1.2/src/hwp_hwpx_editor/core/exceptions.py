"""
예외 클래스들

extract-hwp 라이브러리의 견고한 오류 처리를 참고하여 개선되었습니다.
표준화된 예외 처리와 로깅 기능을 제공합니다.
"""

import logging
from pathlib import Path
from typing import Optional, Union

logger = logging.getLogger(__name__)


class HWPParserError(Exception):
    """
    HWP 파서 기본 예외 클래스.

    모든 HWP 관련 예외의 기반 클래스입니다.

    Args:
        message: 오류 메시지
        filepath: 관련 파일 경로 (선택사항)
        cause: 원인 예외 (선택사항)
    """

    def __init__(
        self,
        message: str,
        filepath: Optional[Union[str, Path]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        self.message = message
        self.filepath = Path(filepath) if filepath else None
        self.cause = cause

        # 표준화된 오류 메시지 생성
        full_message = message
        if filepath:
            full_message += f" (파일: {filepath})"

        super().__init__(full_message)

        # 원인 예외가 있다면 로깅
        if cause:
            logger.debug(f"예외 원인: {cause}", exc_info=cause)


class JVMNotStartedError(HWPParserError):
    """JVM이 시작되지 않은 경우 발생하는 예외."""
    pass


class FileNotFoundError(HWPParserError):
    """파일을 찾을 수 없는 경우 발생하는 예외."""
    pass


class PermissionDeniedError(HWPParserError):
    """파일 접근 권한이 없는 경우 발생하는 예외."""
    pass


class UnsupportedFileFormatError(HWPParserError):
    """지원하지 않는 파일 형식인 경우 발생하는 예외."""
    pass


class EncryptedFileError(HWPParserError):
    """암호화된 파일을 처리하려는 경우 발생하는 예외."""
    pass


class FileTooLargeError(HWPParserError):
    """파일이 너무 큰 경우 발생하는 예외."""
    pass


class EmptyFileError(HWPParserError):
    """빈 파일인 경우 발생하는 예외."""
    pass


class ParsingError(HWPParserError):
    """파일 파싱 중 오류가 발생한 경우."""
    pass


class WritingError(HWPParserError):
    """파일 쓰기 중 오류가 발생한 경우."""
    pass


class HWPLibError(HWPParserError):
    """hwplib 관련 오류가 발생한 경우."""
    pass


class HWPXLibError(HWPParserError):
    """hwpxlib 관련 오류가 발생한 경우."""
    pass


class ValidationError(HWPParserError):
    """입력 데이터 검증 실패시 발생하는 예외."""
    pass


def create_error_message(
    operation: str,
    filepath: Union[str, Path],
    error: Exception
) -> str:
    """
    표준화된 오류 메시지를 생성합니다.

    Args:
        operation: 수행된 작업명
        filepath: 관련 파일 경로
        error: 발생한 예외

    Returns:
        표준화된 오류 메시지 문자열

    Example:
        >>> create_error_message("파일 읽기", "doc.hwp", FileNotFoundError())
        "파일 읽기 실패: doc.hwp - [Errno 2] No such file or directory"
    """
    filepath_str = str(filepath)
    return f"{operation} 실패: {filepath_str} - {str(error)}"


def log_operation_result(
    operation: str,
    filepath: Union[str, Path],
    success: bool,
    details: Optional[str] = None,
    error: Optional[Exception] = None
) -> None:
    """
    작업 결과를 표준화된 방식으로 로깅합니다.

    Args:
        operation: 수행된 작업명
        filepath: 관련 파일 경로
        success: 작업 성공 여부
        details: 추가 세부 정보
        error: 실패시 예외 객체

    Example:
        >>> log_operation_result("텍스트 추출", "doc.hwp", True, "1500자 추출")
        INFO: 텍스트 추출 성공: doc.hwp (1500자 추출)
    """
    filepath_str = str(filepath)

    if success:
        message = f"{operation} 성공: {filepath_str}"
        if details:
            message += f" ({details})"
        logger.info(message)
    else:
        message = f"{operation} 실패: {filepath_str}"
        if details:
            message += f" - {details}"
        if error:
            logger.error(message, exc_info=error)
        else:
            logger.error(message)


def safe_operation(
    operation_name: str,
    filepath: Optional[Union[str, Path]] = None
) -> callable:
    """
    안전한 작업 실행을 위한 데코레이터.

    예외를 적절히 처리하고 로깅합니다.

    Args:
        operation_name: 작업명
        filepath: 관련 파일 경로

    Returns:
        데코레이트된 함수

    Example:
        @safe_operation("파일 읽기", "document.hwp")
        def read_file():
            # 작업 코드
            pass
    """
    def decorator(func: callable) -> callable:
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                log_operation_result(operation_name, filepath or "unknown", True)
                return result
            except Exception as e:
                log_operation_result(
                    operation_name,
                    filepath or "unknown",
                    False,
                    str(e),
                    e
                )
                raise
        return wrapper
    return decorator


def validate_file_exists(filepath: Union[str, Path]) -> Path:
    """
    파일 존재 여부를 검증합니다.

    Args:
        filepath: 검증할 파일 경로

    Returns:
        Path 객체

    Raises:
        FileNotFoundError: 파일이 존재하지 않음
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}", str(filepath))
    return path


def validate_file_access(filepath: Union[str, Path], access_mode: int = 4) -> Path:
    """
    파일 접근 권한을 검증합니다.

    Args:
        filepath: 검증할 파일 경로
        access_mode: 접근 모드 (os.R_OK, os.W_OK 등)

    Returns:
        Path 객체

    Raises:
        PermissionDeniedError: 권한이 없음
    """
    import os

    path = Path(filepath)
    if not os.access(path, access_mode):
        mode_name = "읽기" if access_mode == os.R_OK else "쓰기"
        raise PermissionDeniedError(f"파일 {mode_name} 권한이 없습니다: {filepath}", str(filepath))
    return path


def validate_file_size(filepath: Union[str, Path], max_size_mb: int = 100) -> Path:
    """
    파일 크기를 검증합니다.

    Args:
        filepath: 검증할 파일 경로
        max_size_mb: 최대 허용 크기 (MB)

    Returns:
        Path 객체

    Raises:
        FileTooLargeError: 파일이 너무 큼
        EmptyFileError: 빈 파일임
    """
    path = Path(filepath)
    size_bytes = path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    if size_bytes == 0:
        raise EmptyFileError(f"빈 파일입니다: {filepath}", str(filepath))

    if size_mb > max_size_mb:
        raise FileTooLargeError(
            ".1f",
            str(filepath)
        )

    return path
