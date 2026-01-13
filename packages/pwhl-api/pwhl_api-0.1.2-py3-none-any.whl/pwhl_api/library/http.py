import requests

class HTTPResponse:
    def __init__(self, status_code: int, response: dict, url: str):
        self.status_code = status_code
        self.response = response
        self.url = url

    def json(self):
        return self.response
    
class HTTPClient:
    hockeytechresponse = HTTPResponse
    headers = None
    proxies = None
    def __init__(self, headers: dict = None, proxies: dict = None):
        self.headers = headers
        self.proxies = proxies

    def get(self, base_url: str, endpoint: str, params: dict = None) -> HTTPResponse:
        if self.proxies is None:
            self.proxies = {
                "http": None,
                "https": None
            }
        if self.headers is None:
            self.headers = {
                "Host": "https://lscluster.hockeytech.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Referer": "https://lscluster.hockeytech.com/",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "Sec-Ch-Ua": '"Chromium";v="140", "Google Chrome";v="140", "Not;A=Brand";v="24"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Fetch-Dest": "empty",
            }
        if params is not None:
             endpoint += "&" + "&".join([f"{key}={value}" for key, value in params.items()])
        
        url = base_url.format(endpoint = endpoint)
        response = requests.get(url, headers=self.headers, proxies=self.proxies)
        url = response.url
        contents = response.text
        status_code = response.status_code
        hockeytechresponse = HTTPResponse(status_code = status_code, response = contents, url = url)
        return hockeytechresponse
        

    