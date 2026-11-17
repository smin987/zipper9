import os
import shutil
import subprocess
from zipper9_ui.app import (
    Zipper9App,
    is_archive_file,
    find_primary_archive,
    get_archive_folder_name,
)

def test_split_archive_detection_and_drop():
    seven_path = r'C:\Program Files\7-Zip\7z.exe'

    # 1. 확장자 및 아카이브 판별 테스트
    split_samples = [
        "archive.7z.001",
        "archive.7z.002",
        "archive.zip.001",
        "archive.zip.002",
        "backup.part1.rar",
        "backup.part2.rar",
        "data.z01",
        "data.z02",
        "file.001",
        "file.002",
        "test.alz",
        "test.a00",
        "test.egg",
        "test.vol1.egg",
    ]

    # 임시 파일 생성 후 is_archive_file 테스트
    temp_dir = os.path.abspath("test_split_tmp")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        for s in split_samples:
            p = os.path.join(temp_dir, s)
            with open(p, "w") as f:
                f.write("mock")
            assert is_archive_file(p) == True, f"{s} 가 아카이브로 인식되어야 합니다!"

        print("1. All split extensions recognized as archive successfully!")

        # 2. get_archive_folder_name 테스트
        assert get_archive_folder_name(os.path.join(temp_dir, "archive.7z.001")) == "archive"
        assert get_archive_folder_name(os.path.join(temp_dir, "archive.zip.001")) == "archive"
        assert get_archive_folder_name(os.path.join(temp_dir, "backup.part1.rar")) == "backup"
        assert get_archive_folder_name(os.path.join(temp_dir, "data.z01")) == "data"
        assert get_archive_folder_name(os.path.join(temp_dir, "file.001")) == "file"
        print("2. get_archive_folder_name cleaned split extensions cleanly!")

        # 3. find_primary_archive 볼륨 우선순위 테스트
        p_001 = os.path.join(temp_dir, "archive.7z.001")
        p_002 = os.path.join(temp_dir, "archive.7z.002")
        # 002가 먼저 리스트에 있어도 001이 우선 선택되어야 함
        selected = find_primary_archive([p_002, p_001])
        assert selected == p_001, f"001이 우선 선택되어야 함: {selected}"

        # 002만 드롭되었더라도 같은 디렉토리에 001이 있으면 001로 자동 교정
        selected_single_002 = find_primary_archive([p_002])
        assert selected_single_002 == p_001, f"002 단독 드롭 시 001로 자동 교정되어야 함: {selected_single_002}"

        print("3. find_primary_archive primary volume selection passed!")

        # 4. 실제 GUI 앱에서 드롭 시뮬레이션: 압축하기가 아닌 '스마트 압축해제' 탭으로 전환되는지 검증!
        # 실제 7z 분할 압축 생성
        src_txt = os.path.join(temp_dir, "source.txt")
        with open(src_txt, "w") as f:
            f.write("A" * 100000)

        out_7z = os.path.join(temp_dir, "real_split.7z")
        subprocess.run([seven_path, "a", "-t7z", "-v30k", out_7z, src_txt], capture_output=True)

        real_001 = os.path.join(temp_dir, "real_split.7z.001")
        real_002 = os.path.join(temp_dir, "real_split.7z.002")

        app = Zipper9App()
        app.withdraw()

        # 초기 탭은 compress
        assert app.active_tab == "compress"

        # 분할 압축 파일들을 드롭 처리
        app._handle_drop_files_safe([real_002, real_001])

        # 검증: 'extract' 탭으로 자동 전환되었는지!
        assert app.active_tab == "extract", f"분할 압축 파일 드롭 시 extract 탭으로 전환되어야 합니다! (현재: {app.active_tab})"
        assert app.selected_archive_for_extract == real_001, f"로드된 아카이브가 001이어야 합니다: {app.selected_archive_for_extract}"
        assert app.btn_extract_start.cget("text") == "⚡ 압축해제"

        # 목록에 실제 원본 파일만 있고 헤더 볼륨명(real_split.7z)이 없는지 검증
        entries = app.extract_preview.get("1.0", "end")
        assert "source.txt" in entries, "실제 압축된 source.txt가 미리보기에 나타나야 합니다!"
        assert "real_split.7z " not in entries, "분할 볼륨 헤더 파일명이 오염되어 들어가면 안 됩니다!"

        app.destroy()
        print("4. GUI Drag & Drop automatic transition to extract tab verified 100%!")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_split_archive_detection_and_drop()
    print("All Split Archive Drop Tests Passed Successfully!")
