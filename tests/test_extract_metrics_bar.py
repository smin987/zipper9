"""
Zipper9 압축 해제 탭 1줄 메트릭 요약 바(Extract Metrics Summary Bar) 단위 테스트
"""

import os
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from zipper9_ui.app import Zipper9App
from zipper9_ui.bridge.i18n import set_language


class TestExtractMetricsBar(unittest.TestCase):
    """압축 해제 화면의 1줄 메트릭 요약 바 표출 및 다국어 렌더링 검증"""

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
    def test_single_line_metrics_summary_korean(self, mock_msgbox):
        """한글 모드에서 '총 파일 수 N개, 원본 용량 X, 압축 절감률 Y%' 형식으로 1줄 표출되는지 검증"""
        app = Zipper9App()
        try:
            app._on_language_change("KO")
            app.update()
            app._load_archive_for_extract(self.zip_path)
            app.update()

            summary_text = app.lbl_extract_metrics_summary.cget("text")
            self.assertIn("총 파일 수 2개", summary_text)
            self.assertIn("원본 용량", summary_text)
            self.assertIn("압축 절감률", summary_text)
            self.assertIn("%", summary_text)

            # 불필요한 부가 카드 텍스트가 없는지 확인
            self.assertNotIn("디렉토리 내 파일 수", summary_text)
            self.assertNotIn("압축 크기:", summary_text)
        finally:
            app.destroy()

    @patch("tkinter.messagebox.showinfo")
    def test_single_line_metrics_summary_english(self, mock_msgbox):
        """영문 모드에서 'Total Files: N, Uncompressed Size: X, Space Saved: Y%' 형식으로 1줄 표출되는지 검증"""
        app = Zipper9App()
        try:
            app._on_language_change("EN")
            app.update()
            app._load_archive_for_extract(self.zip_path)
            app.update()

            summary_text = app.lbl_extract_metrics_summary.cget("text")
            self.assertIn("Total Files: 2", summary_text)
            self.assertIn("Uncompressed Size:", summary_text)
            self.assertIn("Space Saved:", summary_text)
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
