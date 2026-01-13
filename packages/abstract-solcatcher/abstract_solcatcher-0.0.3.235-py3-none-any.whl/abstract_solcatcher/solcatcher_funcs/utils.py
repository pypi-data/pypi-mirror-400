import asyncio,requests,json
from abstract_utilities import *
from abstract_solana import RateLimiter
from abstract_apis import make_request,get_url,make_endpoint,get_headers,get_async_response
def try_solcatcher_io(method = None):
  method = get_method(method=method)
  try:
    url,status_code = postFlaskRequest(url=getSolcatcherFlaskUrl(),endpoint='get_rate_limit',data=json.dumps({"method":method}),status_code=True)
    return url,status_code 
  except:
    pass
  return None,500
def try_log_response(method = None,response=None):
  method = get_method(method=method)
  response = get_resp(response=response)
  try:
    response = postFlaskRequest(url=getSolcatcherFlaskUrl(),endpoint='log_response',data=json.dumps({"method":method,"response":response}),status_code=True)
    return response 
  except:
    pass
class CheckSolcatcher(metaclass=SingletonMeta):
  def __init__(self):
    if not hasattr(self, 'initialized'):
      self.initialized = True
      self.solcatcher_on = True
      url,self.status_code = try_solcatcher_io()
      if self.status_code != 200 and get_url(url=url) == None:
        self.solcatcher_on=False
      self.rateLimiter = RateLimiter()
  def get_rate_url(self,method=None):
    if self.solcatcher_on:
      url,response_code = try_solcatcher_io(method = method)
    if self.solcatcher_on == False or self.status_code != 200:
       self.solcatcher_on = False
       method = get_method(method=method)
       url = self.rateLimiter.get_url(method=method)
    return get_url(url=url)
  def log_response(self,method=None,response=None):
    if self.solcatcher_on:
       try_log_response(method = method,response=response)
    if self.solcatcher_on == False:
      method = get_method(method=method)
      response = get_resp(response=response)
      self.rateLimiter.log_response(method=method,response=response)  
def rate_limit(method=None,response=None):
  if response is not None:
      CheckSolcatcher().log_response(method=method,response=response)
      return
  return CheckSolcatcher().get_rate_url(method=method)
