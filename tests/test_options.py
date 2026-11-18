from zipper9_ui.app import Zipper9App, parse_split_size

def run_options_test():
    # 1. 분할 크기 파싱 테스트
    assert parse_split_size("분할 안 함 (기본)") is None
    assert parse_split_size("10 MB (디스코드 무료)") == "10m"
    assert parse_split_size("25 MB (이메일 첨부)") == "25m"
    assert parse_split_size("100 MB") == "100m"
    assert parse_split_size("500 MB") == "500m"
    assert parse_split_size("1 GB") == "1g"
    assert parse_split_size("2 GB (네이버/다음 대용량)") == "2g"
    assert parse_split_size("4 GB (FAT32 한계)") == "4g"
    assert parse_split_size("150m") == "150m"
    assert parse_split_size("1.5g") == "1536m"
    assert parse_split_size("700") == "700m"
    print("parse_split_size tests passed successfully!")

    # 2. GUI 위젯 인스턴스 검증
    app = Zipper9App()
    app.withdraw()

    assert hasattr(app, "entry_password"), "entry_password 위젯 누락"
    assert hasattr(app, "btn_show_pwd"), "btn_show_pwd 위젯 누락"
    assert hasattr(app, "chk_encrypt_header"), "chk_encrypt_header 위젯 누락"
    assert hasattr(app, "combo_split"), "combo_split 위젯 누락"

    # 비밀번호 입력 및 토글 테스트
    app.entry_password.insert(0, "mypassword123")
    assert app.entry_password.cget("show") == "*"
    app._toggle_pwd_visibility()
    assert app.entry_password.cget("show") == ""
    app._toggle_pwd_visibility()
    assert app.entry_password.cget("show") == "*"

    # 분할 콤보박스 테스트
    app.combo_split.set("100 MB")
    assert parse_split_size(app.combo_split.get()) == "100m"

    app.destroy()
    print("GUI Option Widgets and Interactions passed successfully!")

if __name__ == "__main__":
    run_options_test()
