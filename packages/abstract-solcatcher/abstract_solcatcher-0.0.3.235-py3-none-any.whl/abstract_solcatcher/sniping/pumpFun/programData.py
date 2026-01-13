import struct,base58,base64
from construct import Struct, Bytes
from .logManager import get_log_value_from_key
def decode_program_data(program_data,all_js={}):
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
def decode_metaDatas(encoded_data):
    metadata_struct = Struct(
        "name" / Bytes(32),
        "symbol" / Bytes(14),
        "uri" / Bytes(72),
    )
    # Decode the Base64 data
    decoded_data = base64.b64decode(encoded_data)
    # Parse the data
    parsed_metadata = metadata_struct.parse(decoded_data)
    # Convert bytes to strings where appropriate
    name = parsed_metadata.name.strip()[16:]
    symbol = parsed_metadata.symbol.strip()[3:]
    uri = parsed_metadata.uri.strip()[4:]
    return {"name":str(name.decode('utf-8')),"symbol":symbol.decode('utf-8'),"uri":uri.decode('utf-8')}
def decode_metaData(encoded_data):
    keys = ["padding","name","symbol","uri"]
    # Decode the Base64 data
    decoded_data = base64.b64decode(encoded_data)
    metaJs={}
    count = 0
    last_zero=0
    value=None

    for i,each in enumerate(decoded_data):
        if each == 0:
            if value != None:
                count+=1
            last_zero = i+1
            value = None
        else:
            try:
                value = decoded_data[last_zero:i-1].decode('utf-8')
                metaJs[keys[count]]=value
            except:
                pass
        #print(metadata_struct.parse(decoded_data[last_zero:]).name.strip())
    return metaJs
def get_program_data(log=None,logs=None,logNotifications=None):
    logs = [str(log).split('Program data: ')[-1] for log in make_list(log or logs or get_log_value_from_key(lognotification, 'logs')) if 'Program data: ' in str(log)]
    return logs
def break_logs(logNotifications=None,logs=None,log=None):
    program_datas = get_program_data(log=log,logs=logs,logNotifications=logNotifications)
    for i,program_data in enumerate(program_datas):
        if i == 0:
            parsed_data = decode_program_data(str(edata),{}) or {}
        else:
            parsed_data.update(decode_metaData(str(edata)) or {})
    return parsed_data  
