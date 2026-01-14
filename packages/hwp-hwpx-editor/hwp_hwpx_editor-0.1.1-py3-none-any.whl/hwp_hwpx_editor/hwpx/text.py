"""
HWPX 텍스트 처리 모듈

HWPX 문서의 모든 텍스트 요소를 순회하고 교체하는 기능을 제공합니다.

지원하는 텍스트 위치:
- 본문 (body paragraphs)
- 표 셀 (table cells, including nested tables)
- 각주 (footnotes)
- 미주 (endnotes)
- 메모 (memos)
"""

from typing import Callable, Iterator, Tuple, Any, Optional
import logging

logger = logging.getLogger(__name__)


class HWPXTextIterator:
    """
    HWPX 문서의 모든 텍스트 요소를 순회합니다.

    본문, 표, 각주, 미주, 메모 등 모든 위치의 텍스트를 찾습니다.
    """

    def __init__(self, hwpx_file: Any):
        self._hwpx_file = hwpx_file

    def iter_all_texts(self) -> Iterator[Tuple[Any, str, str]]:
        """
        문서의 모든 T 요소를 순회합니다.

        Yields:
            (T_element, text, location) 튜플
            location: "body", "table", "footnote", "endnote", "memo"
        """
        for section in self._get_sections():
            yield from self._iter_section_texts(section)

    def _get_sections(self):
        section_list = self._hwpx_file.sectionXMLFileList()
        for i in range(section_list.count()):
            yield section_list.get(i)

    def _iter_section_texts(self, section: Any) -> Iterator[Tuple[Any, str, str]]:
        for p_idx in range(section.countOfPara()):
            para = section.getPara(p_idx)
            yield from self._iter_paragraph_texts(para, "body")

    def _iter_paragraph_texts(
        self, para: Any, location: str
    ) -> Iterator[Tuple[Any, str, str]]:
        for r_idx in range(para.countOfRun()):
            run = para.getRun(r_idx)
            yield from self._iter_run_texts(run, location)

    def _iter_run_texts(
        self, run: Any, location: str
    ) -> Iterator[Tuple[Any, str, str]]:
        for ri_idx in range(run.countOfRunItem()):
            item = run.getRunItem(ri_idx)
            item_type = type(item).__name__

            if item_type.endswith(".T"):
                text = item.onlyText()
                if text and str(text).strip():
                    yield (item, str(text), location)

            elif "Table" in item_type:
                yield from self._iter_table_texts(item)

            elif item_type.endswith(".Ctrl"):
                yield from self._iter_ctrl_texts(item)

    def _iter_table_texts(self, table: Any) -> Iterator[Tuple[Any, str, str]]:
        for row_idx in range(table.countOfTr()):
            tr = table.getTr(row_idx)
            for col_idx in range(tr.countOfTc()):
                tc = tr.getTc(col_idx)
                sublist = tc.subList()
                if sublist:
                    yield from self._iter_sublist_texts(sublist, "table")

    def _iter_sublist_texts(
        self, sublist: Any, location: str
    ) -> Iterator[Tuple[Any, str, str]]:
        for p_idx in range(sublist.countOfPara()):
            para = sublist.getPara(p_idx)
            yield from self._iter_paragraph_texts(para, location)

    def _iter_ctrl_texts(self, ctrl: Any) -> Iterator[Tuple[Any, str, str]]:
        try:
            ctrl_items = ctrl.ctrlItems()
            if ctrl_items is None:
                return

            for ci_idx in range(ctrl_items.count()):
                ci = ctrl_items.get(ci_idx)
                ci_name = type(ci).__name__

                location = self._determine_ctrl_location(ci, ci_name)

                if hasattr(ci, "subList"):
                    sublist = ci.subList()
                    if sublist:
                        yield from self._iter_sublist_texts(sublist, location)
        except Exception:
            pass

    def _determine_ctrl_location(self, ci: Any, ci_name: str) -> str:
        if "FootNote" in ci_name:
            return "footnote"
        elif "EndNote" in ci_name:
            return "endnote"
        elif "FieldBegin" in ci_name:
            try:
                if hasattr(ci, "type") and "MEMO" in str(ci.type()):
                    return "memo"
            except Exception:
                pass
        return "body"


class HWPXTextReplacer:
    """
    HWPX 문서의 텍스트를 교체합니다.

    Example:
        >>> replacer = HWPXTextReplacer(doc._java_object)
        >>>
        >>> # 모든 텍스트를 대문자로
        >>> count = replacer.replace_all(str.upper)
        >>>
        >>> # 표 텍스트만 교체
        >>> count = replacer.replace_by_location(
        ...     lambda t: t.replace("old", "new"),
        ...     locations=["table"]
        ... )
        >>>
        >>> # 본문 + 표만 교체 (각주, 미주, 메모 제외)
        >>> count = replacer.replace_by_location(
        ...     my_replacer,
        ...     locations=["body", "table"]
        ... )
    """

    def __init__(self, hwpx_file: Any):
        self._hwpx_file = hwpx_file
        self._iterator = HWPXTextIterator(hwpx_file)

    def replace_all(self, replacer: Callable[[str], str]) -> int:
        """
        모든 텍스트를 교체합니다.

        Args:
            replacer: 텍스트 변환 함수

        Returns:
            교체된 요소 수
        """
        return self.replace_by_location(replacer, locations=None)

    def replace_by_location(
        self, replacer: Callable[[str], str], locations: Optional[list] = None
    ) -> int:
        """
        특정 위치의 텍스트만 교체합니다.

        Args:
            replacer: 텍스트 변환 함수
            locations: 교체할 위치 리스트 ["body", "table", "footnote", "endnote", "memo"]
                       None이면 모든 위치

        Returns:
            교체된 요소 수
        """
        count = 0

        for t_elem, text, location in self._iterator.iter_all_texts():
            if locations is None or location in locations:
                new_text = replacer(text)
                if new_text != text:
                    t_elem.clear()
                    t_elem.addText(new_text)
                    count += 1

        return count

    def replace_tables_only(self, replacer: Callable[[str], str]) -> int:
        """표 텍스트만 교체합니다."""
        return self.replace_by_location(replacer, locations=["table"])

    def replace_body_only(self, replacer: Callable[[str], str]) -> int:
        """본문 텍스트만 교체합니다 (표, 각주 등 제외)."""
        return self.replace_by_location(replacer, locations=["body"])

    def replace_notes_only(self, replacer: Callable[[str], str]) -> int:
        """각주/미주 텍스트만 교체합니다."""
        return self.replace_by_location(replacer, locations=["footnote", "endnote"])

    def replace_memos_only(self, replacer: Callable[[str], str]) -> int:
        """메모 텍스트만 교체합니다."""
        return self.replace_by_location(replacer, locations=["memo"])
