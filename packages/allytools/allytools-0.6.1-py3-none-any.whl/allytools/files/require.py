from pathlib import Path
from typing import Iterable, Optional

def ensure_folder(path: Path) -> Path:
    """
    Ensure that a directory exists. Create it if missing.
    """
    if path.exists():
        if not path.is_dir():
            raise ValueError(f"Expected a directory path, got a file path: {path}")
    else:
        path.mkdir(parents=True, exist_ok=True)
    return path

def require_dir(path: Path) -> Path:
    """
    Require that a directory exists.
    """
    if not path.exists():
        raise FileNotFoundError(f"Directory does not exist: {path}")
    if not path.is_dir():
        raise FileNotFoundError(f"Path is not a directory: {path}")
    return path


def require_file(
    *,
    path: Path,
    suffixes: str | Iterable[str] = (),
) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    if not path.is_file():
        raise FileNotFoundError(f"Expected file, got directory: {path}")

    if suffixes:
        if isinstance(suffixes, str):
            suffixes = (suffixes,)

        if path.suffix not in suffixes:
            raise ValueError(
                f"Invalid file suffix: {path.suffix!r}, "
                f"expected one of {tuple(suffixes)} for {path}")

def require_paths(
    *paths: Path,
    files: Iterable[Path] = (),
    dirs: Iterable[Path] = (),
) -> None:
    errors: list[str] = []


    for p in paths:
        if not p.exists():
            errors.append(f"Missing path: {p}")

    for p in dirs:
        if not p.exists():
            errors.append(f"Missing directory: {p}")
        elif not p.is_dir():
            errors.append(f"Expected directory, got file: {p}")

    for p in files:
        if not p.exists():
            errors.append(f"Missing file: {p}")
        elif not p.is_file():
            errors.append(f"Expected file, got directory: {p}")

    if errors:
        raise FileNotFoundError("\n".join(errors))