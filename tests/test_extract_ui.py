import os
import subprocess
from zipper9_ui.app import Zipper9App

def test_extract_button_and_labels():
    seven_path = r'C:\Program Files\7-Zip\7z.exe'
    sample_file = "test_src_btn.txt"
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write("Button layout test data")

    out_zip = os.path.abspath("test_btn_layout.zip")
    cmd = [seven_path, 'a', '-tzip', '-y', out_zip, sample_file]
    subprocess.run(cmd, capture_output=True)

    try:
        app = Zipper9App()
        app.withdraw()

        # 1. 압축해제 화면의 최상단 액션바 및 버튼 순서(원래 버전: [위치 지정...] -> [⚡ 압축해제]) 검증
        assert app.btn_extract_start.cget("text") == "⚡ 압축해제", f"초기 버튼 텍스트 불일치: {app.btn_extract_start.cget('text')}"
        
        # 액션바가 드래그 & 드롭 영역 상단(0번째 자식)에 위치해야 함
        extract_children = app.page_extract.winfo_children()
        action_bar = extract_children[0]
        assert app.lbl_extract_target_info.master == action_bar
        assert app.btn_extract_start.master.master == action_bar

        btn_box_children = app.btn_extract_start.master.winfo_children()
        extract_idx = btn_box_children.index(app.btn_extract_start)
        custom_idx = next(i for i, w in enumerate(btn_box_children) if getattr(w, '_text', '') == '위치 지정...')
        assert custom_idx < extract_idx, f"위치지정 버튼이 압축해제 버튼보다 앞에 위치해야 합니다 (원래버전)! custom_idx={custom_idx}, extract_idx={extract_idx}"

        # 2. 아카이브 로드 후에도 버튼 텍스트가 경로에 가려지거나 길어지지 않고 '⚡ 압축해제'인지 검증
        app._load_archive_for_extract(out_zip)
        assert app.btn_extract_start.cget("text") == "⚡ 압축해제", f"로드 후 버튼 텍스트 불일치: {app.btn_extract_start.cget('text')}"

        # 3. 대상 정보 레이블에 정상적으로 경로 안내가 표기되는지 검증
        target_info = app.lbl_extract_target_info.cget("text")
        assert "📍 대상:" in target_info or "해제 위치:" in target_info, f"대상 안내 정보 불일치: {target_info}"

        # 4. 초기화 후에도 '⚡ 압축해제' 유지되는지 검증
        app._clear_extract_view()
        assert app.btn_extract_start.cget("text") == "⚡ 압축해제", f"초기화 후 버튼 텍스트 불일치: {app.btn_extract_start.cget('text')}"

        app.destroy()
        print("Test: Extract button text & layout test passed 100%!")
    finally:
        if os.path.exists(sample_file): os.remove(sample_file)
        if os.path.exists(out_zip): os.remove(out_zip)

if __name__ == "__main__":
    test_extract_button_and_labels()
