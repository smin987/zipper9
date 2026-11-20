"""zipper9 경량 모던 툴팁 컴포넌트.

CustomTkinter 및 Tkinter 위젯에 마우스 호버 시 세련된 다크/라이트 툴팁을 표시합니다.
"""

import tkinter as tk
from typing import Callable, Union
import customtkinter as ctk


class ModernTooltip:
    """위젯 마우스 호버 시 우아하게 떠오르는 경량 툴팁."""

    def __init__(
        self,
        widget: tk.Widget,
        text: Union[str, Callable[[], str]],
        delay_ms: int = 250,
    ):
        self.widget = widget
        self.text_source = text
        self.delay_ms = delay_ms
        self._tip_window: tk.Toplevel | None = None
        self._after_id: str | None = None

        self.widget.bind("<Enter>", self._on_enter, add="+")
        self.widget.bind("<Leave>", self._on_leave, add="+")
        self.widget.bind("<ButtonPress>", self._on_leave, add="+")

    def _get_text(self) -> str:
        if callable(self.text_source):
            return self.text_source()
        return str(self.text_source)

    def _on_enter(self, event=None):
        self._schedule()

    def _on_leave(self, event=None):
        self._unschedule()
        self._hide()

    def _schedule(self):
        self._unschedule()
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _unschedule(self):
        if self._after_id:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _show(self):
        text = self._get_text()
        if not text or not self.widget.winfo_exists():
            return

        if self._tip_window:
            return

        # 위젯 절대 화면 좌표 계산
        try:
            x = self.widget.winfo_rootx() + (self.widget.winfo_width() // 2)
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        except Exception:
            return

        self._tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)

        # 현재 테마 감지
        mode = ctk.get_appearance_mode().lower()
        bg_color = "#1e2227" if mode == "dark" else "#ffffff"
        fg_color = "#f1f3f5" if mode == "dark" else "#212529"
        border_color = "#3b4252" if mode == "dark" else "#dee2e6"

        frame = tk.Frame(
            tw,
            background=bg_color,
            highlightbackground=border_color,
            highlightthickness=1,
            padx=8,
            pady=4,
        )
        frame.pack()

        label = tk.Label(
            frame,
            text=text,
            justify=tk.LEFT,
            background=bg_color,
            foreground=fg_color,
            font=("Malgun Gothic", 9, "bold"),
        )
        label.pack()

        # 화면 밖 벗어남 방지 보정
        tw.update_idletasks()
        tip_w = tw.winfo_width()
        screen_w = tw.winfo_screenwidth()
        if x + (tip_w // 2) > screen_w - 10:
            x = screen_w - tip_w - 10
        else:
            x = max(10, x - (tip_w // 2))
        tw.wm_geometry(f"+{x}+{y}")

    def _hide(self):
        if self._tip_window:
            try:
                self._tip_window.destroy()
            except Exception:
                pass
            self._tip_window = None

    def update_text(self, new_text: Union[str, Callable[[], str]]):
        """툴팁 텍스트 갱신"""
        self.text_source = new_text
