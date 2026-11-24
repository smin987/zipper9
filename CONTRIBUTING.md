# zipper9 Contribution Guidelines & CLA / 기여 가이드라인 및 기여자 라이선스 계약

Thank you for your interest in contributing to **zipper9**!
**zipper9** 프로젝트에 관심을 가져주셔서 감사합니다!

This document outlines guidelines for contributing, coding standards, and our mandatory Contributor License Agreement (CLA) to ensure the sustainable and legally sound development of the project.
본 문서는 프로젝트의 지속 가능하고 법적으로 안전한 개발을 위한 기여 안내, 코딩 표준 및 필수 기여자 라이선스 계약(CLA)을 규정합니다.

---

## 1. Contributor License Agreement (CLA) [Mandatory / 필수 동의]

> [!IMPORTANT]
> ### 📜 ENGLISH: Mandatory Contributor Consent
> **zipper9** adopts a **Fair-Code (Source-Available)** license model providing 100% free binaries to all users. To ensure long-term sustainability, **commercial, dual-licensed, or Pro editions** may be introduced in the future.
> 
> Under open-source legal principles, incorporating external contributions into future commercial or dual-licensed distributions **legally requires the explicit prior consent of all contributors**.
> 
> By submitting a Pull Request (PR) to this repository, you explicitly agree to the following terms:
> 
> 1. **Grant of Rights for Commercial & Dual Licensing**:
>    - You grant the original Author (smin987) a **perpetual, worldwide, non-exclusive, royalty-free, irrevocable, and sublicensable license** to use, modify, adapt, compile, bundle, distribute, sublicense, and sell your Contribution (including code, documentation, scripts, and assets).
>    - The Author may include your Contribution in both current free/source-available releases and future **commercial, proprietary, dual-licensed, or Pro editions** without restriction or compensation.
> 2. **Warranty of Original Work**:
>    - You warrant that the Contribution is your own original creation and that you have full legal right to grant the rights above. You represent that your Contribution does not infringe upon any third-party patents, copyrights, trade secrets, or proprietary licenses.
> 3. **Disclaimer of Warranty**:
>    - Your Contribution is provided "AS-IS", without warranties of any kind, consistent with Section 6 of the `LICENSE` file.
> 
> ---
> 
> ### 📜 한국어: 기여자 라이선스 계약 (CLA) 동의 필수
> **zipper9**은 모든 사용자에게 100% 무료 바이너리를 제공하는 **Fair-Code(Source-Available)** 라이선스 모델을 채택하고 있으며, 향후 프로젝트의 지속 가능성을 위해 **프로(Pro) 버전, 듀얼 라이선스, 또는 상용 패키지**가 도입될 수 있습니다.
> 
> 오픈소스 법률 원칙상 외부 기여자의 코드가 포함된 상태에서 상용/듀얼 라이선스로 전환하거나 유료 버전을 배포하려면 **기여자 전원의 사전 동의가 법적으로 필수**입니다.
> 
> 따라서 **zipper9에 Pull Request(PR)를 제출하는 모든 기여자는 아래 사항에 명시적으로 동의하는 것으로 간주됩니다:**
> 
> 1. **상용/듀얼 라이선스 포함 권한 부여**:
>    - 기여자는 본인이 제출한 코드, 패치, 문서, 자산 등 모든 기여물(Contribution)에 대해, 프로젝트 원작자(smin987)에게 **영구적이고, 전 세계적이며, 비독점적이고, 무상(로열티 프리)이며, 취소 불가능하고 서브라이선스가 가능한 권한**을 부여합니다.
>    - 원작자는 해당 기여물을 zipper9의 무료 버전뿐만 아니라, **향후 출시될 수 있는 상용(Commercial), 듀얼(Dual), 프로(Pro) 또는 유료 라이선스 버전에도 제한 없이 포함, 수정, 컴파일, 판매 및 재배포**할 수 있습니다.
> 2. **순수 창작물 보증**:
>    - 기여자는 제출한 코드가 본인의 독자적인 순수 창작물이며, 제3자의 특허, 저작권, 영업비밀 또는 독점 라이선스를 침해하지 않음을 보증합니다.
> 3. **라이선스 면책 동의**:
>    - 기여물은 `LICENSE` 제6조에 따라 "있는 그대로(AS-IS)" 제공되며 어떠한 보증도 수반하지 않습니다.

---

## 2. Bug Reports & Feature Requests / 버그 리포트 및 기능 제안

- Please file issues on [GitHub Issues](https://github.com/smin987/zipper9/issues).
- 버그나 개선 아이디어는 [GitHub Issues](https://github.com/smin987/zipper9/issues)에 등록해 주세요.
- When filing a bug report, please include:
  - OS version / 운영체제 버전 (e.g., Windows 11 23H2, Ubuntu 24.04, macOS Sonoma)
  - zipper9 version / 앱 버전 (e.g., v1.0.1)
  - Steps to reproduce & target archive format / 재현 단계 및 대상 아카이브 포맷 (ZIP, 7Z, TAR, ALZ 등)
  - Error logs or screenshots / 에러 로그 또는 화면 캡처

---

## 3. Development Setup / 로컬 개발 환경 설정

1. **Fork & Clone repository / 저장소 포크 및 복제**:
   ```bash
   git clone https://github.com/<your-username>/zipper9.git
   cd zipper9
   ```

2. **Virtual Environment & Dependencies / 가상환경 및 의존성 설치**:
   ```bash
   python -m venv .venv
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   # Linux / macOS
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run Application / 로컬 실행**:
   ```bash
   python main.py
   ```

4. **Run Tests / 단위 테스트 실행**:
   ```bash
   pytest tests/
   ```

---

## 4. Pull Request Submission Rules / PR 제출 규칙

1. **Branch Naming / 브랜치 명명 규칙**:
   - Features: `feature/<feature-name>` (예: `feature/fastcdc-dedup`)
   - Fixes: `fix/<bug-name>` (예: `fix/context-menu-duplicate`)
2. **Unit Tests / 단위 테스트 필수**:
   - Ensure all existing tests pass (`pytest tests/`) and add new test cases for new functionality.
   - 기존 단위 테스트 100% 통과 확인 및 신규 기능/버그 픽스에 대한 테스트 케이스를 필수로 동봉해 주세요.
3. **Commit Convention / 커밋 메시지 컨벤션**:
   - Follow Conventional Commits: `feat: ...`, `fix: ...`, `docs: ...`, `refactor: ...`, `test: ...`
4. **Mandatory CLA Check / PR 템플릿의 CLA 동의 필수**:
   - Check the mandatory CLA consent checkboxes in the Pull Request template.
   - PR 생성 시 나타나는 템플릿의 CLA 동의 체크박스(`[x]`)를 반드시 체크해 주셔야 병합이 진행됩니다.
