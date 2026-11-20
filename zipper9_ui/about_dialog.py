"""zipper9 정보 및 오픈소스 라이선스 안내 다이얼로그 모듈.

Image Optimizer 스타일의 세련된 모던 Fluent 다이얼로그를 통해
소프트웨어 라이선스 정책, 기업 100% 무료 보증, ALZ/EGG 컴플라이언스 및 제3자 오픈소스 목록을 안내합니다.
"""

import os
import sys
import webbrowser
import customtkinter as ctk
from zipper9_ui.bridge.i18n import t, get_language


class AboutLicenseDialog(ctk.CTkToplevel):
    """정보 및 오픈소스 라이선스 모달 다이얼로그."""

    def __init__(self, parent, app_version: str):
        super().__init__(parent)

        self.parent = parent
        self.app_version = app_version
        self.lang = get_language()

        # 창 기본 설정
        self.title(t("dialog_about_title"))
        self.geometry("620x580")
        self.minsize(580, 480)
        self.transient(parent)
        self.grab_set()

        # 부모 창 중앙 배치
        self._center_window()

        self._build_ui()

    def _center_window(self):
        self.update_idletasks()
        try:
            pw = self.parent.winfo_width()
            ph = self.parent.winfo_height()
            px = self.parent.winfo_rootx()
            py = self.parent.winfo_rooty()
            w, h = 620, 580
            x = px + max(0, (pw - w) // 2)
            y = py + max(0, (ph - h) // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _build_ui(self):
        # 상단 타이틀 바 프레임
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=20, pady=(16, 8))

        lbl_title = ctk.CTkLabel(
            top_bar,
            text="⚡ zipper9",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#212529", "#ffffff"),
        )
        lbl_title.pack(side="left", padx=(0, 8))

        # 버전 뱃지
        lbl_ver = ctk.CTkLabel(
            top_bar,
            text=f"v{self.app_version}" if not self.app_version.startswith("v") else self.app_version,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#4dabf7",
        )
        lbl_ver.pack(side="left", pady=(4, 0))

        # 본문 스크롤 영역
        scroll = ctk.CTkScrollableFrame(
            self,
            corner_radius=8,
            fg_color=("#f8f9fa", "#1e2227"),
            border_width=1,
            border_color=("#dee2e6", "#2c3036"),
        )
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        # 1. 앱 기본 정보 카드
        self._build_info_card(scroll)

        # 구분선
        sep1 = ctk.CTkFrame(scroll, height=1, fg_color=("#e9ecef", "#2c3036"))
        sep1.pack(fill="x", pady=12)

        # 2. 소프트웨어 라이선스 정책
        self._build_license_policy(scroll)

        # 구분선
        sep2 = ctk.CTkFrame(scroll, height=1, fg_color=("#e9ecef", "#2c3036"))
        sep2.pack(fill="x", pady=12)

        # 3. 주요 포맷 컴플라이언스 (ALZ/EGG/RAR)
        self._build_format_compliance(scroll)

        # 구분선
        sep3 = ctk.CTkFrame(scroll, height=1, fg_color=("#e9ecef", "#2c3036"))
        sep3.pack(fill="x", pady=12)

        # 4. 제3자 오픈소스 소프트웨어 표
        self._build_third_party_table(scroll)

        # 하단 액션 버튼 바
        action_bar = ctk.CTkFrame(self, fg_color="transparent")
        action_bar.pack(fill="x", padx=20, pady=(0, 16))

        btn_repo = ctk.CTkButton(
            action_bar,
            text=t("dialog_open_repo"),
            width=130,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#e9ecef", "#2c3036"),
            hover_color=("#dee2e6", "#3a3f47"),
            text_color=("#212529", "#f1f3f5"),
            command=self._open_repo,
        )
        btn_repo.pack(side="left", padx=(0, 8))

        btn_lic = ctk.CTkButton(
            action_bar,
            text=t("dialog_open_license_file"),
            width=150,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#e9ecef", "#2c3036"),
            hover_color=("#dee2e6", "#3a3f47"),
            text_color=("#212529", "#f1f3f5"),
            command=self._open_license_file,
        )
        btn_lic.pack(side="left")

        btn_close = ctk.CTkButton(
            action_bar,
            text=t("dialog_close"),
            width=80,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#4dabf7", "#1c7ed6"),
            hover_color=("#339af0", "#1864ab"),
            text_color="#ffffff",
            command=self.destroy,
        )
        btn_close.pack(side="right")

    def _build_info_card(self, parent):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(fill="x", pady=(4, 0))

        title = ctk.CTkLabel(
            box,
            text="zipper9 (Source-Available Freeware)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#212529", "#ffffff"),
            anchor="w",
        )
        title.pack(fill="x")

        copy_text = "저작권 (c) 2026 smin987. All rights reserved." if self.lang == "KO" else "Copyright (c) 2026 smin987. All rights reserved."
        lbl_copy = ctk.CTkLabel(
            box,
            text=copy_text,
            font=ctk.CTkFont(size=11),
            text_color=("#6c757d", "#adb5bd"),
            anchor="w",
        )
        lbl_copy.pack(fill="x", pady=(2, 0))

        repo_link = ctk.CTkLabel(
            box,
            text="공식 저장소: https://github.com/smin987/zipper9" if self.lang == "KO" else "Official Repository: https://github.com/smin987/zipper9",
            font=ctk.CTkFont(size=11, underline=True),
            text_color=("#1971c2", "#4dabf7"),
            cursor="hand2",
            anchor="w",
        )
        repo_link.pack(fill="x", pady=(2, 0))
        repo_link.bind("<Button-1>", lambda e: self._open_repo())

    def _build_license_policy(self, parent):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(fill="x")

        sec_title = "1. 소프트웨어 라이선스 정책" if self.lang == "KO" else "1. Software License Policy"
        lbl_sec = ctk.CTkLabel(
            box,
            text=sec_title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#212529", "#ffffff"),
            anchor="w",
        )
        lbl_sec.pack(fill="x", pady=(0, 6))

        if self.lang == "KO":
            p1 = "• 컴파일 바이너리 (Freeware): 공식 배포되는 실행 파일(.exe, .deb, .dmg 등)은 개인, 교육 기관, 비영리 단체는 물론 상업/기업 사용자 누구나 100% 영구 무료로 업무에 자유롭게 사용할 수 있습니다."
            p2 = "• 소스코드 (Source-Available): 개인 연구, 학습, 보안 감사 및 공식 저장소 기여(PR) 목적의 로컬 수정은 전면 허용됩니다. 단, 영리 단체 및 기업 사용자의 소스코드 수정 및 커스텀 빌드 제작은 엄격히 금지되며(공식 바이너리 사용 필수), 경쟁 제품 출시 목적의 수정 및 무단 배포는 금지됩니다."
        else:
            p1 = "• Compiled Binaries (Freeware): Officially distributed binaries (.exe, .deb, .dmg, etc.) are 100% free forever for personal, educational, non-profit, and commercial / enterprise use."
            p2 = "• Source Code (Source-Available): Local inspection, study, security auditing, and contributing (PRs) are permitted for individual developers. Modifying source code or distributing derivative builds by commercial entities, as well as developing competing archiving products, is strictly prohibited."

        lbl_p1 = ctk.CTkLabel(box, text=p1, font=ctk.CTkFont(size=11), text_color=("#495057", "#ced4da"), justify="left", wraplength=540, anchor="w")
        lbl_p1.pack(fill="x", pady=(0, 4))

        lbl_p2 = ctk.CTkLabel(box, text=p2, font=ctk.CTkFont(size=11), text_color=("#495057", "#ced4da"), justify="left", wraplength=540, anchor="w")
        lbl_p2.pack(fill="x")

    def _build_format_compliance(self, parent):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(fill="x")

        sec_title = "2. 주요 포맷 컴플라이언스 (법적 안전성)" if self.lang == "KO" else "2. Format Legal Compliance"
        lbl_sec = ctk.CTkLabel(
            box,
            text=sec_title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#212529", "#ffffff"),
            anchor="w",
        )
        lbl_sec.pack(fill="x", pady=(0, 6))

        if self.lang == "KO":
            c1 = "• ALZ 포맷 공식 지원 (기업 무료 보증): 알집(ALZip) 독자 포맷인 ALZ(.alz, .a00) 해제는 100% 순수 자유 오픈소스 unalz (zlib/libpng License) 엔진을 탑재하여, 기업체 및 관공서에서도 알툴즈 라이선스 단속 우려 없이 완전 무료로 안전하게 사용할 수 있습니다."
            c2 = "• EGG 포맷 영구 배제 (Legal Risk Zero): 알집 EGG 포맷은 이스트소프트의 상업적 재배포 제한 및 독점 조항으로 인한 기업 고객의 저작권 분쟁 리스크를 원천 차단하기 위해 공식 지원 대상에서 배제되었습니다."
            c3 = "• 독점 포맷(RAR) 준수: Alexander Roshal의 특허 압축 생성 알고리즘은 미구현하며, 오픈소스 UnRAR 모듈을 통한 안전한 읽기 전용 해제만 제공합니다."
        else:
            c1 = "• ALZ Format Support (Enterprise Safe): Decompression of ALZip proprietary ALZ (.alz, .a00) format is powered by the 100% free open-source unalz (zlib/libpng License) engine, completely free of license audit risks for enterprise users."
            c2 = "• EGG Format Exclusion (Zero Legal Risk): ESTsoft EGG format is permanently excluded to eliminate potential copyright disputes stemming from proprietary commercial redistribution restrictions."
            c3 = "• Proprietary RAR Compliance: Proprietary RAR compression algorithms are not implemented; only safe read-only decompression via open-source UnRAR is supported."

        for c in [c1, c2, c3]:
            lbl = ctk.CTkLabel(box, text=c, font=ctk.CTkFont(size=11), text_color=("#495057", "#ced4da"), justify="left", wraplength=540, anchor="w")
            lbl.pack(fill="x", pady=(0, 4))

    def _build_third_party_table(self, parent):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(fill="x")

        sec_title = "3. 사용된 제3자 오픈소스 소프트웨어 (Third-Party OSS)" if self.lang == "KO" else "3. Third-Party Open Source Software"
        lbl_sec = ctk.CTkLabel(
            box,
            text=sec_title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#212529", "#ffffff"),
            anchor="w",
        )
        lbl_sec.pack(fill="x", pady=(0, 6))

        # 테이블 헤더
        tbl_frame = ctk.CTkFrame(box, corner_radius=6, fg_color=("#e9ecef", "#252930"), border_width=1, border_color=("#dee2e6", "#343a40"))
        tbl_frame.pack(fill="x", pady=(0, 4))

        col_w = [110, 110, 150, 150]
        headers = ["컴포넌트", "라이선스", "저작권자", "비고"] if self.lang == "KO" else ["Component", "License", "Author", "Notes"]

        hdr_row = ctk.CTkFrame(tbl_frame, fg_color="transparent")
        hdr_row.pack(fill="x", padx=8, pady=4)

        for h, w in zip(headers, col_w):
            lbl = ctk.CTkLabel(hdr_row, text=h, width=w, font=ctk.CTkFont(size=11, weight="bold"), text_color=("#212529", "#ffffff"), anchor="w")
            lbl.pack(side="left")

        # 테이블 데이터
        oss_data = [
            ("7-Zip & unRAR", "LGPL v2.1+*", "Igor Pavlov, A. Roshal", "멀티코어 압축 엔진" if self.lang == "KO" else "Multi-core Engine"),
            ("unalz", "zlib/libpng", "Kippler", "ALZ 오픈소스 해제기" if self.lang == "KO" else "ALZ Open-Source Engine"),
            ("LZ4", "BSD 2-Clause", "Yann Collet", "초고속 스트리밍 압축" if self.lang == "KO" else "Ultra-fast Streaming"),
            ("Zstandard (zstd)", "BSD 3-Clause", "Meta Platforms, Inc.", "초고속 압축 엔진" if self.lang == "KO" else "Ultra-fast Compressor"),
            ("CustomTkinter", "CC0 / MIT", "Tom Schimansky", "Fluent GUI 프레임워크" if self.lang == "KO" else "Fluent GUI Framework"),
            ("Rust Crates", "MIT / Apache 2.0", "Rust Contributors", "Win11 모던 쉘 확장" if self.lang == "KO" else "Win11 Shell Extension"),
        ]

        for item in oss_data:
            row = ctk.CTkFrame(tbl_frame, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=2)
            for val, w in zip(item, col_w):
                # 라이선스 강조
                tcolor = "#20c997" if "zlib" in val else ("#4dabf7" if "LGPL" in val or "BSD" in val else ("#495057", "#ced4da"))
                lbl = ctk.CTkLabel(row, text=val, width=w, font=ctk.CTkFont(size=10), text_color=tcolor, anchor="w")
                lbl.pack(side="left")

    def _open_repo(self):
        webbrowser.open("https://github.com/smin987/zipper9")

    def _open_license_file(self):
        """로컬 LICENSE 또는 THIRD_PARTY_LICENSES.md 파일 열기"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if getattr(sys, "frozen", False):
            base_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))

        for candidate in ["THIRD_PARTY_LICENSES.md", "LICENSE"]:
            p = os.path.join(base_dir, candidate)
            if os.path.isfile(p):
                try:
                    os.startfile(p)
                    return
                except Exception:
                    pass
        webbrowser.open("https://github.com/smin987/zipper9/blob/main/THIRD_PARTY_LICENSES.md")
