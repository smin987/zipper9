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
    def test_plan_b_toggle_window_resize(self, mock_msgbox):
        """설정 토글 시 창 하단이 접히고(축소) 펴지는(확장) B안 동작 검증"""
        app = Zipper9App()
        try:
            # 펼친 상태 기준 초기화 (760x780)
            app.settings_expanded = True
            app.geometry("760x780+100+100")
            app.minsize(660, 660)
            app.update()

            # 초기 상태 검증
            self.assertTrue(app.settings_expanded)
            self.assertIn("▼", app.lbl_settings_toggle_title.cget("text"))
            self.assertNotIn("⚙️", app.lbl_settings_toggle_title.cget("text"))
            self.assertNotIn("·", app.lbl_settings_toggle_title.cget("text"))

            # 1. 접기 (Collapse) 트리거
            app._toggle_settings_panel()
            app.update()

            # 접힘 상태 검증
            self.assertFalse(app.settings_expanded)
            self.assertIn("▶", app.lbl_settings_toggle_title.cget("text"))

            geom_collapsed = app.geometry()
            m = re.match(r"^(\d+)x(\d+)", geom_collapsed)
            self.assertIsNotNone(m)
            w_col, h_col = int(m.group(1)), int(m.group(2))
            
            # 접혔을 때 높이가 약 536~545 수준으로 줄어들었는지 검증
            self.assertLess(h_col, 600, f"Collapsed height should be < 600, got {h_col}")
            self.assertGreaterEqual(h_col, 420, f"Collapsed height should be >= 420, got {h_col}")

            # 2. 다시 펼치기 (Expand) 트리거
            app._toggle_settings_panel()
            app.update()

            # 펼침 복원 상태 검증
            self.assertTrue(app.settings_expanded)
            self.assertIn("▼", app.lbl_settings_toggle_title.cget("text"))

            geom_expanded = app.geometry()
            m2 = re.match(r"^(\d+)x(\d+)", geom_expanded)
            self.assertIsNotNone(m2)
            w_exp, h_exp = int(m2.group(1)), int(m2.group(2))

            # 원래 높이 780 수준으로 복원되었는지 검증
            self.assertGreaterEqual(h_exp, 750, f"Expanded height should be >= 750, got {h_exp}")

        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
