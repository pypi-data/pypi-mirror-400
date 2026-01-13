from importlib.resources import files, as_file
from pathlib import Path

def extract_all_files():
    resource_dir = files("my_package").joinpath("data")
    dest_dir = Path.home() / "my_package_data"
    dest_dir.mkdir(exist_ok=True)

    with as_file(resource_dir) as src_dir:
        for file in src_dir.iterdir():
            if file.is_file():
                dest = dest_dir / file.name
                dest.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")

    return dest_dir
