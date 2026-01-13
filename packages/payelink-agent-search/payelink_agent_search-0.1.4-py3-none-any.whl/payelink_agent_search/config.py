from dataclasses import dataclass
from typing import Dict, Optional

from ._version import __version__

@dataclass(frozen=True)
class ClientConfig:
    base_url: str = "http://127.0.0.1:8000"
    timeout: float = 60.0
    retries: int = 2
    api_key: Optional[str] = None
    extra_headers: Optional[Dict[str, str]] = None
    user_agent: str = f"payelink-agent-search-sdk/{__version__}"