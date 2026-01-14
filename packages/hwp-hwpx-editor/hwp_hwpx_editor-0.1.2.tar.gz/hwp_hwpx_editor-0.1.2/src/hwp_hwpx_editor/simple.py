"""
간단한 텍스트 추출 함수들 (extract-hwp 스타일)

extract-hwp 라이브러리의 단순함과 견고함을 참고하여 구현했습니다.
강력한 파일 검증과 오류 처리 기능을 제공합니다.
"""

import os
import logging
from pathlib import Path
from typing import Tuple, Optional, Union

from .parser import HWPParser
from .document import DocumentType
from .core.exceptions import (
    FileNotFoundError as HWPFileNotFoundError,
    PermissionDeniedError,
    UnsupportedFileFormatError,
    EncryptedFileError,
    FileTooLargeError,
    EmptyFileError,
    ParsingError,
    validate_file_exists,
    validate_file_access,
    validate_file_size,
    log_operation_result,
)

logger = logging.getLogger(__name__)


def extract_text_from_hwp(filepath: Union[str, Path]) -> Tuple[str, Optional[str]]:
    """
    HWP/HWPX 파일에서 텍스트를 추출합니다 (extract-hwp 스타일).

    extract-hwp 라이브러리의 간단한 API를 참고하여 구현했습니다.
    강력한 파일 검증과 오류 처리를 제공합니다.

    Args:
        filepath: HWP 또는 HWPX 파일 경로

    Returns:
        tuple: (추출된_텍스트, 오류_메시지) 형태의 튜플
               성공시 오류_메시지는 None

    Raises:
        FileNotFoundError: 파일을 찾을 수 없음
        PermissionDeniedError: 파일 접근 권한이 없음
        UnsupportedFileFormatError: 지원하지 않는 파일 형식
        EncryptedFileError: 암호화된 파일
        FileTooLargeError: 파일이 너무 큼
        EmptyFileError: 빈 파일
    """
    filepath_obj = Path(filepath)

    try:
        # 1. 파일 존재 및 기본 검증
        validate_file_exists(filepath_obj)
        validate_file_access(filepath_obj, os.R_OK)
        validate_file_size(filepath_obj)

        # 2. 파일 형식 검증
        if not _is_supported_format(filepath_obj):
            raise UnsupportedFileFormatError(
                f"지원하지 않는 파일 형식입니다: {filepath_obj.suffix}",
                str(filepath_obj),
            )

        # 3. 암호화 파일 체크
        if is_hwp_file_password_protected(filepath_obj):
            raise EncryptedFileError("암호로 보호된 파일입니다", str(filepath_obj))

        # 4. 텍스트 추출
        parser = HWPParser()
        text = ""

        with parser.read(filepath_obj) as doc:
            text = doc.extract_text() or ""

            # 텍스트 정리
            text = text.strip()

        log_operation_result("텍스트 추출", filepath_obj, True, f"{len(text)}자")
        return text, None

    except (
        HWPFileNotFoundError,
        PermissionDeniedError,
        UnsupportedFileFormatError,
        EncryptedFileError,
        FileTooLargeError,
        EmptyFileError,
    ):
        # 이미 적절한 예외가 발생했으므로 재발생
        raise
    except Exception as e:
        error_msg = f"텍스트 추출 중 오류: {str(e)}"
        log_operation_result("텍스트 추출", filepath_obj, False, error_msg, e)
        return "", error_msg


def _is_supported_format(filepath: Path) -> bool:
    """파일 형식이 지원되는지 확인합니다."""
    supported_extensions = {".hwp", ".hwpx"}
    return filepath.suffix.lower() in supported_extensions


def extract_text_from_hwpx(filepath: Union[str, Path]) -> str:
    """
    HWPX 파일에서 텍스트를 추출합니다 (extract-hwp 스타일).

    Args:
        filepath: HWPX 파일 경로

    Returns:
        추출된 텍스트 (오류 시 빈 문자열)

    Raises:
        UnsupportedFileFormatError: HWPX 파일이 아님
        기타 extract_text_from_hwp의 예외들
    """
    filepath_obj = Path(filepath)

    if filepath_obj.suffix.lower() != ".hwpx":
        raise UnsupportedFileFormatError(
            f"HWPX 파일이 아닙니다: {filepath_obj.suffix}", str(filepath_obj)
        )

    text, error = extract_text_from_hwp(filepath_obj)
    return text if error is None else ""


