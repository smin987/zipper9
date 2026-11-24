# ⚡ zipper9 v1.0.1 Release Notes / 릴리즈 노트

[English (영어)](#english) | [한국어 (Korean)](#korean)

---

<a id="english" name="english"></a>
# ⚡ zipper9 v1.0.1 Release (English)

Ultra-lightweight, blazing-fast multi-format archiver with modern Fluent UI, full Windows 11 context menu integration, and enterprise-grade format compliance.

---

## 📦 Download Assets & OS Installation Guide

### 1. Download Packages & Assets
| Operating System | Architecture | Package / Asset Name | Description |
| :--- | :--- | :--- | :--- |
| **🪟 Windows 11 / 10** | x86_64 (64-bit) | [`zipper9-windows-x64.exe`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-windows-x64.exe) | Single standalone portable executable (Recommended) |
| **🪟 Windows 11 / 10** | x86_64 (64-bit) | [`zipper9-v1.0.1-windows-x64.zip`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-v1.0.1-windows-x64.zip) | Portable ZIP archive with binaries & docs |
| **🍎 macOS** | Universal (Intel & Apple Silicon) | [`zipper9-v1.0.1-macos.dmg`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-v1.0.1-macos.dmg) | Apple Disk Image installer (.app bundle) |
| **🐧 Linux (Debian / Ubuntu / Mint)** | x86_64 (amd64) | [`zipper9_1.0.1_amd64.deb`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9_1.0.1_amd64.deb) | Native Debian package installer |
| **🐧 Linux (Raspberry Pi 4/5 / ARM)** | aarch64 (arm64) | [`zipper9_1.0.1_arm64.deb`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9_1.0.1_arm64.deb) | Native Debian package for 64-bit ARM Linux |
| **🐧 Linux (Generic Standalone)** | x86_64 | [`zipper9-v1.0.1-linux-x86_64.tar.gz`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-v1.0.1-linux-x86_64.tar.gz) | Standalone portable tarball binary |
| **🐧 Linux (Generic ARM SBCs)** | aarch64 | [`zipper9-v1.0.1-linux-aarch64.tar.gz`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-v1.0.1-linux-aarch64.tar.gz) | Standalone portable tarball for ARM64 |

---

### 2. OS-Specific Installation Instructions

#### 🪟 Windows 11 / 10
- **Standalone Portable Execution (No installation required)**:
  1. Download [`zipper9-windows-x64.exe`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-windows-x64.exe).
  2. Move it to your preferred folder (e.g., `C:\Tools\zipper9\` or Desktop) and double-click to launch.
- **Windows Explorer Context Menu Auto-Sync**:
  - Running `zipper9-windows-x64.exe` automatically registers and syncs both Windows 11 Modern and Classic Explorer right-click context menus (`Compress with zipper9`, `Extract with zipper9`).
  - To update, simply overwrite the old executable with the new version or run the new executable once.

#### 🍎 macOS (Apple Silicon & Intel)
- **Installing via DMG Package**:
  1. Download [`zipper9-v1.0.1-macos.dmg`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-v1.0.1-macos.dmg).
  2. Double-click to open the DMG, then drag `zipper9.app` into your **Applications** folder.
  3. **First-launch Gatekeeper Notice**:
     - If macOS displays an *"unidentified developer"* prompt on first launch, open **Finder** ➔ navigate to **Applications** ➔ right-click `zipper9.app` ➔ select **Open**, and click **Open** in the confirmation dialog.

#### 🐧 Linux (Ubuntu / Debian / Raspberry Pi OS / Generic Linux)
- **Debian / Ubuntu / Mint / Pop!_OS (`.deb` package)**:
  ```bash
  # For x86_64 (Intel/AMD 64-bit)
  sudo apt install ./zipper9_1.0.1_amd64.deb

  # For ARM64 (Raspberry Pi 4/5, Apple Silicon VMs, Cloud ARM)
  sudo apt install ./zipper9_1.0.1_arm64.deb
  ```
- **Generic Linux Standalone Tarball (Run anywhere without root privileges)**:
  ```bash
  # Extract tarball
  tar -xzf zipper9-v1.0.1-linux-x86_64.tar.gz
  cd zipper9
  ./zipper9
  ```

---

## 🚀 Key New Features (v1.0.1)

- **Extensive Expansion of Protected DefaultIcon & File Associations to 36 Formats**:
  - Toggling **[Display Archive File Icon]** now applies zipper9's brand icon across **36 pure archive and package formats** (`CAB`, `WIM`, `LHA`, `LZH`, `ARJ`, `DEB`, `RPM`, `TBZ2`, `TXZ`, `IMG`, `BIN`, `UDF`, `PKG`, etc.).
  - Preserves Windows native virtual disk mounting (`.iso`) and installers/virtual disks (`.msi`, `.vhd`, `.vhdx`, `.vmdk`, `.sfx.exe`).
- **Comprehensive Decompression Support for 46 Archive, Disk Image & Package Formats**:
  - Full support registered in `SUPPORTED_EXTRACT_EXTS` across 46 total extensions including standard archives (`ZIP`, `7Z`, `RAR`), Linux packages (`DEB`, `RPM`, `TAR.GZ`, `TAR.XZ`), and modern streaming formats (`LZ4`, `ZSTD`).
  - *Note: EGG format is permanently excluded due to proprietary commercial redistribution restrictions.*
- **UDF ISO Optical Disk Image Creation & Triple-Standard (ISO 9660, Joliet, UDF) Extraction**:
  - **Creation**: Supports standard **UDF 2.60** preserving large files (>4GB) and Unicode filenames without loss.
  - **Extraction**: Supports ISO 9660, Joliet, and UDF standards directly through 7-Zip native engine without virtual drive mounting.
- **Default Preference Overhaul**:
  - Explorer right-click context menu integration is now enabled (**ON**) by default on fresh installations.
  - Initial interface language standardized to global **English (`EN`)** (one-click toggleable to Korean).
- **Slim Single-Line 3-Metric Decompression Cards**:
  - Re-engineered dashboard cards into a slim, single-line horizontal layout (height reduced from 108px to ~38px), expanding the file preview listbox (`extract_preview`) for comfortable scroll-free inspection.
- **Intelligent Packaging (Batch Compress Regular Files + Existing Archives)**:
  - Dropping regular files and existing archives together packages all items into a unified archive instead of switching to decompression.
- **Accordion Settings Panel with Dynamic Window Resizing (Plan B)**:
  - Collapsible **[▼/▶ Settings]** panel smoothly adjusts window height (820px ➔ 580px) while maintaining full view of active settings via summary badges.
- **Real-Time Context Menu Progress Dialog (`InstantProgressDialog`)**:
  - Lightweight popup showing real-time percentage (%), currently processed filename (`Cascadia Mono`), elapsed time, and safe cancellation with auto-rollback.
- **Official ALZ (`.alz`, `.a00`) Archive Decompression Support**:
  - Powered 100% by the permissive open-source engine (`unalz`, zlib/libpng License), guaranteeing **zero license audit risk for enterprise environments**.
- **Official Linux ARM64 (aarch64) Standalone Binary & Package Support**:
  - Full native support for Raspberry Pi 4/5, Apple Silicon VMs, and AWS Graviton servers.
- **Standardized Windows Standalone Portable Binary Naming (`zipper9-windows-x64.exe`)**.
- **Modern In-App `[ℹ️ About / Licenses]` Dialog**:
  - Fluent dialog with freeware guarantees, ALZ unalz audit safety, and third-party OSS license tables.
- **Smart Version Badge with Non-Blocking 24-Hour GitHub Update Check**.

---

## 🛡️ Fixes & Improvements

- **100% Automatic Rollback & Cleanup of Incomplete Files on Cancellation**:
  - Purges partial files of any size upon cancel/close, including Windows lock retry defense and automatic cleanup of empty directories (`rmdir`).
- **Pre-Validation & Safe UX for Non-Standard / Corrupted Archives (Wii/GameCube ROMs, etc.)**:
  - Displays a clean alert (*"Unsupported archive format"*) without crashing or switching views when non-standard disc images are dropped.
- **Full Localization for English (EN) Mode Dashboard & File Previews**.
- **Blocking Prevention & 9.7s High-Speed Unit Test Execution**.
- **Automatic 0-Byte Phantom File Cleanup on Password / CRC Errors**.
- **Automatic Context Menu ExePath Auto-Sync**.
- **Enhanced Archive File List Readability (Cascadia Mono 11pt)**.

---

## 📄 License & Fair-Code Terms

Distributed under the **[zipper9 Fair-Code License Agreement](https://github.com/smin987/zipper9/blob/main/LICENSE)**:
- **Compiled Binaries**: 100% completely FREE forever for personal, educational, non-profit, and **commercial / enterprise use**.
- **Source Code**: Public for study, security auditing, and upstream contributions (CLA applies). Modifying source code for commercial use or developing competing utilities is strictly prohibited.

---

## 💖 Support & Sponsorship

If zipper9 brings value to your daily workflow, please consider sponsoring the developer. Your support directly funds performance optimizations, multi-platform releases, and new features! ☕✨

<div align="center">

[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa?style=for-the-badge&logo=github&logoColor=white)](https://github.com/sponsors/smin987) &nbsp; [![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/smin987) &nbsp; [![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/smin987)

</div>

---
---

<a id="korean" name="korean"></a>
# ⚡ zipper9 v1.0.1 릴리즈 (Korean)

모던 Fluent UI, Windows 11 탐색기 우클릭 메뉴 완벽 연동, 기업 환경 100% 무료 보증 라이선스를 탑재한 초경량·초고속 멀티 포맷 아카이버 zipper9입니다.

---

## 📦 다운로드 에셋 및 OS별 설치 안내

### 1. 다운로드 패키지 및 에셋 목록
| 운영체제 | 아키텍처 | 파일명 / 에셋 링크 | 설명 |
| :--- | :--- | :--- | :--- |
| **🪟 Windows 11 / 10** | x86_64 (64비트) | [`zipper9-windows-x64.exe`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-windows-x64.exe) | 단독 포터블 무설치 실행 파일 (권장) |
| **🪟 Windows 11 / 10** | x86_64 (64비트) | [`zipper9-v1.0.1-windows-x64.zip`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-v1.0.1-windows-x64.zip) | 실행 파일 및 라이선스 문서 포함 압축본 |
| **🍎 macOS** | Universal (인텔 & 애플 실리콘) | [`zipper9-v1.0.1-macos.dmg`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-v1.0.1-macos.dmg) | macOS 전용 DMG 디스크 이미지 패키지 |
| **🐧 Linux (Debian / Ubuntu / Mint)** | x86_64 (amd64) | [`zipper9_1.0.1_amd64.deb`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9_1.0.1_amd64.deb) | 데비안/우분투 계열 설치용 .deb 패키지 |
| **🐧 Linux (라즈베리 파이 4/5 / ARM)** | aarch64 (arm64) | [`zipper9_1.0.1_arm64.deb`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9_1.0.1_arm64.deb) | 64비트 ARM 리눅스 전용 .deb 패키지 |
| **🐧 Linux (범용 무설치 타르볼)** | x86_64 | [`zipper9-v1.0.1-linux-x86_64.tar.gz`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-v1.0.1-linux-x86_64.tar.gz) | 설치 없이 바로 실행하는 x86_64 바이너리 |
| **🐧 Linux (범용 ARM SBCs)** | aarch64 | [`zipper9-v1.0.1-linux-aarch64.tar.gz`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-v1.0.1-linux-aarch64.tar.gz) | 설치 없이 바로 실행하는 ARM64 바이너리 |

---

### 2. 운영체제별 설치 및 실행 가이드

#### 🪟 Windows 11 / 10
- **단독 포터블 실행 (별도 인스톨러 불필요)**:
  1. [`zipper9-windows-x64.exe`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-windows-x64.exe) 파일을 다운로드합니다.
  2. 원하는 폴더(예: `C:\Tools\zipper9\` 또는 바탕화면)로 이동한 뒤 더블클릭하여 바로 실행합니다.
- **Windows 탐색기 우클릭 메뉴 자동 동기화**:
  - `zipper9-windows-x64.exe`를 최초 1회 실행하면 Windows 11 모던 1단계 메뉴 및 클래식 우클릭 메뉴(`zipper9으로 압축하기`, `zipper9으로 풀기`)가 자동으로 레지스트리에 등록 및 경로 동기화됩니다.
  - 새 버전으로 업데이트할 때는 기존 파일 위치에 그대로 덮어쓰기하거나, 새 위치에서 한 번만 더블클릭해 주시면 됩니다.

#### 🍎 macOS (Apple Silicon & Intel)
- **DMG 패키지 설치 방법**:
  1. [`zipper9-v1.0.1-macos.dmg`](https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-v1.0.1-macos.dmg) 파일을 다운로드합니다.
  2. DMG 파일을 더블클릭하여 연 후, `zipper9.app`을 **Applications(응용 프로그램)** 폴더로 드래그합니다.
  3. **최초 실행 시 게이트키퍼(Gatekeeper) 안내**:
     - 최초 실행 시 *"확인되지 않은 개발자가 배포했기 때문에..."* 경고창이 나타날 경우, **Finder** ➔ **응용 프로그램** 폴더에서 `zipper9.app`을 마우스 우클릭 ➔ **열기**를 선택하고 확인 창에서 **열기**를 눌러주시면 이후 정상 실행됩니다.

#### 🐧 Linux (우분투 / 데비안 / 라즈베리 파이 OS / 기타 리눅스)
- **데비안 / 우분투 계열 (`.deb` 패키지)**:
  ```bash
  # x86_64 (인텔/AMD 64비트)
  sudo apt install ./zipper9_1.0.1_amd64.deb

  # ARM64 (라즈베리 파이 4/5, 애플 실리콘 가상머신, 클라우드 ARM 서버)
  sudo apt install ./zipper9_1.0.1_arm64.deb
  ```
- **범용 무설치 타르볼 (루트 권한 없이 바로 실행)**:
  ```bash
  # 압축 해제 및 실행
  tar -xzf zipper9-v1.0.1-linux-x86_64.tar.gz
  cd zipper9
  ./zipper9
  ```

---

## 🚀 주요 신규 기능 (v1.0.1)

- **시스템 보호형 압축 파일 아이콘(DefaultIcon) 및 파일 연결 36종 대폭 확장**:
  - 상단 헤더의 **[압축 아이콘 파일 표시]** 스위치를 켰을 때 전용 아이콘(`archive_icon.ico`)이 적용되는 포맷을 **순수 아카이브 36종으로 대폭 확장**했습니다.
  - Windows 기본 가상 드라이브 마운트 보존을 위해 `.iso`는 안전하게 제외되었으며, 인스톨러/가상디스크(`.msi`, `.vhd`, `.vhdx`, `.vmdk`, `.sfx.exe`) 역시 고유 동작을 보존하도록 원천 분리했습니다.
- **광범위한 아카이브·디스크 이미지·시스템 패키지 압축 해제 46종 확장자 전면 등록 지원**:
  - 표준 압축 포맷(`ZIP`, `7Z`, `RAR`), 리눅스 패키지(`DEB`, `RPM`, `TAR.GZ`, `TAR.XZ`), 최신 초고속 아카이브(`LZ4`, `ZSTD`) 등 총 46종 지원. (*EGG 포맷은 이스트소프트의 상업적 재배포 제한 및 독점 라이선스 문제로 영구 제외*)
- **ISO 광학 디스크 이미지 UDF 압축 생성 및 3대 규격(ISO 9660, Joliet, UDF) 압축 해제 공식 지원**:
  - **생성**: 대용량 파일(4GB 초과) 및 유니코드를 무손실 보존하는 **UDF 2.60** 규격 지원.
  - **해제**: 가상 드라이브 마운트 없이 ISO 내부 파일 목록 즉시 탐색 및 원클릭 추출 지원.
- **기본 환경설정 개편**:
  - 신규 설치 시 탐색기 우클릭 메뉴가 기본적으로 **활성화(ON)** 상태로 등록되어 무마찰 즉시 압축/해제 사용 가능.
  - 초기 기본 언어를 글로벌 표준인 **영어(`EN`)**로 지정 (원클릭으로 한국어 전환 가능).
- **압축 해제 3단 메트릭 카드 슬림화 및 하단 파일 목록 뷰 대폭 확장**:
  - 카드 높이를 108px에서 ~38px로 슬림화하여 하단 파일 목록 프리뷰 공간을 대폭 확장.
- **지능형 아카이브 패키징**:
  - 일반 파일과 압축 파일이 함께 드롭되면 모든 대상을 단일 아카이브로 패키징 압축.
- **설정 아코디언 패널 및 GUI 창 하단 동적 축소/확장(Plan B) 탑재**:
  - `[▼/▶ 설정]` 패널 토글 시 윈도우 높이가 부드럽게 축소(820px ➔ 580px)/확장.
- **우클릭 즉시 압축/해제 실시간 진행창 (`InstantProgressDialog`) 탑재**:
  - 실시간 진행률(%), 처리 중인 파일명, 경과 시간 표시 및 불완전 파일 자동 롤백 지원.
- **ALZ (`.alz`, `.a00`) 아카이브 압축 해제 공식 지원**:
  - 순수 오픈소스 엔진(`unalz`, zlib/libpng 라이선스) 기반으로 작동하여 **기업 환경에서도 라이선스 단속 위험 없이 완전 무료**로 안전하게 사용 가능.
- **Linux ARM64 (aarch64) 정식 빌드 및 패키지 지원** (라즈베리 파이 4/5, 애플 실리콘 VM).
- **Windows 단독 포터블 실행 파일 공식 명칭 표준화 (`zipper9-windows-x64.exe`)**.
- **앱 내 모던 `[ℹ️ 정보 / 라이선스]` 다이얼로그 탑재**.
- **스마트 버전 뱃지 및 24시간 논블로킹 GitHub 업데이트 체크 탑재**.

---

## 🛡️ 안정성 및 품질 개선

- **압축 해제 중단/취소 시 불완전 파일 및 잔여 폴더 100% 자동 롤백 클린업**.
- **비표준/콘솔 롬(Wii/GameCube FST 등) 및 손상된 아카이브 사전 유효성 검증 및 방어 UX 탑재**.
- **영문 모드(EN) 압축 해제 대시보드 및 파일 목록 완전 다국어화**.
- **단위 테스트 무한 대기(블로킹) 방어 및 9.7초 초고속 통과**.
- **암호 불일치/CRC 오류 시 0-Byte 유령 파일 자동 롤백 및 청소**.
- **우클릭 메뉴 실행 경로 자동 동기화 (Auto-Sync) 기능 탑재**.
- **아카이브 파일 목록 가독성 개선 (Cascadia Mono 11pt 최적화)**.

---

## 📄 라이선스 정책 (Fair-Code)

본 소프트웨어는 **[zipper9 Fair-Code License Agreement](https://github.com/smin987/zipper9/blob/main/LICENSE)**에 따라 배포됩니다:
- **컴파일 바이너리**: 개인, 교육기관, 공공기관 및 **일반 기업(상업적 업무 환경) 모두 완전 무료**로 영구 사용하실 수 있습니다.
- **소스코드**: 학습, 연구, 보안 감사 및 공식 기여(CLA 적용) 목적으로 공개되어 있으며, 영리 기업의 소스코드 수정 및 경쟁 제품 출시는 엄격히 금지됩니다.

---

## 💖 후원 안내 (Sponsorship)

zipper9이 유용하셨다면 개발자를 응원해 주세요! 여러분의 소중한 후원은 성능 최적화, 멀티플랫폼 지원 및 새로운 혁신 기능을 지속적으로 개발하는 데 큰 힘이 됩니다. ☕✨

<div align="center">

[![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa?style=for-the-badge&logo=github&logoColor=white)](https://github.com/sponsors/smin987) &nbsp; [![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/smin987) &nbsp; [![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/smin987)

</div>
