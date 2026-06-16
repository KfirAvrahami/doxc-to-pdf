#!/usr/bin/env python3
"""
DOCX to PDF converter for SAP SM69 / SXPG_COMMAND_EXECUTE.

Usage:
    python convert.py <input_path> <output_path>

Arguments:
    input_path   Absolute path to the source .docx file on the application server.
    output_path  Absolute path where the resulting .pdf will be written.

Exit codes:
    0  Conversion succeeded.
    1  Wrong number of arguments (usage error).
    2  Input file not found or unsupported extension.
    3  Conversion failed (dxpdf error).

SM69 setup (Windows example):
    Operating System Command : C:\Python3xx\python.exe
    Parameters               : C:\sap\scripts\convert.py
    Additional Params Allowed: checked

ABAP call example:
    CONCATENATE lv_input_path ' ' lv_output_path INTO lv_params.
    CALL FUNCTION 'SXPG_COMMAND_EXECUTE'
      EXPORTING
        commandname           = 'Z_DOCX_TO_PDF'
        additional_parameters = lv_params
        terminationwait       = 'X'
        stdout                = 'X'
        stderr                = 'X'
      TABLES
        exec_protocol         = lt_log
      EXCEPTIONS
        OTHERS                = 15.

NOTE: ADDITIONAL_PARAMETERS is limited to 128 characters in SXPG_COMMAND_EXECUTE.
Keep file paths short (e.g. C:\tmp\in.docx C:\tmp\out.pdf).
"""

import sys
from pathlib import Path

ALLOWED_EXTENSIONS = {".docx", ".doc", ".odt", ".rtf", ".txt"}


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "ERROR: Expected exactly 2 arguments.\n"
            "Usage: python convert.py <input_path> <output_path>",
            file=sys.stderr,
        )
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(2)

    if input_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        print(
            f"ERROR: Unsupported file type '{input_path.suffix}'. "
            f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            file=sys.stderr,
        )
        sys.exit(2)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import dxpdf  # noqa: PLC0415

        dxpdf.convert_file(str(input_path), str(output_path))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Conversion failed: {exc}", file=sys.stderr)
        sys.exit(3)

    if not output_path.exists():
        print("ERROR: Conversion produced no output file.", file=sys.stderr)
        sys.exit(3)

    print(f"OK: {input_path} -> {output_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
