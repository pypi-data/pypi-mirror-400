import struct,base58,base64,time,json
from abstract_utilities import safe_json_loads,get_any_value,SingletonMeta,make_list
from ...database_calls import abstract_solcatcher_rate_limited_call, TypescriptRequest,call_rate_limit,call_log_response,FlaskRequest,get_body
from abstract_apis import postRpcRequest
def get_pumpfun_program_wallet():
    return "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
def get_wallet(wallet_type=None):
    wallet_types = {"pumpFun":get_pumpfun_program_wallet()}
    wallet_type = wallet_type or "pumpFun"
    for walletType,wallet_address in wallet_types.items():
        if walletType.lower() == wallet_type.lower():
            return wallet_address
    return list(wallet_types.values())[0]
def get_socket_url():
    return "wss://api.mainnet-beta.solana.com/"
def get_websocket_params(jsonrpc=None,id=None,method=None,params=None,mentions=None,commitment=None,wallet_type=None,wallet_address=None):
    jsonrpc = str(float(jsonrpc or 2))
    id = int(id or 1)
    method = method or "logsSubscribe"
    wallet_type=wallet_type or "pumpFun"
    wallet_address = get_wallet(wallet_type)
    mentions = make_list(mentions or [wallet_address])
    commitment = commitment or "processed"
    params = make_list(params or [{"mentions": mentions},{"commitment": commitment}])
    return json.dumps({
        "jsonrpc": jsonrpc,
        "id": id,
        "method": method,
        "params": params})
def get_signatures(creator_wallet):
    signatures = abstract_solcatcher_rate_limited_call('get_signatures_for_address', creator_wallet, limit=1000)
    return signatures
def check_dict(obj):
    if obj and not isinstance(obj,dict):
        obj = safe_json_loads(obj)
    return obj
def get_log_value(log):
    log = check_dict(log)
    return log.get('params').get('result').get('value')
def get_log_value_from_key(log,key):
    return get_log_value(log).get(key)
