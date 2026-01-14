from pathlib import Path

import pytest

from kaizo import ConfigParser

X = 5

main_py = """
def raise_error():
  raise ValueError("error")
"""

ignore_config = """
local: main.py
x:
  module: local
  source: raise_error
  policy: ignore
"""

raise_config = """
local: main.py
x:
  module: local
  source: raise_error
  policy: raise
"""


def test_ignore_exception(tmp_path: Path) -> None:
    module = tmp_path / "main.py"
    module.write_text(main_py)

    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text(ignore_config)

    parser = ConfigParser(cfg_file)
    out = parser.parse()

    assert out["x"] is None


def test_raise_exception(tmp_path: Path) -> None:
    module = tmp_path / "main.py"
    module.write_text(main_py)

    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text(raise_config)

    parser = ConfigParser(cfg_file)
    out = parser.parse()

    with pytest.raises(ValueError, match="error"):
        out["x"]
