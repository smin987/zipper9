"""zipper9 Main GUI Application - Commercial Grade Edition.
Modern, lightweight compression/decompression interface powered by CustomTkinter.
Supports:
- ZIP (Zstandard, Deflate, Store)
- 7-Zip (.7z) (LZMA2 Ultra)
- Linux TAR (.tar.gz, .tar.xz, .tar.bz2, .tar.lz4, .tar)
- Apple formats (.dmg, .pkg, .xip)
- RAR archives (.rar, RAR4/RAR5)
Smart Architecture:
- 100% Native Multi-Core C++ Engine (7z.exe -mmt=on) & Official C Pipeline (lz4.exe)
- Zero-Friction Auto-Switch between Compress & Extract on Drag & Drop
- Smart Bandizip-style Decompression: avoids redundant nested folders when single root folder exists
- Non-blocking OLE Drag & Drop via safe asynchronous mainloop scheduling
"""

import os
import re
import sys
import subprocess
import threading
import traceback
import multiprocessing
import webbrowser

# 프로젝트 루트 디렉터리를 sys.path에 추가 (탐색기 우클릭 등 외부 작업 디렉터리 실행 시 모듈 임포트 보장)
_app_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_app_dir)
if _root_dir not in sys.path:
    sys.path.insert(0, _root_dir)

try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
except ImportError:
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "필수 라이브러리 누락",
        "customtkinter가 설치되어 있지 않습니다.\n'pip install -r requirements.txt'를 실행해 주세요.",
    )
    sys.exit(1)

try:
    import windnd
    HAS_WINDND = True
except ImportError:
    HAS_WINDND = False

from zipper9_ui.bridge.worker import (
    CompressionWorker,
    is_native_engine_active,
    is_7z_available,
    is_lz4_available,
    list_archive_entries,
    SUPPORTED_EXTRACT_EXTS,
)
from zipper9_ui.bridge.context_menu import (
    register_context_menu,
    unregister_context_menu,
    is_context_menu_registered,
)
from zipper9_ui.bridge.file_association import (
    register_file_associations,
    unregister_file_associations,
    is_file_associations_registered,
)
from zipper9_ui.bridge.instant_ops import (
    run_instant_compress,
    run_instant_extract,
)
from zipper9_ui.bridge.settings import (
    load_settings,
    save_settings,
)
from zipper9_ui.bridge.i18n import (
    t,
    set_language,
    get_language,
    SUPPORTED_LANGUAGES,
)

APP_VERSION = "v1.0.0"
GITHUB_REPO_URL = "https://github.com/smin987/zipper9"


class ModernSegmentedButton(ctk.CTkSegmentedButton):
    """선택된 탭(파란색 배경)은 항상 선명한 흰색 글자(#ffffff),
    선택되지 않은 탭(회색 배경)은 가독성 높은 차콜(#495057)을 유지하는 확장 세그먼트 버튼"""

    def _create_buttons_from_values(self):
        super()._create_buttons_from_values()
        self._sync_button_text_colors()

    def _select_button_by_value(self, value: str):
        super()._select_button_by_value(value)
        self._sync_button_text_colors()

    def _unselect_button_by_value(self, value: str):
        super()._unselect_button_by_value(value)
        self._sync_button_text_colors()

    def set(self, value: str, *args, **kwargs):
        super().set(value, *args, **kwargs)
        self._sync_button_text_colors()

    def configure(self, **kwargs):
        super().configure(**kwargs)
        self._sync_button_text_colors()

    def _sync_button_text_colors(self):
        for val, btn in getattr(self, "_buttons_dict", {}).items():
            if val == self._current_value:
                btn.configure(text_color="#ffffff")
            else:
                btn.configure(text_color=("#495057", "#adb5bd"))


EXTRA_ALGO_KEYS = [
    "algo_extra_store",
    "algo_extra_tarxz",
    "algo_extra_tarbz2",
    "algo_extra_tar",
]

SPLIT_PRESET_KEYS = [
    "split_preset_none",
    "split_preset_10mb",
    "split_preset_25mb",
    "split_preset_100mb",
    "split_preset_500mb",
    "split_preset_1gb",
    "split_preset_2gb",
    "split_preset_4gb",
]


