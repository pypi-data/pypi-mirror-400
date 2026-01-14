# project

This repository contains a minimal `project/` package with placeholder encoded model files.

Files added:

- `project/__init__.py` — package init
- `project/app.py` — small CLI demo to load the model and scaler
- `project/loader.py` — loader utilities (decodes base64 if present)
- `project/model/final.enc` — placeholder encoded model (base64 text)
- `project/model/scaler.enc` — placeholder encoded scaler (base64 text)
- `tools/encrypt_models.py` — utility to base64-encode a file into the `project/model` directory
- `pyproject.toml` — minimal project metadata

Try it (PowerShell):

```powershell
# Encode a real model file into the project/model directory
python .\tools\encrypt_models.py --src .\some_model.pkl --dst .\project\model\final.enc

# Run the demo loader
python .\project\app.py --model .\project\model\final.enc --scaler .\project\model\scaler.enc
```

Notes:
- The "encryption" here is simple base64 encoding for portability and demo purposes. Replace with a real encryption method if you need confidentiality.
a5SS84Y4qJa1XC7jksY3NQRfpH4J8oXlomhsKAQmyHI=