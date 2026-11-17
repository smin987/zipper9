# zipper9 멀티플랫폼 바이너리 패키징 및 배포 가이드 (v1.0.0)

본 문서는 `zipper9 v1.0.0`의 3대 운영체제(**Windows 11**, **Debian Linux**, **macOS**) 바이너리 패키징, 빌드 절차 및 배포 규격을 설명합니다.

---

## 📌 플랫폼별 배포 규격 요약

| 플랫폼 | 지원 아키텍처 | 배포 포맷 | 내장/요구 네이티브 엔진 | 데스크톱 통합 방식 |
| :--- | :--- | :--- | :--- | :--- |
| **Windows 11 / 10** | x86_64 | `zipper9.exe` (독립 실행파일)<br>`zipper9_shell.msix` (확장 패키지) | `tools/` 번들 (`7z.exe`, `lz4.exe`, `zstd.exe`) | Win11 모던 1단계 우클릭 (`IExplorerCommand` Rust COM)<br>클래식 우클릭 & 확장자 연결 |
| **Debian / Ubuntu** | amd64, arm64 | `zipper9_1.0.0_amd64.deb`<br>`zipper9-1.0.0-x86_64.AppImage` | 시스템 패키지 (`7zip` / `p7zip-full`, `lz4`, `zstd`) | XDG `.desktop` (`/usr/share/applications/`)<br>Nautilus / Nemo / Thunar 컨텍스트 스크립트 |
| **macOS** | Universal (Apple Silicon & Intel) | `zipper9-1.0.0.dmg`<br>`zipper9.app` (애플리케이션 번들) | Homebrew (`7zz`, `lz4`, `zstd`) 또는 번들 내장 | `/Applications` 드래그 설치<br>Finder 빠른 동작(Quick Actions) / Services |

---

## 1. Windows 11 / 10 배포 빌드

### 1.1 독립 실행 바이너리 (`zipper9.exe`) 빌드
PyInstaller를 통해 모든 C/C++ 네이티브 엔진과 CustomTkinter 자산을 하나의 18MB 단일 실행파일로 번들링합니다:

```powershell
# 가상환경 활성화 및 빌드 실행
.\.venv\Scripts\activate
pip install -r requirements.txt pyinstaller
pyinstaller zipper9.spec --noconfirm
```
- 결과물: `dist/zipper9.exe`

### 1.2 Windows 11 최상위 1단계 우클릭 확장 (`zipper9_shell.msix`) 빌드
Visual C++ 런타임 종속성 없는 단독 Rust COM DLL을 빌드하고 MSIX Sparse Package로 디지털 서명합니다:

```powershell
# 1. Rust COM DLL 컴파일 (Release)
cargo build --release --manifest-path crates/zipper9_shell/Cargo.toml
Copy-Item target\release\zipper9_shell.dll tools\modern_shell\ -Force

# 2. 인증서 생성 및 MSIX 패키징 (최초 1회)
powershell -ExecutionPolicy Bypass -File tools\create_cert_official.ps1
powershell -ExecutionPolicy Bypass -File tools\build_msix.ps1
```
- 결과물: `tools/zipper9_shell.msix`

---

## 2. Debian Linux 배포 (`.deb` 패키지)

### 2.1 사전 필수 패키지
Debian 11/12 및 Ubuntu 22.04/24.04 LTS 환경:
```bash
sudo apt update
sudo apt install -y python3 python3-tk python3-pip 7zip lz4 zstd
pip3 install customtkinter darkdetect
```

### 2.2 `.deb` 패키지 디렉터리 구조
```text
zipper9_1.0.0_amd64/
├── DEBIAN/
│   ├── control                 # 패키지 메타데이터 및 의존성
│   └── postinst                # 설치 후 아이콘 캐시 갱신 스크립트
├── usr/
│   ├── bin/
│   │   └── zipper9             # 실행 래퍼 스크립트
│   ├── share/
│   │   ├── applications/
│   │   │   └── zipper9.desktop # 앱 런처 및 파일 확장자 연결
│   │   ├── icons/hicolor/256x256/apps/
│   │   │   └── zipper9.png     # 애플리케이션 아이콘
│   │   └── zipper9/            # Python 소스코드 번들
│   │       ├── main.py
│   │       └── zipper9_ui/
```

