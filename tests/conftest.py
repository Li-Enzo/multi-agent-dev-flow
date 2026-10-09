"""pytest 公共配置：定位 scripts/ 目录并提供脚本运行助手。"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


@pytest.fixture()
def run_script():
    """以子进程方式运行 scripts/ 下脚本，返回 CompletedProcess。"""
    def _run(name, *args, env_extra=None):
        import os
        env = dict(os.environ)
        env.update(env_extra or {})
        return subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / name), *map(str, args)],
            capture_output=True, text=True, encoding="utf-8", env=env,
        )
    return _run
