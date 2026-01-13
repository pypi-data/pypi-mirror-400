from aiohttp import ClientResponse


class UnexpectedThirdPartyResponseError(ValueError):
    response: ClientResponse

    def __init__(self, response: ClientResponse, response_text: str) -> None:
        self.response = response
        request_info = response.request_info
        super().__init__(
            f"Unexpected response for {request_info.method} {request_info.url}: "
            f"{response.status} - {response_text}"
        )
