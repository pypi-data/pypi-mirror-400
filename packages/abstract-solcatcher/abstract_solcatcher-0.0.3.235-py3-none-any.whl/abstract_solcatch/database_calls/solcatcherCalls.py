import logging,asyncio
# Suppress logs below WARNING level
logging.basicConfig(level=logging.WARNING)
from abstract_apis import make_request,asyncPostRequest
from ..utils import *

async def SolcatcherApiCall(url=None,endpoint=None, *args, **kwargs):
    """
    Asynchronously resolves arguments and makes a POST request to Solcatcher Flask URL.
    """
    # Resolve coroutines in args
    resolved_args = [await arg if asyncio.iscoroutine(arg) else arg for arg in args]
    
    # Resolve coroutines in kwargs
    resolved_kwargs = {
        k: await v if asyncio.iscoroutine(v) else v
        for k, v in kwargs.items()
    }

    # Make the asynchronous POST request
    return await asyncPostRequest(
        url=getSolcatcherFlaskUrl(),
        endpoint=endpoint,
        data={"args": resolved_args, **resolved_kwargs}
    )

def makeSolcatcherRequest(url, data=None, headers=None, get_post=None, endpoint=None, status_code=False, raw_response=False, response_result=None, load_nested_json=True, auth=None, *args, **kwargs):
    """
    Generic function to make a request to a Solcatcher endpoint.
    """
    request_data = {"args": args, **kwargs}  # Merge args and kwargs into the data payload
    return make_request(
        url=url,
        data=data or request_data,  # Use provided data or the constructed request_data
        headers=headers,
        get_post=get_post,
        endpoint=endpoint,
        status_code=status_code,
        raw_response=raw_response,
        response_result=response_result,
        load_nested_json=load_nested_json,
        auth=auth
    )

def SolcatcherRequest(endpoint,get_post=None, *args, **kwargs):
    """
    Makes a POST request to a Typescript endpoint.
    """
    get_post = get_post or 'POST'
    url = getSolcatcherUrl()
    return makeSolcatcherRequest(url=url, endpoint=endpoint, get_post=get_post , *args, **kwargs)


def FlaskRequest(endpoint,get_post=None, *args, **kwargs):
    """
    Makes a POST request to a Typescript endpoint.
    """
    get_post = get_post or 'POST'
    url = getSolcatcherFlaskUrl()
    return makeSolcatcherRequest(url=url, endpoint=endpoint,get_post=get_post , *args, **kwargs)

def TypescriptRequest(endpoint,get_post=None, *args, **kwargs):
    """
    Makes a POST request to a Typescript endpoint.
    """
    get_post = get_post or 'POST'
    url = getSolcatcherTsUrl()
    return makeSolcatcherRequest(url=url, endpoint=endpoint,get_post=get_post , *args, **kwargs)

