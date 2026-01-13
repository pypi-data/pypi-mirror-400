from .utils import getEndpointUrl,get_async_response
from abstract_apis import getRequest,requests,asyncPostRpcRequest,asyncPostRequest,asyncGetRequest,get_headers
from abstract_utilities import make_list
import json
async def dbinsert(tableName=None,searchValue=None,insertValues=None,dbName=None,dbType=None,**kwargs):
    response = await asyncPostRequest(url=getEndpointUrl("dbInsert"), data={"tableName":tableName, "searchValue":searchValue,"insertValues":insertValues,"dbName":dbName,"dbType":dbType}, **kwargs)
    return response
def dbInsert(tableName=None,searchValue=None,insertValues=None,dbName=None,dbType=None,**kwargs):
    return get_async_response(dbinsert,tableName=tableName,searchValue=searchValue,insertValues=insertValues,dbName=dbName,dbType=dbType,**kwargs)

async def dbsearch(tableName=None,searchValue=None,dbName=None,dbType=None,**kwargs):
    response = await asyncPostRequest(url=getEndpointUrl("dbSearch"), data={"tableName":tableName, "searchValue":searchValue,"dbName":dbName,"dbType":dbType},**kwargs)
    return response

def dbSearch(tableName=None,searchValue=None,dbName=None,dbType=None,**kwargs):
    return get_async_response(dbsearch, tableName=tableName,searchValue=searchValue,dbName=dbName,dbType=dbType,**kwargs)

async def asyncMakeLimitedDbCall(*args,tableName=None,searchValue=None,function=None,dbName=None,dbType=None,**kwargs):
    tableName=tableName or method
    response = await dbsearch(tableName=tableName,searchValue=searchValue,dbName=dbName,dbType=dbType,status_code=True)
    if response and response[1] == 200 and response[0]:
      print(f'search of {method} in table {tableName} successful ')
      return response
    if function:
        insertValue = await function(*args,**kwargs)
    else:
        insertValue = await asyncMakeLimitedCall(**kwargs)
    
    response = await dbinsert(tableName=tableName,searchValue=searchValue,insertValue=insertValue,dbName=dbName,dbType=dbType,status_code=True)
    return response
def makeLimitedDbCall(*args,tableName=None,searchValue=None,function=None,dbName=None,dbType=None,**kwargs):
    return get_async_response(asyncMakeLimitedDbCall, *args,tableName=tableName,searchValue=searchValue,function=function,dbName=dbName,dbType=dbType,**kwargs)


async def makeDbCall(*args,method=None,tableName=None,searchValue=None,insertValue=None,function=None,**kwargs):
    response = await dbsearch(tableName,searchValue)
    if response:
        return response
    insertValue = await function(*args,**kwargs)
    await dbinsert(tableName,searchValue,insertValue)
    return insertValue

async def asyncMakeLimitedCall(method=None, params=[],**kwargs):
    urls = await async_get_rate_limit_url(method)
    response = await asyncPostRpcRequest(
        url=urls.get('url'), method=method, params=params, status_code=True, response_result='result'
    )
    
    if response[1] == 429:
        response = await asyncPostRpcRequest(
            url=urls.get('url2'), method=method, params=params, response_result='result', status_code=True
        )
    response = response[0]
    await async_log_response(method,response)
    return response
def makeLimitedCall(method=None, params=[]):
    return get_async_response(asyncMakeLimitedCall, method, params)

async def async_get_rate_limit_url(method='default_method'):
    return await asyncGetRequest(url=getEndpointUrl("rate_limit"),data={"method":str(method)})

def get_rate_limit_url(method_name, *args, **kwargs):
    return get_async_response(async_get_rate_limit_url, method_name, *args, **kwargs)

async def async_log_response(method='default_method', response_data={}):
    return await asyncPostRequest(url=getEndpointUrl("log_response"),data={"method":str(method),"response_data":response_data})

def log_response(method_name, response_data, *args, **kwargs):
    return get_async_response(async_log_response, method_name, response_data, *args, **kwargs)
