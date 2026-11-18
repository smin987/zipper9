"""
Zipper9 일반 파일과 압축 파일 혼합 드롭/추가 시 패키징 등록 동작 단위 테스트
"""

import os
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from zipper9_ui.app import Zipper9App


class TestDropAndPackageBehavior(unittest.TestCase):
    """일반 파일 유무에 따른 스마트 드롭(패키징 vs 압축해제) 동작 검증"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir_path = self.temp_dir.name

        # 테스트용 일반 파일 생성
        self.plain_file = os.path.join(self.dir_path, "sample.txt")
        with open(self.plain_file, "w", encoding="utf-8") as f:
            f.write("plain text content")

        # 테스트용 압축 파일(.zip) 생성
        self.zip_file = os.path.join(self.dir_path, "archive.zip")
        with zipfile.ZipFile(self.zip_file, "w") as zf:
            zf.writestr("inner.txt", "inside zip")

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("tkinter.messagebox.showinfo")
    def test_pure_archive_drop_triggers_extract(self, mock_msgbox):
        """1. 아무 파일도 없는 상태에서 압축 파일만 단독 드롭 시 -> 압축해제 탭으로 자동 전환"""
        app = Zipper9App()
        try:
            app.set_active_tab("compress")
            app.selected_sources.clear()

            # 순수 압축 파일 단독 드롭
            app._handle_drop_files_safe([self.zip_file])
            app.update()

            self.assertEqual(app.active_tab, "extract")
            self.assertEqual(app.selected_archive_for_extract, self.zip_file)
        finally:
            app.destroy()

    @patch("tkinter.messagebox.showinfo")
    def test_mixed_drop_triggers_compress_packaging(self, mock_msgbox):
        """2. 일반 파일과 압축 파일이 함께 드롭된 경우 -> 압축하기 탭 유지 및 모두 등록"""
        app = Zipper9App()
        try:
            app.set_active_tab("compress")
            app.selected_sources.clear()

            # 일반 파일 + 압축 파일 동시 드롭
            app._handle_drop_files_safe([self.plain_file, self.zip_file])
            app.update()

            self.assertEqual(app.active_tab, "compress")
            self.assertIn(self.plain_file, app.selected_sources)
            self.assertIn(self.zip_file, app.selected_sources)
            self.assertEqual(len(app.selected_sources), 2)
        finally:
            app.destroy()

    @patch("tkinter.messagebox.showinfo")
    def test_archive_added_when_plain_files_already_exist(self, mock_msgbox):
        """3. 이미 일반 파일이 등록된 상태에서 압축 파일 추가 드롭 시 -> 압축하기 탭 유지 및 함께 패키징"""
        app = Zipper9App()
        try:
            app.set_active_tab("compress")
            app.selected_sources = [self.plain_file]

            # 압축 파일 추가 드롭
            app._handle_drop_files_safe([self.zip_file])
            app.update()

            self.assertEqual(app.active_tab, "compress")
            self.assertIn(self.plain_file, app.selected_sources)
            self.assertIn(self.zip_file, app.selected_sources)
            self.assertEqual(len(app.selected_sources), 2)
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
