import os
import subprocess
from unittest.mock import patch
from tkinter import messagebox
from zipper9_ui.app import Zipper9App

def test_extract_finish_open_explorer():
    # 임시 zip 파일 생성
    seven_path = os.path.abspath(r'tools\7z\7z.exe')
    sample_file = "test_src_finish.txt"
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write("Test content")
    out_zip = os.path.abspath("test_finish_explorer.zip")
    subprocess.run([seven_path, 'a', '-tzip', '-y', out_zip, sample_file], capture_output=True)

    old_askyesno = messagebox.askyesno
    try:
        # Case 1: [확인] (Yes) 클릭 시 -> explorer.exe Popen 호출, 앱 종료하지 않고 유지, _clear_extract_view() 검증
        app1 = Zipper9App()
        app1.withdraw()
        app1._load_archive_for_extract(out_zip)

        destroy_called1 = [False]
        orig_destroy1 = app1.destroy
        def mock_app_destroy1():
            destroy_called1[0] = True
            orig_destroy1()
        app1.destroy = mock_app_destroy1

        clear_called1 = [False]
        orig_clear1 = app1._clear_extract_view
        def mock_app_clear1():
            clear_called1[0] = True
            orig_clear1()
        app1._clear_extract_view = mock_app_clear1

        askyesno_called1 = [False]
        def mock_yes(title, message):
            askyesno_called1[0] = True
            return True
        messagebox.askyesno = mock_yes

        def mock_extract_sync1(archive_path, output_dir, password=None, on_progress=None, on_finish=None, on_error=None):
            if on_finish:
                on_finish("테스트 압축 해제 완료")

        app1.worker.extract_async = mock_extract_sync1

        with patch("subprocess.Popen") as mock_popen:
            app1._start_extraction()
            try:
                app1.update()
            except Exception:
                pass

            assert askyesno_called1[0], "askyesno 팝업이 호출되어야 합니다."
            assert mock_popen.called, "explorer.exe Popen이 호출되어야 합니다."
            explorer_args = mock_popen.call_args[0][0]
            assert "explorer.exe" in explorer_args, f"explorer.exe가 인자에 포함되어야 합니다: {explorer_args}"
            assert not destroy_called1[0], "Case 1: [확인] 시 앱이 종료되지 않고 유지되어야 합니다!"
            assert clear_called1[0], "Case 1: [확인] 시 다음 작업을 위해 _clear_extract_view()가 호출되어야 합니다."
            print("Case 1 (Yes -> Open Explorer & Keep App Open) Passed 100%!", flush=True)

            orig_destroy1()

        # Case 2: [아니오] (No) 클릭 시 -> explorer 열지 않고 앱 창 유지, _clear_extract_view() 호출 검증
        app2 = Zipper9App()
        app2.withdraw()
        app2._load_archive_for_extract(out_zip)

        destroy_called2 = [False]
        orig_destroy2 = app2.destroy
        def mock_app_destroy2():
            destroy_called2[0] = True
            orig_destroy2()
        app2.destroy = mock_app_destroy2

        clear_called2 = [False]
        orig_clear2 = app2._clear_extract_view
        def mock_app_clear2():
            clear_called2[0] = True
            orig_clear2()
        app2._clear_extract_view = mock_app_clear2

        askyesno_called2 = [False]
        def mock_no(title, message):
            askyesno_called2[0] = True
            return False
        messagebox.askyesno = mock_no

        def mock_extract_sync2(archive_path, output_dir, password=None, on_progress=None, on_finish=None, on_error=None):
            if on_finish:
                on_finish("테스트 압축 해제 완료")

        app2.worker.extract_async = mock_extract_sync2

        with patch("subprocess.Popen") as mock_popen:
            app2._start_extraction()
            try:
                app2.update()
            except Exception:
                pass

            assert askyesno_called2[0], "askyesno 팝업이 호출되어야 합니다."
            assert not mock_popen.called, "아니오 시 explorer.exe Popen이 호출되지 않아야 합니다."
            assert not destroy_called2[0], "아니오 시 창이 닫히지 않아야 합니다."
            assert clear_called2[0], "아니오 시 다음 작업을 위해 _clear_extract_view()가 호출되어야 합니다."
            print("Case 2 (No -> Keep App Open & Clear View) Passed 100%!", flush=True)

            orig_destroy2()

    finally:
        messagebox.askyesno = old_askyesno
        if os.path.exists(sample_file): os.remove(sample_file)
        if os.path.exists(out_zip): os.remove(out_zip)

if __name__ == "__main__":
    test_extract_finish_open_explorer()
    print("All Explorer Finish Handler Tests Passed Successfully!", flush=True)
