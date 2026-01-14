from pathlib import Path

from kaizo import ConfigParser
from kaizo.utils import FnWithKwargs

X = 5
Y = 6
Z = 7

main_py = f"""
def fn(x,y,z):
  return (x,y,z)

def fn2(cb):
    return cb({X},{Y})
"""


lazy_config = f"""
local: main.py
a:
    module: local
    source: fn
    lazy: true
    args:
        z: {Z}
b:
    module: local
    source: fn2
    args:
        cb: .{{a}}
"""


def test_lazy_injection(tmp_path: Path) -> None:
    module = tmp_path / "main.py"
    module.write_text(main_py)

    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text(lazy_config)

    parser = ConfigParser(cfg_file, kwargs={"injected": X})
    out = parser.parse()

    assert isinstance(out["a"], FnWithKwargs)
    assert out["b"] == (X, Y, Z)
