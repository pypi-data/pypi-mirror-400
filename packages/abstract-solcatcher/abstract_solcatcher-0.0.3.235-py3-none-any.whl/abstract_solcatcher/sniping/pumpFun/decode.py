import struct,base58,base64,time,json
from abstract_utilities import safe_json_loads,get_any_value,SingletonMeta,make_list
def parse_data(program_data,all_js={}):
    # Step 1: Base64 decode the input program data
    decoded_data = base64.b64decode(program_data)
    
    offset = 8  # Adjusted offset to skip the first 8 bytes
    parsed = all_js
    
    try:
        # 32-byte publicKey (mint)
        mint = decoded_data[offset:offset + 32]
        parsed['mint'] = base58.b58encode(mint).decode('utf-8')
        offset += 32
        
        # 8-byte u64 (solAmount)
        parsed['solAmount'], = struct.unpack_from('<Q', decoded_data, offset)
        offset += 8
        
        # 8-byte u64 (tokenAmount)
        parsed['tokenAmount'], = struct.unpack_from('<Q', decoded_data, offset)
        offset += 8
        
        # 1-byte bool (isBuy)
        parsed['isBuy'], = struct.unpack_from('<?', decoded_data, offset)
        offset += 1
        
        # 32-byte publicKey (user)
        user = decoded_data[offset:offset + 32]
        parsed['user_address'] = base58.b58encode(user).decode('utf-8')
        offset += 32
        
        # 8-byte i64 (timestamp)
        parsed['timestamp'], = struct.unpack_from('<q', decoded_data, offset)
        offset += 8
        
        # 8-byte u64 (virtualSolReserves)
        parsed['virtualSolReserves'], = struct.unpack_from('<Q', decoded_data, offset)
        offset += 8
        
        # 8-byte u64 (virtualTokenReserves)
        parsed['virtualTokenReserves'], = struct.unpack_from('<Q', decoded_data, offset)
        
    except struct.error as e:
        print(f"Struct error: {e}")
        return None
    return parsed
def get_program_data(response, all_js={}):
    """
    Extract and parse program data from logs.
    """
    try:
        logs = get_logs(response)
        for log in logs:
            if log.startswith('Program data: '):
                base64_data = log[len('Program data: '):]
                all_js = parse_data(base64_data, all_js)
    except Exception as e:
        logger.error(f"Error parsing program data: {e}")
    return all_js
def get_program_data(response,all_js={}):
    logs = get_logs(response)
    for log in logs:
        if log.startswith('Program data: '):
            base64_data = log[len('Program data: '):]
            all_js = parse_data(base64_data,all_js)
    return all_js
def get_pumpfun_proghram_wallet():
    return "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
def get_wallet(wallet_type=None):
    wallet_types = {"pumpFun":get_pumpfun_proghram_wallet()}
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
    method = 'getSignaturesForAddress'
    url = call_rate_limit(method=method)
    body = get_body('get_signatures_for_address', creator_wallet, limit=1000)
    signatures = postRpcRequest(url=url, **body)
    call_log_response(method=method, response=signatures)
    return signatures
def test_it():
    
    logd = {'jsonrpc': '2.0', 'method': 'logsNotification', 'params': {'result': {'context': {'slot': 302009204}, 'value': {'signature': 'poSi4pY6MTmK79W4FyqSUtpGSfgoPzu77mwVYkbktqp4wyq4qtLw8qpHjCAnUUb8Q9i8nJGTEYyJxUp2hwMiJtu', 'err': 'sdffsdf', 'logs': ['Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program ComputeBudget111111111111111111111111111111 invoke [1]', 'Program ComputeBudget111111111111111111111111111111 success', 'Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW invoke [1]', 'Program log: Instruction: PumpSell', 'Program 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P invoke [2]', 'Program log: Instruction: Sell', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [3]', 'Program log: Instruction: Transfer', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 4645 of 107609 compute units', 'Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success', 'Program 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P invoke [3]', 'Program 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P consumed 2003 of 99479 compute units', 'Program 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P success', 'Program data: vdt/007mYe7oh9/peHrXFNq4S++LHVOYSLzIMMrBsxC18cwELmrCxnbY0H4AAAAAQLJ375tAAAAAqudgL7+RixOJeYKxNmsEFpIy7yATPAuxu60l99nvOzpBWzpnAAAAAD6IZfwGAAAAusCYV7/PAwA+3EEAAAAAALoohgsu0QIA', 'Program 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P consumed 36417 of 132167 compute units', 'Program 6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P success', 'Program 11111111111111111111111111111111 invoke [2]', 'Program 11111111111111111111111111111111 success', 'Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW consumed 57186 of 149700 compute units', 'Program BSfD6SHZigAfDWSjzD5Q41jw8LmKwtmjskPH9XW1mrRW success', 'Program 11111111111111111111111111111111 invoke [1]', 'Program 11111111111111111111111111111111 success']}}, 'subscription': 55791892}}
    start = time.time()
    error = get_log.get_err(log=logd)
    long = time.time() - start
    input(f"{long} seconds seconds to get {error}")
    start = time.time()
    error = get_any_value(logd,'err')
    long = time.time() - start
    input(f"{long} seconds seconds to get {error}")
    log = logd
    start = time.time()
    for each in ['params','result','value','err']:
        log = log.get(each)
    new = time.time() - start
    input(f"{new} seconds to get {log}")
    log = logd
    start = time.time()
    log = log.get('params').get('result').get('value').get('err')
    new = time.time() - start
    input(f"{new} seconds to get {log}")
    print(f"long was {(long/new)*100}% slower")
    input(log)
