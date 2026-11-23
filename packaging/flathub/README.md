# Zipper9 Flathub (Flatpak) 패키징 및 공식 등록 가이드

본 문서는 **Zipper9**(`io.github.smin987.zipper9`)을 글로벌 리눅스 앱스토어인 **[Flathub](https://flathub.org)**에 공식 제출하고 등록하기 위한 전체 프로세스를 단계별로 설명합니다.

> [!CAUTION]
> **Flathub 공식 AI 정책 (Strictly Human-Driven Policy)**
> Flathub는 자원봉사자 리뷰어 보호와 생태계 품질 관리를 위해 **PR 제출, 커밋 메시지, PR 설명문 작성 및 리뷰어와의 모든 소통 과정에서 AI/LLM 자동화 및 대필을 엄격히 금지**하고 있습니다.
> AI 도구로 자동 생성된 PR이나 AI 에이전트 제출이 확인될 경우 **사전 경고 없이 PR이 즉시 Close(반려) 처리되며 계정이 영구 밴(Permanent Ban)**될 수 있습니다.
> 따라서 **반드시 개발자 본인이 직접 브랜치를 푸시하고 GitHub 웹에서 본인의 문장으로 PR을 작성하여 제출**해야 합니다.


---

## 1. 사전 준비 및 패키지 파일 구성

Flathub 제출용 파일들은 프로젝트의 `packaging/flathub/` 디렉터리에 모두 준비되어 있습니다:

| 파일명 | 역할 | 설명 |
| :--- | :--- | :--- |
| `io.github.smin987.zipper9.yaml` | **Flatpak 매니페스트** | 빌드 시스템, 런타임(`org.freedesktop.Platform 24.08`), 권한(`--filesystem=host`), 멀티 아키텍처(x86_64, aarch64) 바이너리 소스 및 체크섬 정의 |
| `io.github.smin987.zipper9.metainfo.xml` | **AppStream 메타데이터** | Flathub 및 리눅스 소프트웨어 센터(GNOME Software, KDE Discover)에 표시되는 앱 설명, 스크린샷 4종, 릴리즈 노트, OARS 1.1 콘텐츠 등급 |
| `io.github.smin987.zipper9.desktop` | **XDG 데스크톱 엔트리** | 리눅스 시스템 메뉴 등록, 카테고리(`Utility;Archiving;`), 지원 MimeType 및 `%F` 파일 인자 매핑 |
| `io.github.smin987.zipper9.png` | **고해상도 앱 아이콘** | 256x256 해상도의 공식 아이콘 에셋 |

---

## 2. Flathub 공식 신규 앱 등록 절차 (Pull Request)

Flathub는 GitHub 기반의 신규 앱 승인 워크플로우를 사용합니다.

### 2.1 1단계: Flathub 공식 저장소 Fork
1. 브라우저로 [https://github.com/flathub/flathub](https://github.com/flathub/flathub)에 접속합니다.
2. 우측 상단의 **Fork** 버튼을 클릭하여 본인 계정(`smin987`)으로 포크합니다.

### 2.2 2단계: 신규 앱 브랜치 생성 및 파일 배치
로컬 터미널(WSL 또는 Linux 환경 권장)에서 포크한 저장소를 클론하고 브랜치를 생성합니다:

```bash
# 1. 포크한 flathub 저장소 클론
git clone https://github.com/smin987/flathub.git
cd flathub

# 2. 신규 앱 전용 브랜치 생성 (App ID와 동일한 브랜치명 권장)
git checkout -b add-io.github.smin987.zipper9

# 3. 신규 앱 디렉터리 생성 및 파일 복사
#    (Flathub new submission 규격: App ID 이름의 서브폴더가 아닌, PR 루트에 파일들을 배치하거나 flathub repo 규정에 맞춥니다)
#    * 최신 flathub/flathub submission 규칙: 루트에 아래 4개 파일을 배치합니다.
cp /path/to/zipper9/packaging/flathub/* .

# 4. 파일 상태 확인
ls -la io.github.smin987.zipper9.*
# io.github.smin987.zipper9.yaml
# io.github.smin987.zipper9.metainfo.xml
# io.github.smin987.zipper9.desktop
# io.github.smin987.zipper9.png
```

### 2.3 3단계: 로컬 빌드 및 유효성 검증 (선택 권장)
리눅스/WSL 환경에 `flatpak`과 `flatpak-builder`가 설치되어 있다면 제출 전 로컬 검증을 실행할 수 있습니다:

```bash
# 런타임 및 SDK 설치 (최초 1회)
flatpak install flathub org.freedesktop.Platform//24.08 org.freedesktop.Sdk//24.08

# AppStream 메타데이터 구문 검증
appstreamcli validate io.github.smin987.zipper9.metainfo.xml

# 로컬 빌드 테스트
flatpak-builder --force-clean --user --install-deps-from=flathub build-dir io.github.smin987.zipper9.yaml

# 로컬 실행 테스트
flatpak-builder --run build-dir io.github.smin987.zipper9.yaml zipper9
```

### 2.4 4단계: 커밋 및 Pull Request 제출
```bash
git add io.github.smin987.zipper9.*
git commit -m "Add io.github.smin987.zipper9"
git push origin add-io.github.smin987.zipper9
```

1. GitHub의 포크 저장소 페이지에서 **Compare & pull request** 버튼을 클릭합니다.
2. **PR 제목**: `New app: io.github.smin987.zipper9`
3. **PR 내용**:
   - Flathub의 PR 템플릿 체크리스트를 확인하고 체크합니다.
   - **권한 설명 (Permission Justification)**:
     - `--filesystem=host`: Zipper9 is a file archiver utility. It requires broad filesystem access to allow users to open, extract, and compress files and directories located anywhere on their local storage.

---


### 💡 Flathub 제출 시 필수 준비사항 (ImageOptimizer 실전 경험 기반)

#### 1. 리눅스 구동 영상 첨부 필수 (.mp4)
- Flathub PR 체크리스트에는 **"Please attach a video showcasing the application on Linux using the Flatpak."** 항목이 필수입니다.
- **WSLg 15초 영상 제작 레시피**:
  1. Windows 11의 WSLg 터미널에서 리눅스 바이너리를 실행합니다:
     ```bash
     cd /tmp
     curl -sLO https://github.com/smin987/zipper9/releases/download/v1.0.1/zipper9-v1.0.1-linux-x86_64.tar.gz
     tar -xzf zipper9-v1.0.1-linux-x86_64.tar.gz
     cd zipper9-v1.0.1-linux-x86_64
     ./zipper9
     ```
  2. Windows 단축키 `Win + Shift + S` (동영상 녹화 모드)를 눌러 zipper9 화면의 파일 열기/압축 해제 동작을 10~15초간 간단히 녹화합니다 (`.mp4`).
  3. GitHub PR 본문 입력창에 해당 `.mp4` 파일을 드래그 앤 드롭하면 자동으로 업로드 영상 링크가 생성됩니다.

#### 2. 신규 프로젝트 유예 정책 (`too-new` 라벨) 대비
- Flathub는 일회성 토이 프로젝트 유입을 막기 위해 신규 저장소에 대해 `too-new` 라벨을 달고 1~2개월의 개발 이력 및 유지보수 증명을 요구할 수 있습니다 (실제 ImageOptimizer v1.1.3 PR #11329 사례).
- 혹시 `too-new` 라벨과 함께 PR이 닫히더라도 거절이 아니며, 1~2개월 동안 커밋과 릴리즈를 유지한 뒤 PR에 재검토(Revisit) 요청 댓글을 남기면 정상 승인 절차를 밟게 됩니다.

---

## 3. Flathub CI 빌드 봇 검증 및 심사 (Review Process)

1. **자동 빌드 검증 (`flathubbot`)**:
   - PR이 생성되면 Flathub의 `flathubbot`이 자동으로 x86_64 및 aarch64 아키텍처 빌드, AppStream 린트 검사를 실행하고 테스트 빌드 링크를 댓글로 제공합니다.
2. **리뷰어 피드백 대응**:
   - Flathub 관리자/리뷰어가 추가 요구사항이나 권한 관련 질문을 남길 경우 응답하고 브랜치에 추가 커밋을 푸시하면 자동 재빌드됩니다.
3. **승인 및 머지**:
   - 심사가 통과되면 관리자가 PR을 머지합니다.
   - 머지 즉시 Flathub 조직 하위에 독립 공식 저장소 **`https://github.com/flathub/io.github.smin987.zipper9`**가 자동 생성되고 개발자(`smin987`)에게 관리자 권한이 부여됩니다.

---

## 4. Flathub 개발자 공식 인증 (Developer Verification)

Flathub에서 **공식 인증 배지(Verified Badge)**를 획득하는 방법:

1. [https://flathub.org](https://flathub.org)에 접속하여 우측 상단에서 **GitHub 계정(`smin987`)**으로 로그인합니다.
2. **Developer Portal** (`My Apps`) 메뉴로 이동합니다.
3. `io.github.smin987.zipper9` 애플리케이션을 선택합니다.
4. **App Verification** 섹션에서 GitHub 계정 인증을 진행합니다:
   - App ID가 `io.github.smin987.zipper9` 형식이므로, `smin987` GitHub 계정과 연결되어 1클릭으로 즉시 **공식 개발자 인증 완료(Verified)** 처리됩니다.

---

## 5. 향후 버전 릴리즈 업데이트 워크플로우

새로운 버전(예: `v1.0.2`)이 릴리즈되면 다음 2가지 방법 중 하나로 Flathub를 간편하게 업데이트할 수 있습니다:

### 방법 A: 전용 저장소(`flathub/io.github.smin987.zipper9`)에 직접 커밋
1. `io.github.smin987.zipper9.yaml` 파일에서:
   - `url`의 버전 태그 변경 (`v1.0.1` ➔ `v1.0.2`)
   - `sha256` 해시값을 새 릴리즈 tar.gz의 해시로 갱신
2. `io.github.smin987.zipper9.metainfo.xml` 파일의 `<releases>` 태그 상단에 새 버전 릴리즈 노트 추가.
3. 변경사항을 `flathub/io.github.smin987.zipper9`의 `master` 브랜치에 푸시하면 Flathub 봇이 자동으로 빌드하여 수 시간 내에 전 세계 사용자에게 업데이트를 배포합니다.

### 방법 B: Flathub 봇 자동 업데이트 (Flatpak External Data Checker)
- Flathub 저장소에 `flathub.json` 또는 GitHub Release 모니터링 설정을 추가하면, GitHub Releases에 새 버전이 올라올 때 봇이 자동으로 PR을 생성하도록 구성할 수도 있습니다.
