import io
import joblib
from cryptography.fernet import Fernet
import importlib.resources as res

# 🔐 Obfuscate key (example pattern)
_K1 = b"wAXQsXg8HwcpupgPMQ-p"
_K2 = b"lqGdnx_R_q2BioXVvXn_AYc="

KEY = _K1 + _K2  # simple obfuscation

def load_model_and_scaler():
    f = Fernet(KEY)

    with res.files("project.model").joinpath("final.enc").open("rb") as fp:
        model_bytes = f.decrypt(fp.read())
        model = joblib.load(io.BytesIO(model_bytes))

    with res.files("project.model").joinpath("scaler.enc").open("rb") as fp:
        scaler_bytes = f.decrypt(fp.read())
        scaler = joblib.load(io.BytesIO(scaler_bytes))

    return model, scaler
