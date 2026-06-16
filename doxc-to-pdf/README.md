# DOCX to PDF Converter — SAP SM69

See the [root README](../README.md) for full setup and usage instructions.

## Quick reference

| File | Purpose |
|------|---------|
| `converter-backend/convert.py` | Script deployed on the SAP app server |
| `converter-backend/requirements.txt` | Python dependency (`dxpdf==0.2.25`) |
| `converter-backend/download_wheels.bat` | Download wheels on an internet-connected machine |
| `converter-backend/install_offline.bat` | Install wheels on the offline SAP app server |

## Minimal usage

```powershell
python convert.py "C:\tmp\input.docx" "C:\tmp\output.pdf"
```

Exit code 0 = success. See root README for SM69 and ABAP setup.
