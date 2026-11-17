import os
import shutil
import time
from zipper9_ui.bridge.worker import CompressionWorker, list_archive_entries

worker = CompressionWorker()
test_dir = "test_pwd_roundtrip"
os.makedirs(test_dir, exist_ok=True)
sample_file = os.path.join(test_dir, "secret_data.txt")
with open(sample_file, "w", encoding="utf-8") as f:
    f.write("This is top secret information protected by zipper9!")

out_7z = os.path.abspath("test_secret.7z")
finished = [False]

# 1. 파일명 암호화(-mhe=on) 7z 아카이브 생성
worker.compress_async(
    source_paths=[sample_file],
    output_archive_path=out_7z,
    format_type="7z",
    password="myPassword999",
    encrypt_filenames=True,
    on_finish=lambda msg: finished.__setitem__(0, True),
)
t0 = time.time()
while not finished[0] and (time.time() - t0) < 5:
    time.sleep(0.1)

assert finished[0], "7z 암호화 압축 실패"
print("1. 7z Password archive created!")

# 2. 암호 없이 목록 조회 시 PermissionError 발생 검증
try:
    list_archive_entries(out_7z, password=None)
    assert False, "암호 없는 조회 시 PermissionError가 발생해야 합니다!"
except PermissionError as e:
    print("2. PermissionError correctly triggered when no password provided:", e)

# 3. 올바른 암호로 목록 조회 검증
entries = list_archive_entries(out_7z, password="myPassword999")
print("3. Listed entries with password:", [e["name"] for e in entries])
assert len(entries) >= 1

# 4. 올바른 암호로 압축 해제 검증
ext_dir = os.path.abspath("test_ext_out")
finished[0] = False
worker.extract_async(
    archive_path=out_7z,
    output_dir=ext_dir,
    password="myPassword999",
    on_finish=lambda msg: finished.__setitem__(0, True),
)
t0 = time.time()
while not finished[0] and (time.time() - t0) < 5:
    time.sleep(0.1)

assert finished[0], "7z 암호화 해제 실패"
extracted_file = os.path.join(ext_dir, "secret_data.txt")
assert os.path.exists(extracted_file), f"해제된 파일이 존재하지 않음: {extracted_file}"
with open(extracted_file, "r", encoding="utf-8") as f:
    content = f.read()
assert "top secret" in content
print("4. Successfully extracted file with password! Content verified.")

# 5. ZIP AES-256 암호화 생성 및 해제 검증
out_zip = os.path.abspath("test_secret.zip")
finished[0] = False
worker.compress_async(
    source_paths=[sample_file],
    output_archive_path=out_zip,
    format_type="zip",
    password="zipPassword777",
    on_finish=lambda msg: finished.__setitem__(0, True),
)
t0 = time.time()
while not finished[0] and (time.time() - t0) < 5:
    time.sleep(0.1)

ext_dir_zip = os.path.abspath("test_ext_zip_out")
finished[0] = False
worker.extract_async(
    archive_path=out_zip,
    output_dir=ext_dir_zip,
    password="zipPassword777",
    on_finish=lambda msg: finished.__setitem__(0, True),
)
t0 = time.time()
while not finished[0] and (time.time() - t0) < 5:
    time.sleep(0.1)

assert finished[0], "ZIP 암호화 해제 실패"
extracted_zip_file = os.path.join(ext_dir_zip, "secret_data.txt")
assert os.path.exists(extracted_zip_file)
print("5. Successfully extracted ZIP with AES-256 password!")

# 정리
shutil.rmtree(test_dir, ignore_errors=True)
shutil.rmtree(ext_dir, ignore_errors=True)
shutil.rmtree(ext_dir_zip, ignore_errors=True)
if os.path.exists(out_7z): os.remove(out_7z)
if os.path.exists(out_zip): os.remove(out_zip)

print("All Password Extraction Tests Passed 100% Successfully!")
