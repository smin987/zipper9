import os
import tempfile
from tkinter import messagebox
from zipper9_ui.bridge.worker import list_archive_entries
from zipper9_ui.app import Zipper9App
from zipper9_ui.bridge.i18n import t

def test_unsupported_archive_backend():
    """7-Zip이 지원하지 않는 가짜/콘솔 아카이브 파일에 대해 ValueError 발생 여부 검증"""
    with tempfile.NamedTemporaryFile(suffix=".iso", delete=False) as f:
        f.write(b"NOT_A_VALID_ISO_OR_ARCHIVE_DATA_1234567890")
        dummy_iso = f.name

    try:
        # 가짜 iso 파일은 7z가 열 수 없으므로 ValueError 발생해야 함
        raised = False
        try:
            list_archive_entries(dummy_iso)
        except ValueError as e:
            raised = True
            assert "UNSUPPORTED_ARCHIVE" in str(e)
        assert raised, "가짜 iso 파일에 대해 ValueError가 발생해야 합니다."
        print("Backend test passed: ValueError successfully raised for invalid archive.")
    finally:
        if os.path.exists(dummy_iso):
            os.remove(dummy_iso)

    # 실제 Wii ROM 파일이 존재하는 경우 실물 파일로도 검증
    wii_iso = r"D:\mirror\GAME\Wii\Wii Roms\Virtua Striker 2002.iso"
    if os.path.exists(wii_iso):
        raised_wii = False
        try:
            list_archive_entries(wii_iso)
        except ValueError as e:
            raised_wii = True
            assert "UNSUPPORTED_ARCHIVE" in str(e)
        assert raised_wii, "Virtua Striker 2002.iso에 대해 ValueError가 발생해야 합니다."
        print("Backend test passed: Virtua Striker 2002.iso correctly raised ValueError.")


def test_unsupported_archive_drop_ui():
    """드롭 시 미지원 아카이브인 경우 경고창 표출 및 압축풀기 탭 진입 차단 검증"""
    with tempfile.NamedTemporaryFile(suffix=".iso", delete=False) as f:
        f.write(b"NOT_A_VALID_ISO_OR_ARCHIVE_DATA_1234567890")
        dummy_iso = f.name

    app = Zipper9App()
    app.withdraw()

    warning_events = []
    def mock_showwarning(title, message):
        warning_events.append({"title": title, "message": message})
        print(f"[Mock showwarning] {title}: {message}")

    old_showwarning = messagebox.showwarning
    messagebox.showwarning = mock_showwarning

    try:
        # 1. 초기 탭은 compress 확인
        assert app.active_tab == "compress"

        # 2. 미지원 .iso 파일 드롭 시뮬레이션
        app._handle_drop_files_safe([dummy_iso])

        # 3. 경고창 표출 여부 확인
        assert len(warning_events) == 1, "경고창이 정확히 1회 표시되어야 합니다."
        lang = getattr(app, "current_lang", "KO")
        expected_msg = t("err_unsupported_archive_format", lang=lang)
        assert warning_events[0]["message"] == expected_msg, f"경고 메시지 불일치: {warning_events[0]['message']} vs {expected_msg}"

        # 4. 화면이 extract로 자동 진입하지 않고 compress에 그대로 유지되어야 함!
        assert app.active_tab == "compress", "미지원 파일 드롭 시 압축 풀기 탭으로 전환되지 않아야 합니다."

        # 5. 상태표시줄에도 미지원 포맷 메시지 표시 확인
        assert expected_msg in app.lbl_status.cget("text")

        # 6. 직접 _load_archive_for_extract 호출 시에도 차단되는지 확인
        warning_events.clear()
        app._load_archive_for_extract(dummy_iso)
        assert len(warning_events) == 1, "직접 로드 시에도 경고창이 표시되어야 합니다."
        assert app.active_tab == "compress", "직접 로드 실패 시에도 extract 탭으로 전환되지 않아야 합니다."

        print("UI test passed: Unsupported archive properly intercepted without switching tabs.")
    finally:
        messagebox.showwarning = old_showwarning
        app.destroy()
        if os.path.exists(dummy_iso):
            os.remove(dummy_iso)

if __name__ == "__main__":
    test_unsupported_archive_backend()
    test_unsupported_archive_drop_ui()
    print("All unsupported archive alert tests passed 100%!")
