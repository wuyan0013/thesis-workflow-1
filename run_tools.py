# -*- coding: utf-8 -*-
"""
启动论文工具箱应用
在端口 8502 上运行 Streamlit 应用
"""

import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    app_path = Path(__file__).parent / "app_tools.py"

    print("=" * 50)
    print("ThesisAI 论文工具箱")
    print("=" * 50)
    print(f"启动地址: http://localhost:8502")
    print("功能: 论文降重 | 降AIGC率")
    print("=" * 50)

    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        "--server.port", "8502",
        "--server.headless", "true"
    ])
