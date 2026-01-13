from pathlib import Path
from .utils import QueryString, ApiResponse, UrlManager, RequestsManager, Headers

class NsHolen:
    """
    NsHolen is a python libraby dedicated to simplify the repetitive steps of developing wrappers for the NationStates API, such as query management, while giving you liberty
    """
    def __init__(self):
        self._urlManager = UrlManager()
        self._requestsManager = RequestsManager()
    
    def url_manager(self):
        return self._urlManager
    def requests_manager(self):
        return self._requestsManager
    def new_query(self):
        return QueryString()