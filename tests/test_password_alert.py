import os
import shutil
import zipfile
import subprocess
from tkinter import messagebox
from zipper9_ui.app import Zipper9App

seven_path = os.path.abspath(r'tools\7z\7z.exe')

# 1. 암호 ZIP 생성
sample_file = "test_src_alert.txt"
with open(sample_file, "w", encoding="utf-8") as f:
    f.write("Secret data for alert test!")

out_zip = os.path.abspath("test_pwd_alert.zip")
cmd = [seven_path, 'a', '-tzip', '-y', '-pMySecretKey', out_zip, sample_file]
subprocess.run(cmd, capture_output=True)

# 2. GUI 앱 인스턴스화
app = Zipper9App()
app.withdraw()

# 3. 아카이브 로드
app._load_archive_for_extract(out_zip)
print("Is archive encrypted detected:", app.is_archive_encrypted)
assert app.is_archive_encrypted == True, "암호화된 아카이브가 감지되어야 합니다!"

# 4. 비밀번호 입력 없이 _start_extraction 실행 시 알림창(showwarning) 호출 가로채기 테스트
warning_called = [False]
warning_title = [""]
warning_msg = [""]

def mock_showwarning(title, message):
    warning_called[0] = True
    warning_title[0] = title
    warning_msg[0] = message
    print(f"Mock showwarning caught: [{title}] {message}")

old_showwarning = messagebox.showwarning
messagebox.showwarning = mock_showwarning

try:
    # 비밀번호 입력란이 비어있는 상태에서 해제 호출
    app.entry_extract_password.delete(0, "end")
    app._start_extraction()

    assert warning_called[0] == True, "비밀번호 미입력 시 알림창이 떠야 합니다!"
    assert "암호" in warning_title[0] or "비밀번호" in warning_title[0]
    assert "비밀번호" in warning_msg[0] or "암호" in warning_msg[0]
    print("Test: Warning messagebox successfully triggered when password not entered!")
finally:
    messagebox.showwarning = old_showwarning

app.destroy()
if os.path.exists(sample_file): os.remove(sample_file)
if os.path.exists(out_zip): os.remove(out_zip)

print("All Password Alert Tests Passed 100% Successfully!")
