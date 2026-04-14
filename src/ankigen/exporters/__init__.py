from pathlib import Path


def get_export_format(output_path: str | None) -> str:
    """Determine export format from output path extension.

    Returns 'apkg' for .apkg files, 'tsv' for everything else (including stdout).
    """
    if output_path is None:
        return "tsv"
    if Path(output_path).suffix.lower() == ".apkg":
        return "apkg"
    return "tsv"
