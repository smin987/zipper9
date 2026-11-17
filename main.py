import os
import sys

# 프로젝트 루트 디렉터리를 sys.path 최우선으로 등록
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from zipper9_ui.app import main

if __name__ == "__main__":
    main()
