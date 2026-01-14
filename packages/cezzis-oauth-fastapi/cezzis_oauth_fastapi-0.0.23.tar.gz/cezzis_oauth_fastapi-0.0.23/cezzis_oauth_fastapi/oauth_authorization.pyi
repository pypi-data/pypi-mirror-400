from cezzis_oauth_fastapi.oauth_config import OAuthConfig as OAuthConfig
from fastapi import Request as Request
from typing import Callable

def oauth_authorization(scopes: list[str], config_provider: Callable[[], OAuthConfig]): ...
