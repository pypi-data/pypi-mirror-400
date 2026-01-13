import httpx
import time
from typing import Any, Dict, Optional, Union
from flotorch.sdk.logger.global_logger import get_logger
from flotorch.sdk.logger.utils.models import HttpRequest

logger = get_logger()

JSONType = Union[Dict[str, Any], list]



async def async_http_get(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None
) -> Any:
    """
    Asynchronously send a GET request.

    Args:
        url: The URL to send the request to.
        headers: Optional HTTP headers to include in the request.
        params: Optional query parameters to include in the request.
        timeout: Optional timeout for the request in seconds.

    Returns:
        The parsed JSON response, or raw text if response is not JSON.

    Raises:
        APIError: If the response status code is not 2xx.
    """
    start_time = time.time()
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=params, timeout=timeout)
        duration = time.time() - start_time
        # logger.info(
        #     HttpRequest(method='GET', url=url, status_code=resp.status_code, duration=duration)
        # )
        return _parse_response(resp)

async def async_http_post(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[JSONType] = None,
    timeout: Optional[float] = None,
    return_headers: Optional[bool] = False
) -> Any:
    """
    Asynchronously send a POST request with a JSON body.

    Args:
        url: The URL to send the request to.
        headers: Optional HTTP headers to include in the request.
        json: Optional JSON body to include in the request.
        timeout: Optional timeout for the request in seconds.

    Returns:
        The parsed JSON response, or raw text if response is not JSON.

    Raises:
        APIError: If the response status code is not 2xx.
    """
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.post(url, headers=headers, json=json, timeout=timeout)
        latency = float(resp.headers.get("x-gateway-total-latency", 0))
        # logger.info(
        #     HttpRequest(method='POST', url=url, status_code=resp.status_code, duration=latency, request_type='async')
        # )
        if return_headers:
            return _parse_response(resp), resp.headers
        else:
            return _parse_response(resp)

async def async_http_put(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[JSONType] = None,
    timeout: Optional[float] = None
) -> Any:
    """
    Asynchronously send a PUT request with a JSON body.

    Args:
        url: The URL to send the request to.
        headers: Optional HTTP headers to include in the request.
        json: Optional JSON body to include in the request.
        timeout: Optional timeout for the request in seconds.

    Returns:
        The parsed JSON response, or raw text if response is not JSON.

    Raises:
        APIError: If the response status code is not 2xx.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.put(url, headers=headers, json=json, timeout=timeout)
        # logger.info(
        #     HttpRequest(method='PUT', url=url, status_code=resp.status_code, request_type='async')
        # )
        return _parse_response(resp)

async def async_http_patch(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[JSONType] = None,
    timeout: Optional[float] = None
) -> Any:
    """
    Asynchronously send a PATCH request with a JSON body.

    Args:
        url: The URL to send the request to.
        headers: Optional HTTP headers to include in the request.
        json: Optional JSON body to include in the request.
        timeout: Optional timeout for the request in seconds.

    Returns:
        The parsed JSON response, or raw text if response is not JSON.

    Raises:
        APIError: If the response status code is not 2xx.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.patch(url, headers=headers, json=json, timeout=timeout)
        # logger.info(
        #     HttpRequest(method='PATCH', url=url, status_code=resp.status_code, request_type='async')
        # )
        return _parse_response(resp)

