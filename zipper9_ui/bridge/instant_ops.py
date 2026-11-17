"""우클릭 컨텍스트 메뉴 즉시 실행 (Instant Operations) 핸들러 모듈.

- --compress-instant: 일반 파일/폴더 우클릭 시 현재 폴더에 즉시 .zip 파일 생성
- --extract-instant: 압축 파일 우클릭 시 즉시 해제
  * 단, 암호가 걸려있는 경우 GUI를 실행하여 비밀번호 입력 유도
"""

import os
import sys
import time
from typing import Optional

from zipper9_ui.bridge.worker import (
    CompressionWorker,
    list_archive_entries,
)
from zipper9_ui.bridge.i18n import t, set_language
from zipper9_ui.bridge.settings import load_settings


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


def check_archive_has_single_root_folder(entries: list) -> tuple[bool, Optional[str]]:
    """아카이브 내부가 단일 최상위 폴더 1개에 통으로 묶여있는지 판별."""
    if not entries:
        return False, None

    root_items = set()
    has_root_file = False

    for e in entries:
        name = e.get("name", "").replace("\\", "/").strip("/")
        if not name:
            continue
        parts = name.split("/")
        if parts[0] in ("__MACOSX", ".DS_Store"):
            continue

        root_name = parts[0]
        root_items.add(root_name)
        if len(parts) == 1 and not e.get("is_dir", False):
            has_root_file = True

    if len(root_items) == 1 and not has_root_file:
        single_name = list(root_items)[0]
        return True, single_name
    return False, None


def get_conflicting_extracted_files(entries: list, output_dir: str) -> list[str]:
    """해제 대상 디렉터리에 이미 존재하는 파일들의 목록을 반환"""
    conflicts = []
    if not entries or not output_dir:
        return conflicts
    for e in entries:
        if e.get("is_dir", False):
            continue
        name = e.get("name", "").strip()
        if not name:
            continue
        rel_path = name.replace("/", os.sep).replace("\\", os.sep)
        full_path = os.path.join(output_dir, rel_path)
        if os.path.isfile(full_path):
            conflicts.append(full_path)
    return conflicts


def get_archive_folder_name(archive_path: str) -> str:
    """압축 파일명에서 확장자를 제거하여 해제 대상 기본 폴더명 반환"""
    import re
    base = os.path.basename(archive_path)
    base = re.sub(r"\.(?:7z|zip|tar|rar|gz|xz|bz2|lz4|zst)\.\d{3}$", "", base, flags=re.IGNORECASE)
    base = re.sub(r"\.part\d+\.rar$", "", base, flags=re.IGNORECASE)
    base = re.sub(r"\.vol\d+(?:\+\d+)?\.egg$", "", base, flags=re.IGNORECASE)
    base = re.sub(r"\.\d{3}$", "", base)
    base = re.sub(r"\.[za]\d{2,}$", "", base, flags=re.IGNORECASE)
    base = re.sub(r"\.r\d{2,}$", "", base, flags=re.IGNORECASE)

    lower = base.lower()
    for de in [".tar.gz", ".tar.xz", ".tar.bz2", ".tar.lz4", ".tar.zst", ".tgz", ".txz", ".tbz2"]:
        if lower.endswith(de):
            return base[: -len(de)]
    return os.path.splitext(base)[0]


def is_archive_password_protected(archive_path: str) -> tuple[bool, Optional[list]]:
    """아카이브의 암호화 여부를 검사합니다.
    Returns:
        (is_encrypted, entries_list_if_accessible)
    """
    try:
        entries = list_archive_entries(archive_path, password=None)
        has_encrypted_entry = any(e.get("is_encrypted", False) for e in entries)
        return has_encrypted_entry, entries
    except PermissionError:
        # 7z 헤더 암호화 등
        return True, None
    except Exception:
        return False, None


def show_native_notification(title: str, message: str, is_error: bool = False):
    """Windows 네이티브 알림 표시 (ctypes MessageBoxW)"""
    if sys.platform == "win32":
        try:
            import ctypes
            # MB_OK(0x0) | MB_ICONINFORMATION(0x40) or MB_ICONERROR(0x10) | MB_SYSTEMMODAL(0x1000)
            icon = 0x10 if is_error else 0x40
            flags = 0x0 | icon | 0x1000
            ctypes.windll.user32.MessageBoxW(0, message, title, flags)
            return
        except Exception:
            pass
    print(f"[{title}] {message}")


