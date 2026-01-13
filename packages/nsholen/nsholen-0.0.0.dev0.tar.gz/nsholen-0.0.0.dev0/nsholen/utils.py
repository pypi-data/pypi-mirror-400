import requests
from urllib.parse import quote_plus, urljoin
from typing import Any, Callable

class Headers:
    def __init__(self, headers: dict[str, str] | None = None):
        self.headers = headers if headers else {}
    
    def __call__(self, key: str = None, default: Any | None = None):
        if key:
            return self.headers.get(key, default)
        return self.headers

    def update_headers(self, headers: dict[str, str]) -> None:
        self.headers.update(headers)
    def remove_header(self, key: str) -> None:
        del self.headers[key]
    def clear_all(self) -> None:
        self.headers = {}

class ApiResponse:
    def __init__(self, status_code: int, binary, text: str, headers: Any):
        self.status_code: int = status_code
        self.text: str = text
        self.binary: bin = binary
        self.response_headers: Headers= Headers(headers)
    
    def __str__(self):
        return f"[STATUS: {self.status_code}]"
    
    def response_headers(self) -> Headers:
        """
        Returns NationStates API's headers response as a Headers() object.
        """
        return self.response_headers

class QueryString:
    def __init__(self):
        self.arguments = []
        self.key_arguments = {}
    
    def __str__(self):
        return "QueryString()"

    def set_arguments(self, args: list[str], kwargs: dict[str | list[str]] | None = None) -> None:
        if args:
            self.arguments = args
        if kwargs:
            for k, v in kwargs.items():
                self.key_arguments.update({k: v})
        
        
    def build(self):
        def parse_arguments(separator: str, args: list[str] | dict[str, str]) -> str:
                    if isinstance(args, list):
                        return separator.join(args)
                    elif isinstance(args, str):
                        return args
                    elif isinstance(args, dict):
                        items = separator.join([f"{k}={parse_arguments("+", v)}" for k, v in args.items()])
                        return items
        params = self.arguments
        key_params = self.key_arguments
        
        final_query = "q="
        final_query += f"{parse_arguments("+", params)}"
        if key_params:
            final_query += f";{parse_arguments(";", key_params)}"
        return final_query

class UrlManager:
    def __init__(self):
        pass
    
    def build_url(self,
            base: str,
            path: list[str] = None,
            unique_slug: tuple[str, str] | None = None,
            querystring: QueryString = None) -> str:
                final_url = base
                query = querystring
                sep = "?"
                if path:
                    parsed_path = "/".join(path)
                    final_url += f"/{parsed_path}"
                if unique_slug:
                    sep = "&"
                    key: str = unique_slug[0]
                    value: str = unique_slug[1]
                    final_url += f"?{key}={value}"
                if query:
                    final_url += f"{sep}{query.build()}"
                return final_url

class RequestsManager:
    def __init__(self):
        self.ratelimit_policy: tuple[int, int]
        self.sleep_time: int
        self.headers: Headers = None
        self.requests_made: int = 0

    def set_headers(self, new_headers: Headers) -> None:
        self.headers = new_headers
    def set_ratelimit_policy(self, new_policy: tuple[int, int]) -> None:
        self.ratelimit_policy = new_policy
    def set_sleep_time(self, new_sleep_time: int) -> None:
        self.sleep_time = new_sleep_time
    def make_request(self, url: str, specific_headers: Headers = None) -> ApiResponse:
        def do_request():
            active_headers_in_request = specific_headers if specific_headers else self.headers()
            print(f"{active_headers_in_request=}")
            response = requests.get(url, headers=active_headers_in_request)
            api_response = ApiResponse(response.status_code, response.content, response.text, response.headers)
            return api_response
        api_response = do_request()
        return api_response
        

if __name__ == "__main__":
    ...