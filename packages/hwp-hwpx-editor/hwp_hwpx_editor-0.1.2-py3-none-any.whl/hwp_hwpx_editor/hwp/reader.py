"""
HWP 파일 읽기 모듈

Java HWP 라이브러리를 사용하여 HWP 5.0 파일을 읽고 파싱합니다.
강력한 오류 처리와 검증 기능을 제공합니다.
"""

import jpype
from pathlib import Path
from typing import Optional, Union, Any
import logging

from ..core import ensure_jvm_running, HWPLibError, FileNotFoundError, ParsingError
from ..core.exceptions import (
    validate_file_exists,
    validate_file_access,
    validate_file_size,
)

logger = logging.getLogger(__name__)


class HWPReader:
    """
    HWP 파일 읽기 클래스.

    Java HWP 라이브러리를 사용하여 HWP 5.0 파일을 안전하게 읽고 파싱합니다.
    """

    def __init__(self) -> None:
        """HWPReader 인스턴스를 초기화합니다."""
        ensure_jvm_running()

        # Java 클래스 import (실패시 명확한 오류 메시지)
        try:
            self._HWPReader = jpype.JClass("kr.dogfoot.hwplib.reader.HWPReader")
            self._HWPFile = jpype.JClass("kr.dogfoot.hwplib.object.HWPFile")
            logger.debug("HWP Java 클래스들을 성공적으로 import했습니다")
        except Exception as e:
            error_msg = f"HWP Java 클래스 import 실패: {e}"
            logger.error(error_msg)
            raise HWPLibError(error_msg) from e

    def read_file(self, file_path: Union[str, Path]) -> "jpype.JObject":
        """
        HWP 파일을 읽어 HWPFile 객체를 반환합니다.

        Args:
            file_path: HWP 파일 경로

        Returns:
            HWPFile 객체 (Java 객체)

        Raises:
            FileNotFoundError: 파일을 찾을 수 없음
            ParsingError: 파일 파싱 중 오류
            HWPLibError: HWP 라이브러리 관련 오류
        """
        file_path_obj = Path(file_path)

        # 1. 파일 검증
        validate_file_exists(file_path_obj)
        validate_file_access(file_path_obj)
        validate_file_size(file_path_obj)

        # 2. HWP 파일 형식 검증
        if file_path_obj.suffix.lower() != ".hwp":
            raise ParsingError(
                f"HWP 파일 형식이 아닙니다: {file_path_obj.suffix}", str(file_path_obj)
            )

        try:
            logger.info(f"HWP 파일 읽기 시작: {file_path_obj}")

            # 3. Java HWP 라이브러리를 사용하여 파일 읽기
            hwp_file = self._HWPReader.fromFile(str(file_path_obj.resolve()))

            if hwp_file is None:
                raise ParsingError(
                    "HWP 파일 파싱에 실패했습니다 (null 반환)", str(file_path_obj)
                )

            # 4. 기본 구조 검증
            self._validate_hwp_structure(hwp_file, file_path_obj)

            logger.info(f"HWP 파일 읽기 성공: {file_path_obj}")
            return hwp_file

        except jpype.JException as e:
            # Java 레벨 예외 처리
            error_msg = f"HWP 파일 파싱 실패: {e}"
            logger.error(error_msg)
            raise ParsingError(error_msg, str(file_path_obj)) from e

        except (FileNotFoundError, ParsingError, HWPLibError):
            # 이미 적절한 예외가 발생했으므로 재발생
            raise

        except Exception as e:
            # 예상치 못한 예외 처리
            error_msg = f"HWP 파일 읽기 중 예상치 못한 오류: {e}"
            logger.error(error_msg)
            raise HWPLibError(error_msg, str(file_path_obj)) from e

    def _validate_hwp_structure(
        self, hwp_file: "jpype.JObject", file_path: Path
    ) -> None:
        """
        HWP 파일의 기본 구조를 검증합니다.

        Args:
            hwp_file: HWPFile 객체
            file_path: 파일 경로 (오류 메시지용)

        Raises:
            ParsingError: 구조 검증 실패시
        """
        try:
            # BodyText 존재 확인
            body_text = hwp_file.getBodyText()
            if body_text is None:
                raise ParsingError("HWP 파일에 BodyText가 없습니다", str(file_path))

            # SectionList 존재 및 유효성 확인
            section_list = body_text.getSectionList()
            if section_list is None:
                raise ParsingError("HWP 파일에 SectionList가 없습니다", str(file_path))

            section_count = section_list.size()
            if section_count == 0:
                raise ParsingError("HWP 파일에 유효한 섹션이 없습니다", str(file_path))

            # 각 섹션의 기본 검증
            for i in range(min(section_count, 5)):  # 처음 5개 섹션까지만 검증
                section = section_list.get(i)
                if section is None:
                    logger.warning(f"섹션 {i}이 null입니다: {file_path}")
                    continue

                # 문단 목록 확인
                para_list = section.getParagraphs()
                if para_list is not None and len(para_list) > 0:
                    logger.debug(f"섹션 {i} 검증 완료 (문단 수: {len(para_list)})")

            logger.debug(f"HWP 파일 구조 검증 완료: {section_count}개 섹션")

        except ParsingError:
            raise  # 이미 적절한 예외
        except Exception as e:
            error_msg = f"HWP 파일 구조 검증 실패: {e}"
            logger.error(error_msg)
            raise ParsingError(error_msg, str(file_path)) from e

    def get_file_info(self, file_path: Union[str, Path]) -> dict:
        """
        HWP 파일의 기본 정보를 반환합니다 (파일을 완전히 읽지 않고).

        Args:
            file_path: HWP 파일 경로

        Returns:
            파일 정보 딕셔너리

        Raises:
            FileNotFoundError: 파일을 찾을 수 없음
            ParsingError: 파일 헤더 파싱 실패
        """
        file_path_obj = Path(file_path)

        try:
            validate_file_exists(file_path_obj)
            validate_file_access(file_path_obj)

            # 기본 파일 정보
            stat = file_path_obj.stat()
            info = {
                "path": str(file_path_obj),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "extension": file_path_obj.suffix.lower(),
                "is_hwp": file_path_obj.suffix.lower() == ".hwp",
            }

            # HWP 헤더 정보 (가능한 경우)
            if file_path_obj.suffix.lower() == ".hwp":
                try:
                    # OLE 파일로 시도해서 기본 정보 추출
                    import olefile

                    if olefile.isOleFile(str(file_path_obj)):
                        with olefile.OleFileIO(str(file_path_obj)) as ole:
                            streams = ole.listdir()
                            info.update(
                                {
                                    "is_ole_file": True,
                                    "streams": streams,
                                    "has_file_header": "FileHeader"
                                    in [s[0] for s in streams],
                                }
                            )
                    else:
                        info["is_ole_file"] = False

                except Exception as e:
                    logger.debug(f"HWP 헤더 정보 추출 실패: {e}")
                    info["header_error"] = str(e)

            return info

        except (FileNotFoundError, ParsingError):
            raise
        except Exception as e:
            error_msg = f"파일 정보 추출 실패: {e}"
            logger.error(error_msg)
            raise ParsingError(error_msg, str(file_path_obj)) from e

    def __repr__(self) -> str:
        """객체 표현."""
        return f"HWPReader(jvm_ready={jpype.isJVMStarted()})"
