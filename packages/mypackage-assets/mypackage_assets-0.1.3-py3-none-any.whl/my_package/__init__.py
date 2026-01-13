from pathlib import Path
from .extractor import extract_all_files

FLAG = Path.home() / ".my_package_initialized"

if not FLAG.exists():
    extract_all_files()
    FLAG.touch()
