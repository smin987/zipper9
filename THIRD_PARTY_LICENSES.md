[ENGLISH](#english) | [한국어](#korean)

<a id="english"></a>
# Third-Party Open Source Software Notices

zipper9 utilizes several third-party open-source libraries, modules, and standalone tools. This document provides copyright attributions, license identifiers, and terms as required by their respective licenses.

---

## 1. 7-Zip & unRAR

- **Project URL**: [https://www.7-zip.org/](https://www.7-zip.org/)
- **Component**: `tools/7z/7z.exe`, `tools/7z/7z.dll`
- **Copyright**: 
  - Copyright (C) 1999-2026 Igor Pavlov (7-Zip)
  - Copyright (C) 1993-2026 Alexander Roshal (unRAR portion)
- **License**: **GNU Lesser General Public License version 2.1 or later (LGPL-2.1-or-later)** with unRAR restriction
- **License Link**: [https://www.7-zip.org/license.txt](https://www.7-zip.org/license.txt)
- **unRAR License Restriction Notice**:
  - The 7-Zip source code is released under the GNU LGPL license, except for the unRAR portion.
  - The unRAR portion cannot be used to re-create the RAR compression algorithm, which is proprietary.
  - Distribution of modified unRAR source code in separate form is strictly prohibited without written permission from the copyright holder (Alexander Roshal).
  - zipper9 only uses 7-Zip for decompression and does not implement or distribute any proprietary RAR compression algorithm.

---

## 2. unalz

- **Project URL**: [http://www.kippler.com/win/unalz/](http://www.kippler.com/win/unalz/)
- **Component**: `tools/unalz/unalz.exe`
- **Copyright**: Copyright (C) 2004-2026 Kippler (kippler@gmail.com)
- **License**: **zlib/libpng License**
- **License Link**: [https://opensource.org/licenses/Zlib](https://opensource.org/licenses/Zlib)
- **Enterprise Safe ALZ Support**:
  - Decompression of the ALZip proprietary ALZ format (`.alz`, `.a00`) is powered entirely by Kippler's independent open-source engine `unalz` under the permissive zlib/libpng License.
  - This grants unrestricted freedom for commercial use and redistribution, guaranteeing that corporate and enterprise environments can extract ALZ files completely free of charge without licensing audit risks.

---

## 3. LZ4

- **Project URL**: [https://lz4.github.io/lz4/](https://lz4.github.io/lz4/)
- **Component**: `tools/lz4/lz4.exe`
- **Copyright**: Copyright (C) 2011-2026 Yann Collet
- **License**:
  - Library (`liblz4`): **BSD 2-Clause License**
  - Command Line Interface (`lz4.exe`): **GNU General Public License version 2.0 (GPL-2.0)**
- **Compliance & IPC Boundary Information**:
  - zipper9 executes `lz4.exe` as an independent external process via standard IPC pipes. It does not statically or dynamically link to `lz4.exe` internal symbols, ensuring complete GPL v2.0 boundary compliance.

---

## 4. Zstandard (zstd)

- **Project URL**: [https://facebook.github.io/zstd/](https://facebook.github.io/zstd/)
- **Component**: `tools/zstd/zstd.exe`
- **Copyright**: Copyright (C) 2016-2026 Meta Platforms, Inc. (formerly Facebook, Inc.)
- **License**: **BSD 3-Clause License** / GNU General Public License version 2.0 (Dual License - zipper9 adopts BSD 3-Clause)
- **License Link**: [https://github.com/facebook/zstd/blob/dev/LICENSE](https://github.com/facebook/zstd/blob/dev/LICENSE)

---

## 5. CustomTkinter

- **Project URL**: [https://github.com/TomSchimansky/CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **Component**: Modern Fluent GUI Framework
- **Copyright**: Copyright (C) 2022-2026 Tom Schimansky
- **License**: **Creative Commons Zero v1.0 Universal (CC0 1.0)** / **MIT License**
- **License Link**: [https://github.com/TomSchimansky/CustomTkinter/blob/master/LICENSE](https://github.com/TomSchimansky/CustomTkinter/blob/master/LICENSE)

---

## 6. Windnd

- **Project URL**: [https://github.com/harveybao/windnd](https://github.com/harveybao/windnd)
- **Component**: Windows Drag & Drop Hook Module
- **Copyright**: Copyright (C) 2019-2026 Harvey Bao
- **License**: **MIT License**
- **License Link**: [https://github.com/harveybao/windnd/blob/master/LICENSE](https://github.com/harveybao/windnd/blob/master/LICENSE)

---

## 7. DarkDetect

- **Project URL**: [https://github.com/albertopol/darkdetect](https://github.com/albertopol/darkdetect)
- **Component**: OS Dark Mode Detection
- **Copyright**: Copyright (C) 2019-2026 Alberto Sottile
- **License**: **BSD 3-Clause License**
- **License Link**: [https://github.com/albertopol/darkdetect/blob/master/LICENSE](https://github.com/albertopol/darkdetect/blob/master/LICENSE)

---

## 8. Rust Crates & Windows Shell Extension

- **Component**: `tools/modern_shell/zipper9_shell.dll`, `zipper9_core`
- **Copyright**: Copyright (C) The Rust Project Contributors & Crates Authors
- **License**: **MIT License** and/or **Apache License 2.0**
- **Used Crates**: `pyo3`, `flate2`, `zstd`, `rayon`, `thiserror`, `zip`, `windows-sys`, `walkdir`. All dependencies utilize standard permissive licenses.

---

## 9. Python Runtime (CPython)

- **Project URL**: [https://www.python.org/](https://www.python.org/)
- **Copyright**: Copyright (C) 2001-2026 Python Software Foundation. All rights reserved.
- **License**: **Python Software Foundation (PSF) License Agreement**
- **License Link**: [https://docs.python.org/3/license.html](https://docs.python.org/3/license.html)

---

## 10. PyInstaller

- **Project URL**: [https://pyinstaller.org/](https://pyinstaller.org/)
- **Copyright**: Copyright (C) 2005-2026 PyInstaller Development Team.
- **License**: **GNU General Public License version 2 (GPL-2.0) with Bootloader Exception**
- **Note**: The Bootloader Exception permits distribution of self-contained executables created by PyInstaller under the author's chosen license without requiring the application code to be GPL licensed.

---
---

[ENGLISH](#english) | [한국어](#korean)

<a id="korean"></a>
# 제3자 오픈소스 소프트웨어 라이선스 고지문 (한국어 안내)

zipper9은 여러 제3자 오픈소스 라이브러리, 모듈 및 독립 실행 도구를 기반으로 동작합니다. 본 문서는 각 오픈소스 라이선스에 따라 요구되는 저작권 고지, 라이선스 식별자 및 관련 약관을 제공합니다.

---

## 1. 7-Zip & unRAR
- **저작권**: 
  - Copyright (C) 1999-2026 Igor Pavlov (7-Zip)
  - Copyright (C) 1993-2026 Alexander Roshal (unRAR portion)
- **라이선스**: **GNU Lesser General Public License version 2.1 이상 (LGPL-2.1+)** with unRAR 제한 조항
- **unRAR 라이선스 제한 조항 고지**:
  - 7-Zip 소스코드는 unRAR 부분을 제외하고 GNU LGPL 라이선스에 따라 배포됩니다.
  - unRAR 부분은 독점 기술인 RAR 압축 생성 알고리즘을 재현하는 데 사용할 수 없습니다.
  - 저작권자(Alexander Roshal)의 서면 동의 없이 수정된 unRAR 소스코드를 별도로 배포하는 것은 엄격히 금지됩니다.
  - zipper9은 오직 압축 해제 용도로만 7-Zip 모듈을 호출하며, 독점 RAR 압축 알고리즘을 일절 구현하거나 배포하지 않습니다.

---

## 2. unalz (알집 ALZ 오픈소스 해제 엔진)
- **저작권**: Copyright (C) 2004-2026 Kippler (kippler@gmail.com)
- **라이선스**: **zlib/libpng License**
- **기업 및 공공기관 100% 무료 보증**:
  - 알집(ALZip)의 독자 규격인 ALZ(`.alz`, `.a00`) 아카이브 해제는 zlib/libpng 라이선스를 따르는 Kippler 님의 순수 오픈소스 unalz 엔진을 통해 수행됩니다.
  - 상업적 업무 환경을 포함하여 어떠한 제약 없이 자유롭게 사용 및 재배포가 가능하므로, 기업체 및 관공서에서도 알툴즈 상업용 라이선스 단속 우려 없이 100% 무료로 안심하고 사용할 수 있습니다.

---

## 3. LZ4 (초고속 스트리밍 압축)
- **저작권**: Copyright (C) 2011-2026 Yann Collet
- **라이선스**:
  - 라이브러리 (`liblz4`): **BSD 2-Clause License**
  - 커맨드라인 CLI (`lz4.exe`): **GNU General Public License v2.0 (GPL-2.0)**
- **컴플라이언스 안내**:
  - zipper9은 표준 IPC 파이프를 통해 `lz4.exe`를 독립된 외부 프로세스로 실행합니다. 내부 심볼을 정적/동적으로 링크하지 않으므로 GPL v2.0 프로세스 경계 컴플라이언스를 완벽히 준수합니다.

---

## 4. Zstandard (zstd)
- **저작권**: Copyright (C) 2016-2026 Meta Platforms, Inc.
- **라이선스**: **BSD 3-Clause License** / GPL v2.0 (듀얼 라이선스 - zipper9은 BSD 3-Clause 채택)

---

## 5. CustomTkinter (모던 GUI 프레임워크)
- **저작권**: Copyright (C) 2022-2026 Tom Schimansky
- **라이선스**: **Creative Commons Zero v1.0 Universal (CC0 1.0)** / **MIT License**

---

## 6. Windnd (Windows 드래그 앤 드롭 훅)
- **저작권**: Copyright (C) 2019-2026 Harvey Bao
- **라이선스**: **MIT License**

---

## 7. DarkDetect (OS 다크 모드 감지)
- **저작권**: Copyright (C) 2019-2026 Alberto Sottile
- **라이선스**: **BSD 3-Clause License**

---

## 8. Rust Crates & Windows 11 모던 셸 확장 모듈
- **저작권**: Copyright (C) The Rust Project Contributors & Crates Authors
- **라이선스**: **MIT License** / **Apache License 2.0**
- **사용 크레이트**: `pyo3`, `flate2`, `zstd`, `rayon`, `thiserror`, `zip`, `windows-sys`, `walkdir`. 모든 의존성은 표준 허용적 오픈소스 라이선스에 따라 안전하게 사용됩니다.

---

## 9. Python Runtime (CPython)
- **저작권**: Copyright (C) 2001-2026 Python Software Foundation.
- **라이선스**: **PSF License Agreement**

---

## 10. PyInstaller (독립 실행 파일 패키징)
- **저작권**: Copyright (C) 2005-2026 PyInstaller Development Team.
- **라이선스**: **GNU General Public License version 2 (GPL-2.0) with Bootloader Exception**
- **안내**: Bootloader Exception 조항에 따라 PyInstaller로 생성된 단독 실행 바이너리는 개발자가 선택한 라이선스(Fair-Code)에 따라 배포될 수 있으며 앱 소스코드에 GPL 전파가 면제됩니다.
