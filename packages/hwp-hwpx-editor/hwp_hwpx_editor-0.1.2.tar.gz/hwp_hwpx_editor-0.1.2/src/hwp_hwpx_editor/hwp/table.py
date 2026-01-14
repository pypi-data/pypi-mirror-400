"""
HWP 표 조작 모듈
"""

from typing import Optional, List
import jpype
import logging

from ..core import ensure_jvm_running, HWPLibError

logger = logging.getLogger(__name__)


class HWPTableManager:
    """HWP 표 조작 클래스"""

    def __init__(self):
        ensure_jvm_running()

        # Java 클래스 import
        try:
            self._TableCellMerger = jpype.JClass(
                "kr.dogfoot.hwplib.tool.TableCellMerger"
            )
            self._ControlTable = jpype.JClass(
                "kr.dogfoot.hwplib.object.bodytext.control.ControlTable"
            )
            self._ControlType = jpype.JClass(
                "kr.dogfoot.hwplib.object.bodytext.control.ControlType"
            )
        except Exception as e:
            raise HWPLibError(f"Failed to import table classes: {e}")

    def merge_cells(
        self,
        table_control: "jpype.JObject",
        start_row: int,
        start_col: int,
        end_row: int,
        end_col: int,
    ) -> bool:
        """
        표의 셀들을 병합합니다.

        Args:
            table_control: ControlTable 객체
            start_row: 시작 행 인덱스 (0부터 시작)
            start_col: 시작 열 인덱스 (0부터 시작)
            end_row: 끝 행 인덱스 (포함)
            end_col: 끝 열 인덱스 (포함)

        Returns:
            성공 여부
        """
        try:
            # Java 메소드 호출 (1-based 인덱스 사용)
            self._TableCellMerger.mergeCell(
                table_control,
                start_row + 1,  # 1-based로 변환
                start_col + 1,  # 1-based로 변환
                end_row + 1,  # 1-based로 변환
                end_col + 1,  # 1-based로 변환
            )
            logger.debug(
                f"Merged cells from ({start_row},{start_col}) to ({end_row},{end_col})"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to merge cells: {e}")
            return False

    def remove_row(self, table_control: "jpype.JObject", row_index: int) -> bool:
        """
        표의 행을 삭제합니다.

        Args:
            table_control: ControlTable 객체
            row_index: 삭제할 행 인덱스 (0부터 시작)

        Returns:
            성공 여부
        """
        try:
            # 행 객체 제거
            table_control.getRowList().remove(row_index)

            # 표 행 개수 조정
            table_control.getTable().setRowCount(table_control.getRowList().size())

            # 행별 셀 개수 리스트에서 제거
            table_control.getTable().getCellCountOfRowList().remove(row_index)

            # 남은 행들의 셀 rowIndex 조정
            row_count = table_control.getRowList().size()
            for i in range(row_count):
                if i >= row_index:  # 삭제된 행 이후의 행들
                    row = table_control.getRowList().get(i)
                    cell_list = row.getCellList()
                    for cell in cell_list:
                        list_header = cell.getListHeader()
                        current_row_index = list_header.getRowIndex()
                        if current_row_index > row_index:
                            list_header.setRowIndex(current_row_index - 1)

            logger.debug(f"Removed row at index {row_index}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove row at index {row_index}: {e}")
            return False

    def get_table_info(self, table_control: "jpype.JObject") -> dict:
        """
        표의 정보를 가져옵니다.

        Args:
            table_control: ControlTable 객체

        Returns:
            표 정보 딕셔너리
        """
        try:
            table = table_control.getTable()
            info = {
                "row_count": table.getRowCount(),
                "column_count": table.getColumnCount(),
                "cell_spacing": table.getCellSpacing(),
                "border_fill_id": table.getBorderFillId(),
                "rows": [],
            }

            # 각 행의 셀 개수
            cell_counts = []
            cell_count_list = table.getCellCountOfRowList()
            for i in range(cell_count_list.size()):
                cell_counts.append(cell_count_list.get(i))
            info["cell_counts_per_row"] = cell_counts

            # 행 정보
            row_list = table_control.getRowList()
            for row_idx in range(row_list.size()):
                row = row_list.get(row_idx)
                cell_list = row.getCellList()
                cells_info = []

                for cell_idx in range(cell_list.size()):
                    cell = cell_list.get(cell_idx)
                    list_header = cell.getListHeader()
                    cells_info.append(
                        {
                            "row_index": list_header.getRowIndex(),
                            "col_index": list_header.getColIndex(),
                            "row_span": list_header.getRowSpan(),
                            "col_span": list_header.getColSpan(),
                            "width": list_header.getWidth(),
                            "height": list_header.getHeight(),
                            "paragraph_count": cell.getParagraphList().size(),
                        }
                    )

                info["rows"].append({"cells": cells_info})

            return info
        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return {}

    def extract_table_text(self, table_control: "jpype.JObject") -> List[List[str]]:
        """
        표에서 셀별 텍스트를 추출합니다.

        Args:
            table_control: ControlTable 객체

        Returns:
            2차원 리스트: [[셀1, 셀2, ...], [셀1, 셀2, ...], ...]

        Raises:
            ValueError: 잘못된 표 컨트롤 객체
            RuntimeError: 텍스트 추출 중 오류
        """
        if table_control is None:
            raise ValueError("표 컨트롤 객체가 None입니다")

        try:
            from .extractor import HWPTextExtractor, TextExtractMethod

            result: List[List[str]] = []
            extractor = HWPTextExtractor()

            row_list = table_control.getRowList()
            if row_list is None:
                raise ValueError("표에 행 목록이 없습니다")

            row_count = row_list.size()
            if row_count == 0:
                logger.warning("표에 행이 없습니다")
                return []

            for row_idx in range(row_count):
                row = row_list.get(row_idx)
                if row is None:
                    logger.warning(f"행 {row_idx}이 None입니다")
                    result.append([])
                    continue

                cell_list = row.getCellList()
                if cell_list is None:
                    logger.warning(f"행 {row_idx}에 셀 목록이 없습니다")
                    result.append([])
                    continue

                row_texts: List[str] = []
                cell_count = cell_list.size()

                for cell_idx in range(cell_count):
                    cell = cell_list.get(cell_idx)
                    if cell is None:
                        row_texts.append("")
                        continue

                    paragraph_list = cell.getParagraphList()
                    cell_text = ""

                    # 셀 내 텍스트 추출
                    if paragraph_list and paragraph_list.size() > 0:
                        try:
                            cell_text = extractor.extract_text(
                                paragraph_list, TextExtractMethod.OnlyMainParagraph
                            )
                            cell_text = cell_text.strip() if cell_text else ""
                        except Exception as e:
                            logger.debug(
                                f"셀 ({row_idx}, {cell_idx}) 텍스트 추출 실패: {e}"
                            )
                            cell_text = ""
                    else:
                        # 빈 셀
                        cell_text = ""

                    row_texts.append(cell_text)

                result.append(row_texts)

            logger.debug(f"표에서 {len(result)}행의 텍스트를 추출했습니다")
            return result

        except ValueError:
            raise  # 입력 검증 오류는 그대로 전달
        except Exception as e:
            error_msg = f"표 텍스트 추출 실패: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def get_table_as_markdown(self, table_control: "jpype.JObject") -> str:
        """
        표를 마크다운 형식으로 변환합니다.

        Args:
            table_control: ControlTable 객체

        Returns:
            마크다운 형식의 표 문자열 (빈 표인 경우 빈 문자열)

        Raises:
            ValueError: 잘못된 표 컨트롤 객체
            RuntimeError: 변환 중 오류
        """
        if table_control is None:
            raise ValueError("표 컨트롤 객체가 None입니다")

        try:
            table_text = self.extract_table_text(table_control)

            if not table_text or not table_text[0]:
                logger.debug("표가 비어있어 마크다운으로 변환할 수 없습니다")
                return ""

            markdown_lines: List[str] = []

            for i, row in enumerate(table_text):
                if not row:  # 빈 행은 건너뜀
                    continue

                # 셀 내용 정리 및 이스케이핑
                clean_row = []
                for cell in row:
                    if cell is None:
                        clean_cell = ""
                    else:
                        # 줄바꿈을 공백으로 변환하고 양쪽 공백 제거
                        clean_cell = (
                            str(cell).replace("\n", " ").replace("\r", " ").strip()
                        )
                        # 마크다운 특수 문자 이스케이핑
                        clean_cell = clean_cell.replace("|", "\\|").replace(
                            "\\", "\\\\"
                        )
                    clean_row.append(clean_cell)

                # 빈 행이 아닌 경우에만 추가
                if any(clean_row):  # 적어도 하나의 셀이 내용이 있는 경우
                    # 마크다운 행 생성
                    markdown_lines.append("| " + " | ".join(clean_row) + " |")

                    # 첫 번째 유효 행 다음에 구분선 추가
                    if i == 0:
                        separators = ["---"] * len(clean_row)
                        markdown_lines.append("| " + " | ".join(separators) + " |")

            result = "\n".join(markdown_lines)
            logger.debug(f"표를 마크다운으로 변환했습니다 ({len(markdown_lines)}줄)")
            return result

        except ValueError:
            raise  # 입력 검증 오류는 그대로 전달
        except Exception as e:
            error_msg = f"표 마크다운 변환 실패: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def get_table_as_csv(
        self, table_control: "jpype.JObject", delimiter: str = ","
    ) -> str:
        """
        표를 CSV 형식으로 변환합니다.

        Args:
            table_control: ControlTable 객체
            delimiter: 구분자 (기본값: ",")

        Returns:
            CSV 형식의 표 문자열 (빈 표인 경우 빈 문자열)

        Raises:
            ValueError: 잘못된 표 컨트롤 객체 또는 구분자
            RuntimeError: 변환 중 오류
        """
        if table_control is None:
            raise ValueError("표 컨트롤 객체가 None입니다")

        if not delimiter or len(delimiter) == 0:
            raise ValueError("구분자는 빈 문자열일 수 없습니다")

        if len(delimiter) > 10:  # 비합리적으로 긴 구분자 제한
            raise ValueError("구분자가 너무 깁니다 (최대 10자)")

        try:
            import csv
            from io import StringIO

            table_text = self.extract_table_text(table_control)

            if not table_text or not table_text[0]:
                logger.debug("표가 비어있어 CSV로 변환할 수 없습니다")
                return ""

            output = StringIO()

            # CSV 작성자 설정 (안전한 옵션들 사용)
            writer = csv.writer(
                output,
                delimiter=delimiter,
                quoting=csv.QUOTE_MINIMAL,  # 필요한 경우에만 따옴표 사용
                escapechar="\\",  # 이스케이프 문자
                lineterminator="\n",  # 줄바꿈 문자
            )

            valid_rows = 0
            for row in table_text:
                if not row:  # 빈 행은 건너뜀
                    continue

                # 셀 내용 정리
                clean_row = []
                for cell in row:
                    if cell is None:
                        clean_cell = ""
                    else:
                        # 줄바꿈을 공백으로 변환하고 양쪽 공백 제거
                        clean_cell = (
                            str(cell).replace("\n", " ").replace("\r", " ").strip()
                        )
                    clean_row.append(clean_cell)

                # 빈 행이 아닌 경우에만 작성
                if any(clean_row):  # 적어도 하나의 셀이 내용이 있는 경우
                    writer.writerow(clean_row)
                    valid_rows += 1

            if valid_rows == 0:
                logger.debug("표에 유효한 데이터가 없어 빈 CSV를 반환합니다")
                return ""

            result = output.getvalue().strip()
            logger.debug(
                f"표를 CSV로 변환했습니다 ({valid_rows}행, 구분자: '{delimiter}')"
            )
            return result

        except ValueError:
            raise  # 입력 검증 오류는 그대로 전달
        except Exception as e:
            error_msg = f"표 CSV 변환 실패: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def create_simple_table(
        self,
        hwp_file: "jpype.JObject",
        section_index: int,
        paragraph_index: int,
        rows: int,
        cols: int,
        cell_texts: Optional[List[List[str]]] = None,
    ) -> Optional["jpype.JObject"]:
        """
        간단한 표를 생성합니다. (실험적 기능)

        Args:
            hwp_file: HWPFile 객체
            section_index: 섹션 인덱스
            paragraph_index: 문단 인덱스
            rows: 행 개수
            cols: 열 개수
            cell_texts: 셀 텍스트들 (2차원 리스트, 옵션)

        Returns:
            생성된 ControlTable 객체 또는 None
        """
        try:
            logger.warning(
                "create_simple_table is experimental and may not work correctly"
            )
            logger.warning(
                "For production use, please create tables using the Java API directly"
            )

            # 섹션과 문단 가져오기
            section = hwp_file.getBodyText().getSectionList().get(section_index)
            paragraph = section.getParagraph(paragraph_index)

            # 표 컨트롤 생성을 위한 확장 문자 추가
            paragraph.getText().addExtendCharForTable()

            # 표 컨트롤 추가
            table_control = paragraph.addNewControl(self._ControlType.Table)

            # 표 레코드 설정 (기본값)
            table = table_control.getTable()
            table.getProperty().setDivideAtPageBoundary(
                jpype.JClass(
                    "kr.dogfoot.hwplib.object.bodytext.control.table.DivideAtPageBoundary"
                ).DivideByCell
            )
            table.getProperty().setAutoRepeatTitleRow(False)
            table.setRowCount(rows)
            table.setColumnCount(cols)
            table.setCellSpacing(0)
            table.setLeftInnerMargin(0)
            table.setRightInnerMargin(0)
            table.setTopInnerMargin(0)
            table.setBottomInnerMargin(0)

            # 기본 보더필 ID 설정 (0번 사용)
            table.setBorderFillId(0)

            # 행별 셀 개수 설정
            for _ in range(rows):
                table.getCellCountOfRowList().add(cols)

            # 기본 행과 셀들은 Java API를 통해 직접 생성해야 함
            # 이 부분은 매우 복잡하므로 기본 구조만 생성하고
            # 세부 설정은 사용자가 직접 Java 객체를 조작하도록 함

            logger.info(f"Created basic table structure: {rows}x{cols}")
            return table_control

        except Exception as e:
            logger.error(f"Failed to create simple table: {e}")
            return None
