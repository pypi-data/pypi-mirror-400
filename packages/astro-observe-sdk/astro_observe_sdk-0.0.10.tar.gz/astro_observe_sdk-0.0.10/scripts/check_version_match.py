import re
import sys
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent.parent
    pyproject_path = root / "pyproject.toml"
    constants_path = root / "src" / "astro_observe_sdk" / "constants.py"

    # Read pyproject.toml
    with open(pyproject_path, "r", encoding="utf-8") as f:
        pyproject_content = f.read()
    match_pyproject = re.search(r'version\s*=\s*["\']([^"\']+)["\']', pyproject_content)
    if not match_pyproject:
        print("Could not find version in pyproject.toml", file=sys.stderr)
        sys.exit(1)
    pyproject_version = match_pyproject.group(1)

    # Read constants.py
    with open(constants_path, "r", encoding="utf-8") as f:
        constants_content = f.read()
    match_constants = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', constants_content)
    if not match_constants:
        print("Could not find __version__ in constants.py", file=sys.stderr)
        sys.exit(1)
    const_version = match_constants.group(1)

    # Compare
    if pyproject_version != const_version:
        print("Version mismatch detected:")
        print(f"   pyproject.toml : {pyproject_version}")
        print(f"   constants.py   : {const_version}")
        sys.exit(1)

    print(f"Versions match: {pyproject_version}")


if __name__ == "__main__":
    main()
