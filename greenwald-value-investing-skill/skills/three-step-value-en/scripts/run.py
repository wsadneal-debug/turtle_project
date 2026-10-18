#!/usr/bin/env python3
"""Run the bundled standard-library valuation helper."""
from pathlib import Path
import sys


def _library_path() -> Path:
    script = Path(__file__).resolve()
    bundled = script.parent / "lib"
    if bundled.exists():
        if not (bundled / "asset_value_ai" / "portable.py").is_file():
            raise RuntimeError("Incomplete skill bundle: missing portable calculation helper")
        return bundled
    # Source-checkout development only: derive the repository from this file,
    # without using the working directory, environment, or an installed package.
    repository = script.parents[3]
    expected_script = repository / "skills" / "three-step-value-en" / "scripts" / "run.py"
    source = repository / "src"
    if (script == expected_script and (repository / "pyproject.toml").is_file()
            and (source / "asset_value_ai" / "portable.py").is_file()):
        return source
    raise RuntimeError("Missing bundled library; use the complete three-step-value-en distribution")


def main() -> int:
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(_library_path()))
    from asset_value_ai.portable import main as portable_main
    return portable_main()


if __name__ == "__main__":
    raise SystemExit(main())
