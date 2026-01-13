from pwhl_api.library.http import HTTPClient, HTTPResponse
class HTTPEndpointClient(HTTPClient):
    base_url = "https://lscluster.hockeytech.com/feed/index.php?feed={endpoint}"
    def get(self, endpoint: str, params: dict = None) -> HTTPResponse:
        response = super().get(self.base_url, endpoint, params= params)
        return HTTPEndpointResponse(response)

class HTTPEndpointResponse(HTTPResponse):
    def __init__(self, HTTPResponse: HTTPResponse):
        super().__init__(HTTPResponse.status_code, HTTPResponse.response, HTTPResponse.url)
    def get_raw_json(self):
        import json
        return json.loads(self.response.response.strip("()"))
    
    def get_data_frame(self):
        pass