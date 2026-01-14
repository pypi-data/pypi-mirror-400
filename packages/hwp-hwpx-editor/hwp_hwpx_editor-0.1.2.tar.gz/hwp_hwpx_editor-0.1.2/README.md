# HWP-HWPX Editor

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Java 8+](https://img.shields.io/badge/java-8+-red.svg)](https://adoptium.net/)
[![PyPI version](https://badge.fury.io/py/hwp-hwpx-editor.svg)](https://pypi.org/project/hwp-hwpx-editor/)

**JVM 기반 HWP/HWPX 문서 편집 라이브러리** - hwp-hwpx-parser의 확장 패키지

## 특징

- **문서 편집**: 텍스트 수정, 필드 조작, 표 관리, 이미지/하이퍼링크 삽입
- **통합 API**: HWP/HWPX 파일을 동일한 인터페이스로 처리
- **Java 라이브러리**: 검증된 hwplib/hwpxlib 기반
- **Fast Layer**: JVM 없이 텍스트 추출도 가능 (hwp-hwpx-parser 포함)
- **extract-hwp 호환**: 기존 코드 쉽게 마이그레이션

## 설치

```bash
pip install hwp-hwpx-editor
```

### 요구사항

- **Python**: 3.8 이상
- **Java**: 8 이상 (JRE 또는 JDK)
- **의존성**: `hwp-hwpx-parser`, `JPype1` (자동 설치)

## 빠른 시작

```python
from hwp_hwpx_editor import HWPEditor

# 에디터 초기화 (JVM 자동 시작)
editor = HWPEditor()

# 문서 열기
doc = editor("document.hwp")

# 텍스트 추출
text = doc.extract_text()
print(text)

# 문서 저장
doc.save("output.hwp")
doc.close()
```

### 컨텍스트 매니저 사용

```python
from hwp_hwpx_editor import HWPEditor, Document

editor = HWPEditor()

with editor.read("document.hwpx") as doc:
    text = doc.extract_text()
    doc.save("output.hwpx")
```

## API 레퍼런스

### HWPEditor (메인 진입점)

```python
from hwp_hwpx_editor import HWPEditor

editor = HWPEditor()

# 파일 읽기
doc = editor("document.hwp")        # 간단한 호출
doc = editor.read("document.hwpx")  # 명시적 호출

# 빈 문서 생성
from hwp_hwpx_editor import DocumentType
doc = editor.create_blank(DocumentType.HWP)
doc = editor.create_blank(DocumentType.HWPX)
```

### Document 클래스

```python
# 기본 속성
doc.document_type   # DocumentType.HWP 또는 DocumentType.HWPX
doc.file_path       # 파일 경로
doc.is_modified     # 수정 여부
doc.version         # 버전 정보
doc.sections        # 섹션 리스트

# 텍스트 추출
doc.extract_text()                   # JVM 기반 추출
doc.extract_text_fast()              # Fast Layer (JVM 불필요)
doc.extract_text_with_notes_fast()   # 텍스트 + 각주/미주/링크

# 객체 찾기
doc.find_all("table")      # 모든 표
doc.find_all("image")      # 모든 이미지
doc.find_all("paragraph")  # 모든 문단
doc.find_all("comment")    # 모든 주석

# 저장
doc.save()                  # 원본 경로에 저장
doc.save("new_file.hwp")    # 다른 경로에 저장
doc.close()                 # 리소스 해제
```

### HWP 전용 기능

```python
# 필드 조작
doc.get_field_text("필드명")
doc.set_field_text("필드명", "새 텍스트")

# 표 조작
tables = doc.get_tables()
doc.get_table_info(table)
doc.extract_table_text(table)
doc.get_table_as_markdown(table)
doc.get_table_as_csv(table)
doc.merge_table_cells(table, start_row, start_col, end_row, end_col)
doc.remove_table_row(table, row_index)

# 미디어 삽입
doc.insert_image(section_idx, para_idx, "image.png", width=100, height=50)
doc.insert_hyperlink(section_idx, para_idx, "링크텍스트", "https://...")

# 주석(숨은 설명)
comments = doc.find_comments()
doc.get_comment_text(comment)
doc.get_comment_info(comment)
doc.create_comment(section_idx, para_idx, "주석 내용")
```

### HWPX 전용 기능

```python
# 객체 찾기
doc.find_tables()
doc.find_images()
doc.find_paragraphs()
doc.find_memo_properties()

# 메모 관리
doc.get_memo_info(memo_property)
doc.create_memo_property(memo_id="memo1", width=200, fill_color="#FFFF00")
doc.set_memo_shape_reference(section_idx, "memo1")
doc.find_memos_in_content()

# 텍스트 일괄 교체
doc.replace_all_texts(str.upper)  # 모든 텍스트 대문자로
doc.replace_all_texts(my_func, locations=["body", "table"])  # 본문+표만
doc.replace_table_texts(my_func)  # 표 텍스트만

# 고급 표 관리
table_manager = doc.get_hwpx_table_manager()
```

### 간단한 텍스트 추출 (extract-hwp 호환)

```python
from hwp_hwpx_editor import (
    extract_text_from_hwp,
    extract_text_from_hwpx,
    is_hwp_file_password_protected,
)

# 간단한 추출
text, error = extract_text_from_hwp("document.hwp")
if error is None:
    print(text)

# 암호화 확인
if is_hwp_file_password_protected("document.hwp"):
    print("암호화된 파일")
```

### Fast Layer (JVM 불필요)

hwp-hwpx-parser의 기능을 그대로 사용할 수 있습니다:

```python
from hwp_hwpx_editor import Reader, read

# 통합 리더
with Reader("document.hwp") as r:
    print(r.text)
    print(r.tables)

# 또는 Document의 fast 메서드
doc = editor("document.hwpx")
text = doc.extract_text_fast()      # JVM 불필요
result = doc.extract_text_with_notes_fast()
memos = doc.get_memos_fast()
```

## 예제

### 필드 텍스트 일괄 교체 (HWP)

```python
from hwp_hwpx_editor import HWPEditor

editor = HWPEditor()

with editor.read("form.hwp") as doc:
    doc.set_field_text("이름", "홍길동")
    doc.set_field_text("주소", "서울시 강남구")
    doc.save("filled_form.hwp")
```

### 텍스트 일괄 교체 (HWPX)

```python
from hwp_hwpx_editor import HWPEditor

editor = HWPEditor()

def replace_lorem(text):
    return text.replace("Lorem", "한글")

with editor.read("document.hwpx") as doc:
    # 모든 위치의 텍스트 교체 (본문, 표, 각주, 미주, 메모)
    count = doc.replace_all_texts(replace_lorem)
    print(f"{count}개 교체됨")
    doc.save("output.hwpx")
```

### 표 데이터 추출 (HWP)

```python
from hwp_hwpx_editor import HWPEditor

editor = HWPEditor()

with editor.read("report.hwp") as doc:
    tables = doc.get_tables()
    for i, table in enumerate(tables):
        print(f"=== 표 {i+1} ===")
        print(doc.get_table_as_markdown(table))
```

## 지원 기능

### HWP 파일

| 기능 | 상태 |
|------|------|
| 텍스트 추출 | ✅ |
| 필드 읽기/쓰기 | ✅ |
| 표 조작 | ✅ |
| 이미지 삽입 | ✅ |
| 하이퍼링크 삽입 | ✅ |
| 주석 관리 | ✅ |
| 빈 문서 생성 | ✅ |

### HWPX 파일

| 기능 | 상태 |
|------|------|
| 텍스트 추출 | ✅ |
| 객체 찾기 | ✅ |
| 메모 관리 | ✅ |
| 텍스트 일괄 교체 | ✅ |
| 중첩 표 지원 | ✅ |
| 빈 문서 생성 | ✅ |

## JVM 관리

```python
from hwp_hwpx_editor import (
    initialize_jvm,
    shutdown_jvm,
    is_jvm_running,
    JVMManager,
)

# JVM은 HWPEditor 생성 시 자동 시작됨
# 필요시 수동 관리:
initialize_jvm()  # JVM 시작
is_jvm_running()  # 상태 확인
shutdown_jvm()    # JVM 종료 (프로그램 종료 전)
```

## 라이선스

Apache License 2.0

## 관련 프로젝트

- [hwp-hwpx-parser](https://github.com/KimDaehyeon6873/hwp-hwpx-parser) - 순수 Python HWP/HWPX 파서 (읽기 전용)
- [hwplib](https://github.com/neolord0/hwplib) - Java HWP 라이브러리
- [hwpxlib](https://github.com/neolord0/hwpxlib) - Java HWPX 라이브러리
