# zipper9 PlantUML 다이어그램 문서

본 디렉터리는 `zipper9`의 시스템 아키텍처 및 동작 메커니즘을 시각화한 PlantUML 다이어그램(`.wsd`) 파일들을 보관합니다.

---

## 📄 다이어그램 목록

| 파일명 | 다이어그램 종류 | 주요 내용 |
| :--- | :--- | :--- |
| [architecture.wsd](architecture.wsd) | 컴포넌트 아키텍처 | Python UI(CustomTkinter), Bridge(Worker), Rust Core(PyO3/Codec/Archive) 간의 계층 구조 및 데이터 흐름 |
| [class_diagram.wsd](class_diagram.wsd) | 클래스 다이어그램 | `Zipper9App`, `CompressionWorker`, PyO3 노출 모델(`ProgressEvent`, `ZipEntryInfo`) 및 Rust API 인터페이스 |
| [sequence_compression.wsd](sequence_compression.wsd) | 시퀀스 (압축) | 파일 추가부터 64KB 스트리밍 청크 압축, 실시간 진행률 콜백, 완료 알림까지의 전체 흐름 |
| [sequence_extraction.wsd](sequence_extraction.wsd) | 시퀀스 (해제) | 아카이브 미리보기, Zip-Slip 방지 검증, 디렉터리 복원 및 실시간 진행률 전달 흐름 |
| [usecase.wsd](usecase.wsd) | 유스케이스 | 사용자와 시스템 간의 상호작용 (압축, 해제, 알고리즘 선택, 테마 변경, 모니터링 등) |

---

## 🔍 VS Code에서 미리보기 (Preview) 방법

`D:\mirror\dev\MyPython\Toy_Projects\plantUML사용법.md` 기준:

1. VS Code에서 위의 `.wsd` 파일 중 하나를 엽니다.
2. 키보드 단축키 **`Alt` + `D`**를 누르면 오른쪽에 실시간 렌더링 다이어그램 미리보기가 표시됩니다.
3. 이미지(PNG/SVG)로 내보내려면:
   - `Ctrl` + `Shift` + `P` 누름
   - `PlantUML: Export Current Diagram` 검색 및 선택
   - 원하는 이미지 포맷(`png`, `svg` 등) 선택
