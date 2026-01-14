from typing import Protocol

class OAuthConfig(Protocol):
    domain: str
    audience: str
    algorithms: list[str]
    issuer: str