def run_instant_compress(target_path: str) -> bool:
    """일반 파일 또는 폴더를 현재 위치에 초고속 .zip으로 즉시 압축합니다."""
    try:
        set_language(load_settings().get("language", "KO"))
    except Exception:
        pass

    if not os.path.exists(target_path):
        show_native_notification(t("dialog_error"), f"대상을 찾을 수 없습니다:\n{target_path}", is_error=True)
        return False

    target_abs = os.path.abspath(target_path)
    target_dir = os.path.dirname(target_abs)
    base_name = os.path.basename(target_abs)
    if os.path.isfile(target_abs):
        base_name = os.path.splitext(base_name)[0]

    out_zip = get_unique_filepath(target_dir, base_name, ".zip")

    worker = CompressionWorker()
    start_time = time.time()
    try:
        worker.compress_sync(
            source_paths=[target_abs],
            output_archive_path=out_zip,
            format_type="zip",
            zip_method="zstd",
        )
        elapsed = time.time() - start_time
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass
        return True
    except Exception as e:
        show_native_notification("압축 오류", f"압축 중 오류가 발생했습니다:\n{e}", is_error=True)
        return False


def run_instant_extract(archive_path: str) -> str:
    """압축 파일을 현재 위치에 즉시 해제합니다.
    Returns:
        "LAUNCH_GUI": 암호가 감지되어 GUI 창을 띄워야 함
        "SUCCESS": 압축 해제 성공
        "ERROR": 오류 발생
    """
    try:
        set_language(load_settings().get("language", "KO"))
    except Exception:
        pass

    if not os.path.exists(archive_path):
        show_native_notification(t("dialog_error"), f"압축 파일을 찾을 수 없습니다:\n{archive_path}", is_error=True)
        return "ERROR"

    archive_abs = os.path.abspath(archive_path)

    # 1. 암호화 여부 사전 검사
    is_encrypted, entries = is_archive_password_protected(archive_abs)
    if is_encrypted:
        # 암호가 있으면 GUI를 실행하도록 신호 반환
        return "LAUNCH_GUI"

    # 2. 암호가 없으므로 스마트 폴더링 후 즉시 해제
    archive_dir = os.path.dirname(archive_abs)
    is_single_root, single_root_name = check_archive_has_single_root_folder(entries or [])

    if is_single_root:
        # 단일 폴더 통 압축이면 현재 폴더에 바로 풀어서 이중 폴더 방지
        out_dir = archive_dir
    else:
        # 루트에 파일들이 흩어져 있으면 아카이브명으로 폴더를 만들어서 안전하게 해제
        folder_name = get_archive_folder_name(archive_abs)
        out_dir = os.path.join(archive_dir, folder_name)

    # 3. 동일한 파일 존재 여부 사전 검사
    conflicts = get_conflicting_extracted_files(entries or [], out_dir)
    if conflicts:
        dup_count = len(conflicts)
        sample_name = os.path.basename(conflicts[0])
        if dup_count == 1:
            confirm_msg = t("overwrite_confirm_single", name=sample_name)
        else:
            confirm_msg = t("overwrite_confirm_multi", count=dup_count, name=sample_name)

        if sys.platform == "win32":
            try:
                import ctypes
                # MB_YESNO(0x4) | MB_ICONQUESTION(0x20) | MB_SYSTEMMODAL(0x1000)
                res = ctypes.windll.user32.MessageBoxW(
                    0, confirm_msg, t("overwrite_confirm_title"), 0x4 | 0x20 | 0x1000
                )
                if res != 6:  # IDYES == 6
                    return "CANCEL"
            except Exception:
                pass

    os.makedirs(out_dir, exist_ok=True)

    worker = CompressionWorker()
    start_time = time.time()
    try:
        worker.extract_sync(
            archive_path=archive_abs,
            output_dir=out_dir,
            password=None,
        )
        elapsed = time.time() - start_time
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass
        return "SUCCESS"
    except Exception as e:
        err_msg = str(e)
        if "PASSWORD_REQUIRED" in err_msg or "wrong password" in err_msg.lower():
            # 해제 시점에 암호 에러가 감지된 경우에도 GUI로 유도
            return "LAUNCH_GUI"
        show_native_notification("해제 오류", f"압축 해제 중 오류가 발생했습니다:\n{e}", is_error=True)
        return "ERROR"
