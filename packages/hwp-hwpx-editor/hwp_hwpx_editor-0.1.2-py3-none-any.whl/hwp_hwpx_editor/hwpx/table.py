"""
HWPX 표 관리 모듈

HWPX 문서의 표(Table) 접근, 텍스트 추출/교체 기능을 제공합니다.

주요 기능:
- 모든 표 찾기 (중첩 표 포함)
- 표 셀 텍스트 추출
- 표 셀 텍스트 교체
- 표 구조 탐색
"""

from typing import List, Optional, Callable, Iterator, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class HWPXTableManager:
    """
    HWPX 표 관리 클래스

    HWPX 문서의 표를 탐색하고 텍스트를 추출/교체합니다.
    중첩된 표(표 안의 표)도 처리합니다.

    Example:
        >>> from hwp_hwpx_editor import HWPEditor
        >>> editor = HWPEditor()
        >>> doc = editor("sample.hwpx")
        >>>
        >>> manager = HWPXTableManager(doc._java_object)
        >>> tables = manager.get_all_tables()
        >>> print(f"Found {len(tables)} tables")
        >>>
        >>> # 표 텍스트 추출
        >>> for table in tables:
        ...     text = manager.extract_table_text(table)
        ...     print(text)
        >>>
        >>> # 표 텍스트 교체
        >>> manager.replace_all_table_texts(lambda text: "REPLACED")
        >>> doc.save("output.hwpx")
    """

    def __init__(self, hwpx_file: Any):
        """
        Args:
            hwpx_file: HWPXFile Java 객체
        """
        self._hwpx_file = hwpx_file

    def get_sections(self) -> List[Any]:
        """섹션 목록을 반환합니다."""
        sections = []
        section_list = self._hwpx_file.sectionXMLFileList()
        for i in range(section_list.count()):
            sections.append(section_list.get(i))
        return sections

    def get_all_tables(self, include_nested: bool = True) -> List[Any]:
        """
        문서의 모든 표를 찾습니다.

        Args:
            include_nested: True면 중첩된 표(표 안의 표)도 포함

        Returns:
            Table 객체 리스트
        """
        tables = []

        for section in self.get_sections():
            for p_idx in range(section.countOfPara()):
                para = section.getPara(p_idx)
                self._find_tables_in_paragraph(para, tables, include_nested)

        return tables

    def _find_tables_in_paragraph(
        self, para: Any, tables: List[Any], include_nested: bool
    ) -> None:
        """문단에서 표를 찾습니다."""
        for r_idx in range(para.countOfRun()):
            run = para.getRun(r_idx)
            for ri_idx in range(run.countOfRunItem()):
                item = run.getRunItem(ri_idx)
                item_type = type(item).__name__

                if "Table" in item_type:
                    tables.append(item)
                    if include_nested:
                        self._find_nested_tables(item, tables)

    def _find_nested_tables(self, table: Any, tables: List[Any]) -> None:
        """표 안의 중첩된 표를 찾습니다."""
        for row_idx in range(table.countOfTr()):
            tr = table.getTr(row_idx)
            for col_idx in range(tr.countOfTc()):
                tc = tr.getTc(col_idx)
                sublist = tc.subList()
                if sublist:
                    for p_idx in range(sublist.countOfPara()):
                        para = sublist.getPara(p_idx)
                        self._find_tables_in_paragraph(para, tables, True)

    def get_table_size(self, table: Any) -> Tuple[int, int]:
        """
        표의 크기(행, 열)를 반환합니다.

        Returns:
            (row_count, col_count) 튜플
        """
        return (table.rowCnt(), table.colCnt())

    def extract_table_text(self, table: Any) -> List[List[str]]:
        """
        표에서 셀별 텍스트를 추출합니다.

        Args:
            table: Table Java 객체

        Returns:
            2차원 리스트: [[row0_cell0, row0_cell1, ...], [row1_cell0, ...], ...]
        """
        rows = []

        for row_idx in range(table.countOfTr()):
            tr = table.getTr(row_idx)
            row_cells = []

            for col_idx in range(tr.countOfTc()):
                tc = tr.getTc(col_idx)
                cell_text = self._extract_cell_text(tc)
                row_cells.append(cell_text)

            rows.append(row_cells)

        return rows

    def _extract_cell_text(self, tc: Any) -> str:
        """셀에서 텍스트를 추출합니다."""
        texts = []
        sublist = tc.subList()
        if sublist:
            for p_idx in range(sublist.countOfPara()):
                para = sublist.getPara(p_idx)
                texts.append(self._extract_paragraph_text(para))
        return " ".join(texts).strip()

    def _extract_paragraph_text(self, para: Any) -> str:
        """문단에서 텍스트를 추출합니다."""
        texts = []
        for r_idx in range(para.countOfRun()):
            run = para.getRun(r_idx)
            for ri_idx in range(run.countOfRunItem()):
                item = run.getRunItem(ri_idx)
                if hasattr(item, "onlyText"):
                    text = item.onlyText()
                    if text:
                        texts.append(str(text))
        return " ".join(texts)

    def iter_table_texts(self, table: Any) -> Iterator[Tuple[Any, str]]:
        """
        표의 모든 T 요소와 텍스트를 순회합니다.

        Yields:
            (T_element, text) 튜플
        """
        for row_idx in range(table.countOfTr()):
            tr = table.getTr(row_idx)
            for col_idx in range(tr.countOfTc()):
                tc = tr.getTc(col_idx)
                yield from self._iter_cell_texts(tc)

    def _iter_cell_texts(self, tc: Any) -> Iterator[Tuple[Any, str]]:
        """셀의 모든 T 요소와 텍스트를 순회합니다."""
        sublist = tc.subList()
        if sublist:
            yield from self._iter_sublist_texts(sublist)

    def _iter_sublist_texts(self, sublist: Any) -> Iterator[Tuple[Any, str]]:
        """SubList의 모든 T 요소와 텍스트를 순회합니다."""
        for p_idx in range(sublist.countOfPara()):
            para = sublist.getPara(p_idx)
            yield from self._iter_paragraph_texts(para)

    def _iter_paragraph_texts(self, para: Any) -> Iterator[Tuple[Any, str]]:
        """문단의 모든 T 요소와 텍스트를 순회합니다."""
        for r_idx in range(para.countOfRun()):
            run = para.getRun(r_idx)
            yield from self._iter_run_texts(run)

    def _iter_run_texts(self, run: Any) -> Iterator[Tuple[Any, str]]:
        """Run의 모든 T 요소와 텍스트를 순회합니다 (중첩 표 포함)."""
        for ri_idx in range(run.countOfRunItem()):
            item = run.getRunItem(ri_idx)
            item_type = type(item).__name__

            if item_type.endswith(".T"):
                text = item.onlyText()
                if text:
                    yield (item, str(text))
            elif "Table" in item_type:
                yield from self.iter_table_texts(item)

    def replace_table_text(
        self, table: Any, replacer: Callable[[str], str], include_nested: bool = True
    ) -> int:
        """
        표의 텍스트를 교체합니다.

        Args:
            table: Table Java 객체
            replacer: 텍스트 변환 함수 (old_text -> new_text)
            include_nested: True면 중첩된 표의 텍스트도 교체

        Returns:
            교체된 텍스트 요소 수
        """
        count = 0

        for row_idx in range(table.countOfTr()):
            tr = table.getTr(row_idx)
            for col_idx in range(tr.countOfTc()):
                tc = tr.getTc(col_idx)
                count += self._replace_cell_text(tc, replacer, include_nested)

        return count

    def _replace_cell_text(
        self, tc: Any, replacer: Callable[[str], str], include_nested: bool
    ) -> int:
        """셀의 텍스트를 교체합니다."""
        count = 0
        sublist = tc.subList()
        if sublist:
            count += self._replace_sublist_text(sublist, replacer, include_nested)
        return count

    def _replace_sublist_text(
        self, sublist: Any, replacer: Callable[[str], str], include_nested: bool
    ) -> int:
        """SubList의 텍스트를 교체합니다."""
        count = 0
        for p_idx in range(sublist.countOfPara()):
            para = sublist.getPara(p_idx)
            count += self._replace_paragraph_text(para, replacer, include_nested)
        return count

    def _replace_paragraph_text(
        self, para: Any, replacer: Callable[[str], str], include_nested: bool
    ) -> int:
        """문단의 텍스트를 교체합니다."""
        count = 0
        for r_idx in range(para.countOfRun()):
            run = para.getRun(r_idx)
            count += self._replace_run_text(run, replacer, include_nested)
        return count

    def _replace_run_text(
        self, run: Any, replacer: Callable[[str], str], include_nested: bool
    ) -> int:
        """Run의 텍스트를 교체합니다."""
        count = 0
        for ri_idx in range(run.countOfRunItem()):
            item = run.getRunItem(ri_idx)
            item_type = type(item).__name__

            if item_type.endswith(".T"):
                old_text = item.onlyText()
                if old_text and str(old_text).strip():
                    new_text = replacer(str(old_text))
                    item.clear()
                    item.addText(new_text)
                    count += 1
            elif include_nested and "Table" in item_type:
                count += self.replace_table_text(item, replacer, include_nested)

        return count

    def replace_all_table_texts(
        self, replacer: Callable[[str], str], include_nested: bool = True
    ) -> int:
        """
        문서의 모든 표 텍스트를 교체합니다.

        Args:
            replacer: 텍스트 변환 함수 (old_text -> new_text)
            include_nested: True면 중첩된 표의 텍스트도 교체

        Returns:
            교체된 텍스트 요소 수

        Example:
            >>> # 모든 표 텍스트를 대문자로 변환
            >>> count = manager.replace_all_table_texts(str.upper)
            >>>
            >>> # lorem ipsum으로 교체
            >>> def to_lorem(text):
            ...     return "Lorem ipsum " * (len(text) // 12 + 1)
            >>> count = manager.replace_all_table_texts(to_lorem)
        """
        tables = self.get_all_tables(include_nested=False)
        total = 0

        for table in tables:
            total += self.replace_table_text(table, replacer, include_nested)

        logger.info(f"Replaced {total} text elements in {len(tables)} tables")
        return total
