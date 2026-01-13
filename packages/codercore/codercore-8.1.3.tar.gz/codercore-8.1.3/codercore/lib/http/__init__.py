from contextlib import asynccontextmanager

from aiohttp import ClientResponse, ContentTypeError

from codercore.lib.http.exceptions import UnexpectedThirdPartyResponseError


@asynccontextmanager
async def verify_third_party_response(response: ClientResponse) -> None:
    try:
        yield
    except (ValueError, KeyError, ContentTypeError):
        raise UnexpectedThirdPartyResponseError(response, await response.text())
