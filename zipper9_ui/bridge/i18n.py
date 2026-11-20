"""zipper9 다국어(i18n) 번역 관리 모듈.

한국어(KO) 및 영어(EN) 언어팩을 제공하며,
동적 언어 전환 및 포맷팅 문자열을 지원합니다.
"""

from typing import Any, Dict

SUPPORTED_LANGUAGES = ["KO", "EN"]
DEFAULT_LANGUAGE = "KO"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # 윈도우 타이틀 & 헤더
    "app_title": {
        "KO": "zipper9 - 초고속 파일압축",
        "EN": "zipper9 - High-Speed Archiver",
    },
    "core_native": {
        "KO": "● Native C++ ({cores}-Core 가동 중)",
        "EN": "● Native C++ ({cores}-Core Active)",
    },
    "core_python": {
        "KO": "● Python Core 가동 중",
        "EN": "● Python Core Active",
    },
    "dark_mode": {
        "KO": "다크 모드",
        "EN": "Dark Mode",
    },
    "context_menu_toggle": {
        "KO": "마우스 우클릭 메뉴 활성화",
        "EN": "Context Menu Integration",
    },
    "archive_icon_toggle": {
        "KO": "압축 파일 아이콘 표시",
        "EN": "Archive File Icons",
    },
    "btn_sponsor": {
        "KO": "💖 후원하기",
        "EN": "💖 Sponsor",
    },
    "btn_about_license": {
        "KO": "ℹ️ 정보 / 라이선스",
        "EN": "ℹ️ About / License",
    },
    "tooltip_update_available": {
        "KO": "최신 업데이트가 있습니다.",
        "EN": "A new update is available.",
    },
    "tooltip_up_to_date": {
        "KO": "최신 버전을 사용 중입니다.",
        "EN": "You are using the latest version.",
    },
    "dialog_about_title": {
        "KO": "zipper9 정보 및 오픈소스 라이선스",
        "EN": "zipper9 About & Open Source Licenses",
    },
    "dialog_open_repo": {
        "KO": "🌐 GitHub 저장소",
        "EN": "🌐 GitHub Repository",
    },
    "dialog_open_license_file": {
        "KO": "📄 라이선스 문서 열기",
        "EN": "📄 Open License File",
    },
    "dialog_close": {
        "KO": "닫기",
        "EN": "Close",
    },

    # 네비게이션
    "nav_compress": {
        "KO": "  📦 아카이브 압축 (Compress)  ",
        "EN": "  📦 Compress Archive  ",
    },
    "nav_extract": {
        "KO": "  📂 스마트 압축해제 (Extract)  ",
        "EN": "  📂 Smart Extraction  ",
    },

    # 압축 탭: 드롭존 & 목록
    "drop_empty_prompt": {
        "KO": "📥 여기에 파일이나 폴더를 끌어다 놓으세요 (Drag & Drop)",
        "EN": "📥 Drag & Drop files or folders here",
    },
    "btn_add_files": {
        "KO": "+ 파일 추가",
        "EN": "+ Add Files",
    },
    "btn_add_folder": {
        "KO": "+ 폴더 추가",
        "EN": "+ Add Folder",
    },
    "btn_clear_all": {
        "KO": "전체 비우기",
        "EN": "Clear All",
    },
    "label_target": {
        "KO": "📍 대상:",
        "EN": "📍 Target:",
    },
    "btn_browse_target": {
        "KO": "위치지정...",
        "EN": "Browse...",
    },
    "btn_compress_start": {
        "KO": "⚡ 압축하기",
        "EN": "⚡ Compress Now",
    },
    "summary_items_count": {
        "KO": "항목: {count}개 ({size})",
        "EN": "Items: {count} ({size})",
    },
    "target_placeholder": {
        "KO": "파일을 추가하면 대상 경로가 자동 계산됩니다.",
        "EN": "Target path will be calculated automatically once files are added.",
    },

    # 알고리즘 카드
    "algo_zstd_title": {
        "KO": "Zstandard",
        "EN": "Zstandard",
    },
    "algo_zstd_desc": {
        "KO": "Meta의 현대적 올인원 고속/고압축 알고리즘",
        "EN": "Modern balanced high-speed & high-ratio by Meta",
    },
    "algo_store_title": {
        "KO": "Store (무압축)",
        "EN": "Store (Uncompressed)",
    },
    "algo_store_desc": {
        "KO": "압축 없이 단일 ZIP 파일로 초고속 패키징",
        "EN": "Ultra-fast packaging into single ZIP without compression",
    },
    "algo_7z_title": {
        "KO": "7z: LZMA2",
        "EN": "7z: LZMA2",
    },
    "algo_7z_desc": {
        "KO": "7-Zip 네이티브 엔진 기반 표준 고압축",
        "EN": "Standard high ratio powered by 7-Zip native engine",
    },
    "algo_lz4_title": {
        "KO": "TAR: LZ4",
        "EN": "TAR: LZ4",
    },
    "algo_lz4_desc": {
        "KO": "초당 500MB+ 번개 압축 (백업/게임 에셋)",
        "EN": "500MB/s+ lightning speed (backups/game assets)",
    },
    "algo_speed": {
        "KO": "속도:",
        "EN": "Speed:",
    },
    "algo_ratio": {
        "KO": "압축률:",
        "EN": "Ratio:",
    },
    "algo_extra_placeholder": {
        "KO": "다른 압축 알고리즘 선택...",
        "EN": "Choose other compression algorithms...",
    },
    "algo_extra_store": {
        "KO": "ZIP: 무압축 (Store · 초고속 패키징)",
        "EN": "ZIP: Store (Uncompressed · Ultra-fast)",
    },
    "algo_extra_tarxz": {
        "KO": "TAR: .tar.xz (XZ · 고압축)",
        "EN": "TAR: .tar.xz (XZ · High Ratio)",
    },
    "algo_extra_tarbz2": {
        "KO": "TAR: .tar.bz2 (Bzip2)",
        "EN": "TAR: .tar.bz2 (Bzip2)",
    },
    "algo_extra_tar": {
        "KO": "TAR: .tar (무압축 Tarball)",
        "EN": "TAR: .tar (Tarball · Uncompressed)",
    },
    "algo_extra_iso": {
        "KO": "ISO: .iso (UDF · 광학 디스크 이미지)",
        "EN": "ISO: .iso (UDF · Optical Disc Image)",
    },

    # 설정 접이식 패널 (Collapsible Settings)
    "settings_title_expanded": {
        "KO": "▼ 설정(알고리즘, 보안 암호, 분할 압축)",
        "EN": "▼ Settings (Algorithm, Password, Split)",
    },
    "settings_title_collapsed": {
        "KO": "▶ 설정(알고리즘, 보안 암호, 분할 압축)",
        "EN": "▶ Settings (Algorithm, Password, Split)",
    },

    # 고급 옵션
    "advanced_options_title": {
        "KO": "고급 압축 옵션 (보안 암호화 & 분할 압축)",
        "EN": "Advanced Options (Encryption & Volume Splitting)",
    },
    "label_password": {
        "KO": "보안 비밀번호 (선택사항):",
        "EN": "Security Password (Optional):",
    },
    "placeholder_password": {
        "KO": "비밀번호 입력...",
        "EN": "Enter password...",
    },
    "chk_encrypt_filenames": {
        "KO": "7z 파일명 암호화 (목록 숨김)",
        "EN": "Encrypt 7z file names (Hide headers)",
    },
    "chk_verify_integrity": {
        "KO": "압축 후 무결성 검사",
        "EN": "Verify integrity after compression",
    },
    "label_split_volume": {
        "KO": "분할 압축:",
        "EN": "Split Volume:",
    },
    "split_none": {
        "KO": "분할 안 함 (기본)",
        "EN": "No Splitting (Default)",
    },
    "split_preset_none": {
        "KO": "분할 안 함 (기본)",
        "EN": "No Splitting (Default)",
    },
    "split_preset_10mb": {
        "KO": "10 MB (디스코드 무료)",
        "EN": "10 MB (Discord Free)",
    },
    "split_preset_25mb": {
        "KO": "25 MB (이메일 첨부)",
        "EN": "25 MB (Email Attachment)",
    },
    "split_preset_100mb": {
        "KO": "100 MB",
        "EN": "100 MB",
    },
    "split_preset_500mb": {
        "KO": "500 MB",
        "EN": "500 MB",
    },
    "split_preset_1gb": {
        "KO": "1 GB",
        "EN": "1 GB",
    },
    "split_preset_2gb": {
        "KO": "2 GB (네이버/다음 대용량)",
        "EN": "2 GB (Web Mail Large)",
    },
    "split_preset_4gb": {
        "KO": "4 GB (FAT32 한계)",
        "EN": "4 GB (FAT32 Limit)",
    },

    # 압축 해제 탭
    "btn_select_archive": {
        "KO": "📂 압축 파일 선택...",
        "EN": "📂 Select Archive...",
    },
    "btn_browse_archive": {
        "KO": "📂 압축된 파일 찾아보기...",
        "EN": "📂 Browse Archive File...",
    },
    "btn_reselect_archive": {
        "KO": "다른 파일 선택...",
        "EN": "Select Another File...",
    },
    "extract_drop_title": {
        "KO": "압축을 해제할 아카이브 파일을 여기에 끌어다 놓으세요 (Drag & Drop)",
        "EN": "Drag & drop archive files here to extract",
    },
    "extract_drop_sub": {
        "KO": "어디든 파일을 끌어다 놓으시면 내부 파일 구조와 압축률 요약 대시보드가 즉시 로드됩니다.",
        "EN": "Drop files anywhere to inspect structure and compression ratio dashboard instantly.",
    },
    "extract_drop_smart_tip": {
        "KO": "💡 단일 폴더 통 압축은 이중 폴더를 만들지 않고 현재 위치에 깔끔하게 풀어드립니다.",
        "EN": "💡 Smart Extract extracts archives without creating redundant nested folders.",
    },
    # 1줄 메트릭 요약 바 (Extract Metrics Summary Bar)
    "extract_metrics_summary": {
        "KO": "총 파일 수 {count}개, 원본 용량 {uncompressed}, 압축 절감률 {ratio}%",
        "EN": "Total Files: {count}, Uncompressed Size: {uncompressed}, Space Saved: {ratio}%",
    },
    "extract_metrics_summary_empty": {
        "KO": "총 파일 수 --개, 원본 용량 --, 압축 절감률 --%",
        "EN": "Total Files: --, Uncompressed Size: --, Space Saved: --%",
    },
    "card_total_files": {
        "KO": "📊 총 파일 수",
        "EN": "📊 Total Files",
    },
    "card_orig_size": {
        "KO": "💾 원본 용량",
        "EN": "💾 Uncompressed Size",
    },
    "card_ratio": {
        "KO": "📉 압축 절감률",
        "EN": "📉 Space Saved",
    },
    "card_pending": {
        "KO": "대기 중",
        "EN": "Pending",
    },
    "metric_unit_items": {
        "KO": "개",
        "EN": "items",
    },
    "metric_sub_total_files": {
        "KO": "아카이브 내 총 파일",
        "EN": "Total items in archive",
    },
    "metric_sub_compressed": {
        "KO": "압축 크기: {size}",
        "EN": "Compressed size: {size}",
    },
    "metric_sub_space_saved": {
        "KO": "디스크 공간 절감",
        "EN": "Disk space saved",
    },
    "tree_hdr_name": {
        "KO": "항목명",
        "EN": "Item Name",
    },
    "tree_hdr_orig_size": {
        "KO": "원본 크기",
        "EN": "Original Size",
    },
    "tree_hdr_comp_size": {
        "KO": "압축 크기",
        "EN": "Compressed",
    },
    "structure_single": {
        "KO": " [구조: 단일 폴더 '{root}/']",
        "EN": " [Structure: Single Root Folder '{root}/']",
    },
    "structure_multi": {
        "KO": " [구조: 다중 파일/항목]",
        "EN": " [Structure: Multi-item root]",
    },
    "selected_archive_text": {
        "KO": "선택됨: {name}{enc} ({path})",
        "EN": "Selected: {name}{enc} ({path})",
    },
    "encrypted_tag": {
        "KO": "암호화 보호됨",
        "EN": "Encrypted",
    },
    "status_archive_analyzed": {
        "KO": "아카이브 분석 완료: {name} ({count}개 파일)",
        "EN": "Archive analyzed: {name} ({count} files)",
    },
    "dialog_pwd_required": {
        "KO": "🔒 암호 필요",
        "EN": "🔒 Password Required",
    },
    "dialog_pwd_required_msg": {
        "KO": "'{name}' 파일은 암호로 보호되어 있습니다.\n비밀번호를 입력하세요:",
        "EN": "'{name}' is protected with a password.\nPlease enter password:",
    },
    "status_pwd_cancelled": {
        "KO": "암호가 입력되지 않아 열람이 취소되었습니다: {name}",
        "EN": "Preview cancelled: password not provided for {name}",
    },
    "dialog_select_archive": {
        "KO": "압축된 파일 선택",
        "EN": "Select Archive File",
    },
    "dialog_select_files_to_compress": {
        "KO": "압축할 파일 선택",
        "EN": "Select Files to Compress",
    },
    "dialog_select_dir_to_compress": {
        "KO": "압축할 폴더 선택",
        "EN": "Select Folder to Compress",
    },
    "drop_extract_empty": {
        "KO": "📥 여기에 압축 파일을 끌어다 놓으세요 (.zip, .7z, .rar, .tar, .gz, .xz, .lz4...)",
        "EN": "📥 Drag & drop an archive file here (.zip, .7z, .rar, .tar, .gz, .xz, .lz4...)",
    },
    "metric_total_files": {
        "KO": "총 파일 수",
        "EN": "Total Files",
    },
    "metric_compressed_size": {
        "KO": "압축 크기",
        "EN": "Compressed Size",
    },
    "metric_uncompressed_size": {
        "KO": "해제 크기",
        "EN": "Uncompressed Size",
    },
    "metric_space_saved": {
        "KO": "용량 절감률",
        "EN": "Space Saved",
    },
    "tree_col_name": {
        "KO": "파일명",
        "EN": "File Name",
    },
    "tree_col_orig_size": {
        "KO": "원본 크기",
        "EN": "Original Size",
    },
    "tree_col_comp_size": {
        "KO": "압축 크기",
        "EN": "Compressed",
    },
    "tree_col_ratio": {
        "KO": "압축률",
        "EN": "Ratio",
    },
    "tree_col_mtime": {
        "KO": "수정일",
        "EN": "Modified Date",
    },
    "label_extract_password": {
        "KO": "보안 비밀번호:",
        "EN": "Password:",
    },
    "placeholder_extract_password": {
        "KO": "압축해제 비밀번호 입력",
        "EN": "Enter extract password...",
    },
    "label_extract_dest": {
        "KO": "📍 해제 위치:",
        "EN": "📍 Extract to:",
    },
    "extract_target_empty": {
        "KO": "해제 위치: 아카이브 파일을 선택하거나 끌어다 놓으세요.",
        "EN": "Extract to: Select or drag and drop an archive file.",
    },
    "extract_target_single": {
        "KO": "📍 해제 위치: '{loc}\\{root}\\' (단일 폴더 직접 해제)",
        "EN": "📍 Extract to: '{loc}\\{root}\\' (Direct extraction)",
    },
    "extract_target_nested": {
        "KO": "📍 해제 위치: '{loc}\\{folder}\\' (새 폴더 생성 후 해제)",
        "EN": "📍 Extract to: '{loc}\\{folder}\\' (Extract to new folder)",
    },
    "btn_browse_extract_dest": {
        "KO": "위치지정...",
        "EN": "Browse...",
    },
    "btn_extract_here": {
        "KO": "📂 여기에 바로 풀기",
        "EN": "📂 Extract Here",
    },
    "btn_extract_to_folder": {
        "KO": "📁 알아서 압축 풀기",
        "EN": "📁 Smart Extract",
    },
    "overwrite_confirm_title": {
        "KO": "파일 덮어쓰기 확인",
        "EN": "Overwrite Confirmation",
    },
    "overwrite_confirm_single": {
        "KO": "'{name}' 파일이 대상 위치에 이미 존재합니다.\n\n파일이 존재합니다. 덮어쓰시겠습니까?",
        "EN": "'{name}' already exists in destination.\n\nFile exists. Do you want to overwrite?",
    },
    "overwrite_confirm_multi": {
        "KO": "대상 위치에 동일한 파일이 이미 {count}개 존재합니다.\n(예: {name})\n\n파일이 존재합니다. 덮어쓰시겠습니까?",
        "EN": "{count} conflicting files already exist in destination.\n(e.g., {name})\n\nFiles exist. Do you want to overwrite?",
    },
    "status_extract_cancelled_overwrite": {
        "KO": "압축 해제가 취소되었습니다. (덮어쓰기 취소)",
        "EN": "Extraction cancelled. (Overwrite aborted)",
    },

    # 상태바 & 알림
    "status_archive_icon_on": {
        "KO": "✅ 압축 파일 아이콘이 활성화되었습니다 (Windows 탐색기 연동)",
        "EN": "✅ Archive file icons enabled (Explorer integrated)",
    },
    "status_archive_icon_off": {
        "KO": "✅ 압축 파일 아이콘이 기본값으로 복원되었습니다.",
        "EN": "✅ Archive file icons restored to default.",
    },
    "status_ready": {
        "KO": "준비 완료. 파일이나 폴더를 끌어다 놓으세요.",
        "EN": "Ready. Drag and drop files or folders.",
    },
    "status_compressing": {
        "KO": "압축 진행 중...",
        "EN": "Compressing in progress...",
    },
    "status_iso_creating": {
        "KO": "ISO (UDF) 디스크 이미지 생성 중...",
        "EN": "Creating ISO (UDF) disc image...",
    },
    "status_extracting": {
        "KO": "압축 해제 진행 중...",
        "EN": "Extracting in progress...",
    },
    "status_compress_success": {
        "KO": "✅ 압축 완료! ({path})",
        "EN": "✅ Compression completed! ({path})",
    },
    "status_extract_success": {
        "KO": "✅ 압축 해제 완료! ({path})",
        "EN": "✅ Extraction completed! ({path})",
    },
    "status_archive_detected": {
        "KO": "📍 압축 파일 감지: '스마트 압축해제' 화면으로 자동 전환되었습니다 ({name})",
        "EN": "📍 Archive detected: Switched to Smart Extraction ({name})",
    },
    "status_files_detected": {
        "KO": "📍 일반 파일 감지: '압축하기' 화면으로 자동 전환되어 {count}개 항목이 추가되었습니다.",
        "EN": "📍 Files detected: Switched to Compress and added {count} items.",
    },
    "status_files_added": {
        "KO": "{count}개 항목이 추가되었습니다.",
        "EN": "{count} items added.",
    },
    "status_auto_selected_7z": {
        "KO": "📍 7z 파일명 암호화를 위해 '7-Zip (LZMA2 Ultra)' 알고리즘으로 자동 선택되었습니다.",
        "EN": "📍 '7-Zip (LZMA2 Ultra)' algorithm automatically selected for file name encryption.",
    },

    # 경고 및 에러 다이얼로그
    "err_unsupported_archive_format": {
        "KO": "지원하지 않는 형식의 압축 포맷입니다.",
        "EN": "Unsupported archive format.",
    },
    "dialog_warning": {
        "KO": "경고",
        "EN": "Warning",
    },
    "dialog_error": {
        "KO": "오류",
        "EN": "Error",
    },
    "dialog_info": {
        "KO": "알림",
        "EN": "Information",
    },
    "msg_encrypt_header_only_7z": {
        "KO": "파일명 암호화(목록 숨김)는 7z 포맷에서만 지원됩니다.\n선택하신 알고리즘으로 변경되면서 '7z 파일명 암호화' 체크가 해제되었습니다.",
        "EN": "File name encryption is only supported in 7z format.\n'Encrypt 7z file names' has been unchecked.",
    },
    "msg_iso_no_password": {
        "KO": "ISO 디스크 이미지는 비밀번호 암호화를 지원하지 않습니다.\n암호 설정을 해제하고 계속 진행합니다.",
        "EN": "ISO disc images do not support password encryption.\nProceeding without encryption.",
    },
    "msg_iso_no_split": {
        "KO": "ISO 디스크 이미지는 분할 압축을 지원하지 않습니다.\n분할 설정을 해제하고 계속 진행합니다.",
        "EN": "ISO disc images do not support volume splitting.\nProceeding without volume splitting.",
    },
    "err_no_source": {
        "KO": "압축할 파일이나 폴더를 먼저 추가해 주세요.",
        "EN": "Please add files or folders to compress first.",
    },
    "err_no_archive": {
        "KO": "해제할 압축 파일을 먼저 선택해 주세요.",
        "EN": "Please select an archive file to extract first.",
    },
    "err_invalid_dest": {
        "KO": "유효한 대상 경로를 지정해 주세요.",
        "EN": "Please specify a valid destination path.",
    },
    "context_menu_on_msg": {
        "KO": "마우스 우클릭 메뉴가 성공적으로 등록되었습니다.\n(Windows 11 모던 1단계 메뉴 및 클래식 메뉴 지원)",
        "EN": "Context menu integration activated successfully.\n(Supports Windows 11 Modern & Classic Menu)",
    },
    "context_menu_off_msg": {
        "KO": "마우스 우클릭 메뉴가 안전하게 해제되었습니다.",
        "EN": "Context menu integration has been removed.",
    },
    "context_menu_err_msg": {
        "KO": "마우스 우클릭 메뉴 등록/해제 중 오류가 발생했습니다.",
        "EN": "An error occurred while updating context menu integration.",
    },

    # 완료 및 상태 알림
    "status_compress_done": {
        "KO": "압축 완료 ({elapsed:.2f}초 소요)",
        "EN": "Compression completed ({elapsed:.2f}s elapsed)",
    },
    "status_verifying_integrity": {
        "KO": "아카이브 무결성 검증 중...",
        "EN": "Verifying archive integrity...",
    },
    "status_compress_done_verified": {
        "KO": "압축 및 무결성 검증 완료 (100% 정상, {elapsed:.2f}초 소요)",
        "EN": "Compression & integrity verification completed (100% Ok, {elapsed:.2f}s elapsed)",
    },
    "err_integrity_failed": {
        "KO": "압축 파일 무결성 검사 실패! 데이터 손상이 감지되었습니다.\n{detail}",
        "EN": "Archive integrity verification failed! Data corruption detected.\n{detail}",
    },
    "status_extract_done": {
        "KO": "압축 해제 완료 ({elapsed:.2f}초 소요)",
        "EN": "Extraction completed ({elapsed:.2f}s elapsed)",
    },
    "status_extracting_to": {
        "KO": "압축 해제 중: {dest} 에 푸는 중...",
        "EN": "Extracting to: {dest}...",
    },
    "status_extract_prog_simple": {
        "KO": "해제 중: {file} ({percent:.0f}%) [{elapsed:.1f}s]",
        "EN": "Extracting: {file} ({percent:.0f}%) [{elapsed:.1f}s]",
    },
    "status_extract_prog_detail": {
        "KO": "해제 중: {file} ({proc} / {tot}) - {percent:.1f}% [{elapsed:.1f}s]",
        "EN": "Extracting: {file} ({proc} / {tot}) - {percent:.1f}% [{elapsed:.1f}s]",
    },
    "compress_finish_title": {
        "KO": "압축 완료",
        "EN": "Compression Complete",
    },
    "compress_finish_msg": {
        "KO": "{msg}\n\n생성된 파일 위치:\n{path}",
        "EN": "{msg}\n\nArchive Created:\n{path}",
    },
    "extract_finish_title": {
        "KO": "압축 해제 완료",
        "EN": "Extraction Complete",
    },
    "extract_finish_msg": {
        "KO": "{msg}\n\n📂 저장 폴더:\n{folder}\n\n해당 폴더를 탐색기에서 여시겠습니까?",
        "EN": "{msg}\n\n📂 Output Folder:\n{folder}\n\nDo you want to open this folder in File Explorer?",
    },
    "warn_select_archive_first": {
        "KO": "먼저 압축을 해제할 아카이브 파일을 선택하세요.",
        "EN": "Please select an archive file to extract first.",
    },
    "err_extract_failed": {
        "KO": "압축 해제 중 오류 발생:\n{err}",
        "EN": "An error occurred during extraction:\n{err}",
    },
    "err_compress_failed": {
        "KO": "압축 중 오류 발생:\n{err}",
        "EN": "An error occurred during compression:\n{err}",
    },
    "err_open_archive_failed": {
        "KO": "아카이브 파일을 열 수 없습니다:\n{err}",
        "EN": "Cannot open archive file:\n{err}",
    },
    "err_load_files_failed": {
        "KO": "파일을 불러오는 중 오류가 발생했습니다:\n{err}",
        "EN": "An error occurred while loading files:\n{err}",
    },
    "pwd_required_title": {
        "KO": "암호 입력 필요",
        "EN": "Password Required",
    },
    "pwd_required_msg": {
        "KO": "'{name}' 파일은 비밀번호로 보호되어 있습니다.\n\n암호 입력란에 비밀번호를 입력해 주시기 바랍니다.",
        "EN": "'{name}' is password protected.\n\nPlease enter the password in the password field.",
    },
    "pwd_wrong_title": {
        "KO": "암호 불일치",
        "EN": "Incorrect Password",
    },
    "pwd_wrong_msg": {
        "KO": "입력하신 비밀번호가 올바르지 않습니다.\n비밀번호를 다시 확인해 주세요.",
        "EN": "The password you entered is incorrect.\nPlease check and try again.",
    },
}


_current_language = DEFAULT_LANGUAGE


def set_language(lang: str) -> None:
    """전역 기본 언어 설정 (KO 또는 EN)"""
    global _current_language
    if lang.upper() in SUPPORTED_LANGUAGES:
        _current_language = lang.upper()


def get_language() -> str:
    """현재 설정된 언어 반환"""
    return _current_language


def t(key: str, lang: str = None, **kwargs: Any) -> str:
    """키에 해당하는 다국어 텍스트 반환. kwargs를 통한 포맷팅 지원."""
    active_lang = (lang or _current_language).upper()
    if active_lang not in SUPPORTED_LANGUAGES:
        active_lang = DEFAULT_LANGUAGE

    entry = TRANSLATIONS.get(key)
    if not entry:
        return key

    text = entry.get(active_lang, entry.get(DEFAULT_LANGUAGE, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
