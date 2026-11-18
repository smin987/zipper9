"""우클릭 컨텍스트 메뉴 즉시 실행 (Instant Operations) 핸들러 모듈.

- --compress-instant: 일반 파일/폴더 우클릭 시 현재 폴더에 즉시 .zip 파일 생성
- --extract-instant: 압축 파일 우클릭 시 즉시 해제
  * 단, 암호가 걸려있는 경우 GUI를 실행하여 비밀번호 입력 유도
"""

import os
import sys
import threading
import time
from typing import Callable, Optional

import customtkinter as ctk

from zipper9_ui.bridge.worker import (
    CompressionWorker,
    list_archive_entries,
)
from zipper9_ui.bridge.i18n import t, set_language
from zipper9_ui.bridge.settings import load_settings


class InstantProgressDialog(ctk.CTk):
    """우클릭 즉시 압축/해제 전용 콤팩트 진행상태 다이얼로그.

    - 실시간 진행률 (%) 및 프로그레스바 표시
    - 현재 처리 중인 개별 파일명 및 경과 시간 표시
    - 취소 버튼 지원 (프로세스 즉시 중단 및 불완전 파일 정리)
    - 완료 시 완료음 재생 후 자동 종료
    """

    def __init__(
        self,
        title: str,
        operation_name: str,
        target_name: str,
        worker_task_fn: Callable[[CompressionWorker, Callable[[dict], None]], None],
        on_cancel_cleanup: Optional[Callable[[], None]] = None,
    ):
        super().__init__()

        self.worker_task_fn = worker_task_fn
        self.on_cancel_cleanup = on_cancel_cleanup
        self.worker = CompressionWorker()
        self.result_status = "PENDING"
        self.error_message: Optional[str] = None
        self.is_done = False
        self.start_time = time.time()
        self._timer_id: Optional[str] = None

        # 테마 적용
        try:
            settings = load_settings()
            saved_theme = settings.get("theme", "System")
            ctk.set_appearance_mode(saved_theme)
            ctk.set_default_color_theme("blue")
        except Exception:
            pass

        # 윈도우 속성 설정
        self.title(title)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        try:
            self.lift()
            self.focus_force()
        except Exception:
            pass

        # 앱 아이콘 설정
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            icon_path = os.path.join(base_dir, "tools", "icon.ico")
            if os.path.isfile(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

        # 창 크기 및 화면 중앙 배치
        dlg_width = 480
        dlg_height = 195
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, int((sw - dlg_width) / 2))
        y = max(0, int((sh - dlg_height) / 2))
        self.geometry(f"{dlg_width}x{dlg_height}+{x}+{y}")

        # 창 닫기(X) 클릭 시 취소 핸들러
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        # UI 위젯 구축
        mono_font = "Cascadia Mono" if sys.platform == "win32" else "monospace"

        container = ctk.CTkFrame(self, corner_radius=12, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=16)

        # 1. 헤더 (작업 타이틀 + 대상 이름 / 우측 백분율)
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 6))

        left_header = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_header.pack(side="left", fill="x", expand=True)

        lbl_op = ctk.CTkLabel(
            left_header,
            text=operation_name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#212529", "#f8f9fa"),
            anchor="w",
        )
        lbl_op.pack(fill="x")

        # 대상 파일명 말줄임
        disp_target = target_name
        if len(disp_target) > 36:
            disp_target = disp_target[:18] + "..." + disp_target[-15:]

        lbl_target = ctk.CTkLabel(
            left_header,
            text=disp_target,
            font=ctk.CTkFont(size=11),
            text_color=("#6c757d", "gray70"),
            anchor="w",
        )
        lbl_target.pack(fill="x")

        self.lbl_percentage = ctk.CTkLabel(
            header_frame,
            text="0%",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1c7ed6", "#4dabf7"),
            anchor="e",
            width=80,
        )
        self.lbl_percentage.pack(side="right")

        # 2. 프로그레스 바
        self.progress_bar = ctk.CTkProgressBar(
            container,
            height=12,
            corner_radius=6,
            progress_color=("#1c7ed6", "#4dabf7"),
        )
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", pady=(4, 8))

        # 3. 현재 처리 파일명
        self.lbl_file = ctk.CTkLabel(
            container,
            text="준비 중...",
            font=ctk.CTkFont(family=mono_font, size=10),
            text_color=("#868e96", "gray65"),
            anchor="w",
        )
        self.lbl_file.pack(fill="x", pady=(0, 10))

        # 4. 하단 바 (경과 시간 + 취소 버튼)
        bottom_frame = ctk.CTkFrame(container, fg_color="transparent")
        bottom_frame.pack(fill="x")

        self.lbl_time = ctk.CTkLabel(
            bottom_frame,
            text="⏱ 00:00",
            font=ctk.CTkFont(family=mono_font, size=11),
            text_color=("#868e96", "gray"),
            anchor="w",
        )
        self.lbl_time.pack(side="left")

        self.btn_cancel = ctk.CTkButton(
            bottom_frame,
            text="취소",
            width=72,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#e9ecef", "#2b2d30"),
            text_color=("#495057", "#e9ecef"),
            hover_color=("#fa5252", "#e03131"),
            command=self.on_cancel,
        )
        self.btn_cancel.pack(side="right")

        # 타이머 및 작업 스레드 시작
        self._update_timer()
        self._thread = threading.Thread(target=self._run_task, daemon=True)
        self._thread.start()

    def _update_timer(self):
        if self.is_done:
            return
        elapsed = time.time() - self.start_time
        m = int(elapsed // 60)
        s = int(elapsed % 60)
        try:
            self.lbl_time.configure(text=f"⏱ {m:02d}:{s:02d}")
            self._timer_id = self.after(500, self._update_timer)
        except Exception:
            pass

    def destroy(self):
        self.is_done = True
        if self._timer_id:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None
        super().destroy()

    def _on_progress_callback(self, info: dict):
        if self.is_done:
            return
        self.after(0, lambda: self._update_progress_ui(info))

    def _update_progress_ui(self, info: dict):
        if self.is_done:
            return
        pct = float(info.get("percentage", 0.0))
        norm_pct = min(max(pct / 100.0, 0.0), 1.0)
        self.progress_bar.set(norm_pct)
        self.lbl_percentage.configure(text=f"{int(pct)}%")

        cur_file = info.get("file", "").strip()
        if cur_file:
            if len(cur_file) > 46:
                cur_file = "..." + cur_file[-43:]
            self.lbl_file.configure(text=cur_file)

    def _run_task(self):
        try:
            self.worker_task_fn(self.worker, self._on_progress_callback)
            self.after(0, self._on_task_success)
        except Exception as e:
            self.after(0, lambda err=e: self._on_task_error(err))

    def _on_task_success(self):
        if self.is_done:
            return
        self.is_done = True
        self.result_status = "SUCCESS"
        self.progress_bar.set(1.0)
        self.lbl_percentage.configure(text="100%")
        self.lbl_file.configure(text="✨ 완료되었습니다!", text_color=("#2b8a3e", "#51cf66"))
        self.btn_cancel.configure(state="disabled")

        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass

        self.after(350, self.destroy)

    def _on_task_error(self, error: Exception):
        if self.is_done:
            return
        self.is_done = True
        err_msg = str(error)

        if "PASSWORD_REQUIRED" in err_msg or "wrong password" in err_msg.lower():
            self.result_status = "LAUNCH_GUI"
            self.destroy()
            return

        if "취소" in err_msg or self.result_status == "CANCEL":
            self.result_status = "CANCEL"
            if self.on_cancel_cleanup:
                try:
                    self.on_cancel_cleanup()
                except Exception:
                    pass
            self.destroy()
            return

        self.result_status = "ERROR"
        self.error_message = err_msg
        if self.on_cancel_cleanup:
            try:
                self.on_cancel_cleanup()
            except Exception:
                pass
        self.destroy()

    def on_cancel(self):
        if self.is_done:
            return
        self.is_done = True
        self.result_status = "CANCEL"
        self.btn_cancel.configure(text="취소 중...", state="disabled")
        self.lbl_file.configure(text="작업을 취소하고 있습니다...", text_color="#fa5252")
        self.worker.cancel()

        if self.on_cancel_cleanup:
            try:
                self.on_cancel_cleanup()
            except Exception:
                pass

        self.after(150, self.destroy)


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

    def do_compress(w: CompressionWorker, progress_cb: Callable[[dict], None]):
        w.compress_sync(
            source_paths=[target_abs],
            output_archive_path=out_zip,
            format_type="zip",
            zip_method="zstd",
            on_progress=progress_cb,
        )

    def cleanup_on_cancel():
        if os.path.isfile(out_zip):
            try:
                os.remove(out_zip)
            except Exception:
                pass

    dialog = InstantProgressDialog(
        title="⚡ zipper9 - 압축 진행 중",
        operation_name="압축 진행 중...",
        target_name=os.path.basename(target_abs),
        worker_task_fn=do_compress,
        on_cancel_cleanup=cleanup_on_cancel,
    )
    dialog.mainloop()

    if dialog.result_status == "SUCCESS":
        return True
    elif dialog.result_status == "CANCEL":
        return False
    else:
        if dialog.error_message:
            show_native_notification("압축 오류", f"압축 중 오류가 발생했습니다:\n{dialog.error_message}", is_error=True)
        return False


def run_instant_extract(archive_path: str) -> str:
    """압축 파일을 현재 위치에 즉시 해제합니다.
    Returns:
        "LAUNCH_GUI": 암호가 감지되어 GUI 창을 띄워야 함
        "SUCCESS": 압축 해제 성공
        "CANCEL": 사용자가 취소함
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

    def do_extract(w: CompressionWorker, progress_cb: Callable[[dict], None]):
        w.extract_sync(
            archive_path=archive_abs,
            output_dir=out_dir,
            password=None,
            on_progress=progress_cb,
        )

    def cleanup_on_cancel():
        try:
            worker = CompressionWorker()
            worker._cleanup_corrupted_extractions(out_dir, archive_abs, None)
        except Exception:
            pass

    dialog = InstantProgressDialog(
        title="⚡ zipper9 - 압축 해제 중",
        operation_name="압축 해제 중...",
        target_name=os.path.basename(archive_abs),
        worker_task_fn=do_extract,
        on_cancel_cleanup=cleanup_on_cancel,
    )
    dialog.mainloop()

    if dialog.result_status == "SUCCESS":
        return "SUCCESS"
    elif dialog.result_status == "LAUNCH_GUI":
        return "LAUNCH_GUI"
    elif dialog.result_status == "CANCEL":
        return "CANCEL"
    else:
        if dialog.error_message:
            show_native_notification("해제 오류", f"압축 해제 중 오류가 발생했습니다:\n{dialog.error_message}", is_error=True)
        return "ERROR"
