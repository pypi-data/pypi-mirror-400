from utilities import getEndpointUrl,try_json_dumps,getSolcatcherTsUrl,getSolcatcherFlaskUrl,getSolcatcherUrl,get_method,get_url
from abstract_utilities import eatAll,make_list
from abstract_apis import make_request,get_headers,postRequest
import requests
def getEndpointUrl(endpoint=None,url=None):
  url = url or getSolcatcherFlaskUrl()
  url = eatAll(url,['/'])
  endpoint = eatAll(endpoint,['/'])
  return f"{url}/{endpoint}"
def get_datas(data=None,*args,**kwargs):
  data = data or kwargs
  if not isinstance(data,dict):
    data={"args":args}
  data = try_json_dumps(data)
  return data
def makeSolcatcherRequest(url,endpoint,get_post='POST',*args,**kwargs):
  return make_request(url=url,endpoint=endpoint,get_post=get_post,*args,**kwargs)
def postSolcatcherRequest(url,endpoint,*args,**kwargs):
  url=getSolcatcherUrl()
  return makeSolcatcherRequest(url=url,endpoint=endpoint,get_post='POST',*args,**kwargs)
def getSolcatcherRequest(endpoint,*args,**kwargs):
  url=getSolcatcherUrl()
  return makeSolcatcherRequest(url=url,endpoint=endpoint,get_post='GET',*args,**kwargs)
def postFlaskRequest(endpoint,*args,**kwargs):
  url=getSolcatcherFlaskUrl()
  return postSolcatcherRequest(url=url,endpoint=endpoint,get_post='POST',*args,**kwargs)
def getFlaskRequest(endpoint,*args,**kwargs):
  url=getSolcatcherFlaskUrl()
  return getSolcatcherRequest(url=url,endpoint=endpoint,get_post='GET',*args,**kwargs)
def postTypescriptRequest(endpoint,get_post='POST',*args,**kwargs):
  url=getSolcatcherFlaskUrl()
  return postSolcatcherRequest(url=url,endpoint=endpoint,*args,**kwargs)
def getTypescriptRequest(endpoint,get_post='GET',*args,**kwargs):
  url=getSolcatcherFlaskUrl()
  return getSolcatcherRequest(url=url,endpoint=endpoint,*args,**kwargs)

response = postFlaskRequest(endpoint='rate_limit',data={"method":get_method()},response_result='url')
input(response)
response = getFlaskRequest(endpoint='log_response',data={"method":get_method(),'response_data':response})
input(response)