### 2.3 `DEBIAN/control` 명세 예시
```control
Package: zipper9
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: smin987 <developer@zipper9.org>
Depends: python3 (>= 3.10), python3-tk, 7zip | p7zip-full, lz4, zstd
Description: Ultra-lightweight and high-speed multi-core archiver
 zipper9 combines modern Fluent GUI with native multi-core compression
 engines (7-Zip, LZ4, Zstandard) supporting ZIP, 7z, TAR, and RAR.
```

### 2.4 빌드 및 패키징 명령어
```bash
# deb 패키지 빌드
dpkg-deb --build zipper9_1.0.0_amd64

# 설치 테스트
sudo dpkg -i zipper9_1.0.0_amd64.deb
```

---

## 3. macOS 배포 (`.dmg` 및 `.app` 번들)

### 3.1 사전 필수 환경 (Homebrew)
macOS 12 (Monterey) 이상, Apple Silicon (M1/M2/M3/M4) 및 Intel 호환:
```bash
brew install python-tk 7-zip lz4 zstd create-dmg
pip3 install -r requirements.txt pyinstaller
```

### 3.2 macOS `.app` 번들 컴파일
```bash
pyinstaller \
    --name="zipper9" \
    --windowed \
    --icon="assets/archive_icon.ico" \
    --add-data="assets:assets" \
    --hidden-import="customtkinter" \
    --hidden-import="darkdetect" \
    main.py
```
- 결과물: `dist/zipper9.app`

### 3.3 `.dmg` 드래그-설치 이미지 생성
```bash
create-dmg \
  --volname "zipper9-v1.0.0" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "zipper9.app" 175 120 \
  --hide-extension "zipper9.app" \
  --app-drop-link 425 120 \
  "dist/zipper9-1.0.0-macOS.dmg" \
  "dist/zipper9.app"
```

---

## 4. 공통 아키텍처 자동 감지 (OS 엔진 폴백 메커니즘)

`zipper9_ui/bridge/worker.py`는 모든 플랫폼에서 다음과 같은 우선순위로 네이티브 엔진을 감지합니다:
1. **번들 바이너리 탐색**: 앱 내부 `tools/7z/`, `tools/lz4/`, `tools/zstd/`
2. **시스템 PATH 검색**: `shutil.which("7zz")`, `shutil.which("7z")`, `shutil.which("lz4")`, `shutil.which("zstd")`
3. **OS별 표준 설치 경로 탐색**:
   - Linux: `/usr/bin/7zz`, `/usr/bin/7z`, `/usr/bin/lz4`, `/usr/bin/zstd`
   - macOS: `/opt/homebrew/bin/7zz`, `/usr/local/bin/7zz` 등
4. **Python 표준 라이브러리 폴백**: 최악의 경우에도 순수 Python `tarfile` 및 `zipfile`로 안전하게 백업 구동.

---

## 5. 패키지 관리자 배포 규격 (WinGet, Homebrew, APT)

### 5.1 Windows: WinGet
- **패키지 식별자**: `smin987.zipper9`
- **배포 방식**: `wingetcreate` CLI를 통해 `microsoft/winget-pkgs` 공식 저장소에 PR 등록.
- **설치 명령어**: `winget install smin987.zipper9`

### 5.2 macOS: Homebrew Cask
- **배포 방식**: 메인 저장소의 `zipper9.rb` Cask 파일을 통한 단독 설치 지원 (별도 tap 불필요).
- **심볼릭 링크 바인딩**: `binary "#{appdir}/zipper9.app/Contents/MacOS/zipper9"` 지시자가 포함되어 있어, 터미널에서 `zipper9` 명령어로 즉시 GUI를 띄울 수 있습니다.
- **설치 명령어**: `brew install --cask https://raw.githubusercontent.com/smin987/zipper9/main/zipper9.rb`

### 5.3 Debian / Ubuntu: APT
- **배포 포맷**: `zipper9_1.0.0_amd64.deb`
- **데스크톱 및 CLI 런처**: `/usr/bin/zipper9` 및 `/usr/share/applications/zipper9.desktop` 자동 등록.
- **설치 명령어**: `sudo apt install ./zipper9_1.0.0_amd64.deb`

