from uplink import Body, json, post, response_handler, returns

from bpkio_api.consumer import BpkioSdkConsumer
from bpkio_api.models.Login import LoginCredentials, LoginResponse
from bpkio_api.response_handler import postprocess_response


@response_handler(postprocess_response)
class LoginApi(BpkioSdkConsumer):
    def __init__(self, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)

    @json
    @returns.json()
    @post("login")
    def login(self, body: Body(type=LoginCredentials)) -> LoginResponse:
        """Get the tenant information for the current user"""

    def login_with_credentials(self, email: str, password: str) -> LoginResponse:
        return self.login(body=LoginCredentials(email=email, password=password))
