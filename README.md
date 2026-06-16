# DOCX to PDF Converter — SAP SM69 / SXPG_COMMAND_EXECUTE

Converts `.docx` (and other Word-compatible formats) to PDF from the SAP application server.  
The conversion is triggered via **transaction SM69** and called from ABAP using the function module `SXPG_COMMAND_EXECUTE`.

No LibreOffice, no internet connection, and no external services required at runtime.

---

## Folder structure

```
doxc-to-pdf/converter-backend/
    convert.py           ← the script deployed on the SAP app server
    requirements.txt     ← only: dxpdf==0.2.25
    download_wheels.bat  ← run on internet-connected machine to fetch wheels
    install_offline.bat  ← run on SAP app server to install from local wheels
```

The `docx-to-pdf-ui/` Angular frontend is no longer used and can be ignored.

---

## How it works

```
ABAP program
    │
    │  CALL FUNCTION 'SXPG_COMMAND_EXECUTE'
    │    commandname           = 'Z_DOCX_TO_PDF'
    │    additional_parameters = 'C:\tmp\in.docx C:\tmp\out.pdf'
    ▼
SM69 external command Z_DOCX_TO_PDF
    │  OS command : C:\Python3xx\python.exe
    │  Parameters : C:\sap\scripts\convert.py
    ▼
convert.py <input_path> <output_path>
    │  reads  → input .docx (app server file system)
    │  writes → output .pdf (app server file system)
    │  exit 0 on success, exit 2/3 on error
    ▼
ABAP reads STATUS / EXITCODE / EXEC_PROTOCOL
```

Exit codes returned to ABAP:

| Code | Meaning |
|------|---------|
| 0 | Conversion succeeded |
| 1 | Wrong number of arguments |
| 2 | Input file not found or unsupported extension |
| 3 | Conversion engine error |

---

## Step 1 — Install Python on the SAP application server

1. Download the Python 3 Windows installer from `https://www.python.org/downloads/` on an internet-connected machine and transfer it to the app server.
2. Install Python. During setup, check **"Add Python to PATH"**.
3. Verify in a Command Prompt or PowerShell:
   ```powershell
   python --version
   ```
   Note the full path to `python.exe` (e.g. `C:\Python312\python.exe`). You will need it in SM69.

---

## Step 2 — Install the dxpdf package (offline)

`dxpdf` is a standalone DOCX-to-PDF engine — no LibreOffice, no Microsoft Office, no internet needed at runtime.

### On an internet-connected machine (same Python version + Windows architecture as the app server)

Copy `converter-backend\` to the internet machine, then run:

```bat
cd converter-backend
download_wheels.bat
```

This creates a `wheels\` folder containing `dxpdf-0.2.25-*.whl` and all its dependencies as local files.

### On the SAP application server (offline)

Transfer the entire `converter-backend\` folder (including `wheels\`) to the app server, for example to `C:\sap\scripts\`. Then run:

```bat
cd C:\sap\scripts
install_offline.bat
```

Verify the installation:

```powershell
python -c "import dxpdf; print('dxpdf OK')"
```

---

## Step 3 — Deploy the script

Copy `convert.py` to a permanent location on the app server, for example:

```
C:\sap\scripts\convert.py
```

Test it manually from a Command Prompt:

```powershell
python C:\sap\scripts\convert.py "C:\tmp\test.docx" "C:\tmp\test.pdf"
```

You should see `OK: C:\tmp\test.docx -> C:\tmp\test.pdf` and exit code 0.

---

## Step 4 — Define the external command in SM69

1. Log on to SAP and run transaction **SM69**.
2. Choose **Create** (or **Change** an existing command).
3. Fill in the fields:

   | Field | Value |
   |-------|-------|
   | Command Name | `Z_DOCX_TO_PDF` |
   | Operating System | `Windows NT` |
   | Operating System Command | `C:\Python312\python.exe` *(adjust to your Python path)* |
   | Parameters for OS Command | `C:\sap\scripts\convert.py` |
   | Additional Parameters Allowed | **checked** |

4. Save.
5. Test from SM69: click **Execute** and enter a test parameter string, e.g.:
   ```
   C:\tmp\test.docx C:\tmp\test.pdf
   ```

> **Important — 128-character limit:** `SXPG_COMMAND_EXECUTE` accepts a maximum of 128 characters in `ADDITIONAL_PARAMETERS`. Keep input and output paths short. Use a short temp directory such as `C:\tmp\` to stay within the limit.

---

## Step 5 — Call from ABAP

```abap
DATA: lv_input  TYPE btcxpgpar,
      lv_output TYPE btcxpgpar,
      lv_params TYPE btcxpgpar,
      lv_status TYPE extcmdexex-status,
      lv_exit   TYPE extcmdexex-exitcode,
      lt_log    TYPE TABLE OF btcxpm.

" Build the parameter string: "<input_path> <output_path>"
" Paths must be absolute paths on the APPLICATION SERVER file system.
lv_input  = 'C:\tmp\document.docx'.
lv_output = 'C:\tmp\document.pdf'.
CONCATENATE lv_input ' ' lv_output INTO lv_params.

CALL FUNCTION 'SXPG_COMMAND_EXECUTE'
  EXPORTING
    commandname           = 'Z_DOCX_TO_PDF'
    additional_parameters = lv_params
    operatingsystem       = 'Windows NT'
    terminationwait       = 'X'
    stdout                = 'X'
    stderr                = 'X'
  IMPORTING
    status                = lv_status
    exitcode              = lv_exit
  TABLES
    exec_protocol         = lt_log
  EXCEPTIONS
    no_permission         = 1
    command_not_found     = 2
    parameters_too_long   = 3
    security_risk         = 4
    program_start_error   = 6
    program_termination_error = 7
    OTHERS                = 15.

IF sy-subrc <> 0 OR lv_exit <> 0.
  " Handle error — inspect lt_log for details
  MESSAGE e001(zz) WITH 'Conversion failed. Exit:' lv_exit.
ENDIF.

" Output PDF is now at lv_output on the application server.
" Use AL11 / FILE functions to read or move it as needed.
```

### Passing file paths dynamically

If the input/output paths come from user selection or a logical file name, use transaction **FILE** (logical file path maintenance) and the function module `FILE_GET_NAME` to resolve physical paths before passing them:

```abap
CALL FUNCTION 'FILE_GET_NAME'
  EXPORTING
    logical_filename = 'ZDOCX_INPUT'
  IMPORTING
    file_name        = lv_input
  EXCEPTIONS
    OTHERS           = 1.
```

---

## Supported input formats

| Extension | Format |
|-----------|--------|
| `.docx` | Microsoft Word (Office Open XML) |
| `.doc` | Microsoft Word 97-2003 |
| `.odt` | OpenDocument Text |
| `.rtf` | Rich Text Format |
| `.txt` | Plain text |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `COMMAND_NOT_FOUND` | SM69 command not saved or wrong name | Verify command name `Z_DOCX_TO_PDF` in SM69 |
| `PARAMETERS_TOO_LONG` | Combined path string > 128 chars | Use shorter paths (e.g. `C:\t\`) |
| Exit code 2 | Input file does not exist on app server | Verify the file exists at the given path on the app server (use AL11) |
| Exit code 3 | dxpdf conversion error | Check `lt_log` entries for the Python traceback; verify `dxpdf` is installed |
| `import dxpdf` fails | Wrong Python path in SM69, or dxpdf not installed | Run `install_offline.bat` again; confirm Python path in SM69 matches the one where dxpdf was installed |
