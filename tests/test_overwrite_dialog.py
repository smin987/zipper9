import os
import shutil
import subprocess
from unittest.mock import patch, MagicMock
from tkinter import messagebox
from zipper9_ui.app import Zipper9App, get_conflicting_extracted_files

def test_overwrite_confirmation():
    seven_path = os.path.abspath(r'tools\7z\7z.exe')
    
    # 1. 임시 아카이브 생성 (test_file1.txt, test_file2.txt 포함)
    src_dir = os.path.abspath("test_overwrite_src")
    os.makedirs(src_dir, exist_ok=True)
    file1 = os.path.join(src_dir, "test_file1.txt")
    file2 = os.path.join(src_dir, "test_file2.txt")
    with open(file1, "w", encoding="utf-8") as f:
        f.write("New Archive Content 1")
    with open(file2, "w", encoding="utf-8") as f:
        f.write("New Archive Content 2")

    out_zip = os.path.abspath("test_overwrite.zip")
    subprocess.run([seven_path, 'a', '-tzip', '-y', out_zip, file1, file2], capture_output=True)

    # 2. 압축이 풀릴 대상 폴더 및 이미 존재하는 파일 생성
    # get_archive_folder_name("test_overwrite.zip") -> "test_overwrite"
    archive_dir = os.path.dirname(out_zip)
    target_extract_dir = os.path.join(archive_dir, "test_overwrite")
    os.makedirs(target_extract_dir, exist_ok=True)

    # 대상 디렉터리에 test_file1.txt 미리 생성 (충돌 유발)
    existing_file = os.path.join(target_extract_dir, "test_file1.txt")
    with open(existing_file, "w", encoding="utf-8") as f:
        f.write("Old Existing Content")

    try:
        app = Zipper9App()
        app.withdraw()
        app._load_archive_for_extract(out_zip)

        # 1. get_conflicting_extracted_files 유틸 함수 단독 검증
        conflicts = get_conflicting_extracted_files(app.archive_entries, target_extract_dir)
        assert len(conflicts) == 1, f"충돌 파일 1개가 감지되어야 합니다: {conflicts}"
        assert os.path.basename(conflicts[0]) == "test_file1.txt"
        print("Subtest 1: Conflict detection logic passed 100%!")

        # 2. Case A: '아니오' (False) 선택 시 작업 중단 검증
        askyesno_called = [False]
        askyesno_title = [""]
        askyesno_msg = [""]

        def mock_no(title, msg):
            askyesno_called[0] = True
            askyesno_title[0] = title
            askyesno_msg[0] = msg
            return False

        old_askyesno = messagebox.askyesno
        messagebox.askyesno = mock_no

        mock_worker_called = [False]
        def mock_extract_async(*args, **kwargs):
            mock_worker_called[0] = True

        app.worker.extract_async = mock_extract_async

        try:
            app._start_extraction()

            assert askyesno_called[0], "동일 파일 존재 시 askyesno 대화상자가 반드시 호출되어야 합니다!"
            assert "덮어쓰기" in askyesno_title[0], f"제목에 '덮어쓰기'가 포함되어야 합니다: {askyesno_title[0]}"
            assert "파일이 존재합니다. 덮어쓰시겠습니까?" in askyesno_msg[0], (
                f"메시지에 정확한 사용자 지정 문구가 포함되어야 합니다: {askyesno_msg[0]}"
            )
            assert not mock_worker_called[0], "'아니오' 선택 시 압축 해제 작업이 중단되어야 합니다!"
            assert "취소" in app.lbl_status.cget("text"), f"상태바에 취소 문구가 표출되어야 합니다: {app.lbl_status.cget('text')}"
            print("Subtest 2: 'No' -> Abort extraction passed 100%!")

            # 기존 파일 내용이 유지되었는지 검증
            with open(existing_file, "r", encoding="utf-8") as f:
                content = f.read()
            assert content == "Old Existing Content", "작업 중단 시 기존 파일이 보존되어야 합니다!"

        finally:
            messagebox.askyesno = old_askyesno

        # 3. Case B: '예' (True) 선택 시 덮어쓰기 계속 진행 검증
        askyesno_called_yes = [False]
        def mock_yes(title, msg):
            askyesno_called_yes[0] = True
            return True

        messagebox.askyesno = mock_yes
        mock_worker_called_yes = [False]
        def mock_extract_async_yes(*args, **kwargs):
            mock_worker_called_yes[0] = True

        app.worker.extract_async = mock_extract_async_yes

        try:
            app._start_extraction()
            assert askyesno_called_yes[0], "동일 파일 존재 시 askyesno가 호출되어야 합니다."
            assert mock_worker_called_yes[0], "'예' 선택 시 압축 해제가 계속 진행되어야 합니다!"
            print("Subtest 3: 'Yes' -> Continue extraction & overwrite passed 100%!")
        finally:
            messagebox.askyesno = old_askyesno

        app.destroy()

    finally:
        if os.path.exists(src_dir):
            shutil.rmtree(src_dir, ignore_errors=True)
        if os.path.exists(out_zip):
            os.remove(out_zip)
        if os.path.exists(target_extract_dir):
            shutil.rmtree(target_extract_dir, ignore_errors=True)

if __name__ == "__main__":
    test_overwrite_confirmation()
    print("All Overwrite Confirmation Tests Passed Successfully!")