def extract_text_from_hwp5(filepath: Union[str, Path]) -> str:
    """
    HWP 5.0 파일에서 텍스트를 추출합니다 (extract-hwp 스타일).

    Args:
        filepath: HWP 파일 경로

    Returns:
        추출된 텍스트 (오류 시 빈 문자열)

    Raises:
        UnsupportedFileFormatError: HWP 파일이 아님
        기타 extract_text_from_hwp의 예외들
    """
    filepath_obj = Path(filepath)

    if filepath_obj.suffix.lower() != ".hwp":
        raise UnsupportedFileFormatError(
            f"HWP 파일이 아닙니다: {filepath_obj.suffix}", str(filepath_obj)
        )

    text, error = extract_text_from_hwp(filepath_obj)
    return text if error is None else ""


def is_hwp_file_password_protected(filepath: Union[str, Path]) -> bool:
    """
    HWP/HWPX 파일이 암호로 보호되어 있는지 확인합니다.

    extract-hwp 라이브러리의 암호화 감지 기능을 참고하여 구현했습니다.
    강력한 파일 검증과 오류 처리를 제공합니다.

    Args:
        filepath: 확인할 파일 경로

    Returns:
        암호로 보호된 경우 True, 그렇지 않으면 False

    Raises:
        FileNotFoundError: 파일을 찾을 수 없음
        PermissionDeniedError: 파일 접근 권한이 없음
    """
    filepath_obj = Path(filepath)

    try:
        # 파일 존재 및 접근 권한 검증
        validate_file_exists(filepath_obj)
        validate_file_access(filepath_obj, os.R_OK)

        # 확장자에 따라 처리
        suffix = filepath_obj.suffix.lower()
        if suffix == ".hwpx":
            return _is_hwpx_password_protected(filepath_obj)
        elif suffix == ".hwp":
            return _is_hwp5_password_protected(filepath_obj)
        else:
            logger.debug(f"지원하지 않는 파일 형식: {suffix}")
            return False

    except (HWPFileNotFoundError, PermissionDeniedError):
        raise
    except Exception as e:
        logger.warning(f"암호화 확인 실패 {filepath}: {e}")
        return False  # 안전하게 False 반환  # 안전하게 False 반환


def _is_hwpx_password_protected(filepath: Path) -> bool:
    """
    HWPX 파일의 암호화 여부를 확인합니다.

    HWPX 파일은 ZIP 형식으로, manifest.xml 파일에 암호화 정보가 있습니다.

    Args:
        filepath: HWPX 파일 경로

    Returns:
        암호화된 경우 True
    """
    try:
        import zipfile
        import xml.etree.ElementTree as ET

        with zipfile.ZipFile(filepath, "r") as zip_file:
            # META-INF/manifest.xml 파일 확인
            manifest_path = "META-INF/manifest.xml"
            if manifest_path not in zip_file.namelist():
                logger.debug(f"HWPX 파일에 manifest.xml이 없음: {filepath}")
                return False

            # manifest.xml 읽기 및 파싱
            with zip_file.open(manifest_path) as manifest_file:
                manifest_content = manifest_file.read()

                # XML 파싱 (인코딩 처리)
                try:
                    root = ET.fromstring(manifest_content)
                except ET.ParseError as e:
                    logger.warning(f"XML 파싱 실패 {filepath}: {e}")
                    return False

                # 암호화 데이터 엘리먼트 검색
                for elem in root.iter():
                    tag_name = elem.tag.lower()
                    if "encryption-data" in tag_name or "encryptiondata" in tag_name:
                        logger.debug(f"암호화된 HWPX 파일 감지: {filepath}")
                        return True

                return False

    except zipfile.BadZipFile:
        logger.warning(f"손상된 ZIP 파일: {filepath}")
        return False
    except Exception as e:
        logger.warning(f"HWPX 암호화 확인 실패 {filepath}: {e}")
        return False


def _is_hwp5_password_protected(filepath: Path) -> bool:
    """
    HWP 5.0 파일의 암호화 여부를 확인합니다.

    HWP 5.0 파일은 OLE 형식으로, FileHeader 스트림에 암호화 정보가 있습니다.

    Args:
        filepath: HWP 파일 경로

    Returns:
        암호화된 경우 True
    """
    try:
        # Java 기반 라이브러리를 사용하여 파일 열기 시도
        # 암호화된 파일은 열리지 않으므로 이를 이용한 검증
        parser = HWPParser()

        try:
            with parser.read(filepath) as doc:
                # 파일을 성공적으로 열었으므로 암호화되지 않은 것으로 판단
                logger.debug(f"암호화되지 않은 HWP 파일: {filepath}")
                return False

        except EncryptedFileError:
            # 명시적인 암호화 예외 발생
            logger.debug(f"암호화된 HWP 파일 감지: {filepath}")
            return True

        except Exception as e:
            # 다른 오류의 경우 (파싱 오류, 파일 손상 등)
            # 암호화 여부를 확실히 판별할 수 없으므로 False 반환
            logger.debug(f"HWP 파일 상태 확인 불가 {filepath}: {e}")
            return False

    except Exception as e:
        logger.warning(f"HWP5 암호화 확인 실패 {filepath}: {e}")
        return False


