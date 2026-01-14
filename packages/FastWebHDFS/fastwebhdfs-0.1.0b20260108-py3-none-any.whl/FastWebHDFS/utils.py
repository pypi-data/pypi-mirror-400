import re
from typing import Dict, Any
from urllib.parse import quote


def _validate_path(self,path: str) -> str:
    if not isinstance(path, str):
        raise TypeError("path must be a string")
    if not path.startswith("/"):
        raise ValueError("path must start with '/'")
    return quote(path)

def _validate_permission(self,permission: str) -> str:
    OCTAL = re.compile(r"^[0-7]{3,4}$")
    if not isinstance(permission, str):
        raise TypeError("permission must be a raw octal string (e.g., '755')")
    if not OCTAL.fullmatch(permission):
        raise ValueError(
            f"Invalid octal permission '{permission}'. "
            "Must be 3–4 digits, each between 0–7 (e.g., '755', '1777')."
        )
    return permission

def _query(self,parameters: Dict[str,Any]) -> str:
    return '&'.join(
        f'{k}={v}'
        for k,v in parameters.items()
        if v is not None
    )
