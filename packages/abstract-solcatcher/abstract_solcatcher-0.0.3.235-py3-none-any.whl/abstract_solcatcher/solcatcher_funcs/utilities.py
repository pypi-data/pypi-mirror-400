def getSolcatcherUrl(callType=None):
  if callType == 'flask':
    return getSolcatcherFlaskUrl()
  if callType != None:
    return getSolcatcherTsUrl()
  return 'https://solcatcher.io'
def getSolcatcherFlaskUrl():
  return 'https://solcatcher.io/flask'
def getSolcatcherTsUrl():
  return 'https://solcatcher.io/typescript'

def getEndpointUrl(endpoint=None,url=None):
  
  if endpoint:
    url = eatAll(url,['/'])
    endpoint = eatAll(endpoint,['/'])
    url= f"{url}/{endpoint}"
  return url
def get_url(url=None):
    if isinstance(url,dict):
      url = url.get('url',url)
    return url
def getCallArgs(endpoint):
  return {'getMetaData': ['signature'], 'getPoolData': ['signature'], 'getTransactionData': ['signature'], 'getPoolInfo': ['signature'], 'getMarketInfo': ['signature'], 'getKeyInfo': ['signature'], 'getLpKeys': ['signature'], 'process': ['signature']}.get(get_endpoint(endpoint))
def try_json_dumps(data):
  if isinstance(data,dict):
    try:
      data = json.dumps(data)
    except:
      pass
    return data
def ifListGetSection(listObj,section=0):
  if isinstance(listObj,list):
      if len(listObj)>section:
          return listObj[section]
  return listObj
def updateData(data,**kwargs):
  data.update(kwargs)
  return data
def get_method(method=None):
  return method or 'default_method'
def get_resp(response=None):
  response = response or {}
  if isinstance(response,dict):
    response = {"response":response}
  return response
