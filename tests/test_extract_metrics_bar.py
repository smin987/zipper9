"""
Zipper9 압축 해제 탭 슬림 1줄 3단 메트릭 카드(Extract Metric Cards) 단위 테스트
"""

import os
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from zipper9_ui.app import Zipper9App
from zipper9_ui.bridge.i18n import set_language


class TestExtractMetricsBar(unittest.TestCase):
    """압축 해제 화면의 3단 메트릭 카드 디자인 보존 및 가로 1줄 슬림 배치 검증"""

    def setUp(self):
        set_language("KO")
        self.temp_dir = tempfile.TemporaryDirectory()
        self.zip_path = os.path.join(self.temp_dir.name, "metrics_test.zip")
        with zipfile.ZipFile(self.zip_path, "w") as zf:
            zf.writestr("doc1.txt", "A" * 1024)
            zf.writestr("doc2.txt", "B" * 2048)

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("tkinter.messagebox.showinfo")
    def test_single_line_metric_cards_korean(self, mock_msgbox):
        """한글 모드에서 3단 카드의 디자인(title, value)이 유지되고 가로 1줄로 표출되며 sub 텍스트는 배제되는지 검증"""
        app = Zipper9App()
        try:
            app._on_language_change("KO")
            app.update()
            app._load_archive_for_extract(self.zip_path)
            app.update()

            # 3단 카드가 모두 정상 생성되었는지 확인
            self.assertIn("title", app.card_files)
            self.assertIn("value", app.card_files)
            self.assertNotIn("sub", app.card_files)  # 부가 텍스트 배제 확인

            self.assertIn("title", app.card_orig)
            self.assertIn("value", app.card_orig)
            self.assertNotIn("sub", app.card_orig)

            self.assertIn("title", app.card_ratio)
            self.assertIn("value", app.card_ratio)
            self.assertNotIn("sub", app.card_ratio)

            # 한글 라벨 및 수치 검증
            self.assertEqual(app.card_files["title"].cget("text"), "📊 총 파일 수")
            self.assertIn("2 개", app.card_files["value"].cget("text"))

            self.assertEqual(app.card_orig["title"].cget("text"), "💾 원본 용량")
            self.assertIn("KB", app.card_orig["value"].cget("text"))

            self.assertEqual(app.card_ratio["title"].cget("text"), "📉 압축 절감률")
            self.assertIn("%", app.card_ratio["value"].cget("text"))

            # 제목: 검은색 굵은 글씨 검증
            self.assertEqual(app.card_files["title"].cget("text_color"), ("#000000", "#f8f9fa"))
            self.assertEqual(app.card_orig["title"].cget("text_color"), ("#000000", "#f8f9fa"))
            self.assertEqual(app.card_ratio["title"].cget("text_color"), ("#000000", "#f8f9fa"))

            # 결과값: 15.6%와 동일한 파스텔 민트색(#20c997) 적용 검증
            self.assertEqual(app.card_files["value"].cget("text_color"), "#20c997")
            self.assertEqual(app.card_orig["value"].cget("text_color"), "#20c997")
            self.assertEqual(app.card_ratio["value"].cget("text_color"), "#20c997")

            # 하단 파일 목록 텍스트박스가 230 이상으로 확장되었는지 확인
            self.assertGreaterEqual(app.extract_preview.cget("height"), 230)
        finally:
            app.destroy()

    @patch("tkinter.messagebox.showinfo")
    def test_single_line_metric_cards_english(self, mock_msgbox):
        """영문 모드에서 3단 카드가 영문 라벨로 정상 전환되는지 검증"""
        app = Zipper9App()
        try:
            app._on_language_change("EN")
            app.update()
            app._load_archive_for_extract(self.zip_path)
            app.update()

            self.assertEqual(app.card_files["title"].cget("text"), "📊 Total Files")
            self.assertIn("items", app.card_files["value"].cget("text"))

            self.assertEqual(app.card_orig["title"].cget("text"), "💾 Uncompressed Size")
            self.assertEqual(app.card_ratio["title"].cget("text"), "📉 Space Saved")
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
