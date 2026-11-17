import os
from zipper9_ui.app import Zipper9App

def test_compress_page_layout():
    app = Zipper9App()
    app.withdraw()

    try:
        # 1. page_compress 내 자식 위젯의 패킹 순서 검증
        children = app.page_compress.winfo_children()
        
        # 첫 번째 자식 프레임에 action_bar (대상 경로 및 압축하기 버튼)이 위치해야 함
        action_bar = children[0]
        assert app.lbl_compress_target_info.master == action_bar
        assert app.btn_compress_start.master.master == action_bar

        # 두 번째 자식이 source_scroll_frame (드래그 & 드롭 영역 컨테이너)이어야 함
        assert children[1] == getattr(app.source_scroll_frame, '_parent_frame', app.source_scroll_frame)

        # 세 번째 자식이 toolbar ([파일 추가][폴더 추가][전체 비우기])이어야 함
        toolbar = children[2]
        assert app.lbl_sources_summary.master == toolbar

        print("1. Compress page vertical widget hierarchy verified successfully!")

        # 2. 버튼 텍스트 및 고정 속성 검증
        assert app.btn_compress_start.cget("text") == "⚡ 압축하기"
        assert app.btn_compress_start.cget("width") == 110

        # 파일 추가 시뮬레이션
        sample_path = os.path.abspath("test_dummy.txt")
        with open(sample_path, "w") as f:
            f.write("dummy")

        app.selected_sources.append(sample_path)
        app._update_sources_view()

        # 파일 추가 후에도 버튼 텍스트는 간결하게 '⚡ 압축하기' 유지되고, 대상 정보는 라벨에 출력되는지 확인
        assert app.btn_compress_start.cget("text") == "⚡ 압축하기"
        target_info = app.lbl_compress_target_info.cget("text")
        assert "📍 대상:" in target_info
        assert os.path.dirname(sample_path) in target_info

        # 정리
        if os.path.exists(sample_path):
            os.remove(sample_path)

        app._clear_sources()
        assert app.btn_compress_start.cget("text") == "⚡ 압축하기"

        print("2. Button text consistency & width verification passed!")

        # 3. 압축해제 화면의 버튼 속성과 완벽 대칭/일치 검증
        assert app.btn_extract_start.cget("text") == "⚡ 압축해제"
        assert app.btn_extract_start.cget("width") == 110
        assert app.btn_extract_start.cget("height") == app.btn_compress_start.cget("height")

        print("3. Visual symmetry between Compress and Extract buttons verified 100%!")

    finally:
        app.destroy()

if __name__ == "__main__":
    test_compress_page_layout()
    print("All Compress Page Layout Tests Passed Successfully!")
