import logging
from typing import Any, Dict, Optional
from urllib.parse import urlparse, urlunparse, ParseResult

import requests
from flask import current_app

from ogd.apis.models.enums.RESTType import RESTType
from ogd.apis.models.enums.ResponseStatus import ResponseStatus
from ogd.apis.models.APIResponse import APIResponse

class APIRequest:
    def __init__(self, url:str, request_type:str | RESTType, params:Optional[Dict[str, Any]]=None, body:Optional[Dict[str, Any]]=None, timeout:int=1):
        """Utility function to make it easier to send requests to a remote server during unit testing.

        This function does some basic sanity checking of the target URL,
        maps the request type to the appropriate `requests` function call,
        and performs basic error handling to notify what error occurred.

        :param url: The target URL for the web request
        :type url: str
        :param request: Whether to perform a "GET", "POST", or "PUT" request
        :type request: str
        :param params: A mapping of request parameter names to values. Defaults to {}
        :type params: Dict[str, Any], optional
        :param body: The body of the request to send. Defaults to None
        :type body: Dict[str, Any], optional
        :param logger: A logger to use for debug/error outputs. Defaults to None
        :type logger: logging.Logger, optional
        :raises err: Currently, any exceptions that occur during the request will be raised up.
            If verbose logging is on, a simple debug message indicating the request type and URL is printed first.
        :return: The `Response` object from the request, or None if an error occurred.
        :rtype: requests.Response
        """
        params = params or {}

        self._request_type : RESTType

        if not url.startswith("http://") or url.startswith("https://"):
            url = f"https://{url}"
        if isinstance(request_type, RESTType):
            self._request_type = request_type
        else:
            try:
                self._request_type = RESTType[request_type]
            except KeyError:
                current_app.logger.warning(f"Bad request type {request_type}, defaulting to GET")
                self._request_type = RESTType.GET

        self._url = url
        self._params = params
        self._body = body
        self._timeout = timeout

        
    def Execute(self, logger:Optional[logging.Logger]=None) -> APIResponse:
        ret_val : APIResponse

        if logger is None and current_app:
            logger = current_app.logger

        response : requests.Response
        try:
            match (self._request_type):
                case RESTType.GET:
                    response = requests.get( self._url, params=self._params, timeout=self._timeout)
                case RESTType.POST:
                    response = requests.post(self._url, params=self._params, data=self._body, timeout=self._timeout)
                case RESTType.PUT:
                    response = requests.put( self._url, params=self._params, data=self._body, timeout=self._timeout)
                case _:
                    if logger:
                        logger.warning(f"Bad request type {self._request_type}, defaulting to GET")
                    response = requests.get(self._url, params=self._params, timeout=self._timeout)
        except Exception as err:
            if logger:
                logger.error(f"Error on {self._request_type} request to {self._url} : {err}")
            raise err
        else:
            ret_val = APIResponse.FromResponse(response)
            if logger:
                out = logger.debug if ret_val.Status == ResponseStatus.OK else logger.warning
                out(f"Request sent to:        {self._url}")
                out(f"Response received from: {self._url}")
                out(f"   Status: {ret_val.Status}")
                out(f"   Msg:    {ret_val.Message}")
                out(f"   Value:  {ret_val.Value}")
        return ret_val
