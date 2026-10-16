"""Initialize a private local signing key in the operator's persistent Docker volume."""

import secrets
from pathlib import Path

from app.config import settings

if settings.auth_mode == "local":
    path = Path(settings.auth_key_file)
    if not path.exists():
        with path.open("x") as stream:
            path.chmod(0o600)
            stream.write(secrets.token_hex(64))