async def async_http_delete(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None
) -> Any:
    """
    Asynchronously send a DELETE request.

    Args:
        url: The URL to send the request to.
        headers: Optional HTTP headers to include in the request.
        timeout: Optional timeout for the request in seconds.

    Returns:
        The parsed JSON response, or raw text if response is not JSON.

    Raises:
        APIError: If the response status code is not 2xx.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.delete(url, headers=headers, timeout=timeout)
        # logger.info(
        #     HttpRequest(method='DELETE', url=url, status_code=resp.status_code, request_type='async')
        # )
        return _parse_response(resp)

def http_get(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    timeout: Optional[float] = None
) -> Any:
    """
    Send a GET request.

    Args:
        url: The URL to send the request to.
        headers: Optional HTTP headers to include in the request.
        params: Optional query parameters to include in the request.
        timeout: Optional timeout for the request in seconds.

    Returns:
        The parsed JSON response, or raw text if response is not JSON.

    Raises:
        APIError: If the response status code is not 2xx.
    """
    start_time = time.time()
    with httpx.Client() as client:
        resp = client.get(url, headers=headers, params=params, timeout=timeout)
        duration = time.time() - start_time
        # logger.info(
        #     HttpRequest(method='GET', url=url, status_code=resp.status_code, duration=duration)
        # )
        return _parse_response(resp)

def http_post(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[JSONType] = None,
    timeout: Optional[float] = None,
    return_headers: Optional[bool] = False
) -> Any:
    """
    Send a POST request with a JSON body.

    Args:
        url: The URL to send the request to.
        headers: Optional HTTP headers to include in the request.
        json: Optional JSON body to include in the request.
        timeout: Optional timeout for the request in seconds.

    Returns:
        The parsed JSON response, or raw text if response is not JSON.

    Raises:
        APIError: If the response status code is not 2xx.
    """
    with httpx.Client(follow_redirects=True) as client:
        resp = client.post(url, headers=headers, json=json, timeout=timeout)
        latency = float(resp.headers.get("x-gateway-total-latency", 0))
        # logger.info(
        #     HttpRequest(method='POST', url=url, status_code=resp.status_code, duration=latency)
        # )
        if return_headers:
            return _parse_response(resp), resp.headers
        else:
            return _parse_response(resp)

def http_put(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[JSONType] = None,
    timeout: Optional[float] = None
) -> Any:
    """
    Send a PUT request with a JSON body.

    Args:
        url: The URL to send the request to.
        headers: Optional HTTP headers to include in the request.
        json: Optional JSON body to include in the request.
        timeout: Optional timeout for the request in seconds.

    Returns:
        The parsed JSON response, or raw text if response is not JSON.

    Raises:
        APIError: If the response status code is not 2xx.
    """
    with httpx.Client() as client:
        resp = client.put(url, headers=headers, json=json, timeout=timeout)
        # logger.info(
        #     HttpRequest(method='PUT', url=url, status_code=resp.status_code)
        # )
        return _parse_response(resp)

def http_patch(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    json: Optional[JSONType] = None,
    timeout: Optional[float] = None
) -> Any:
    """
    Send a PATCH request with a JSON body.

    Args:
        url: The URL to send the request to.
        headers: Optional HTTP headers to include in the request.
        json: Optional JSON body to include in the request.
        timeout: Optional timeout for the request in seconds.

    Returns:
        The parsed JSON response, or raw text if response is not JSON.

    Raises:
        APIError: If the response status code is not 2xx.
    """
    with httpx.Client() as client:
        resp = client.patch(url, headers=headers, json=json, timeout=timeout)
        # logger.info(
        #     HttpRequest(method='PATCH', url=url, status_code=resp.status_code)
        # )
        return _parse_response(resp)

def http_delete(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None
) -> Any:
    """
    Send a DELETE request.

    Args:
        url: The URL to send the request to.
        headers: Optional HTTP headers to include in the request.
        timeout: Optional timeout for the request in seconds.

    Returns:
        The parsed JSON response, or raw text if response is not JSON.

    Raises:
        APIError: If the response status code is not 2xx.
    """
    with httpx.Client() as client:
        resp = client.delete(url, headers=headers, timeout=timeout)
        # logger.info(
        #     HttpRequest(method='DELETE', url=url, status_code=resp.status_code)
        # )
        return _parse_response(resp)

class APIError(Exception):
    """
    Exception raised for API response errors.

    Attributes:
        status_code: HTTP status code returned by the API.
        message: Error message from the API response.
    """
    def __init__(self, status_code: int, message: str):
        super().__init__(f"[{status_code}] {message}")
        self.status_code = status_code
        self.message = message


def _parse_response(resp: httpx.Response) -> Any:
    if 200 <= resp.status_code < 300:
        try:
            return resp.json()
        except ValueError:
            return resp.text
    raise APIError(resp.status_code, resp.text)