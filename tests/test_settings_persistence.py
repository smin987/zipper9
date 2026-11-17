"""사용자 설정값 영구 저장 및 복원(Settings Persistence) 단위 테스트.
- load_settings, save_settings 파일 I/O 검증
- Zipper9App 인스턴스 설정 변경 시 자동 저장 및 재실행 시 복원 검증:
  * 테마 (Dark / Light)
  * 선택된 알고리즘 (7z / zstd / lz4 등)
  * 분할 압축 프리셋 (100 MB 등)
  * 파일명 암호화 여부 (True / False)
"""

import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from zipper9_ui.bridge.settings import (
    load_settings,
    save_settings,
    DEFAULT_SETTINGS,
)
from zipper9_ui.app import Zipper9App


class TestSettingsPersistence(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="zipper9_settings_test_")
        self.mock_settings_file = os.path.join(self.temp_dir, "test_settings.json")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load_settings(self):
        """기본 설정 저장 및 로드 파일 I/O 검증"""
        with patch("zipper9_ui.bridge.settings.get_settings_file_path", return_value=self.mock_settings_file):
            # 1. 파일 없을 때 기본값 로드
            loaded = load_settings()
            self.assertEqual(loaded["theme"], "Dark")
            self.assertEqual(loaded["selected_algo"], "zstd")

            # 2. 새 설정 저장
            new_data = dict(DEFAULT_SETTINGS)
            new_data["theme"] = "Light"
            new_data["selected_algo"] = "7z"
            new_data["split_preset"] = "100 MB"
            new_data["encrypt_filenames"] = True
            ok = save_settings(new_data)
            self.assertTrue(ok)
            self.assertTrue(os.path.isfile(self.mock_settings_file))

            # 3. 다시 로드하여 일치 여부 확인
            reloaded = load_settings()
            self.assertEqual(reloaded["theme"], "Light")
            self.assertEqual(reloaded["selected_algo"], "7z")
            self.assertEqual(reloaded["split_preset"], "100 MB")
            self.assertTrue(reloaded["encrypt_filenames"])
            print("Settings file I/O test passed successfully!")

    def test_app_settings_restoration(self):
        """Zipper9App GUI 인스턴스에서 설정 복원 및 저장 동작 검증"""
        with patch("zipper9_ui.bridge.settings.get_settings_file_path", return_value=self.mock_settings_file):
            # 사전에 저장된 커스텀 설정 준비
            custom_settings = {
                "theme": "Light",
                "selected_algo": "7z",
                "extra_algo": "다른 압축 알고리즘 선택...",
                "split_preset": "100 MB",
                "encrypt_filenames": True,
                "window_geometry": "950x720",
            }
            save_settings(custom_settings)

            # 앱 초기화 (설정 자동 복원 검증)
            app = Zipper9App()
            app.withdraw()  # 화면에 띄우지 않고 헤드리스 테스트

            try:
                # 1. 복원된 속성 검증
                self.assertEqual(app.selected_algo, "7z")
                self.assertEqual(app.combo_split.get(), "100 MB")
                self.assertTrue(bool(app.chk_encrypt_header.get()))

                # 2. GUI 상에서 값 변경 후 저장 테스트
                app._select_algo_card("lz4")
                app.combo_split.set("500 MB")
                app.save_current_settings()

                # 3. 설정 파일에 즉시 반영되었는지 확인
                saved_on_disk = load_settings()
                self.assertEqual(saved_on_disk["selected_algo"], "lz4")
                self.assertEqual(saved_on_disk["split_preset"], "500 MB")
                print("App GUI settings restoration and auto-save passed successfully!")

            finally:
                app.destroy()


if __name__ == "__main__":
    unittest.main()