def format_bytes(size: float) -> str:
    """바이트 크기를 사람이 읽기 쉬운 단위로 변환"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


SPLIT_EXT_REGEX = re.compile(
    r"(\.(?:7z|zip|tar|rar|gz|xz|bz2|lz4|zst)\.\d{3}$)|"
    r"(\.\d{3}$)|"
    r"(\.part\d+\.rar$)|"
    r"(\.vol\d+(?:\+\d+)?\.egg$)|"
    r"(\.[za]\d{2,}$)|"
    r"(\.r\d{2,}$)",
    re.IGNORECASE,
)


def get_archive_folder_name(archive_path: str) -> str:
    """압축 파일명에서 분할 확장자 및 복합 확장자를 제거하여 해제 대상 기본 폴더명 반환"""
    base = os.path.basename(archive_path)

    # 1. 분할 압축 확장자 제거: .7z.001, .zip.001, .part1.rar, .vol1.egg, .z01, .001 등
    base = re.sub(r"\.(?:7z|zip|tar|rar|gz|xz|bz2|lz4|zst)\.\d{3}$", "", base, flags=re.IGNORECASE)
    base = re.sub(r"\.part\d+\.rar$", "", base, flags=re.IGNORECASE)
    base = re.sub(r"\.vol\d+(?:\+\d+)?\.egg$", "", base, flags=re.IGNORECASE)
    base = re.sub(r"\.\d{3}$", "", base)
    base = re.sub(r"\.[za]\d{2,}$", "", base, flags=re.IGNORECASE)
    base = re.sub(r"\.r\d{2,}$", "", base, flags=re.IGNORECASE)

    lower = base.lower()
    double_exts = [
        ".tar.gz",
        ".tar.xz",
        ".tar.bz2",
        ".tar.lz4",
        ".tar.zst",
        ".tgz",
        ".txz",
        ".tbz2",
    ]
    for de in double_exts:
        if lower.endswith(de):
            return base[: -len(de)]
    return os.path.splitext(base)[0]


def is_archive_file(path: str) -> bool:
    """주어진 파일 경로가 지원되는 압축 아카이브(분할 압축 포함) 파일인지 확인"""
    if not os.path.isfile(path):
        return False
    lower = path.lower()
    if any(lower.endswith(ext) for ext in SUPPORTED_EXTRACT_EXTS):
        return True
    if SPLIT_EXT_REGEX.search(lower):
        return True
    return False


def _find_first_volume_in_dir(path: str) -> str | None:
    """분할 압축 파일의 후속 볼륨(예: .002, .part2.rar, .z01)일 때 동일 디렉토리 내 1번 볼륨 자동 탐색"""
    directory = os.path.dirname(os.path.abspath(path))
    base = os.path.basename(path)

    # .002, .003 -> .001
    cand = re.sub(r"\.\d{3}$", ".001", base)
    if cand != base:
        p = os.path.join(directory, cand)
        if os.path.isfile(p):
            return p

    # .part2.rar -> .part1.rar 또는 .part01.rar
    if re.search(r"\.part\d+\.rar$", base, re.IGNORECASE):
        for pattern in [r"\.part0*1\.rar$", r"\.part1\.rar$"]:
            for f in os.listdir(directory):
                if re.search(pattern, f, re.IGNORECASE):
                    p_prefix = re.sub(r"\.part\d+\.rar$", "", base, flags=re.IGNORECASE)
                    f_prefix = re.sub(r"\.part\d+\.rar$", "", f, flags=re.IGNORECASE)
                    if p_prefix.lower() == f_prefix.lower():
                        return os.path.join(directory, f)

    # .z01, .z02 -> .zip
    if re.search(r"\.z\d{2,}$", base, re.IGNORECASE):
        zip_name = re.sub(r"\.z\d{2,}$", ".zip", base, flags=re.IGNORECASE)
        p = os.path.join(directory, zip_name)
        if os.path.isfile(p):
            return p

    # .a01, .a02 -> .alz
    if re.search(r"\.a\d{2,}$", base, re.IGNORECASE):
        alz_name = re.sub(r"\.a\d{2,}$", ".alz", base, flags=re.IGNORECASE)
        p = os.path.join(directory, alz_name)
        if os.path.isfile(p):
            return p

    # .r00, .r01 -> .rar
    if re.search(r"\.r\d{2,}$", base, re.IGNORECASE):
        rar_name = re.sub(r"\.r\d{2,}$", ".rar", base, flags=re.IGNORECASE)
        p = os.path.join(directory, rar_name)
        if os.path.isfile(p):
            return p

    return None


def find_primary_archive(paths: list[str]) -> str | None:
    """드롭되거나 전달된 파일 목록 중 해제할 최우선 아카이브 파일(분할 압축 1번 볼륨 우선) 지능적 선별"""
    archive_paths = [p for p in paths if is_archive_file(p)]
    if not archive_paths:
        return None

    # 1. 001 번호 볼륨 우선 (.7z.001, .zip.001, .001 등)
    vol1 = next(
        (p for p in archive_paths if re.search(r"(\.001|\.part0*1\.rar|\.vol0*1\.egg)$", p, re.IGNORECASE)),
        None,
    )
    if vol1:
        return vol1

    # 2. .zip이 포함되어 있는 경우 (.zip + .z01 분할 세트의 메인)
    zip_main = next((p for p in archive_paths if p.lower().endswith(".zip")), None)
    if zip_main:
        return zip_main

    # 3. .rar이 포함되어 있는 경우 (.rar + .r00 분할 세트의 메인)
    rar_main = next((p for p in archive_paths if p.lower().endswith(".rar")), None)
    if rar_main:
        return rar_main

    # 4. .alz 또는 .egg 메인
    alz_main = next((p for p in archive_paths if p.lower().endswith((".alz", ".egg"))), None)
    if alz_main:
        return alz_main

    # 5. 분할 압축의 후속 볼륨만 드롭된 경우, 같은 폴더에서 1번 볼륨 자동 탐색
    first_cand = archive_paths[0]
    first_vol_sibling = _find_first_volume_in_dir(first_cand)
    if first_vol_sibling and os.path.exists(first_vol_sibling):
        return first_vol_sibling

    return first_cand


def get_unique_filepath(target_dir: str, base_name: str, ext: str) -> str:
    """파일명 중복 시 (1), (2) 넘버링을 붙여 고유한 파일 경로 반환"""
    candidate = os.path.join(target_dir, f"{base_name}{ext}")
    if not os.path.exists(candidate):
        return candidate
    idx = 1
    while True:
        candidate = os.path.join(target_dir, f"{base_name} ({idx}){ext}")
        if not os.path.exists(candidate):
            return candidate
        idx += 1


def check_archive_has_single_root_folder(entries: list) -> tuple[bool, str | None]:
    """아카이브 내부가 '단일 최상위 폴더 1개'에 통으로 묶여있는지 판별.
    반환값: (is_single_root, root_folder_name)
    - True: 최상위가 단일 폴더 1개 -> 추가 폴더를 만들지 않고 현재 위치에 바로 해제 (이중 폴더 방지)
    - False: 최상위에 여러 파일/폴더가 공존 -> 파일명으로 폴더를 만들어서 해제
    """
    if not entries:
        return False, None

    root_items = set()
    has_root_file = False

    for e in entries:
        name = e.get("name", "").replace("\\", "/").strip("/")
        if not name:
            continue
        parts = name.split("/")
        # macOS 메타데이터 폴더나 특수 파일 제외
        if parts[0] in ("__MACOSX", ".DS_Store"):
            continue

        root_name = parts[0]
        root_items.add(root_name)

        # 루트 레벨에 바로 파일이 존재하는지 검사
        if len(parts) == 1 and not e.get("is_dir", False):
            has_root_file = True

    # 최상위 루트 항목이 정확히 1개이고, 그 항목이 루트 레벨 단독 파일이 아닌 폴더인 경우
    if len(root_items) == 1 and not has_root_file:
        single_folder = list(root_items)[0]
        return True, single_folder

    return False, None


def get_conflicting_extracted_files(entries: list, output_dir: str) -> list[str]:
    """해제 대상 디렉터리에 이미 존재하는 파일들의 목록을 반환합니다.
    - entries: 아카이브 내부 파일 정보 딕셔너리 리스트 (name, is_dir 등)
    - output_dir: 7z가 실제로 파일들을 풀어낼 최상위 대상 디렉터리
    """
    conflicts = []
    if not entries or not output_dir:
        return conflicts

    for e in entries:
        if e.get("is_dir", False):
            continue

        name = e.get("name", "").strip()
        if not name:
            continue

        # OS 표준 파일 경로 구분자로 치환
        rel_path = name.replace("/", os.sep).replace("\\", os.sep)
        full_path = os.path.join(output_dir, rel_path)

        if os.path.isfile(full_path):
            conflicts.append(full_path)

    return conflicts


def parse_split_size(text: str) -> str | None:
    """사용자 선택/입력 텍스트를 7z -v 옵션 규격(10m, 1g 등)으로 파싱"""
    if not text or "분할 안 함" in text or "no split" in text.lower():
        return None

    # '10 MB', '1 GB' 등에서 앞부분 숫자+단위 추출
    match = re.search(r"(\d+(?:\.\d+)?)\s*([mMgGkKbB])", text)
    if match:
        val = match.group(1)
        unit = match.group(2).lower()
        if "." in val:
            val_float = float(val)
            if unit == "g":
                return f"{int(val_float * 1024)}m"
            elif unit == "m":
                return f"{int(val_float * 1024)}k"
        return f"{int(float(val))}{unit}"

    # 단순히 숫자만 입력된 경우 MB로 기본 간주
    digits_match = re.match(r"^\s*(\d+)\s*$", text)
    if digits_match:
        return f"{digits_match.group(1)}m"

    return None


def get_file_type_badge(path: str) -> tuple[str, str]:
    """경로에 따른 (스마트 뱃지 텍스트, 컬러 코드) 반환"""
    if os.path.isdir(path):
        return "📁 폴더", "#f59f00"  # Pastel Amber Orange

    ext = os.path.splitext(path)[1].lower()

    # 문서 / 텍스트
    if ext in [
        ".txt", ".pdf", ".doc", ".docx", ".hwp", ".hwpx",
        ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".tsv", ".md"
    ]:
        return "📄 문서", "#20c997"  # Pastel Sage Mint

    # 코드 / 개발
    if ext in [
        ".py", ".rs", ".c", ".cpp", ".h", ".hpp", ".cs", ".java",
        ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".json",
        ".xml", ".yaml", ".yml", ".sql", ".sh", ".bat", ".ps1"
    ]:
        return "💻 코드", "#4dabf7"  # Pastel Sky Blue

    # 미디어 / 비디오 / 이미지 / 음악
    if ext in [
        ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".png", ".jpg",
        ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".mp3", ".wav",
        ".flac", ".aac", ".ogg"
    ]:
        return "🎬 미디어", "#9775fa"  # Pastel Soft Violet

    # 압축된 파일들 (별도 압축 아이콘 / 뱃지 표출)
    if ext in [
        ".zip", ".7z", ".rar", ".tar", ".gz", ".xz", ".bz2",
        ".lz4", ".zst", ".tgz", ".dmg", ".pkg", ".iso", ".alz", ".egg"
    ]:
        return "🗜️ 압축", "#ff922b"  # Pastel Coral Orange

    # 일반 바이너리 / 실행 파일
    if ext in [".exe", ".dll", ".bin", ".sys"]:
        return "📦 바이너리", "#4c6ef5"  # Pastel Indigo

    return "📄 파일", "#868e96"  # Pastel Soft Slate


class Zipper9App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 0. 마지막 사용자 설정값 로드
        self.user_settings = load_settings()
        self.settings_expanded = bool(self.user_settings.get("settings_expanded", False))
        self._settings_delta_h = 244

        # 0-1. 다국어(i18n) 설정 초기화
        self.current_lang = self.user_settings.get("lang", "KO")
        set_language(self.current_lang)

        # 1. 윈도우 기본 설정 (설정 접힘 시 760x580, 펼침 시 760x820 또는 저장된 마지막 크기)
        self.title(t("app_title"))
        default_geom = "760x820" if self.settings_expanded else "760x580"
        geom = self.user_settings.get("window_geometry", default_geom)
        
        # High-DPI 배율 중복 누적으로 지나치게 커진 과거 설정값 자동 정규화
        try:
            m = re.match(r"^(\d+)x(\d+)", str(geom))
            if m:
                w, h = int(m.group(1)), int(m.group(2))
                if w > 2560 or h > 1600 or w < 600 or h < 300:
                    geom = default_geom
                    self.user_settings["window_geometry"] = geom
            else:
                geom = default_geom
        except Exception:
            geom = default_geom

        self.geometry(geom)
        if self.settings_expanded:
            self.minsize(660, 700)
        else:
            self.minsize(660, 460)

        # 2. 테마 설정 (저장된 마지막 테마 모드)
        saved_theme = self.user_settings.get("theme", "Dark")
        ctk.set_appearance_mode(saved_theme)
        ctk.set_default_color_theme("blue")

        # 3. 비즈니스 로직 상태
        self.worker = CompressionWorker()
        self.selected_sources = []
        self.selected_archive_for_extract = ""
        self.archive_entries = []
        self.has_single_root_folder = False
        self.single_root_folder_name = None
        self.is_archive_encrypted = False
        self.active_tab = "compress"

        # 알고리즘 선택 상태 (저장된 마지막 알고리즘 복원)
        self.selected_algo = self.user_settings.get("selected_algo", "zstd")
        self.algo_cards = {}

        # 4. UI 빌드
        self._build_ui()
        self._refresh_ui_language()

        # 5. 종료 시 마지막 창 크기 및 상태 저장 이벤트 바인딩
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # 6. 윈도우 렌더링 후 드래그 앤 드롭 초기화
        self.after(150, self._setup_drag_and_drop)

    def _setup_drag_and_drop(self):
        # Windows 관리자 권한 UIPI 드래그 앤 드롭 차단 방어 (ChangeWindowMessageFilter)
        try:
            WM_DROPFILES = 0x0233
            WM_COPYDATA = 0x004A
            WM_COPYGLOBALDATA = 0x0049
            MSGFLT_ALLOW = 1
            for msg in [WM_DROPFILES, WM_COPYDATA, WM_COPYGLOBALDATA]:
                ctypes.windll.user32.ChangeWindowMessageFilter(msg, MSGFLT_ALLOW)
        except Exception:
            pass

        self.update_idletasks()

        if HAS_WINDND:
            try:
                windnd.hook_dropfiles(self, func=self._on_drop_files, force_unicode=True)
            except Exception as e:
                print(f"[경고] 드래그 앤 드롭 후킹 실패: {e}")

    def _on_drop_files(self, file_paths):
        """windnd C WndProc 콜백: 메인 GUI 스레드로 안전하게 비동기 스케줄링하여
        Windows OLE 데드락 및 크래시(Crash)를 원천 차단함."""
        try:
            if not file_paths:
                return

            normalized_paths = []
            for p in file_paths:
                if isinstance(p, bytes):
                    try:
                        p = p.decode("utf-8")
                    except UnicodeDecodeError:
                        p = p.decode("mbcs", errors="replace")
                p = os.path.normpath(str(p))
                if os.path.exists(p):
                    normalized_paths.append(p)

            if normalized_paths:
                self.after(10, lambda paths=normalized_paths: self._handle_drop_files_safe(paths))
        except Exception as e:
            print(f"[드래그 드롭 후킹 에러 방어]: {e}")

    def _handle_drop_files_safe(self, normalized_paths: list[str]):
        """Tkinter 메인 스레드에서 안전하게 실행되는 파일 처리기"""
        try:
            if not normalized_paths:
                return

            current_tab = self.active_tab
            lang = getattr(self, "current_lang", "KO")

            # 드롭된 항목 중 압축 파일(분할 압축 세트 포함) 식별 및 일반 파일 유무 파악
            archive_found = find_primary_archive(normalized_paths)
            has_non_archive_in_drop = any(not is_archive_file(p) for p in normalized_paths)
            has_existing_sources = bool(self.selected_sources)

            # [스마트 압축해제 화면 자동 전환 조건]:
            # 1) 이미 압축하기 목록에 등록된 파일이 전혀 없고,
            # 2) 이번에 드롭된 항목에도 일반(비압축) 파일/폴더가 전혀 없으며,
            # 3) 압축 파일(아카이브)만 순수하게 드롭된 경우에만 압축해제 화면으로 전환!
            should_extract = (
                archive_found is not None
                and not has_existing_sources
                and not has_non_archive_in_drop
            )

            if should_extract:
                switched = (current_tab == "compress")
                if switched:
                    self.set_active_tab("extract")
                self._load_archive_for_extract(archive_found)
                if switched:
                    self.lbl_status.configure(
                        text=t("status_archive_detected", lang=lang, name=os.path.basename(archive_found))
                    )
                return

            # [압축하기 패키징 등록]:
            # - 기존에 일반 파일이 이미 등록되어 있거나,
            # - 이번에 일반 파일과 압축 파일이 함께 들어왔거나,
            # - 일반 파일만 들어온 경우
            # -> 모든 파일(압축 파일 포함)을 압축 대상 목록(selected_sources)에 추가하여 함께 패키징 압축!
            switched = (current_tab == "extract")
            if switched:
                self.set_active_tab("compress")

            added_count = 0
            for p in normalized_paths:
                if p not in self.selected_sources:
                    self.selected_sources.append(p)
                    added_count += 1

            if added_count > 0:
                self._update_sources_view()
                if switched:
                    self.lbl_status.configure(
                        text=t("status_files_detected", lang=lang, count=added_count)
                    )
                else:
                    self.lbl_status.configure(
                        text=t("status_files_added", lang=lang, count=added_count)
                    )
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror(t("dialog_error"), t("err_load_files_failed", err=e))

    # =========================================================================
    # UI 생성부
    # =========================================================================
    def _build_ui(self):
        # 0. 윈도우 배경색 설정 (일반 모드: 포근한 소프트 파스텔 화이트 / 다크 모드: 딥 다크)
        self.configure(fg_color=("#f5f6fa", "#16181b"))

        # 1. 최상단 헤더
        self._build_header()

        # 2. 세그먼트 네비게이션 컨트롤 (알약형 듀얼 스위처)
        self._build_navigation()

        # 3. 메인 컨텐츠 영역 (압축 페이지 / 해제 페이지)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(4, 6))

        self.page_compress = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.page_extract = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        self._setup_compress_page()
        self._setup_extract_page()

        # 초기 탭 활성화: 압축 페이지
        self.page_compress.pack(fill="both", expand=True)

        # 4. 하단 슬림 프로그레스 바 & 상태 바
        self._setup_progress_bar()

    def _build_header(self):
        header_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        header_container.pack(fill="x", padx=20, pady=(12, 2))

        # 1행: 로고 & 타이틀 + CPU 코어 라벨 | (제일 위 오른쪽) 다국어 스위처
        row1 = ctk.CTkFrame(header_container, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 2))

        title_box = ctk.CTkFrame(row1, fg_color="transparent")
        title_box.pack(side="left")

        title_label = ctk.CTkLabel(
            title_box,
            text="⚡ zipper9",
            font=ctk.CTkFont(size=23, weight="bold"),
            text_color=("#212529", "#ffffff"),
        )
        title_label.pack(side="left", padx=(0, 6))

        # 버전 표시 뱃지 (파란색 버튼배경 + 흰색 글자, 클릭 시 GitHub 저장소로 이동)
        self.btn_version = ctk.CTkButton(
            title_box,
            text=APP_VERSION,
            width=52,
            height=20,
            corner_radius=10,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#4dabf7", "#1c7ed6"),
            hover_color=("#339af0", "#1864ab"),
            text_color="#ffffff",
            cursor="hand2",
            command=self._open_github_repo,
        )
        self.btn_version.pack(side="left", padx=(0, 10), pady=(3, 0))

        # Native C++ 엔진 텍스트 (파스텔 톤)
        cores = multiprocessing.cpu_count() or 16
        is_native = is_native_engine_active()
        core_key = "core_native" if is_native else "core_python"
        core_text = t(core_key, cores=cores)
        core_color = "#20c997" if is_native else "#f59f00"

        self.core_label = ctk.CTkLabel(
            row1,
            text=core_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=core_color,
        )
        self.core_label.pack(side="left", padx=(4, 0), pady=4)

        # 다국어 (한글 / EN) 알약형 세그먼트 전환 스위처 (선택 시 파란색 배경 + 흰색 글자)
        self.lang_segmented = ModernSegmentedButton(
            row1,
            values=["한글", "EN"],
            command=self._on_language_change,
            width=76,
            height=26,
            font=ctk.CTkFont(size=11, weight="bold"),
            selected_color="#4dabf7",
            selected_hover_color="#339af0",
            unselected_color=("#e9ecef", "#2c3036"),
            unselected_hover_color=("#dee2e6", "#3a3f47"),
        )
        disp_lang = "한글" if self.current_lang == "KO" else "EN"
        self.lang_segmented.set(disp_lang)
        self.lang_segmented.pack(side="right")

        # 후원하기 버튼 (한/영 전환 스위처 바로 옆 - 포근한 파스텔 벚꽃 핑크)
        self.btn_sponsor = ctk.CTkButton(
            row1,
            text=t("btn_sponsor"),
            command=self._open_sponsor_link,
            width=84,
            height=26,
            corner_radius=13,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#f783ac",
            hover_color="#e64980",
            text_color="#ffffff",
        )
        self.btn_sponsor.pack(side="right", padx=(0, 8))

        # 2행: 마우스 우클릭 설정 & 압축 아이콘 설정 & 다크모드 설정 (줄 바꿈된 2단 좌측 정렬)
        row2 = ctk.CTkFrame(header_container, fg_color="transparent")
        row2.pack(fill="x", pady=(2, 2))

        # 마우스 우클릭 메뉴 활성화 토글 스위치 (왼쪽 첫 번째)
        self.context_menu_switch = ctk.CTkSwitch(
            row2,
            text=t("context_menu_toggle"),
            command=self._toggle_context_menu,
            font=ctk.CTkFont(size=12),
            progress_color="#4dabf7",
            text_color=("#495057", "#f1f5f9"),
        )
        if is_context_menu_registered():
            self.context_menu_switch.select()
            # 기존 우클릭 메뉴가 켜져 있던 경우 새 바이너리/위치로 자동 경로 동기화
            threading.Thread(target=register_context_menu, daemon=True).start()
        else:
            self.context_menu_switch.deselect()
        self.context_menu_switch.pack(side="left", padx=(0, 16))

        # 압축 파일 아이콘 표시 토글 스위치 (왼쪽 두 번째)
        self.archive_icon_switch = ctk.CTkSwitch(
            row2,
            text=t("archive_icon_toggle"),
            command=self._toggle_archive_icon,
            font=ctk.CTkFont(size=12),
            progress_color="#4dabf7",
            text_color=("#495057", "#f1f5f9"),
        )
        if is_file_associations_registered():
            self.archive_icon_switch.select()
        else:
            self.archive_icon_switch.deselect()
        self.archive_icon_switch.pack(side="left", padx=(0, 16))

        # 테마 토글 스위치 (다크 모드 - 왼쪽 세 번째)
        self.theme_switch = ctk.CTkSwitch(
            row2,
            text=t("dark_mode"),
            command=self._toggle_theme,
            onvalue="Dark",
            offvalue="Light",
            font=ctk.CTkFont(size=12),
            progress_color="#4dabf7",
            text_color=("#495057", "#f1f5f9"),
        )
        if self.user_settings.get("theme", "Dark") == "Dark":
            self.theme_switch.select()
        else:
            self.theme_switch.deselect()
        self.theme_switch.pack(side="left")

    def _build_navigation(self):
        """알약형 모던 세그먼트 버튼 네비게이션"""
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=(2, 8))

        self.nav_segmented = ModernSegmentedButton(
            nav_frame,
            values=[t("nav_compress"), t("nav_extract")],
            command=self._on_nav_change,
            height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            selected_color="#4dabf7",
            selected_hover_color="#339af0",
            unselected_color=("#e9ecef", "#2c3036"),
            unselected_hover_color=("#dee2e6", "#3a3f47"),
        )
        self.nav_segmented.set(t("nav_compress"))
        self.nav_segmented.pack(fill="x")

    def _on_nav_change(self, value):
        if "Extract" in value or "압축해제" in value:
            self.set_active_tab("extract")
        else:
            self.set_active_tab("compress")

    def set_active_tab(self, tab_name: str):
        """탭 전환 (화면 전환 및 세그먼트 버튼 동기화)"""
        self.active_tab = tab_name
        if tab_name == "compress":
            self.page_extract.pack_forget()
            self.page_compress.pack(fill="both", expand=True)
            self.nav_segmented.set(t("nav_compress"))
        else:
            self.page_compress.pack_forget()
            self.page_extract.pack(fill="both", expand=True)
            self.nav_segmented.set(t("nav_extract"))

    # =========================================================================
    # 압축 탭 (Compress Page)
    # =========================================================================
    def _setup_compress_page(self):
        # 1. 상단 액션 바 (대상 경로 안내 & 위치지정 / 압축하기 버튼)
        action_bar = ctk.CTkFrame(
            self.page_compress,
            corner_radius=8,
            fg_color=("#ffffff", "#1e2024"),
            border_width=1,
            border_color=("#e9ecef", "#2c2e35"),
        )
        action_bar.pack(fill="x", padx=0, pady=(2, 6))

        # IMPORTANT: pack(side="right")를 먼저 배치하여 창 크기가 줄어들어도
        # 우측 액션 버튼(위치지정, 압축하기)이 절대 가려지거나 밀려나지 않도록 고정
        btn_box = ctk.CTkFrame(action_bar, fg_color="transparent")
        btn_box.pack(side="right", padx=10, pady=8)

        # 좌측: 위치 지정(보조), 우측: 메인 압축 실행
        self.btn_compress_custom_loc = ctk.CTkButton(
            btn_box,
            text=t("btn_browse_target"),
            width=85,
            height=34,
            fg_color=("#f1f3f9", "#373a40"),
            hover_color=("#e5e8f0", "#4a4d55"),
            text_color=("#495057", "#ffffff"),
            border_width=1,
            border_color=("#dce2ee", "#4a4d55"),
            font=ctk.CTkFont(size=12),
            command=lambda: self._start_compression(force_prompt=True),
        )
        self.btn_compress_custom_loc.pack(side="left", padx=4)

        self.btn_compress_start = ctk.CTkButton(
            btn_box,
            text=t("btn_compress_start"),
            width=110,
            height=34,
            fg_color="#4dabf7",
            hover_color="#339af0",
            text_color="#ffffff",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self._start_compression(force_prompt=False),
        )
        self.btn_compress_start.pack(side="left", padx=4)

        # 좌측: 대상 경로 안내 라벨 (남은 공간을 모두 차지하도록 expand)
        self.lbl_compress_target_info = ctk.CTkLabel(
            action_bar,
            text=f"{t('label_target')} {t('target_placeholder')}",
            font=ctk.CTkFont(size=12),
            text_color=("#6c757d", "gray75"),
            anchor="w",
        )
        self.lbl_compress_target_info.pack(side="left", padx=(14, 6), pady=8, fill="x", expand=True)

        # 2. 파일 스크롤 리스트 (드래그 & 드롭 영역)
        self.source_scroll_frame = ctk.CTkScrollableFrame(
            self.page_compress,
            height=200,
            corner_radius=8,
            fg_color=("#ffffff", "#191a1d"),
            border_width=1,
            border_color=("#e9ecef", "#2c2e35"),
        )
        self.source_scroll_frame.pack(fill="both", expand=True, padx=0, pady=(2, 6))

        # 3. 드래그 & 드롭 영역 하단 툴바 ([파일 추가] [폴더 추가] [전체 비우기] / 파일 요약)
        toolbar = ctk.CTkFrame(self.page_compress, fg_color="transparent")
        toolbar.pack(fill="x", padx=0, pady=(2, 6))

        self.btn_add_file = ctk.CTkButton(
            toolbar,
            text=t("btn_add_files"),
            width=100,
            height=32,
            fg_color=("#74c0fc", "#1f6aa5"),
            hover_color=("#4dabf7", "#144870"),
            text_color="#ffffff",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._add_files,
        )
        self.btn_add_file.pack(side="left", padx=(0, 6))

        self.btn_add_dir = ctk.CTkButton(
            toolbar,
            text=t("btn_add_folder"),
            width=100,
            height=32,
            fg_color=("#74c0fc", "#1f6aa5"),
            hover_color=("#4dabf7", "#144870"),
            text_color="#ffffff",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._add_directory,
        )
        self.btn_add_dir.pack(side="left", padx=6)

        self.btn_clear = ctk.CTkButton(
            toolbar,
            text=t("btn_clear_all"),
            width=90,
            height=32,
            fg_color=("#ffe3e3", "#803030"),
            hover_color=("#ffc9c9", "#a83232"),
            text_color=("#e03131", "#ffffff"),
            border_width=1,
            border_color=("#ffa8a8", "#803030"),
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._clear_sources,
        )
        self.btn_clear.pack(side="left", padx=6)

        self.lbl_sources_summary = ctk.CTkLabel(
            toolbar,
            text="항목: 0개 (0.0 B)",
            text_color=("#6c757d", "gray"),
            font=ctk.CTkFont(size=12),
        )
        self.lbl_sources_summary.pack(side="right", padx=6)

        # 초기 드롭 뷰 갱신
        self._update_sources_view()

        # 4. 설정(Settings) 아코디언 토글 바
        self._build_settings_toggle_bar()

        # 5. 설정(Settings) 하위 접이식 컨테이너 (알고리즘 프리셋 전체 + 보안 비밀번호 + 분할 압축 + 7z 파일명 암호화)
        self.settings_container = ctk.CTkFrame(self.page_compress, fg_color="transparent")
        self._build_algo_card_selector(parent=self.settings_container)
        self._build_advanced_options(parent=self.settings_container)

        if self.settings_expanded:
            self.settings_container.pack(fill="x", padx=0, pady=(0, 2))
        self._update_settings_toggle_ui()

    def _map_extra_algo_text(self, text: str, target_lang: str) -> str:
        """언어 전환 시 추가 알고리즘 드롭다운 텍스트를 대상 언어로 매핑"""
        if not text or "선택" in text or "Choose" in text:
            return t("algo_extra_placeholder", lang=target_lang)
        for k in EXTRA_ALGO_KEYS:
            if text == t(k, lang="KO") or text == t(k, lang="EN"):
                return t(k, lang=target_lang)
            if "Store" in text and "store" in k:
                return t(k, lang=target_lang)
            if ".tar.xz" in text and "tarxz" in k:
                return t(k, lang=target_lang)
            if ".tar.bz2" in text and "tarbz2" in k:
                return t(k, lang=target_lang)
            if (".tar " in text or text.endswith(".tar") or "무압축 Tarball" in text or "Uncompressed" in text) and k == "algo_extra_tar":
                return t(k, lang=target_lang)
        return text

    def _map_split_preset_text(self, text: str, target_lang: str) -> str:
        """언어 전환 시 분할 압축 드롭다운 텍스트를 대상 언어로 매핑"""
        if not text or "분할 안 함" in text or "No Splitting" in text:
            return t("split_preset_none", lang=target_lang)
        for k in SPLIT_PRESET_KEYS:
            if text == t(k, lang="KO") or text == t(k, lang="EN"):
                return t(k, lang=target_lang)
            if "10 MB" in text and "10mb" in k:
                return t(k, lang=target_lang)
            if "25 MB" in text and "25mb" in k:
                return t(k, lang=target_lang)
            if "100 MB" in text and "100mb" in k:
                return t(k, lang=target_lang)
            if "500 MB" in text and "500mb" in k:
                return t(k, lang=target_lang)
            if "1 GB" in text and "1gb" in k:
                return t(k, lang=target_lang)
            if "2 GB" in text and "2gb" in k:
                return t(k, lang=target_lang)
            if "4 GB" in text and "4gb" in k:
                return t(k, lang=target_lang)
        return text

    def _build_settings_toggle_bar(self):
        """설정(Settings) 아코디언 토글 바"""
        lang = getattr(self, "current_lang", "KO")
        bar = ctk.CTkFrame(
            self.page_compress,
            corner_radius=8,
            fg_color=("#ffffff", "#1e2024"),
            border_width=1,
            border_color=("#e9ecef", "#2c2e35"),
            height=34,
            cursor="hand2",
        )
        bar.pack(fill="x", padx=0, pady=(3, 3))
        self.settings_toggle_bar = bar

        # 좌측: 화살표 기호 + 압축 상세 설정 제목 라벨 (동그라미 기호 없음)
        title_key = "settings_title_expanded" if self.settings_expanded else "settings_title_collapsed"
        self.lbl_settings_toggle_title = ctk.CTkLabel(
            bar,
            text=t(title_key, lang=lang),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#212529", "gray90"),
            cursor="hand2",
        )
        self.lbl_settings_toggle_title.pack(side="left", padx=(12, 8), pady=6)

        # 우측: 접혀 있을 때 현재 설정 요약 배지 표출
        self.lbl_settings_summary_badge = ctk.CTkLabel(
            bar,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("#1971c2", "#74c0fc"),
            cursor="hand2",
        )
        self.lbl_settings_summary_badge.pack(side="right", padx=(4, 12), pady=6)

        # 마우스 클릭 토글 바인딩
        for widget in [bar, self.lbl_settings_toggle_title, self.lbl_settings_summary_badge]:
            widget.bind("<Button-1>", lambda e: self._toggle_settings_panel())

        # 마우스 호버 효과
        def _on_enter(e):
            bar.configure(fg_color=("#f1f3f9", "#262930"))
        def _on_leave(e):
            bar.configure(fg_color=("#ffffff", "#1e2024"))

        bar.bind("<Enter>", _on_enter)
        bar.bind("<Leave>", _on_leave)
        self.lbl_settings_toggle_title.bind("<Enter>", _on_enter)
        self.lbl_settings_toggle_title.bind("<Leave>", _on_leave)
        self.lbl_settings_summary_badge.bind("<Enter>", _on_enter)
        self.lbl_settings_summary_badge.bind("<Leave>", _on_leave)

    def _toggle_settings_panel(self):
        """설정 아코디언 패널 접기/펼치기 토글 (창 하단 크기 동적 조절 - B안)"""
        self.settings_expanded = not self.settings_expanded
        self.user_settings["settings_expanded"] = self.settings_expanded

        # 윈도우 스케일 배율 및 현재 geometry 파싱
        scale = ctk.ScalingTracker.get_window_scaling(self) or 1.0
        geom_str = str(self.geometry())
        m = re.match(r"^(\d+)x(\d+)(?:([+-]\d+))?(?:([+-]\d+))?", geom_str)
        cur_w = int(m.group(1)) if m else 760
        cur_h = int(m.group(2)) if m else (820 if self.settings_expanded else 580)
        pos_x = m.group(3) if (m and m.group(3)) else ""
        pos_y = m.group(4) if (m and m.group(4)) else ""

        if self.settings_expanded:
            # [펼치기]: 하단으로 창 높이 확장 및 설정 컨테이너 표출
            delta_h = getattr(self, "_settings_delta_h", 244)
            if delta_h < 150:
                delta_h = 244
            self.minsize(660, 700)
            new_h = cur_h + delta_h
            if pos_x and pos_y:
                self.geometry(f"{cur_w}x{new_h}{pos_x}{pos_y}")
            else:
                self.geometry(f"{cur_w}x{new_h}")
            self.settings_container.pack(fill="x", padx=0, pady=(0, 2))
        else:
            # [접기]: 설정 컨테이너 높이 측정 후 숨김 및 하단 창 높이 축소
            measured_h = int(self.settings_container.winfo_height() / scale)
            if measured_h < 150:
                measured_h = int(self.settings_container.winfo_reqheight() / scale)
            if measured_h >= 150:
                self._settings_delta_h = measured_h
            else:
                self._settings_delta_h = 244

            delta_h = self._settings_delta_h
            self.settings_container.pack_forget()
            self.minsize(660, 460)
            new_h = max(460, cur_h - delta_h)
            if pos_x and pos_y:
                self.geometry(f"{cur_w}x{new_h}{pos_x}{pos_y}")
            else:
                self.geometry(f"{cur_w}x{new_h}")

        self._update_settings_toggle_ui()
        self.update_idletasks()
        self.user_settings["window_geometry"] = f"{cur_w}x{new_h}"
        self.save_current_settings()

    def _update_settings_toggle_ui(self):
        """설정 토글 바 제목 및 요약 뱃지 갱신"""
        lang = getattr(self, "current_lang", "KO")
        if not hasattr(self, "lbl_settings_toggle_title"):
            return

        title_key = "settings_title_expanded" if self.settings_expanded else "settings_title_collapsed"
        self.lbl_settings_toggle_title.configure(text=t(title_key, lang=lang))

        if self.settings_expanded:
            if hasattr(self, "lbl_settings_summary_badge"):
                self.lbl_settings_summary_badge.configure(text="")
        else:
            self._update_settings_summary_badge()

    def _update_settings_summary_badge(self):
        """설정 패널이 접혀 있을 때 현재 설정 요약 배지 텍스트 갱신"""
        if not hasattr(self, "lbl_settings_summary_badge") or self.settings_expanded:
            return

        lang = getattr(self, "current_lang", "KO")
        algo_names = {
            "zstd": "ZIP (Zstandard)",
            "7z": "7z (LZMA2)",
            "lz4": "TAR (LZ4)",
            "targz": "TAR (Gzip)",
        }
        algo_disp = algo_names.get(self.selected_algo, "ZIP")
        if self.selected_algo == "extra" and hasattr(self, "combo_extra_algo"):
            extra_val = self.combo_extra_algo.get()
            if "Store" in extra_val:
                algo_disp = "ZIP (Store)"
            elif ".tar.xz" in extra_val:
                algo_disp = "TAR (.tar.xz)"
            elif ".tar.bz2" in extra_val:
                algo_disp = "TAR (.tar.bz2)"
            elif ".tar" in extra_val:
                algo_disp = "TAR (.tar)"

        tags = [f"[ 📦 {algo_disp} ]"]

        # 비밀번호 설정 여부
        if hasattr(self, "entry_password"):
            pwd = self.entry_password.get().strip()
            if pwd:
                tags.append("🔒 " + ("Encrypted" if lang == "EN" else "암호 설정됨"))

        # 분할 압축 설정 여부
        if hasattr(self, "combo_split"):
            split = self.combo_split.get()
            if split and not any(k in split for k in ["분할 안 함", "No Split", "None"]):
                clean_split = split.split("(")[0].strip()
                tags.append(f"✂️ {clean_split}")

        # 7z 헤더 암호화 여부
        if hasattr(self, "chk_encrypt_header") and self.chk_encrypt_header.get():
            tags.append("🛡️ " + ("Header Encrypted" if lang == "EN" else "헤더 암호화"))

        self.lbl_settings_summary_badge.configure(text="  ".join(tags))

    def _build_algo_card_selector(self, parent=None):
        """4개의 세련된 가로형 알고리즘 카드 선택기"""
        container_parent = parent if parent is not None else self.page_compress
        algo_container = ctk.CTkFrame(container_parent, fg_color="transparent")
        algo_container.pack(fill="x", padx=0, pady=(2, 4))

        # 섹션 라벨 + 추가 포맷 드롭다운
        top_line = ctk.CTkFrame(algo_container, fg_color="transparent")
        top_line.pack(fill="x", pady=(0, 4))

        sec_title = ctk.CTkLabel(
            top_line,
            text="Compression Presets" if self.current_lang == "EN" else "압축 알고리즘 프리셋",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#212529", "gray85"),
        )
        sec_title.pack(side="left")
        self.lbl_algo_preset_title = sec_title

        # 보조 드롭다운 (상세 포맷용, 우측 끝 배치)
        lang = getattr(self, "current_lang", "KO")
        extra_values = [t(k, lang=lang) for k in EXTRA_ALGO_KEYS]
        self.combo_extra_algo = ctk.CTkComboBox(
            top_line,
            values=extra_values,
            width=245,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=("#ffffff", "#2a2d34"),
            border_color=("#dee2e6", "#3a3f47"),
            text_color=("#212529", "#f1f5f9"),
            command=self._on_extra_algo_selected,
        )
        saved_extra = self.user_settings.get("extra_algo", t("algo_extra_placeholder", lang=lang))
        self.combo_extra_algo.set(self._map_extra_algo_text(saved_extra, lang))
        self.combo_extra_algo.pack(side="right")

        # 압축 후 무결성 검사 체크박스 (셀렉트 박스 바로 왼쪽 옆에 나란히 배치)
        self.chk_verify_integrity = ctk.CTkCheckBox(
            top_line,
            text=t("chk_verify_integrity"),
            font=ctk.CTkFont(size=11),
            width=20,
            checkbox_width=18,
            checkbox_height=18,
            text_color=("#495057", "gray85"),
            checkmark_color="#ffffff",
            fg_color="#4dabf7",
            command=self.save_current_settings,
        )
        if self.user_settings.get("verify_integrity", False):
            self.chk_verify_integrity.select()
        else:
            self.chk_verify_integrity.deselect()
        self.chk_verify_integrity.pack(side="right", padx=(0, 14))

        # 4개 카드 그리드
        cards_grid = ctk.CTkFrame(algo_container, fg_color="transparent")
        cards_grid.pack(fill="x")
        for i in range(4):
            cards_grid.grid_columnconfigure(i, weight=1)

        speed_lbl = "Speed:" if lang == "EN" else "속도:"
        ratio_lbl = "Ratio:" if lang == "EN" else "압축:"

        card_defs = [
            {
                "key": "zstd",
                "fmt": "📦 ZIP",
                "algo": "Zstandard",
                "sub": "Modern Balanced" if lang == "EN" else "현대 표준 올인원",
                "speed": f"{speed_lbl} ★★★★★",
                "ratio": f"{ratio_lbl} ★★★★☆",
            },
            {
                "key": "7z",
                "fmt": "🗜️ 7z",
                "algo": "LZMA2",
                "sub": "Ultra High Ratio" if lang == "EN" else "초고압축",
                "speed": f"{speed_lbl} ★★★☆☆",
                "ratio": f"{ratio_lbl} ★★★★★",
            },
            {
                "key": "lz4",
                "fmt": "⚡ TAR",
                "algo": "LZ4 Ultra",
                "sub": "500MB/s+ Lightning" if lang == "EN" else "초당 500MB+ 번개",
                "speed": f"{speed_lbl} ★★★★★★",
                "ratio": f"{ratio_lbl} ★★☆☆☆",
            },
            {
                "key": "targz",
                "fmt": "🌐 TAR",
                "algo": "Gzip (.tar.gz)",
                "sub": "Unix/Linux/Mac Standard" if lang == "EN" else "유닉스/리눅스/맥 표준",
                "speed": f"{speed_lbl} ★★★★☆",
                "ratio": f"{ratio_lbl} ★★★☆☆",
            },
        ]

        self.algo_cards = {}
        for idx, item in enumerate(card_defs):
            key = item["key"]
            card_frame = ctk.CTkFrame(
                cards_grid,
                corner_radius=8,
                fg_color=("#ffffff", "#1e2024"),
                border_width=1.5,
                border_color=("#e9ecef", "#2c2e35"),
                cursor="hand2",
            )
            card_frame.grid(row=0, column=idx, padx=3, pady=2, sticky="nsew")

            # 1. 윗줄: 포맷 (ZIP, TAR, 7z)
            lbl_fmt = ctk.CTkLabel(
                card_frame,
                text=item["fmt"],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#4c6ef5", "#748ffc"),
            )
            lbl_fmt.pack(anchor="w", padx=10, pady=(6, 0))

            # 2. 줄바꿈 다음줄: 압축 알고리즘 이름
            lbl_algo = ctk.CTkLabel(
                card_frame,
                text=item["algo"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=("#212529", "#f1f5f9"),
            )
            lbl_algo.pack(anchor="w", padx=10, pady=(0, 2))

            # 3. 설명문 (반디집 단어 제거 -> '초고압축')
            lbl_sub = ctk.CTkLabel(
                card_frame,
                text=item["sub"],
                font=ctk.CTkFont(size=10),
                text_color=("#868e96", "gray"),
            )
            lbl_sub.pack(anchor="w", padx=10, pady=(0, 2))

            # 4. 속도/압축률 게이지 (줄바꿈 적용)
            lbl_stats = ctk.CTkLabel(
                card_frame,
                text=f"{item['speed']}\n{item['ratio']}",
                font=ctk.CTkFont(size=9),
                text_color=("#495057", "gray70"),
                justify="left",
            )
            lbl_stats.pack(anchor="w", padx=10, pady=(0, 6))

            # 클릭 이벤트 바인딩
            for widget in (card_frame, lbl_fmt, lbl_algo, lbl_sub, lbl_stats):
                widget.bind("<Button-1>", lambda e, k=key: self._select_algo_card(k))

            self.algo_cards[key] = {
                "frame": card_frame,
                "fmt": lbl_fmt,
                "algo": lbl_algo,
                "sub": lbl_sub,
                "stats": lbl_stats,
            }

        self._refresh_algo_card_styles()

    def _select_algo_card(self, key: str):
        if key != "7z" and hasattr(self, "chk_encrypt_header") and self.chk_encrypt_header.get():
            self.chk_encrypt_header.deselect()
            if hasattr(self, "user_settings"):
                self.user_settings["encrypt_filenames"] = False
            messagebox.showinfo(t("dialog_info"), t("msg_encrypt_header_only_7z"))

        self.selected_algo = key
        self.combo_extra_algo.set(t("algo_extra_placeholder"))
        self._refresh_algo_card_styles()
        self.save_current_settings()
        self._update_settings_summary_badge()

    def _on_extra_algo_selected(self, choice: str):
        if hasattr(self, "chk_encrypt_header") and self.chk_encrypt_header.get():
            self.chk_encrypt_header.deselect()
            if hasattr(self, "user_settings"):
                self.user_settings["encrypt_filenames"] = False
            messagebox.showinfo(t("dialog_info"), t("msg_encrypt_header_only_7z"))

        self.selected_algo = "extra"
        self._refresh_algo_card_styles()
        self.save_current_settings()
        self._update_settings_summary_badge()

    def _on_encrypt_header_toggle(self):
        """7z 파일명 암호화 체크 토글 핸들러: 체크 시 자동으로 7z 알고리즘 선택"""
        is_checked = bool(self.chk_encrypt_header.get())
        if is_checked:
            if self.selected_algo != "7z":
                self.selected_algo = "7z"
                if hasattr(self, "combo_extra_algo"):
                    self.combo_extra_algo.set(t("algo_extra_placeholder"))
                self._refresh_algo_card_styles()
                if hasattr(self, "lbl_status"):
                    self.lbl_status.configure(text=t("status_auto_selected_7z"))
        self.save_current_settings()
        self._update_settings_summary_badge()

    def _refresh_algo_card_styles(self):
        for key, widgets in self.algo_cards.items():
            frame = widgets["frame"]
            if key == self.selected_algo:
                frame.configure(
                    border_color="#4dabf7",
                    fg_color=("#e7f5ff", "#252b36"),
                )
            else:
                frame.configure(
                    border_color=("#e9ecef", "#2c2e35"),
                    fg_color=("#ffffff", "#1e2024"),
                )

    def _build_advanced_options(self, parent=None):
        """암호 설정 및 분할 압축 고급 옵션 프레임 (2단 줄바꿈 레이아웃)"""
        container_parent = parent if parent is not None else self.page_compress
        opt_box = ctk.CTkFrame(
            container_parent,
            corner_radius=8,
            fg_color=("#ffffff", "#1e2024"),
            border_width=1,
            border_color=("#e9ecef", "#2c2e35"),
        )
        opt_box.pack(fill="x", padx=0, pady=(2, 4))

        # 1행: 암호 설정 영역
        row1 = ctk.CTkFrame(opt_box, fg_color="transparent")
        row1.pack(fill="x", padx=12, pady=(6, 3))

        self.lbl_pwd_title = ctk.CTkLabel(
            row1,
            text=f"🔒 {t('label_password')}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#212529", "gray85"),
        )
        self.lbl_pwd_title.pack(side="left", padx=(0, 6))

        self.entry_password = ctk.CTkEntry(
            row1,
            placeholder_text=t("placeholder_password"),
            show="*",
            width=150,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=("#ffffff", "#2a2d34"),
            border_color=("#dee2e6", "#3a3f47"),
            text_color=("#212529", "#f1f5f9"),
        )
        self.entry_password.pack(side="left", padx=(0, 4))
        self.entry_password.bind("<KeyRelease>", lambda e: self._update_settings_summary_badge())

        self.btn_show_pwd = ctk.CTkButton(
            row1,
            text="👁",
            width=28,
            height=28,
            fg_color=("#f1f3f9", "#2c3036"),
            hover_color=("#e5e8f0", "#3a3f47"),
            text_color=("#495057", "#e2e8f0"),
            border_width=1,
            border_color=("#dce2ee", "#3a3f47"),
            font=ctk.CTkFont(size=12),
            command=self._toggle_pwd_visibility,
        )
        self.btn_show_pwd.pack(side="left", padx=(0, 8))

        # 1행 우측 끝: 분할 압축 묶음 컨테이너
        split_container = ctk.CTkFrame(row1, fg_color="transparent")
        split_container.pack(side="right")

        self.lbl_split_title = ctk.CTkLabel(
            split_container,
            text=f"✂️ {t('label_split_volume')}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#212529", "gray85"),
        )
        self.lbl_split_title.pack(side="left", padx=(0, 6))

        lang = getattr(self, "current_lang", "KO")
        split_values = [t(k, lang=lang) for k in SPLIT_PRESET_KEYS]
        self.combo_split = ctk.CTkComboBox(
            split_container,
            values=split_values,
            width=185,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=("#ffffff", "#2a2d34"),
            border_color=("#dee2e6", "#3a3f47"),
            text_color=("#212529", "#f1f5f9"),
            command=self._on_split_combo_selected,
        )
        saved_split = self.user_settings.get("split_preset", t("split_preset_none", lang=lang))
        self.combo_split.set(self._map_split_preset_text(saved_split, lang))
        self.combo_split.pack(side="left")

        # 2행: 7z 파일명 암호화 체크박스 (2행 우측 끝 정렬)
        row2 = ctk.CTkFrame(opt_box, fg_color="transparent")
        row2.pack(fill="x", padx=12, pady=(2, 6))

        self.chk_encrypt_header = ctk.CTkCheckBox(
            row2,
            text=t("chk_encrypt_filenames"),
            font=ctk.CTkFont(size=11),
            width=20,
            checkbox_width=18,
            checkbox_height=18,
            text_color=("#495057", "gray85"),
            checkmark_color="#ffffff",
            fg_color="#4dabf7",
            command=self._on_encrypt_header_toggle,
        )
        if self.user_settings.get("encrypt_filenames", False):
            self.chk_encrypt_header.select()
        else:
            self.chk_encrypt_header.deselect()
        self.chk_encrypt_header.pack(side="right", padx=0)

    def _on_split_combo_selected(self, choice: str):
        self.save_current_settings()
        self._update_settings_summary_badge()

    def _toggle_pwd_visibility(self):
        cur = self.entry_password.cget("show")
        if cur == "*":
            self.entry_password.configure(show="")
            self.btn_show_pwd.configure(fg_color="#4dabf7", text_color="#ffffff")
        else:
            self.entry_password.configure(show="*")
            self.btn_show_pwd.configure(fg_color=("#f1f3f9", "#2c3036"), text_color=("#495057", "#e2e8f0"))

    def _update_sources_view(self):
        for widget in self.source_scroll_frame.winfo_children():
            widget.destroy()

        if not self.selected_sources:
            empty_box = ctk.CTkFrame(
                self.source_scroll_frame,
                corner_radius=10,
                fg_color=("#ffffff", "#1a1c20"),
                border_width=1,
                border_color=("#dee2e6", "#2a2d34"),
            )
            empty_box.pack(fill="both", expand=True, padx=20, pady=24)

            ctk.CTkLabel(
                empty_box,
                text="📥",
                font=ctk.CTkFont(size=36),
            ).pack(pady=(16, 2))

            ctk.CTkLabel(
                empty_box,
                text=t("drop_empty_prompt"),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#212529", "gray85"),
            ).pack(pady=4)

            ctk.CTkLabel(
                empty_box,
                text="Files from the same folder will be compressed directly to current location." if self.current_lang == "EN" else "동일 폴더의 파일들은 '현재 위치'에 대화상자 없이 즉시 압축됩니다.",
                font=ctk.CTkFont(size=12),
                text_color=("#868e96", "gray"),
            ).pack(pady=(0, 16))

            self.lbl_sources_summary.configure(text=t("summary_items_count", count=0, size="0.0 B"))
            if hasattr(self, "btn_compress_start"):
                self.btn_compress_start.configure(text=t("btn_compress_start"))
            if hasattr(self, "lbl_compress_target_info"):
                self.lbl_compress_target_info.configure(
                    text=f"{t('label_target')} {t('target_placeholder')}"
                )
            return

        total_bytes = 0
        parent_dirs = set()

        for path in self.selected_sources:
            is_dir = os.path.isdir(path)
            badge_text, badge_color = get_file_type_badge(path)

            if is_dir:
                size_str = "폴더"
                parent_dirs.add(os.path.dirname(os.path.abspath(path)))
            else:
                sz = os.path.getsize(path) if os.path.exists(path) else 0
                total_bytes += sz
                size_str = format_bytes(sz)
                parent_dirs.add(os.path.dirname(os.path.abspath(path)))

            row_frame = ctk.CTkFrame(
                self.source_scroll_frame,
                fg_color=("#ffffff", "#22252a"),
                corner_radius=6,
                border_width=1,
                border_color=("#e9ecef", "#2c3036"),
                height=38,
            )
            row_frame.pack(fill="x", pady=2, padx=2)

            # 스마트 타입 뱃지
            badge = ctk.CTkLabel(
                row_frame,
                text=f" {badge_text} ",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=badge_color,
                text_color="#ffffff",
                corner_radius=4,
            )
            badge.pack(side="left", padx=(8, 6), pady=4)

            # 파일/폴더명 (압축 파일 아이콘 모드 활성 시 전용 색상 강조)
            is_archive = (badge_text == "🗜️ 압축")
            show_archive_style = is_archive and getattr(self, "archive_icon_switch", None) and self.archive_icon_switch.get()
            name_color = ("#d9480f", "#ff922b") if show_archive_style else ("#212529", "#f1f5f9")

            name_label = ctk.CTkLabel(
                row_frame,
                text=os.path.basename(path) or path,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=name_color,
                anchor="w",
            )
            name_label.pack(side="left", padx=2, pady=4)

            # 전체 경로 축약 표시
            path_label = ctk.CTkLabel(
                row_frame,
                text=f"({path})",
                font=ctk.CTkFont(size=10),
                text_color=("#868e96", "gray"),
                anchor="w",
            )
            path_label.pack(side="left", padx=8, fill="x", expand=True)

            # 크기 (모노스페이스 스타일)
            size_label = ctk.CTkLabel(
                row_frame,
                text=size_str,
                font=ctk.CTkFont(family="Consolas", size=11),
                text_color=("#495057", "gray70"),
                width=80,
                anchor="e",
            )
            size_label.pack(side="left", padx=6, pady=4)

            # 원클릭 삭제 버튼 (부드러운 파스텔 로즈)
            btn_del = ctk.CTkButton(
                row_frame,
                text="✕",
                width=26,
                height=26,
                fg_color=("#ffe3e3", "#a83232"),
                hover_color=("#ffc9c9", "#d93b3b"),
                text_color=("#e03131", "#ffffff"),
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda p=path: self._remove_single_source(p),
            )
            btn_del.pack(side="right", padx=(4, 8), pady=4)

        # 상태 및 버튼 업데이트
        count_str = t("summary_items_count", count=len(self.selected_sources), size=format_bytes(total_bytes))
        if len(parent_dirs) == 1:
            loc_dir = list(parent_dirs)[0]
            loc_name = os.path.basename(loc_dir) or ("Current Folder" if self.current_lang == "EN" else "현재 폴더")
            summary_info = f"{count_str} | 📍 {loc_name}"
            target_str = f"📍 {t('label_target')} '{loc_dir}\\'"
        else:
            mixed_str = "Mixed Locations (Specify Target)" if self.current_lang == "EN" else "여러 위치 혼합 (저장 위치 지정 필요)"
            summary_info = f"{count_str} | 📍 {mixed_str}"
            target_str = f"📍 {t('label_target')} {mixed_str}"

        if hasattr(self, "btn_compress_start"):
            self.btn_compress_start.configure(text=t("btn_compress_start"))

        self.lbl_sources_summary.configure(text=summary_info)
        if hasattr(self, "lbl_compress_target_info"):
            self.lbl_compress_target_info.configure(text=target_str)

    def _add_files(self):
        lang = getattr(self, "current_lang", "KO")
        paths = filedialog.askopenfilenames(title=t("dialog_select_files_to_compress", lang=lang))
        if paths:
            normalized_paths = [os.path.normpath(p) for p in paths]
            archive_found = find_primary_archive(normalized_paths)
            has_non_archive = any(not is_archive_file(p) for p in normalized_paths)
            has_existing = bool(self.selected_sources)

            # 기존 등록된 파일이 없고, 선택된 파일들도 순수 압축 파일만 있는 경우에만 압축해제 화면으로 전환
            if archive_found and not has_existing and not has_non_archive:
                self.set_active_tab("extract")
                self._load_archive_for_extract(archive_found)
                self.lbl_status.configure(
                    text=t("status_archive_detected", lang=lang, name=os.path.basename(archive_found))
                )
                return

            # 일반 파일이 있거나 함께 선택된 경우 -> 압축하기 목록에 함께 패키징 대상으로 등록
            for p in normalized_paths:
                if p not in self.selected_sources:
                    self.selected_sources.append(p)
            self._update_sources_view()

    def _add_directory(self):
        lang = getattr(self, "current_lang", "KO")
        dir_path = filedialog.askdirectory(title=t("dialog_select_dir_to_compress", lang=lang))
        if dir_path:
            dir_path = os.path.normpath(dir_path)
            if dir_path not in self.selected_sources:
                self.selected_sources.append(dir_path)
            self._update_sources_view()

    def _clear_sources(self):
        self.selected_sources.clear()
        self._update_sources_view()

    def _remove_single_source(self, target_path: str):
        if target_path in self.selected_sources:
            self.selected_sources.remove(target_path)
            self._update_sources_view()
            self.lbl_status.configure(text=f"제거됨: {os.path.basename(target_path)}")

    # =========================================================================
    # 압축 해제 탭 (Extract Page)
    # =========================================================================
    def _setup_extract_page(self):
        # 1. 상단 스마트 액션 바 (드래그 & 드롭 영역의 상단으로 배치!)
        action_bar = ctk.CTkFrame(
            self.page_extract,
            corner_radius=8,
            fg_color=("#ffffff", "#1e2024"),
            border_width=1,
            border_color=("#e9ecef", "#2c2e35"),
        )
        action_bar.pack(fill="x", padx=0, pady=(2, 6))

        # 1. 우측: 위치지정 및 압축해제 실행 버튼 그룹 (너비 고정하여 우측 끝에 배치)
        btn_box = ctk.CTkFrame(action_bar, fg_color="transparent")
        btn_box.pack(side="right", padx=(4, 10), pady=8)

        # 원래 버전 순서: [위치 지정...] (보조) ➔ [⚡ 압축해제] (메인 파스텔 세이지 민트)
        self.btn_extract_custom = ctk.CTkButton(
            btn_box,
            text=t("btn_browse_extract_dest"),
            width=80,
            height=34,
            fg_color=("#f1f3f9", "#373a40"),
            hover_color=("#e5e8f0", "#4a4d55"),
            text_color=("#495057", "#ffffff"),
            border_width=1,
            border_color=("#dce2ee", "#4a4d55"),
            font=ctk.CTkFont(size=12),
            command=lambda: self._start_extraction(force_prompt=True),
        )
        self.btn_extract_custom.pack(side="left", padx=4)

        self.btn_extract_start = ctk.CTkButton(
            btn_box,
            text=t("btn_extract_to_folder"),
            width=125,
            height=34,
            fg_color="#38d9a9",
            hover_color="#20c997",
            text_color="#ffffff",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self._start_extraction(force_prompt=False),
        )
        self.btn_extract_start.pack(side="left", padx=4)

        # 2. 좌측: 2단 컨테이너 (위: 보안 비밀번호 / 아래: 해제 위치 안내)
        left_box = ctk.CTkFrame(action_bar, fg_color="transparent")
        left_box.pack(side="left", fill="both", expand=True, padx=(10, 6), pady=(6, 6))

        # 2-1. 상단: 보안 비밀번호 입력 그룹
        pwd_row = ctk.CTkFrame(left_box, fg_color="transparent")
        pwd_row.pack(fill="x", side="top", anchor="w")

        self.lbl_extract_pwd_title = ctk.CTkLabel(
            pwd_row,
            text=f"🔒 {t('label_extract_password')}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#212529", "gray85"),
        )
        self.lbl_extract_pwd_title.pack(side="left", padx=(0, 4))

        self.entry_extract_password = ctk.CTkEntry(
            pwd_row,
            placeholder_text=t("placeholder_extract_password"),
            show="*",
            width=150,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=("#ffffff", "#2a2d34"),
            border_color=("#dee2e6", "#3a3f47"),
            text_color=("#212529", "#f1f5f9"),
        )
        self.entry_extract_password.pack(side="left", padx=(0, 4))
        self.entry_extract_password.bind("<Return>", lambda e: self._start_extraction(force_prompt=False))

        self.btn_show_extract_pwd = ctk.CTkButton(
            pwd_row,
            text="👁",
            width=28,
            height=28,
            fg_color=("#f1f3f9", "#2c3036"),
            hover_color=("#e5e8f0", "#3a3f47"),
            text_color=("#495057", "#e2e8f0"),
            border_width=1,
            border_color=("#dce2ee", "#3a3f47"),
            font=ctk.CTkFont(size=12),
            command=self._toggle_extract_pwd_visibility,
        )
        self.btn_show_extract_pwd.pack(side="left", padx=(0, 4))

        # 2-2. 하단 (보안 비밀번호 바로 아래): 해제 위치 안내 레이블
        self.lbl_extract_target_info = ctk.CTkLabel(
            left_box,
            text=t("extract_target_empty"),
            font=ctk.CTkFont(size=11),
            text_color=("#495057", "gray70"),
            anchor="w",
            justify="left",
        )
        self.lbl_extract_target_info.pack(fill="x", side="top", anchor="w", pady=(3, 0))

        # 2. 초기 상태 (Empty State: 아카이브 선택 전) 대형 모던 드롭 존 컨테이너
        self.extract_empty_container = ctk.CTkFrame(self.page_extract, fg_color="transparent")
        self.extract_empty_container.pack(fill="both", expand=True, padx=0, pady=(2, 6))

        empty_box = ctk.CTkFrame(
            self.extract_empty_container,
            corner_radius=12,
            fg_color=("#ffffff", "#1a1c20"),
            border_width=1,
            border_color=("#dee2e6", "#2a2d34"),
        )
        empty_box.pack(fill="both", expand=True, padx=10, pady=10)

        # 상단 아이콘
        ctk.CTkLabel(
            empty_box,
            text="📂",
            font=ctk.CTkFont(size=44),
        ).pack(pady=(28, 6))

        lang = getattr(self, "current_lang", "KO")

        # 메인 헤드라인
        self.lbl_extract_drop_title = ctk.CTkLabel(
            empty_box,
            text=t("extract_drop_title", lang=lang),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=("#212529", "gray90"),
        )
        self.lbl_extract_drop_title.pack(pady=4)

        # 서브 안내
        self.lbl_extract_drop_sub = ctk.CTkLabel(
            empty_box,
            text=t("extract_drop_sub", lang=lang),
            font=ctk.CTkFont(size=12),
            text_color=("#868e96", "gray"),
        )
        self.lbl_extract_drop_sub.pack(pady=(0, 16))

        # 지원 포맷 아웃라인 칩 (파스텔 톤 컬러 아웃라인 형태로 스타일링)
        badges_frame = ctk.CTkFrame(empty_box, fg_color="transparent")
        badges_frame.pack(pady=(0, 20))

        formats = [
            ("📦 ZIP", "#4dabf7"),
            ("🗜️ 7z", "#f59f00"),
            ("📚 RAR / RAR5", "#20c997"),
            ("🌐 TAR (gz · xz · bz2 · lz4)", "#38d9a9"),
            ("🍎 Apple (DMG · PKG)", "#9775fa"),
        ]
        for fmt_tag, color in formats:
            ctk.CTkLabel(
                badges_frame,
                text=f"  {fmt_tag}  ",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="transparent",
                border_width=1,
                border_color=color,
                text_color=color,
                corner_radius=6,
                height=26,
            ).pack(side="left", padx=4)

        # 파일 열기 버튼 (파스텔 스카이블루 + 선명한 흰색 글자)
        self.btn_open = ctk.CTkButton(
            empty_box,
            text=t("btn_browse_archive", lang=lang),
            height=38,
            width=220,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#4dabf7",
            hover_color="#339af0",
            text_color="#ffffff",
            command=self._select_archive_file,
        )
        self.btn_open.pack(pady=(0, 16))

        # 하단 스마트 풀기 안내
        self.lbl_extract_drop_smart_tip = ctk.CTkLabel(
            empty_box,
            text=t("extract_drop_smart_tip", lang=lang),
            font=ctk.CTkFont(size=11),
            text_color=("#868e96", "gray65"),
        )
        self.lbl_extract_drop_smart_tip.pack(pady=(0, 16))

        # 3. 로드된 상태 (Loaded State: 아카이브 선택 후) 컨테이너 (초기엔 숨김)
        self.extract_loaded_container = ctk.CTkFrame(self.page_extract, fg_color="transparent")

        # 상단 파일 선택 정보 바
        top_bar = ctk.CTkFrame(self.extract_loaded_container, fg_color="transparent")
        top_bar.pack(fill="x", padx=0, pady=(0, 4))

        self.lbl_selected_archive = ctk.CTkLabel(
            top_bar,
            text="",
            anchor="w",
            text_color=("#212529", "#f1f3f5"),
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.lbl_selected_archive.pack(side="left", fill="x", expand=True, padx=4)

        self.btn_reselect = ctk.CTkButton(
            top_bar,
            text=t("btn_reselect_archive", lang=lang),
            width=120,
            height=30,
            fg_color=("#f1f3f9", "#373a40"),
            hover_color=("#e5e8f0", "#4a4d55"),
            text_color=("#495057", "#ffffff"),
            border_width=1,
            border_color=("#dce2ee", "#4a4d55"),
            font=ctk.CTkFont(size=11),
            command=self._select_archive_file,
        )
        self.btn_reselect.pack(side="right", padx=4)

        # 3단 메트릭 요약 대시보드 (KPI Cards)
        self._build_metric_cards(self.extract_loaded_container)

        # 아카이브 파일 트리/테이블 뷰어
        self.extract_preview = ctk.CTkTextbox(
            self.extract_loaded_container,
            height=190,
            font=ctk.CTkFont(family="Cascadia Mono", size=11),
            corner_radius=8,
            fg_color=("#ffffff", "#191a1d"),
            border_width=1,
            border_color=("#e9ecef", "#2c2e35"),
            text_color=("#212529", "#f1f5f9"),
            spacing1=3,
            spacing3=3,
        )
        self.extract_preview.pack(fill="both", expand=True, padx=0, pady=(4, 4))
        self.extract_preview.configure(state="disabled")

    def _toggle_extract_pwd_visibility(self):
        if hasattr(self, "entry_extract_password"):
            cur = self.entry_extract_password.cget("show")
            if cur == "*":
                self.entry_extract_password.configure(show="")
                self.btn_show_extract_pwd.configure(fg_color="#4dabf7", text_color="#ffffff")
            else:
                self.entry_extract_password.configure(show="*")
                self.btn_show_extract_pwd.configure(fg_color=("#f1f3f9", "#2c3036"), text_color=("#495057", "#e2e8f0"))

    def _build_metric_cards(self, parent_frame=None):
        """3단 메트릭 요약 대시보드 (총 파일 수 / 원본 용량 / 압축 절감률)"""
        parent = parent_frame if parent_frame is not None else self.extract_loaded_container
        metric_container = ctk.CTkFrame(parent, fg_color="transparent")
        metric_container.pack(fill="x", padx=0, pady=(2, 6))

        for i in range(3):
            metric_container.grid_columnconfigure(i, weight=1)

        lang = getattr(self, "current_lang", "KO")
        unit = t("metric_unit_items", lang=lang)
        pending = t("card_pending", lang=lang)
        # Card 1: 총 파일 수
        self.card_files = self._create_stat_card(
            metric_container, 0, t("card_total_files", lang=lang), f"-- {unit}", pending
        )
        # Card 2: 원본 용량
        self.card_orig = self._create_stat_card(
            metric_container, 1, t("card_orig_size", lang=lang), "-- MB", pending
        )
        # Card 3: 절감률 (파스텔 민트)
        self.card_ratio = self._create_stat_card(
            metric_container, 2, t("card_ratio", lang=lang), "-- %", pending, value_color="#20c997"
        )

    def _create_stat_card(self, parent, col, title, initial_val, sub_text, value_color=None):
        card = ctk.CTkFrame(
            parent,
            corner_radius=8,
            fg_color=("#ffffff", "#1e2024"),
            border_width=1,
            border_color=("#e9ecef", "#2c2e35"),
        )
        card.grid(row=0, column=col, padx=3, pady=2, sticky="nsew")

        lbl_title = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#868e96", "gray"),
        )
        lbl_title.pack(anchor="w", padx=12, pady=(8, 2))

        val_color = value_color if value_color else ("#212529", "#f1f5f9")
        lbl_val = ctk.CTkLabel(
            card,
            text=initial_val,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=val_color,
        )
        lbl_val.pack(anchor="w", padx=12, pady=(0, 2))

        lbl_sub = ctk.CTkLabel(
            card,
            text=sub_text,
            font=ctk.CTkFont(size=10),
            text_color=("#868e96", "gray"),
        )
        lbl_sub.pack(anchor="w", padx=12, pady=(0, 8))

        return {"title": lbl_title, "value": lbl_val, "sub": lbl_sub}

    def _select_archive_file(self):
        filter_str = (
            "*.zip;*.7z;*.rar;*.dmg;*.pkg;*.xip;"
            "*.tar;*.tar.lz4;*.lz4;*.tar.gz;*.tgz;*.tar.xz;*.txz;*.tar.bz2;*.tbz2;*.gz;*.xz;*.bz2;"
            "*.alz;*.egg;*.iso;*.wim;*.cab;*.001;*.z01;*.part*.rar"
        )
        lang = getattr(self, "current_lang", "KO")
        if lang == "EN":
            filetypes = [
                ("All Supported Archives", filter_str),
                ("Split Volumes (*.001, *.z01, *.part*.rar)", "*.001;*.z01;*.part*.rar"),
                ("ZIP Archives (*.zip)", "*.zip"),
                ("7-Zip Archives (*.7z, *.7z.001)", "*.7z;*.7z.001"),
                ("LZ4 TAR Archives (*.tar.lz4, *.lz4)", "*.tar.lz4;*.lz4"),
                ("RAR Archives (*.rar, *.part*.rar)", "*.rar;*.part*.rar"),
                ("ALZip Archives (*.alz, *.egg)", "*.alz;*.egg"),
                ("Apple Archives (*.dmg, *.pkg, *.xip)", "*.dmg;*.pkg;*.xip"),
                ("TAR Archives (*.tar.*)", "*.tar;*.tar.gz;*.tgz;*.tar.xz;*.txz;*.tar.bz2"),
                ("All Files (*.*)", "*.*"),
            ]
        else:
            filetypes = [
                ("모든 지원 아카이브", filter_str),
                ("분할 압축 아카이브 (*.001, *.z01, *.part*.rar)", "*.001;*.z01;*.part*.rar"),
                ("ZIP 아카이브 (*.zip)", "*.zip"),
                ("7-Zip 아카이브 (*.7z, *.7z.001)", "*.7z;*.7z.001"),
                ("LZ4 TAR 아카이브 (*.tar.lz4, *.lz4)", "*.tar.lz4;*.lz4"),
                ("RAR 아카이브 (*.rar, *.part*.rar)", "*.rar;*.part*.rar"),
                ("알집 아카이브 (*.alz, *.egg)", "*.alz;*.egg"),
                ("Apple 아카이브 (*.dmg, *.pkg, *.xip)", "*.dmg;*.pkg;*.xip"),
                ("TAR 아카이브 (*.tar.*)", "*.tar;*.tar.gz;*.tgz;*.tar.xz;*.txz;*.tar.bz2"),
                ("모든 파일", "*.*"),
            ]
        path = filedialog.askopenfilename(
            title=t("dialog_select_archive", lang=lang),
            filetypes=filetypes,
        )
        if path:
            primary_path = find_primary_archive([path]) or path
            self._load_archive_for_extract(primary_path)

    def _load_archive_for_extract(self, path: str, password: str | None = None):
        try:
            self.selected_archive_for_extract = path
            if self.active_tab != "extract":
                self.set_active_tab("extract")

            lang = getattr(self, "current_lang", "KO")
            pwd = password or (self.entry_extract_password.get().strip() if hasattr(self, "entry_extract_password") else None)
            try:
                entries = list_archive_entries(path, password=pwd)
            except PermissionError:
                # 파일명 암호화된 아카이브: 사용자에게 비밀번호 입력 팝업 표출
                dialog = ctk.CTkInputDialog(
                    title=t("dialog_pwd_required", lang=lang),
                    text=t("dialog_pwd_required_msg", lang=lang, name=os.path.basename(path)),
                )
                user_pwd = dialog.get_input()
                if user_pwd:
                    if hasattr(self, "entry_extract_password"):
                        self.entry_extract_password.delete(0, "end")
                        self.entry_extract_password.insert(0, user_pwd)
                    return self._load_archive_for_extract(path, password=user_pwd)
                else:
                    self.lbl_status.configure(
                        text=t("status_pwd_cancelled", lang=lang, name=os.path.basename(path))
                    )
                    return

            # 초기 대형 드롭 영역 숨기고 로드 컨테이너 활성화
            self.extract_empty_container.pack_forget()
            self.extract_loaded_container.pack(fill="both", expand=True, padx=0, pady=(2, 6))
            self.archive_entries = entries

            # 암호화 여부 감지
            has_encrypted_entry = any(e.get("is_encrypted", False) for e in entries)
            self.is_archive_encrypted = bool(password or has_encrypted_entry)

            # 단일 폴더 통 압축 여부 판별 (이중 폴더 방지)
            is_single, root_name = check_archive_has_single_root_folder(entries)
            self.has_single_root_folder = is_single
            self.single_root_folder_name = root_name

            # 다국어 지원 렌더링 호출
            self._render_extract_loaded_view()
        except Exception as e:
            traceback.print_exc()
            lang = getattr(self, "current_lang", "KO")
            messagebox.showerror(t("dialog_error", lang=lang), t("err_open_archive_failed", lang=lang, err=e))

    def _render_extract_loaded_view(self):
        """압축 해제 탭: 로드된 아카이브 메트릭 및 파일 목록 미리보기 렌더링 (다국어 지원)"""
        path = getattr(self, "selected_archive_for_extract", "")
        entries = getattr(self, "archive_entries", [])
        if not path or not entries:
            return

        lang = getattr(self, "current_lang", "KO")
        enc_tag = f" 🔒 [{t('encrypted_tag', lang=lang)}]" if getattr(self, "is_archive_encrypted", False) else ""

        # 1. 아카이브 선택 라벨
        if hasattr(self, "lbl_selected_archive"):
            self.lbl_selected_archive.configure(
                text=t("selected_archive_text", lang=lang, name=os.path.basename(path), enc=enc_tag, path=path),
                text_color=("gray10", "#f1f3f5"),
            )

        # 2. 해제 대상 안내 라벨
        folder_name = get_archive_folder_name(path)
        archive_dir = os.path.dirname(os.path.abspath(path))
        loc_name = os.path.basename(archive_dir) or archive_dir

        is_single = getattr(self, "has_single_root_folder", False)
        root_name = getattr(self, "single_root_folder_name", None)

        if is_single:
            info_text = t("extract_target_single", lang=lang, loc=loc_name, root=root_name)
        else:
            info_text = t("extract_target_nested", lang=lang, loc=loc_name, folder=folder_name)

        if hasattr(self, "btn_extract_start"):
            self.btn_extract_start.configure(text=t("btn_extract_to_folder", lang=lang))
        if hasattr(self, "lbl_extract_target_info"):
            self.lbl_extract_target_info.configure(
                text=info_text,
                text_color=("#212529", "gray85"),
            )

        # 3. 3단 메트릭 요약
        total_uncompressed = sum(e["uncompressed_size"] for e in entries)
        total_compressed = sum(e["compressed_size"] for e in entries)
        ratio = (
            ((1.0 - (total_compressed / total_uncompressed)) * 100.0)
            if total_uncompressed > 0 and total_compressed > 0 and total_compressed <= total_uncompressed
            else 0.0
        )

        unit = t("metric_unit_items", lang=lang)
        if hasattr(self, "card_files") and isinstance(self.card_files, dict):
            if "title" in self.card_files:
                self.card_files["title"].configure(text=t("card_total_files", lang=lang))
            if "value" in self.card_files:
                self.card_files["value"].configure(text=f"{len(entries):,} {unit}")
            if "sub" in self.card_files:
                self.card_files["sub"].configure(text=t("metric_sub_total_files", lang=lang))

        if hasattr(self, "card_orig") and isinstance(self.card_orig, dict):
            if "title" in self.card_orig:
                self.card_orig["title"].configure(text=t("card_orig_size", lang=lang))
            if "value" in self.card_orig:
                self.card_orig["value"].configure(text=format_bytes(total_uncompressed))
            if "sub" in self.card_orig:
                self.card_orig["sub"].configure(text=t("metric_sub_compressed", lang=lang, size=format_bytes(total_compressed)))

        if hasattr(self, "card_ratio") and isinstance(self.card_ratio, dict):
            if "title" in self.card_ratio:
                self.card_ratio["title"].configure(text=t("card_ratio", lang=lang))
            if "value" in self.card_ratio:
                self.card_ratio["value"].configure(text=f"{ratio:.1f} %")
            if "sub" in self.card_ratio:
                self.card_ratio["sub"].configure(text=t("metric_sub_space_saved", lang=lang))

        # 4. 파일 트리 테이블 출력
        if hasattr(self, "extract_preview"):
            self.extract_preview.configure(state="normal")
            self.extract_preview.delete("1.0", "end")

            structure_mode = (
                t("structure_single", lang=lang, root=root_name)
                if is_single
                else t("structure_multi", lang=lang)
            )
            col_name = t("tree_hdr_name", lang=lang)
            col_orig = t("tree_hdr_orig_size", lang=lang)
            col_comp = t("tree_hdr_comp_size", lang=lang)

            header = f"[{os.path.basename(path)}]{structure_mode}\n"
            header += f"{col_name:<46} | {col_orig:>13} | {col_comp:>13}\n"
            header += "-" * 78 + "\n"
            self.extract_preview.insert("end", header)

            for e in entries:
                icon = "📁" if e["is_dir"] else "📄"
                u_str = format_bytes(e["uncompressed_size"])
                c_str = format_bytes(e["compressed_size"])
                name_disp = e['name']
                if len(name_disp) > 44:
                    name_disp = name_disp[:41] + "..."
                self.extract_preview.insert(
                    "end", f"{icon} {name_disp:<44} | {u_str:>13} | {c_str:>13}\n"
                )
            self.extract_preview.configure(state="disabled")

        # 5. 상태바 업데이트
        if hasattr(self, "lbl_status") and not self.worker.is_busy():
            self.lbl_status.configure(
                text=t("status_archive_analyzed", lang=lang, name=os.path.basename(path), count=f"{len(entries):,}")
            )

    def _clear_extract_view(self):
        """압축 해제 탭 내용 초기화 - 초기 대형 드롭 존 복원"""
        self.selected_archive_for_extract = ""
        self.archive_entries = []
        self.has_single_root_folder = False
        self.single_root_folder_name = None
        self.is_archive_encrypted = False

        if hasattr(self, "entry_extract_password"):
            self.entry_extract_password.delete(0, "end")

        # 로드 컨테이너 숨기고 초기 대형 드롭 존 복원
        self.extract_loaded_container.pack_forget()
        self.extract_empty_container.pack(fill="both", expand=True, padx=0, pady=(2, 6))

        lang = getattr(self, "current_lang", "KO")
        unit = t("metric_unit_items", lang=lang)
        pending = t("card_pending", lang=lang)

        if hasattr(self, "card_files") and isinstance(self.card_files, dict):
            if "title" in self.card_files:
                self.card_files["title"].configure(text=t("card_total_files", lang=lang))
            if "value" in self.card_files:
                self.card_files["value"].configure(text=f"-- {unit}")
            if "sub" in self.card_files:
                self.card_files["sub"].configure(text=pending)

        if hasattr(self, "card_orig") and isinstance(self.card_orig, dict):
            if "title" in self.card_orig:
                self.card_orig["title"].configure(text=t("card_orig_size", lang=lang))
            if "value" in self.card_orig:
                self.card_orig["value"].configure(text="-- MB")
            if "sub" in self.card_orig:
                self.card_orig["sub"].configure(text=pending)

        if hasattr(self, "card_ratio") and isinstance(self.card_ratio, dict):
            if "title" in self.card_ratio:
                self.card_ratio["title"].configure(text=t("card_ratio", lang=lang))
            if "value" in self.card_ratio:
                self.card_ratio["value"].configure(text="-- %")
            if "sub" in self.card_ratio:
                self.card_ratio["sub"].configure(text=pending)

        self.extract_preview.configure(state="normal")
        self.extract_preview.delete("1.0", "end")
        self.extract_preview.configure(state="disabled")

        if hasattr(self, "btn_extract_start"):
            self.btn_extract_start.configure(text=t("btn_extract_to_folder", lang=lang))
        if hasattr(self, "lbl_extract_target_info"):
            self.lbl_extract_target_info.configure(
                text=t("extract_target_empty", lang=lang),
                text_color=("#475569", "gray75"),
            )

    # =========================================================================
    # 하단 진행 상태 바
    # =========================================================================
    def _setup_progress_bar(self):
        prog_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        prog_frame.pack(fill="x", side="bottom", padx=20, pady=(4, 14))

        self.lbl_status = ctk.CTkLabel(
            prog_frame,
            text="준비됨 - 파일 또는 폴더를 드래그 앤 드롭하세요",
            anchor="w",
            font=ctk.CTkFont(size=11),
            text_color=("#495057", "gray75"),
        )
        self.lbl_status.pack(fill="x", padx=4, pady=(2, 2))

        self.progress_bar = ctk.CTkProgressBar(
            prog_frame,
            height=9,
            corner_radius=5,
            progress_color="#4dabf7",
        )
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=4, pady=(2, 4))

    def save_current_settings(self):
        """현재 UI 상태를 사용자 설정으로 저장 (High-DPI 배율 보정)"""
        try:
            self.user_settings["theme"] = ctk.get_appearance_mode()
            self.user_settings["lang"] = self.current_lang
            self.user_settings["selected_algo"] = self.selected_algo
            if hasattr(self, "combo_extra_algo"):
                self.user_settings["extra_algo"] = self.combo_extra_algo.get()
            if hasattr(self, "combo_split"):
                self.user_settings["split_preset"] = self.combo_split.get()
            if hasattr(self, "chk_encrypt_header"):
                self.user_settings["encrypt_filenames"] = bool(self.chk_encrypt_header.get())
            if hasattr(self, "chk_verify_integrity"):
                self.user_settings["verify_integrity"] = bool(self.chk_verify_integrity.get())
            if hasattr(self, "settings_expanded"):
                self.user_settings["settings_expanded"] = bool(self.settings_expanded)

            # 최대화(zoomed) 상태가 아닐 때의 논리 크기(DPI 배율 보정) 영구 저장
            is_zoomed = False
            try:
                is_zoomed = (self.state() == "zoomed")
            except Exception:
                pass

            if not is_zoomed:
                geom_str = str(self.geometry())
                m = re.match(r"^(\d+)x(\d+)", geom_str)
                if m:
                    w, h = int(m.group(1)), int(m.group(2))
                    if 400 <= w <= 2560 and 300 <= h <= 1600:
                        self.user_settings["window_geometry"] = f"{w}x{h}"
                else:
                    scale = ctk.ScalingTracker.get_window_scaling(self) or 1.0
                    w = int(self.winfo_width() / scale)
                    h = int(self.winfo_height() / scale)
                    if 400 <= w <= 2560 and 300 <= h <= 1600:
                        self.user_settings["window_geometry"] = f"{w}x{h}"

            save_settings(self.user_settings)
        except Exception as e:
            print(f"[설정 저장 오류] {e}")

    def _on_language_change(self, value: str):
        """다국어 세그먼트 버튼 선택 변경 핸들러 ('한글' -> 'KO', 'EN' -> 'EN')"""
        new_lang = "KO" if value in ["한글", "한"] else value
        if new_lang in SUPPORTED_LANGUAGES and new_lang != self.current_lang:
            self.current_lang = new_lang
            set_language(new_lang)
            self.user_settings["lang"] = new_lang
            self.save_current_settings()
            self._refresh_ui_language()

    def _refresh_ui_language(self):
        """현재 언어(KO/EN)에 맞춰 전체 UI 텍스트 실시간 갱신"""
        lang = self.current_lang
        self.title(t("app_title", lang=lang))

        # 1. 헤더 영역
        if hasattr(self, "lang_segmented"):
            disp_lang = "한글" if lang == "KO" else "EN"
            self.lang_segmented.set(disp_lang)
        cores = multiprocessing.cpu_count() or 16
        is_native = is_native_engine_active()
        core_key = "core_native" if is_native else "core_python"
        if hasattr(self, "core_label"):
            self.core_label.configure(text=t(core_key, lang=lang, cores=cores))
        if hasattr(self, "theme_switch"):
            self.theme_switch.configure(text=t("dark_mode", lang=lang))
        if hasattr(self, "context_menu_switch"):
            self.context_menu_switch.configure(text=t("context_menu_toggle", lang=lang))
        if hasattr(self, "archive_icon_switch"):
            self.archive_icon_switch.configure(text=t("archive_icon_toggle", lang=lang))
        if hasattr(self, "btn_sponsor"):
            self.btn_sponsor.configure(text=t("btn_sponsor", lang=lang))

        # 2. 네비게이션 알약 버튼
        if hasattr(self, "nav_segmented"):
            self.nav_segmented.configure(values=[t("nav_compress", lang=lang), t("nav_extract", lang=lang)])
            self.nav_segmented.set(t("nav_compress", lang=lang) if self.active_tab == "compress" else t("nav_extract", lang=lang))

        # 3. 압축 탭 상단 액션바
        if hasattr(self, "btn_compress_custom_loc"):
            self.btn_compress_custom_loc.configure(text=t("btn_browse_target", lang=lang))
        if hasattr(self, "btn_compress_start"):
            self.btn_compress_start.configure(text=t("btn_compress_start", lang=lang))

        # 4. 압축 탭 툴바
        if hasattr(self, "btn_add_file"):
            self.btn_add_file.configure(text=t("btn_add_files", lang=lang))
        if hasattr(self, "btn_add_dir"):
            self.btn_add_dir.configure(text=t("btn_add_folder", lang=lang))
        if hasattr(self, "btn_clear"):
            self.btn_clear.configure(text=t("btn_clear_all", lang=lang))
        if hasattr(self, "chk_verify_integrity"):
            self.chk_verify_integrity.configure(text=t("chk_verify_integrity", lang=lang))

        # 4-1. 설정 아코디언 토글 바
        if hasattr(self, "_update_settings_toggle_ui"):
            self._update_settings_toggle_ui()

        # 5. 알고리즘 프리셋 헤더 및 4종 카드
        if hasattr(self, "lbl_algo_preset_title"):
            self.lbl_algo_preset_title.configure(text="Compression Presets" if lang == "EN" else "압축 알고리즘 프리셋")
        if hasattr(self, "combo_extra_algo"):
            cur_extra = self.combo_extra_algo.get()
            self.combo_extra_algo.configure(values=[t(k, lang=lang) for k in EXTRA_ALGO_KEYS])
            self.combo_extra_algo.set(self._map_extra_algo_text(cur_extra, lang))
        if hasattr(self, "algo_cards") and self.algo_cards:
            sub_map = {
                "zstd": ("Modern Balanced", "현대 표준 올인원"),
                "7z": ("Ultra High Ratio", "초고압축"),
                "lz4": ("500MB/s+ Lightning", "초당 500MB+ 번개"),
                "targz": ("Unix/Linux/Mac Standard", "유닉스/리눅스/맥 표준"),
            }
            stats_map = {
                "zstd": ("Speed: ★★★★★\nRatio: ★★★★☆", "속도: ★★★★★\n압축: ★★★★☆"),
                "7z": ("Speed: ★★★☆☆\nRatio: ★★★★★", "속도: ★★★☆☆\n압축: ★★★★★"),
                "lz4": ("Speed: ★★★★★★\nRatio: ★★☆☆☆", "속도: ★★★★★★\n압축: ★★☆☆☆"),
                "targz": ("Speed: ★★★★☆\nRatio: ★★★☆☆", "속도: ★★★★☆\n압축: ★★★☆☆"),
            }
            for k, w in self.algo_cards.items():
                if k in sub_map and "sub" in w:
                    txt = sub_map[k][0] if lang == "EN" else sub_map[k][1]
                    w["sub"].configure(text=txt)
                if k in stats_map and "stats" in w:
                    txt = stats_map[k][0] if lang == "EN" else stats_map[k][1]
                    w["stats"].configure(text=txt)

        # 6. 고급 옵션
        if hasattr(self, "lbl_pwd_title"):
            self.lbl_pwd_title.configure(text=f"🔒 {t('label_password', lang=lang)}")
        if hasattr(self, "entry_password"):
            self.entry_password.configure(placeholder_text=t("placeholder_password", lang=lang))
        if hasattr(self, "chk_encrypt_header"):
            self.chk_encrypt_header.configure(text=t("chk_encrypt_filenames", lang=lang))
        if hasattr(self, "lbl_split_title"):
            self.lbl_split_title.configure(text=f"✂️ {t('label_split_volume', lang=lang)}")
        if hasattr(self, "combo_split"):
            cur_split = self.combo_split.get()
            self.combo_split.configure(values=[t(k, lang=lang) for k in SPLIT_PRESET_KEYS])
            self.combo_split.set(self._map_split_preset_text(cur_split, lang))

        # 7. 해제 탭 상단 액션바 및 드래그 & 드롭 영역
        if hasattr(self, "lbl_extract_pwd_title"):
            self.lbl_extract_pwd_title.configure(text=f"🔒 {t('label_extract_password', lang=lang)}")
        if hasattr(self, "entry_extract_password"):
            self.entry_extract_password.configure(placeholder_text=t("placeholder_extract_password", lang=lang))
        if hasattr(self, "btn_extract_custom"):
            self.btn_extract_custom.configure(text=t("btn_browse_extract_dest", lang=lang))
        if hasattr(self, "btn_extract_start"):
            self.btn_extract_start.configure(text=t("btn_extract_to_folder", lang=lang))
        if hasattr(self, "lbl_extract_drop_title"):
            self.lbl_extract_drop_title.configure(text=t("extract_drop_title", lang=lang))
        if hasattr(self, "lbl_extract_drop_sub"):
            self.lbl_extract_drop_sub.configure(text=t("extract_drop_sub", lang=lang))
        if hasattr(self, "btn_open"):
            self.btn_open.configure(text=t("btn_browse_archive", lang=lang))
        if hasattr(self, "lbl_extract_drop_smart_tip"):
            self.lbl_extract_drop_smart_tip.configure(text=t("extract_drop_smart_tip", lang=lang))
        if hasattr(self, "btn_reselect"):
            self.btn_reselect.configure(text=t("btn_reselect_archive", lang=lang))

        # 로드된 아카이브가 있으면 메트릭 및 미리보기 전체를 새 언어로 재렌더링
        if getattr(self, "selected_archive_for_extract", None) and getattr(self, "archive_entries", None):
            self._render_extract_loaded_view()
        else:
            if hasattr(self, "lbl_extract_target_info"):
                self.lbl_extract_target_info.configure(text=t("extract_target_empty", lang=lang))
            unit = t("metric_unit_items", lang=lang)
            pending = t("card_pending", lang=lang)
            if hasattr(self, "card_files") and isinstance(self.card_files, dict):
                if "title" in self.card_files:
                    self.card_files["title"].configure(text=t("card_total_files", lang=lang))
                if "value" in self.card_files:
                    self.card_files["value"].configure(text=f"-- {unit}")
                if "sub" in self.card_files:
                    self.card_files["sub"].configure(text=pending)
            if hasattr(self, "card_orig") and isinstance(self.card_orig, dict):
                if "title" in self.card_orig:
                    self.card_orig["title"].configure(text=t("card_orig_size", lang=lang))
                if "sub" in self.card_orig:
                    self.card_orig["sub"].configure(text=pending)
            if hasattr(self, "card_ratio") and isinstance(self.card_ratio, dict):
                if "title" in self.card_ratio:
                    self.card_ratio["title"].configure(text=t("card_ratio", lang=lang))
                if "sub" in self.card_ratio:
                    self.card_ratio["sub"].configure(text=pending)

        # 8. 소스 목록 및 하단 상태바
        self._update_sources_view()
        if hasattr(self, "lbl_status") and not self.worker.is_busy():
            self.lbl_status.configure(text=t("status_ready", lang=lang))

    def _on_window_close(self):
        """창 종료 시 현재 설정 저장 후 안전하게 파괴"""
        self.save_current_settings()
        self.destroy()

    def _toggle_theme(self):
        mode = ctk.get_appearance_mode()
        new_mode = "Light" if mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        self.user_settings["theme"] = new_mode
        self._refresh_algo_card_styles()
        self.save_current_settings()

    def _toggle_context_menu(self):
        target_state = self.context_menu_switch.get()
        if target_state:
            self.lbl_status.configure(text="⏳ 탐색기 마우스 우클릭 메뉴를 활성화하는 중...")
        else:
            self.lbl_status.configure(text="⏳ 탐색기 마우스 우클릭 메뉴를 비활성화하는 중...")

        def _worker():
            if target_state:
                ok = register_context_menu()
                def _on_done():
                    if ok:
                        self.lbl_status.configure(text="✅ 탐색기 마우스 우클릭 메뉴가 활성화되었습니다.")
                    else:
                        self.lbl_status.configure(text="❌ 마우스 우클릭 메뉴 활성화 실패")
                        self.context_menu_switch.deselect()
                    self.user_settings["context_menu"] = bool(ok and target_state)
                    self.save_current_settings()
                self.after(0, _on_done)
            else:
                ok = unregister_context_menu()
                def _on_done():
                    if ok:
                        self.lbl_status.configure(text="탐색기 마우스 우클릭 메뉴가 비활성화되었습니다.")
                    else:
                        self.lbl_status.configure(text="❌ 마우스 우클릭 메뉴 비활성화 실패")
                        self.context_menu_switch.select()
                    self.user_settings["context_menu"] = False
                    self.save_current_settings()
                self.after(0, _on_done)

        threading.Thread(target=_worker, daemon=True).start()

    def _toggle_archive_icon(self):
        target_state = bool(self.archive_icon_switch.get())
        if target_state:
            self.lbl_status.configure(text="⏳ 압축 파일 아이콘을 Windows 탐색기에 연동하는 중...")
        else:
            self.lbl_status.configure(text="⏳ 압축 파일 아이콘 연동을 해제하는 중...")

        def _worker():
            if target_state:
                ok = register_file_associations()
                def _on_done():
                    if ok:
                        self.lbl_status.configure(text=t("status_archive_icon_on"))
                    else:
                        self.lbl_status.configure(text="❌ 압축 파일 아이콘 연동 실패")
                        self.archive_icon_switch.deselect()
                    self.user_settings["archive_icons"] = ok
                    self.save_current_settings()
                    self._update_sources_view()
                self.after(0, _on_done)
            else:
                ok = unregister_file_associations()
                def _on_done():
                    if ok:
                        self.lbl_status.configure(text=t("status_archive_icon_off"))
                    else:
                        self.lbl_status.configure(text="❌ 압축 파일 아이콘 해제 실패")
                        self.archive_icon_switch.select()
                    self.user_settings["archive_icons"] = False
                    self.save_current_settings()
                    self._update_sources_view()
                self.after(0, _on_done)

        threading.Thread(target=_worker, daemon=True).start()

    def _open_github_repo(self):
        """GitHub 저장소 페이지를 브라우저로 오픈"""
        webbrowser.open(GITHUB_REPO_URL)

    def _open_sponsor_link(self):
        """GitHub Sponsors 후원 페이지를 브라우저로 오픈"""
        webbrowser.open("https://github.com/sponsors/smin987")

    # =========================================================================
    # 압축 / 압축 해제 실행
    # =========================================================================
    def _start_compression(self, force_prompt: bool = False):
        if not self.selected_sources:
            messagebox.showwarning(t("dialog_warning"), t("err_no_source"))
            return

        choice_key = self.selected_algo
        lang = getattr(self, "current_lang", "KO")
        archive_label = "Archive" if lang == "EN" else "아카이브"
        all_files_label = "All Files" if lang == "EN" else "모든 파일"

        level_val = None
        if choice_key == "7z":
            ext = ".7z"
            filetypes = [(f"7-Zip {archive_label}", "*.7z"), (all_files_label, "*.*")]
            fmt_type = "7z"
            zip_method = "deflate"
            level_val = 5
        elif choice_key == "lz4":
            ext = ".tar.lz4"
            filetypes = [(f"LZ4 TAR {archive_label}", "*.tar.lz4;*.lz4"), (all_files_label, "*.*")]
            fmt_type = "tar.lz4"
            zip_method = "deflate"
        elif choice_key == "targz":
            ext = ".tar.gz"
            filetypes = [(f"Gzip TAR {archive_label}", "*.tar.gz;*.tgz"), (all_files_label, "*.*")]
            fmt_type = "tar.gz"
            zip_method = "deflate"
        elif choice_key == "extra":
            extra_val = self.combo_extra_algo.get()
            if "Store" in extra_val or "무압축 (Store" in extra_val:
                ext = ".zip"
                filetypes = [(f"ZIP {archive_label}", "*.zip"), (all_files_label, "*.*")]
                fmt_type = "zip"
                zip_method = "store"
            elif ".tar.xz" in extra_val:
                ext = ".tar.xz"
                filetypes = [(f"XZ TAR {archive_label}", "*.tar.xz;*.txz"), (all_files_label, "*.*")]
                fmt_type = "tar.xz"
                zip_method = "deflate"
            elif ".tar.bz2" in extra_val:
                ext = ".tar.bz2"
                filetypes = [(f"Bzip2 TAR {archive_label}", "*.tar.bz2;*.tbz2"), (all_files_label, "*.*")]
                fmt_type = "tar.bz2"
                zip_method = "deflate"
            elif ".tar" in extra_val:
                ext = ".tar"
                filetypes = [(f"TAR {archive_label}", "*.tar"), (all_files_label, "*.*")]
                fmt_type = "tar"
                zip_method = "deflate"
            else:
                ext = ".zip"
                filetypes = [(f"ZIP {archive_label}", "*.zip"), (all_files_label, "*.*")]
                fmt_type = "zip"
                zip_method = "zstd"
        else:  # "zstd" 기본
            ext = ".zip"
            filetypes = [(f"ZIP {archive_label}", "*.zip"), (all_files_label, "*.*")]
            fmt_type = "zip"
            zip_method = "zstd"

        parent_dirs = set(os.path.dirname(os.path.abspath(p)) for p in self.selected_sources)

        if len(self.selected_sources) == 1:
            first = self.selected_sources[0]
            base_name = os.path.splitext(os.path.basename(first))[0] if os.path.isfile(first) else os.path.basename(first)
        else:
            first = self.selected_sources[0]
            first_base = os.path.splitext(os.path.basename(first))[0] if os.path.isfile(first) else os.path.basename(first)
            more_count = len(self.selected_sources) - 1
            base_name = f"{first_base}_and_{more_count}_more" if lang == "EN" else f"{first_base}_외_{more_count}개"

        if len(parent_dirs) == 1 and not force_prompt:
            target_dir = list(parent_dirs)[0]
            out_path = get_unique_filepath(target_dir, base_name, ext)
        else:
            initial_dir = list(parent_dirs)[0] if parent_dirs else os.getcwd()
            save_title = f"Save Archive As ({ext})" if lang == "EN" else f"압축 파일 저장 위치 지정 ({ext})"
            out_path = filedialog.asksaveasfilename(
                title=save_title,
                initialdir=initial_dir,
                initialfile=f"{base_name}{ext}",
                defaultextension=ext,
                filetypes=filetypes,
            )
            if not out_path:
                return

        self.progress_bar.set(0.0)
        self.lbl_status.configure(text=f"[{fmt_type.upper()}] 압축 중: {os.path.basename(out_path)}...")

        def on_progress(info):
            pct = info["percentage"] / 100.0
            self.progress_bar.set(pct)
            cur_file = info.get("file", "").strip()
            if info.get("total") == 100:
                status_text = f"압축 중: {cur_file} ({info['percentage']:.0f}%) [{info['elapsed']:.1f}s]"
            else:
                proc = format_bytes(info.get("processed", 0))
                tot = format_bytes(info.get("total", 0))
                status_text = f"압축 중: {cur_file} ({proc} / {tot}) - {info['percentage']:.1f}% [{info['elapsed']:.1f}s]"
            self.lbl_status.configure(text=status_text)

        def on_finish(msg):
            self.progress_bar.set(1.0)
            self.lbl_status.configure(text=msg)
            messagebox.showinfo(
                t("compress_finish_title"),
                t("compress_finish_msg", msg=msg, path=out_path),
            )
            # 작업 완료 알림창 확인 후 목록 및 일회성 암호 필드 초기화 (사용자 설정 분할 프리셋 등은 기억 유지)
            self._clear_sources()
            if hasattr(self, "entry_password"):
                self.entry_password.delete(0, "end")
            self.progress_bar.set(0.0)
            self.lbl_status.configure(text=f"{t('status_ready')} - {msg}")

        def on_error(err):
            self.lbl_status.configure(text=f"{t('dialog_error')}: {err}")
            messagebox.showerror(t("dialog_error"), t("err_compress_failed", err=err))

        # 암호, 분할 압축 및 무결성 검사 옵션 취득
        pwd_val = self.entry_password.get().strip() or None if hasattr(self, "entry_password") else None
        split_val = parse_split_size(self.combo_split.get()) if hasattr(self, "combo_split") else None
        encrypt_hdr = bool(self.chk_encrypt_header.get()) if hasattr(self, "chk_encrypt_header") else False
        verify_integ = bool(self.chk_verify_integrity.get()) if hasattr(self, "chk_verify_integrity") else False

        self.worker.compress_async(
            source_paths=self.selected_sources,
            output_archive_path=out_path,
            format_type=fmt_type,
            zip_method=zip_method,
            level=level_val,
            password=pwd_val,
            split_size=split_val,
            encrypt_filenames=encrypt_hdr,
            verify_integrity=verify_integ,
            on_progress=lambda info: self.after(0, lambda: on_progress(info)),
            on_finish=lambda msg: self.after(0, lambda: on_finish(msg)),
            on_error=lambda err: self.after(0, lambda: on_error(err)),
        )

    def _start_extraction(self, force_prompt: bool = False, retry_password: str | None = None):
        if not self.selected_archive_for_extract:
            messagebox.showwarning(t("dialog_warning"), t("warn_select_archive_first"))
            return

        archive_path = self.selected_archive_for_extract
        archive_dir = os.path.dirname(os.path.abspath(archive_path))
        folder_name = get_archive_folder_name(archive_path)

        # 비밀번호 획득
        entered_pwd = (
            self.entry_extract_password.get().strip()
            if hasattr(self, "entry_extract_password")
            else ""
        )
        pwd = retry_password or entered_pwd or None

        # 비밀번호가 있는 압축 파일인데 비밀번호 입력 없이 '압축해제'를 시도한 경우 알림창 표출!
        if self.is_archive_encrypted and not pwd:
            messagebox.showwarning(
                t("pwd_required_title"),
                t("pwd_required_msg", name=os.path.basename(archive_path)),
            )
            if hasattr(self, "entry_extract_password"):
                self.entry_extract_password.focus_set()
            return

        if force_prompt:
            chosen_dir = filedialog.askdirectory(
                title=t("btn_choose_folder"),
                initialdir=archive_dir,
            )
            if not chosen_dir:
                return
            out_dir = chosen_dir
            real_result_dir = out_dir
        else:
            if self.has_single_root_folder:
                out_dir = archive_dir
                real_result_dir = (
                    os.path.join(archive_dir, self.single_root_folder_name)
                    if self.single_root_folder_name
                    else archive_dir
                )
            else:
                out_dir = os.path.join(archive_dir, folder_name)
                os.makedirs(out_dir, exist_ok=True)
                real_result_dir = out_dir

        # 동일한 파일 존재 여부 사전 검사 (파일 덮어쓰기 확인)
        entries = getattr(self, "archive_entries", None)
        if not entries:
            try:
                entries = list_archive_entries(archive_path, password=pwd)
                self.archive_entries = entries
            except Exception:
                entries = []

        conflicts = get_conflicting_extracted_files(entries, out_dir)
        if conflicts:
            dup_count = len(conflicts)
            sample_name = os.path.basename(conflicts[0])
            if dup_count == 1:
                confirm_msg = t("overwrite_confirm_single", name=sample_name)
            else:
                confirm_msg = t("overwrite_confirm_multi", count=dup_count, name=sample_name)

            overwrite = messagebox.askyesno(t("overwrite_confirm_title"), confirm_msg)
            if not overwrite:
                self.lbl_status.configure(text=t("status_extract_cancelled_overwrite"))
                self.progress_bar.set(0.0)
                return

        self.progress_bar.set(0.0)
        dest_display = os.path.basename(real_result_dir) or real_result_dir
        self.lbl_status.configure(text=t("status_extracting_to", dest=dest_display))

        def on_progress(info):
            pct = info["percentage"] / 100.0
            self.progress_bar.set(pct)
            cur_file = info.get("file", "").strip()
            if info.get("total") == 100:
                status_text = t(
                    "status_extract_prog_simple",
                    file=cur_file,
                    percent=info["percentage"],
                    elapsed=info["elapsed"],
                )
            else:
                proc = format_bytes(info.get("processed", 0))
                tot = format_bytes(info.get("total", 0))
                status_text = t(
                    "status_extract_prog_detail",
                    file=cur_file,
                    proc=proc,
                    tot=tot,
                    percent=info["percentage"],
                    elapsed=info["elapsed"],
                )
            self.lbl_status.configure(text=status_text)

        def on_finish(msg):
            self.progress_bar.set(1.0)
            self.lbl_status.configure(text=msg)
            open_folder = messagebox.askyesno(
                t("extract_finish_title"),
                t("extract_finish_msg", msg=msg, folder=real_result_dir),
            )
            if open_folder:
                try:
                    target_open = real_result_dir if os.path.exists(real_result_dir) else out_dir
                    target_norm = os.path.normpath(target_open)
                    if sys.platform == "win32":
                        try:
                            import ctypes
                            ctypes.windll.user32.AllowSetForegroundWindow(-1)
                        except Exception:
                            pass
                    if os.path.isfile(target_norm):
                        subprocess.Popen(["explorer.exe", f"/select,{target_norm}"])
                    else:
                        subprocess.Popen(["explorer.exe", target_norm])
                except Exception as e:
                    print(f"탐색기 열기 실패: {e}")
                    try:
                        os.startfile(target_open)
                    except Exception:
                        pass
                try:
                    self.lower()
                except Exception:
                    pass

            # 앱을 종료하지 않고 유지하며 다음 작업을 위해 뷰 초기화
            self._clear_extract_view()
            self.progress_bar.set(0.0)
            self.lbl_status.configure(text=f"{t('status_ready')} - {msg}")

        def on_error(err):
            err_str = str(err)
            lower_err = err_str.lower()
            if (
                "password_required" in lower_err
                or "wrong password" in lower_err
                or "data error in encrypted file" in lower_err
                or "cannot open encrypted" in lower_err
                or "headers error" in lower_err
            ):
                self.is_archive_encrypted = True
                # 비밀번호를 전혀 입력하지 않은 상태였다면 알림창 표출
                if not pwd:
                    messagebox.showwarning(
                        t("pwd_required_title"),
                        t("pwd_required_msg", name=os.path.basename(archive_path)),
                    )
                    if hasattr(self, "entry_extract_password"):
                        self.entry_extract_password.focus_set()
                    return
                else:
                    # 비밀번호를 입력했으나 틀린 경우
                    messagebox.showerror(
                        t("pwd_wrong_title"),
                        t("pwd_wrong_msg"),
                    )
                    if hasattr(self, "entry_extract_password"):
                        self.entry_extract_password.focus_set()
                        self.entry_extract_password.select_range(0, "end")
                    return

            self.lbl_status.configure(text=f"{t('dialog_error')}: {err}")
            messagebox.showerror(t("dialog_error"), t("err_extract_failed", err=err))

        self.worker.extract_async(
            archive_path=self.selected_archive_for_extract,
            output_dir=out_dir,
            password=pwd,
            on_progress=lambda info: self.after(0, lambda: on_progress(info)),
            on_finish=lambda msg: self.after(0, lambda: on_finish(msg)),
            on_error=lambda err: self.after(0, lambda: on_error(err)),
        )


def main():
    args = sys.argv[1:]

    # 1. 탐색기 우클릭 즉시 압축 핸들러
    if len(args) >= 2 and args[0] == "--compress-instant":
        target = args[1]
        run_instant_compress(target)
        sys.exit(0)

    # 2. 탐색기 우클릭 즉시 압축해제 핸들러
    if len(args) >= 2 and args[0] == "--extract-instant":
        archive = args[1]
        action = run_instant_extract(archive)
        if action == "LAUNCH_GUI":
            # 암호화 보호된 아카이브: 사용자 요구사항에 따라 GUI를 띄워 비밀번호 입력 유도
            app = Zipper9App()
            app._load_archive_for_extract(archive)
            if hasattr(app, "entry_extract_password"):
                app.entry_extract_password.focus_set()
            if hasattr(app, "lbl_status"):
                app.lbl_status.configure(
                    text=f"🔒 '{os.path.basename(archive)}' 암호로 보호됨. 상단 암호 입력란에 비밀번호를 입력해 주세요."
                )
            app.mainloop()
            sys.exit(0)
        else:
            sys.exit(0)

    # 3. 일반 실행 또는 파일/폴더 매개변수 전달 실행
    app = Zipper9App()
    if args:
        first_arg = args[0]
        if os.path.exists(first_arg):
            if is_archive_file(first_arg):
                app._load_archive_for_extract(first_arg)
            else:
                app.source_items.append(os.path.abspath(first_arg))
                app._update_sources_view()

    app.mainloop()


if __name__ == "__main__":
    main()
