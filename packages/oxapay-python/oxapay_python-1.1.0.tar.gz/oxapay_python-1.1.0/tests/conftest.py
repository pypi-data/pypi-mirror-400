"""Test configuration.

This project uses a `src/` layout. Adding `src/` to `sys.path` lets tests run
with a plain `pytest` invocation.
"""

from __future__ import annotations

import sys
from pathlib import Path


# Ensure `import oxapay` works when running tests locally.
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))
