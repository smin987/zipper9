"""
Zipper9 설정 아코디언 토글 (Plan B: 윈도우 하단 동적 축소/확장) 단위 테스트
"""

import unittest
from unittest.mock import patch
import customtkinter as ctk
import re

from zipper9_ui.app import Zipper9App
from zipper9_ui.bridge.i18n import t, set_language


class TestSettingsTogglePlanB(unittest.TestCase):
    """설정 아코디언 접기/펼치기 및 윈도우 하단 높이 동적 조절 검증"""

    def setUp(self):
        set_language("KO")

    @patch("tkinter.messagebox.showinfo")
    def test_initial_default_is_collapsed(self, mock_msgbox):
        """기본 설정 상태에서 앱 초기 런칭 시 접힌(collapsed) 상태 및 760x560 크기로 시작하는지 검증"""
        with patch("zipper9_ui.app.load_settings", return_value={}):
            app = Zipper9App()
            try:
                app.update()
                self.assertFalse(app.settings_expanded)
                self.assertIn("▶", app.lbl_settings_toggle_title.cget("text"))
                self.assertFalse(app.settings_container.winfo_ismapped())
                
                geom = app.geometry()
                m = re.match(r"^(\d+)x(\d+)", geom)
                self.assertIsNotNone(m)
                w, h = int(m.group(1)), int(m.group(2))
                self.assertLessEqual(h, 580, f"Initial default height should be compact (<=580), got {h}")
            finally:
                app.destroy()

    @patch("tkinter.messagebox.showinfo")
    def test_plan_b_toggle_window_resize(self, mock_msgbox):
        """설정 토글 시 창 하단이 펴지고(확장) 다시 접히는(축소) B안 동작 검증"""
        with patch("zipper9_ui.app.load_settings", return_value={"settings_expanded": False, "window_geometry": "760x560"}):
            app = Zipper9App()
            try:
                app.update()

                # 초기 상태 검증: 접힘 (Collapsed)
                self.assertFalse(app.settings_expanded)
                self.assertIn("▶", app.lbl_settings_toggle_title.cget("text"))
                self.assertNotIn("⚙️", app.lbl_settings_toggle_title.cget("text"))
                self.assertNotIn("·", app.lbl_settings_toggle_title.cget("text"))

                # 1. 펼치기 (Expand) 트리거
                app._toggle_settings_panel()
                app.update()

                # 펼침 상태 검증
                self.assertTrue(app.settings_expanded)
                self.assertIn("▼", app.lbl_settings_toggle_title.cget("text"))

                geom_expanded = app.geometry()
                m_exp = re.match(r"^(\d+)x(\d+)", geom_expanded)
                self.assertIsNotNone(m_exp)
                w_exp, h_exp = int(m_exp.group(1)), int(m_exp.group(2))
                self.assertGreaterEqual(h_exp, 750, f"Expanded height should be >= 750, got {h_exp}")

                # 2. 다시 접기 (Collapse) 트리거
                app._toggle_settings_panel()
                app.update()

                # 접힘 복원 상태 검증
                self.assertFalse(app.settings_expanded)
                self.assertIn("▶", app.lbl_settings_toggle_title.cget("text"))

                geom_collapsed = app.geometry()
                m_col = re.match(r"^(\d+)x(\d+)", geom_collapsed)
                self.assertIsNotNone(m_col)
                w_col, h_col = int(m_col.group(1)), int(m_col.group(2))

                # 접혔을 때 높이가 약 536~545 수준으로 줄어들었는지 검증
                self.assertLess(h_col, 600, f"Collapsed height should be < 600, got {h_col}")
                self.assertGreaterEqual(h_col, 420, f"Collapsed height should be >= 420, got {h_col}")

            finally:
                app.destroy()


if __name__ == "__main__":
    unittest.main()