def is_hwpx_password_protected(filepath: Union[str, Path]) -> bool:
    """
    HWPX 파일이 암호로 보호되어 있는지 확인합니다.

    Args:
        filepath: HWPX 파일 경로

    Returns:
        암호로 보호된 경우 True

    Raises:
        UnsupportedFileFormatError: HWPX 파일이 아님
        기타 파일 검증 관련 예외들
    """
    filepath_obj = Path(filepath)

    if filepath_obj.suffix.lower() != ".hwpx":
        raise UnsupportedFileFormatError(
            f"HWPX 파일이 아닙니다: {filepath_obj.suffix}", str(filepath_obj)
        )

    return _is_hwpx_password_protected(filepath_obj)


def is_hwp5_password_protected(filepath: Union[str, Path]) -> bool:
    """
    HWP 5.0 파일이 암호로 보호되어 있는지 확인합니다.

    Args:
        filepath: HWP 파일 경로

    Returns:
        암호로 보호된 경우 True

    Raises:
        UnsupportedFileFormatError: HWP 파일이 아님
        기타 파일 검증 관련 예외들
    """
    filepath_obj = Path(filepath)

    if filepath_obj.suffix.lower() != ".hwp":
        raise UnsupportedFileFormatError(
            f"HWP 파일이 아닙니다: {filepath_obj.suffix}", str(filepath_obj)
        )

    return _is_hwp5_password_protected(filepath_obj)


def extract_text_from_hwp_fast(
    filepath: Union[str, Path],
    table_style: str = "markdown",
    image_marker: str = "simple",
) -> Tuple[str, Optional[str]]:
    """
    HWP/HWPX 파일에서 Fast Layer로 텍스트를 추출합니다 (JVM 불필요).

    JVM 없이 순수 Python으로 동작하여 빠릅니다.
    표는 Markdown 형식으로, 이미지는 [IMAGE] 마커로 출력됩니다.

    Args:
        filepath: HWP 또는 HWPX 파일 경로
        table_style: 표 출력 스타일 ("markdown", "csv", "inline")
        image_marker: 이미지 마커 스타일 ("simple", "with_name", "none")

    Returns:
        tuple: (추출된_텍스트, 오류_메시지) 형태의 튜플
               성공시 오류_메시지는 None

    Example:
        >>> text, error = extract_text_from_hwp_fast("document.hwpx")
        >>> if error is None:
        ...     print(text)
    """
    from .fast import (
        HWP5FastReader,
        HWPXFastReader,
        ExtractOptions,
        TableStyle,
        ImageMarkerStyle,
    )

    filepath_obj = Path(filepath)

    try:
        validate_file_exists(filepath_obj)
        validate_file_access(filepath_obj, os.R_OK)
        validate_file_size(filepath_obj)

        if not _is_supported_format(filepath_obj):
            raise UnsupportedFileFormatError(
                f"지원하지 않는 파일 형식입니다: {filepath_obj.suffix}",
                str(filepath_obj),
            )

        options = ExtractOptions()

        style_map = {
            "markdown": TableStyle.MARKDOWN,
            "csv": TableStyle.CSV,
            "inline": TableStyle.INLINE,
        }
        options.table_style = style_map.get(table_style.lower(), TableStyle.MARKDOWN)

        marker_map = {
            "simple": ImageMarkerStyle.SIMPLE,
            "with_name": ImageMarkerStyle.WITH_NAME,
            "none": ImageMarkerStyle.NONE,
        }
        options.image_marker = marker_map.get(
            image_marker.lower(), ImageMarkerStyle.SIMPLE
        )

        suffix = filepath_obj.suffix.lower()
        if suffix == ".hwp":
            with HWP5FastReader(str(filepath_obj)) as reader:
                text = reader.extract_text(options)
        elif suffix == ".hwpx":
            with HWPXFastReader(str(filepath_obj)) as reader:
                text = reader.extract_text(options)
        else:
            raise UnsupportedFileFormatError(
                f"지원하지 않는 파일 형식입니다: {suffix}", str(filepath_obj)
            )

        log_operation_result("Fast 텍스트 추출", filepath_obj, True, f"{len(text)}자")
        return text.strip(), None

    except (
        HWPFileNotFoundError,
        PermissionDeniedError,
        UnsupportedFileFormatError,
        EncryptedFileError,
        FileTooLargeError,
        EmptyFileError,
    ):
        raise
    except Exception as e:
        error_msg = f"Fast 텍스트 추출 중 오류: {str(e)}"
        log_operation_result("Fast 텍스트 추출", filepath_obj, False, error_msg, e)
        return "", error_msg
