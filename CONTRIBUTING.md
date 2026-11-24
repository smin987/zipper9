# zipper9 기여 가이드라인 (Contribution Guidelines)

**zipper9** 프로젝트에 관심을 가져주셔서 감사합니다! 본 문서는 zipper9의 코드 품질을 유지하고, 법적·라이선스적 분쟁 없이 안전하게 프로젝트에 기여(Pull Request, Issue)하기 위한 안내서입니다.

---

## 1. 기여 전 확인 사항 (기여자 라이선스 계약, CLA)

> [!IMPORTANT]
> **Contributor License Agreement (CLA) 동의 필수**
> 
> zipper9은 모든 사용자에게 100% 무료 바이너리를 제공하는 **Fair-Code(Source-Available)** 라이선스 모델을 채택하고 있으며, 향후 프로젝트의 지속 가능성을 위해 **프로(Pro) 버전, 듀얼 라이선스, 또는 상용 패키지**가 도입될 수 있습니다.
> 
> 오픈소스 법률 원칙상 외부 기여자의 코드가 포함된 상태에서 상용/듀얼 라이선스로 전환하거나 유료 버전을 배포하려면 **기여자 전원의 사전 동의가 법적으로 필수**입니다.
> 
> 따라서 **zipper9에 Pull Request(PR)를 제출하는 모든 기여자는 아래 사항에 명시적으로 동의하는 것으로 간주됩니다:**
> 
> 1. **상용/듀얼 라이선스 포함 권한 부여**:
>    - 기여자는 본인이 제출한 코드, 패치, 문서, 자산 등 모든 기여물(Contribution)에 대해, 프로젝트 원작자(smin987)에게 **영구적이고, 전 세계적이며, 비독점적이고, 로열티가 없으며(무상), 서브라이선스가 가능한 라이선스**를 부여합니다.
>    - 원작자는 해당 기여물을 zipper9의 무료/오픈소스 버전뿐만 아니라, **향후 출시될 수 있는 상용(Commercial), 듀얼(Dual), 프로(Pro) 또는 유료 라이선스 버전에도 제한 없이 포함, 수정, 컴파일, 판매 및 재배포**할 수 있습니다.
> 2. **순수 창작물 보증**:
>    - 기여자는 제출한 코드가 본인의 독자적인 순수 창작물이며, 제3자의 특허, 저작권, 영업비밀 또는 제3자 독점 라이선스를 침해하지 않음을 보증합니다.
> 3. **라이선스 면책 동의**:
>    - 기여물은 `LICENSE` 파일의 제6조 면책 조항에 따라 "있는 그대로(AS-IS)" 제공되며 어떠한 보증도 수반하지 않습니다.

모든 Pull Request 제출 시 위 CLA 동의 체크박스(`[x]`)를 필수로 체크해 주셔야 검토 및 병합이 진행됩니다.

---

## 2. 버그 리포트 및 기능 제안

- 새로운 버그를 발견하셨거나 기능 개선 아이디어가 있다면 [GitHub Issues](https://github.com/smin987/zipper9/issues)에 등록해 주세요.
- 버그 리포트 시 다음 정보를 포함해 주시면 빠른 해결에 큰 도움이 됩니다:
  - OS 버전 (예: Windows 11 23H2, Ubuntu 24.04, macOS Sonoma)
  - zipper9 버전 (예: v1.0.1)
  - 문제 발생 재현 단계 및 대상 아카이브 포맷 (ZIP, 7Z, TAR 등)
  - 에러 메시지 또는 화면 캡처

---

## 3. 개발 환경 설정 및 로컬 빌드

1. **저장소 포크 및 클론**:
   ```bash
   git clone https://github.com/<your-username>/zipper9.git
   cd zipper9
   ```
2. **파이썬 가상환경 구성**:
   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   # Linux / macOS
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **로컬 실행**:
   ```bash
   python main.py
   ```
4. **테스트 실행**:
   ```bash
   pytest tests/
   ```

---

## 4. Pull Request 제출 규칙

1. **브랜치 네이밍**:
   - 기능 추가: `feature/<기능명>` (예: `feature/entropy-filter`)
   - 버그 수정: `fix/<버그명>` (예: `fix/context-menu-duplicate`)
2. **단위 테스트 필수**:
   - 코드 수정 시 기존 `tests/` 스위트가 100% 통과해야 하며, 새로운 기능이나 버그 수정에 대한 테스트 케이스를 함께 추가해 주세요.
3. **커밋 메시지 컨벤션**:
   - `feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`, `test: ...` 형식을 권장합니다.
4. **PR 템플릿 작성**:
   - PR을 생성하면 나타나는 템플릿의 체크리스트(테스트 완료 여부 및 **CLA 동의 체크박스**)를 성실히 작성해 주세요.
