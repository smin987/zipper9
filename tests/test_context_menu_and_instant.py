"""우클릭 메뉴 및 즉시 압축/해제(Instant Ops) 단위 테스트.
- context_menu: 레지스트리 등록/해제/상태 판별
- run_instant_compress: 일반 파일 우클릭 시 즉시 .zip 생성
- run_instant_extract: 암호 없는 아카이브 즉시 해제
- run_instant_extract: 암호 있는 아카이브 시 'LAUNCH_GUI' 반환 및 GUI 실행 분기 검증
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from zipper9_ui.bridge.context_menu import (
    register_context_menu,
    unregister_context_menu,
    is_context_menu_registered,
)
from zipper9_ui.bridge.instant_ops import (
    run_instant_compress,
    run_instant_extract,
    is_archive_password_protected,
)
from zipper9_ui.bridge.worker import CompressionWorker, find_7z_binary, list_archive_entries


class TestContextMenuAndInstant(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="zipper9_cm_test_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("zipper9_ui.bridge.context_menu.is_modern_package_registered", return_value=False)
    @patch("zipper9_ui.bridge.context_menu.register_modern_package", return_value=True)
    @patch("zipper9_ui.bridge.context_menu.unregister_modern_package", return_value=True)
    def test_context_menu_registration(self, mock_unreg, mock_reg, mock_is_modern):
        """우클릭 메뉴 등록 및 해제 동작 검증"""
        # 등록
        res_reg = register_context_menu()
        self.assertTrue(res_reg, "우클릭 메뉴 등록 실패")
        self.assertTrue(is_context_menu_registered(), "등록 상태 확인 실패")

        # 해제
        res_unreg = unregister_context_menu()
        self.assertTrue(res_unreg, "우클릭 메뉴 해제 실패")
        self.assertFalse(is_context_menu_registered(), "해제 후 상태 확인 실패")

        # 테스트 후 원래 상태 복원
        register_context_menu()

    @patch("zipper9_ui.bridge.instant_ops.show_native_notification")
    def test_instant_compress(self, mock_notify):
        """일반 파일 우클릭 즉시 압축 검증"""
        test_file = os.path.join(self.temp_dir, "document.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Hello zipper9 instant compress!")

        success = run_instant_compress(test_file)
        self.assertTrue(success, "즉시 압축 실패")

        expected_zip = os.path.join(self.temp_dir, "document.zip")
        self.assertTrue(os.path.isfile(expected_zip), f"압축 파일 미생성: {expected_zip}")
        self.assertGreater(os.path.getsize(expected_zip), 0)
        print("Instant compress test passed successfully!")

    @patch("zipper9_ui.bridge.instant_ops.show_native_notification")
    def test_instant_extract_normal(self, mock_notify):
        """암호 없는 압축파일 우클릭 즉시 해제 검증"""
        # 압축할 소스 파일 생성
        sub_dir = os.path.join(self.temp_dir, "sample_folder")
        os.makedirs(sub_dir, exist_ok=True)
        sample_file = os.path.join(sub_dir, "data.txt")
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("Extracted data payload")

        zip_path = os.path.join(self.temp_dir, "sample_archive.zip")
        worker = CompressionWorker()
        worker.compress_sync(
            source_paths=[sub_dir],
            output_archive_path=zip_path,
            format_type="zip",
            zip_method="zstd",
        )
        self.assertTrue(os.path.isfile(zip_path))

        # 즉시 해제 실행 (기존 파일과의 충돌 방지를 위해 원본 소스 폴더 제거 후 해제)
        shutil.rmtree(sub_dir, ignore_errors=True)
        res = run_instant_extract(zip_path)
        self.assertEqual(res, "SUCCESS")

        # 단일 폴더 통 압축이므로 sample_folder/data.txt가 해제되었는지 확인
        extracted_file = os.path.join(self.temp_dir, "sample_folder", "data.txt")
        self.assertTrue(os.path.isfile(extracted_file), f"해제된 파일 미발견: {extracted_file}")
        print("Instant extract normal test passed successfully!")

    @patch("zipper9_ui.bridge.instant_ops.show_native_notification")
    def test_instant_extract_password_triggers_gui(self, mock_notify):
        """비밀번호 보호된 압축파일 우클릭 시 GUI 런칭('LAUNCH_GUI') 반환 검증"""
        seven_zip = find_7z_binary()
        if not seven_zip:
            self.skipTest("7z 바이너리 없음")

        # 암호 걸린 7z 아카이브 생성
        src_file = os.path.join(self.temp_dir, "secret.txt")
        with open(src_file, "w", encoding="utf-8") as f:
            f.write("Super Confidential!")

        pwd_7z_path = os.path.join(self.temp_dir, "protected_secret.7z")
        import subprocess
        cmd = [seven_zip, "a", "-pmy_secret_123", "-mhe=on", pwd_7z_path, src_file]
        subprocess.run(cmd, capture_output=True, check=True)
        self.assertTrue(os.path.isfile(pwd_7z_path))

        # 암호화 감지 확인
        is_enc, _ = is_archive_password_protected(pwd_7z_path)
        self.assertTrue(is_enc, "암호화 보호 아카이브 감지 실패")

        # 즉시 해제 시도 시 LAUNCH_GUI 반환되는지 확인
        action = run_instant_extract(pwd_7z_path)
        self.assertEqual(action, "LAUNCH_GUI", "암호화 파일에 대해 LAUNCH_GUI를 반환하지 않았습니다!")
        print("Instant extract password-protected -> LAUNCH_GUI trigger verified successfully!")

    @patch("zipper9_ui.bridge.instant_ops.show_native_notification")
    def test_instant_extract_alz(self, mock_notify):
        """ALZ(.alz) 아카이브 우클릭 즉시 해제 및 파일 검증"""
        import base64
        # 62바이트짜리 유효한 테스트용 ALZ 아카이브 (내부에 data.txt -> 'unalz')
        SAMPLE_ALZ_B64 = "QUxaAQoAAABCTFoBCAAgQJqKWyAAAgAMBWQcBwAFAGRhdGEudHh0K81LzKkCAENMWgEAAAAAAAAAAENMWgI="
        alz_path = os.path.join(self.temp_dir, "test_archive.alz")
        with open(alz_path, "wb") as f:
            f.write(base64.b64decode(SAMPLE_ALZ_B64))

        # 내부 엔트리 목록 검사
        entries = list_archive_entries(alz_path)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["name"], "data.txt")

        # 즉시 해제 실행
        res = run_instant_extract(alz_path)
        self.assertEqual(res, "SUCCESS")

        extracted_file = os.path.join(self.temp_dir, "test_archive", "data.txt")
        self.assertTrue(os.path.isfile(extracted_file), f"해제된 파일 미발견: {extracted_file}")
        with open(extracted_file, "r") as f:
            self.assertEqual(f.read().strip(), "unalz")
        print("ALZ instant extract test passed successfully!")


if __name__ == "__main__":
    unittest.main()
