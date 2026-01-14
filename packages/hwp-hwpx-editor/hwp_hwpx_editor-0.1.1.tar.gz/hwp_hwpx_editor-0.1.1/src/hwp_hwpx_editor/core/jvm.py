"""
JVM 관리 모듈

JPype를 사용하여 Java Virtual Machine을 시작하고 관리합니다.
스레드 안전한 싱글톤 패턴과 강력한 예외 처리를 제공합니다.
"""

import os
import threading
from pathlib import Path
from typing import Optional, List, Union
import logging

from .exceptions import JVMNotStartedError, HWPLibError

# JPype import (없으면 일부 기능 제한)
try:
    import jpype
    import jpype.imports

    JPYPE_AVAILABLE = True
except ImportError:
    JPYPE_AVAILABLE = False
    jpype = None

logger = logging.getLogger(__name__)


class JVMManager:
    """
    Java Virtual Machine 관리자.

    스레드 안전한 싱글톤 패턴으로 JVM을 관리합니다.
    """

    _instance: Optional["JVMManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "JVMManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            with self._lock:
                if not hasattr(self, "_initialized"):
                    self._initialized = True
                    self._classpath: List[str] = []
                    self._jvm_started = False
                    self._jvm_args: List[str] = []

    @property
    def classpath(self) -> List[str]:
        """JVM 클래스패스를 반환합니다."""
        with self._lock:
            return self._classpath.copy()

    @property
    def is_jvm_started(self) -> bool:
        """JVM이 시작되었는지 여부를 반환합니다."""
        with self._lock:
            return self._jvm_started and self._is_jpype_jvm_running()

    def add_jar(self, jar_path: Union[str, Path]) -> None:
        """
        클래스패스에 JAR 파일을 추가합니다.

        Args:
            jar_path: 추가할 JAR 파일 경로

        Raises:
            FileNotFoundError: JAR 파일이 존재하지 않음
            ValueError: 유효하지 않은 JAR 파일
        """
        jar_path_obj = Path(jar_path)

        if not jar_path_obj.exists():
            raise FileNotFoundError(f"JAR 파일을 찾을 수 없습니다: {jar_path}")

        if not jar_path_obj.suffix.lower() == ".jar":
            raise ValueError(f"JAR 파일이 아닙니다: {jar_path}")

        jar_path_str = str(jar_path_obj.resolve())

        with self._lock:
            if jar_path_str not in self._classpath:
                self._classpath.append(jar_path_str)
                logger.debug(f"JAR 파일을 클래스패스에 추가: {jar_path_str}")
            else:
                logger.debug(f"JAR 파일이 이미 클래스패스에 있음: {jar_path_str}")

    def add_jars_from_directory(self, directory: Union[str, Path]) -> int:
        """
        디렉토리에서 모든 JAR 파일을 클래스패스에 추가합니다.

        Args:
            directory: JAR 파일들이 있는 디렉토리 경로

        Returns:
            추가된 JAR 파일 개수

        Raises:
            FileNotFoundError: 디렉토리가 존재하지 않음
            NotADirectoryError: 디렉토리가 아님
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            raise FileNotFoundError(f"JAR 디렉토리를 찾을 수 없습니다: {directory}")

        if not dir_path.is_dir():
            raise NotADirectoryError(f"디렉토리가 아닙니다: {directory}")

        added_count = 0
        for jar_file in dir_path.glob("*.jar"):
            try:
                self.add_jar(jar_file)
                added_count += 1
            except Exception as e:
                logger.warning(f"JAR 파일 추가 실패: {jar_file} - {e}")

        logger.info(
            f"JAR 디렉토리에서 {added_count}개 파일을 클래스패스에 추가: {directory}"
        )
        return added_count

    def _is_jpype_jvm_running(self) -> bool:
        """JPype를 통해 JVM이 실제로 실행 중인지 확인합니다."""
        if not JPYPE_AVAILABLE:
            return False
        try:
            return jpype.isJVMStarted()
        except Exception:
            return False

    def start_jvm(self, jvm_args: Optional[List[str]] = None) -> None:
        """
        JVM을 시작합니다.

        Args:
            jvm_args: 추가 JVM 옵션들

        Raises:
            RuntimeError: JPype를 사용할 수 없거나 JVM 시작 실패시
            ValueError: 클래스패스에 JAR 파일이 없을 때
        """
        with self._lock:
            self._start_jvm_locked(jvm_args)

    def _start_jvm_locked(self, jvm_args: Optional[List[str]] = None) -> None:
        """락이 걸린 상태에서 JVM을 시작합니다."""
        if not JPYPE_AVAILABLE:
            raise RuntimeError(
                "JPype를 사용할 수 없습니다. JPype1을 설치하세요: pip install JPype1"
            )

        if self._jvm_started:
            logger.debug("JVM이 이미 시작되었습니다")
            return

        if not self._classpath:
            raise ValueError(
                "클래스패스에 JAR 파일이 없습니다. "
                "add_jar() 또는 add_jars_from_directory()를 먼저 호출하세요."
            )

        # JVM 옵션 구성
        jvm_options = self._build_jvm_options(jvm_args)

        try:
            logger.info(f"JVM 시작 중... (클래스패스: {len(self._classpath)}개 파일)")

            # JVM 시작
            jpype.startJVM(classpath=self._classpath, *jvm_options)

            self._jvm_started = True
            logger.info("JVM이 성공적으로 시작되었습니다")

        except Exception as e:
            error_msg = f"JVM 시작 실패: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def _build_jvm_options(self, user_args: Optional[List[str]] = None) -> List[str]:
        """JVM 옵션을 구성합니다."""
        # 기본 JVM 옵션
        options = [
            "-Djava.awt.headless=true",  # GUI 없는 환경
            "-Dfile.encoding=UTF-8",  # UTF-8 인코딩
            "-Djava.util.logging.config.class=java.util.logging.LogManager",  # 로깅 설정
            "-Xmx512m",  # 최대 힙 크기 (필요시 조정)
        ]

        # 사용자 지정 옵션 추가
        if user_args:
            options.extend(user_args)

        # 중복 제거
        seen = set()
        unique_options = []
        for option in options:
            if option not in seen:
                seen.add(option)
                unique_options.append(option)

        return unique_options

    def shutdown_jvm(self) -> None:
        """JVM을 종료합니다."""
        with self._lock:
            self._shutdown_jvm_locked()

    def _shutdown_jvm_locked(self) -> None:
        """락이 걸린 상태에서 JVM을 종료합니다."""
        if not JPYPE_AVAILABLE:
            logger.debug("JPype를 사용할 수 없어 JVM 종료를 건너뜁니다")
            return

        if not self._jvm_started:
            logger.debug("JVM이 실행 중이 아닙니다")
            return

        try:
            logger.info("JVM 종료 중...")
            jpype.shutdownJVM()
            self._jvm_started = False
            logger.info("JVM이 성공적으로 종료되었습니다")
        except Exception as e:
            logger.warning(f"JVM 종료 중 오류 발생: {e}")
            # 강제 종료 플래그 설정
            self._jvm_started = False

    def is_jvm_running(self) -> bool:
        """JVM이 실행 중인지 확인합니다."""
        with self._lock:
            return self._jvm_started and self._is_jpype_jvm_running()

    def restart_jvm(self, jvm_args: Optional[List[str]] = None) -> None:
        """
        JVM을 재시작합니다.

        Args:
            jvm_args: 새로운 JVM 옵션들
        """
        logger.info("JVM 재시작 중...")
        self.shutdown_jvm()
        self.start_jvm(jvm_args)

    def get_jvm_info(self) -> dict:
        """
        JVM 정보를 반환합니다.

        Returns:
            JVM 상태 정보 딕셔너리
        """
        with self._lock:
            return {
                "is_started": self._jvm_started,
                "is_actually_running": self._is_jpype_jvm_running(),
                "classpath_count": len(self._classpath),
                "jpype_available": JPYPE_AVAILABLE,
                "jvm_args": self._jvm_args.copy() if self._jvm_args else [],
            }

    def __enter__(self) -> "JVMManager":
        """컨텍스트 매니저 진입."""
        self.start_jvm()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """컨텍스트 매니저 종료."""
        self.shutdown_jvm()

    def __repr__(self) -> str:
        """객체 표현."""
        status = "실행중" if self.is_jvm_running else "중지됨"
        return f"JVMManager(status={status}, jars={len(self._classpath)})"


# 전역 JVM 매니저 인스턴스
_jvm_manager_instance: Optional[JVMManager] = None


def get_jvm_manager() -> JVMManager:
    """
    전역 JVM 매니저 인스턴스를 반환합니다.

    Returns:
        JVMManager 싱글톤 인스턴스
    """
    global _jvm_manager_instance
    if _jvm_manager_instance is None:
        _jvm_manager_instance = JVMManager()
    return _jvm_manager_instance


def initialize_jvm(
    jars_directory: Optional[Union[str, Path]] = None, auto_start: bool = False
) -> JVMManager:
    """
    JVM을 초기화합니다.

    Args:
        jars_directory: JAR 파일들이 있는 디렉토리 경로.
                       None이면 패키지 내의 jars 디렉토리를 자동 감지합니다.
        auto_start: 초기화 후 바로 JVM을 시작할지 여부

    Returns:
        초기화된 JVMManager 인스턴스

    Raises:
        FileNotFoundError: JAR 디렉토리를 찾을 수 없음
        RuntimeError: JVM 시작 실패시 (auto_start=True인 경우)
    """
    manager = get_jvm_manager()

    # JAR 디렉토리 결정
    if jars_directory is None:
        jars_directory = _find_default_jars_directory()

    try:
        # JAR 파일들 추가
        added_count = manager.add_jars_from_directory(jars_directory)
        if added_count == 0:
            logger.warning(f"JAR 파일을 찾을 수 없음: {jars_directory}")

        # 자동 시작
        if auto_start:
            manager.start_jvm()

        logger.info(f"JVM 초기화 완료: {added_count}개 JAR 파일 추가")
        return manager

    except Exception as e:
        logger.error(f"JVM 초기화 실패: {e}")
        raise


def _find_default_jars_directory() -> Path:
    """
    기본 JAR 디렉토리를 찾습니다.

    Returns:
        JAR 디렉토리 경로

    우선순위:
    1. 패키지 내 jars 디렉토리
    2. 현재 작업 디렉토리의 jars 디렉토리
    """
    # 1. 패키지 내 jars 디렉토리 (core/jvm.py -> hwp_hwpx_editor/jars)
    package_jars = Path(__file__).parent.parent / "jars"
    if package_jars.exists() and package_jars.is_dir():
        return package_jars

    # 2. 현재 작업 디렉토리의 jars 디렉토리
    cwd_jars = Path.cwd() / "jars"
    if cwd_jars.exists() and cwd_jars.is_dir():
        return cwd_jars

    # 3. 기본값 (패키지 내)
    return package_jars


def ensure_jvm_running() -> None:
    """
    JVM이 실행 중이지 않으면 시작합니다.

    JVM이 아직 초기화되지 않은 경우 기본 설정으로 초기화합니다.
    """
    manager = get_jvm_manager()

    if not manager.is_jvm_running():
        # JAR 파일이 없으면 초기화 시도
        if not manager.classpath:
            try:
                initialize_jvm()
            except Exception as e:
                logger.warning(f"JVM 자동 초기화 실패: {e}")

        # JVM 시작
        if manager.classpath:
            manager.start_jvm()
        else:
            raise JVMNotStartedError("JVM을 시작할 수 없습니다: JAR 파일이 없음")


def shutdown_jvm() -> None:
    """JVM을 종료합니다."""
    manager = get_jvm_manager()
    manager.shutdown_jvm()


def is_jvm_running() -> bool:
    """
    JVM이 실행 중인지 확인합니다.

    Returns:
        실행 중이면 True
    """
    manager = get_jvm_manager()
    return manager.is_jvm_running()


# 하위 호환성을 위한 별칭
jvm_manager = get_jvm_manager()
