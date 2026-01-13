from .key.signer import sign_license
from .key.verifier import verify_license

try:
    from ._version import version as __version__
except Exception:  # 後備（理論上不太會用到）
    __version__ = "0.0.0"

__all__ = ["sign_license", "verify_license"]
