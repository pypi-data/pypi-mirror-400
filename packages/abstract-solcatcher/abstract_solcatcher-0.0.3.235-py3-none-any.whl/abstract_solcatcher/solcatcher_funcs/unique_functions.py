from .api_calls import solcatcher_api_call,get_solcatcher_rpc_db_call
from abstract_solana import get_pubkey,Pubkey,return_oldest_last_and_original_length_from_signature_array,get_sigkey
def getGenesisSignature(address,before=None,limit=None,commitment=None):
    before = before or None
    genesisSignature = None
    limit = limit or 1000
    commitment = commitment or "confirmed"
    while True:
        signatureArray = solcatcher_api_call('getSignaturesForAddress',address=address,before=before,limit=limit,commitment=commitment)
        signatureArrayInfo = return_oldest_last_and_original_length_from_signature_array(signatureArray)
        genesisSignature = signatureArrayInfo.get("oldestValid") or genesisSignature
        if before == signatureArrayInfo.get("oldest") or signatureArrayInfo.get("length") < limit:
            return genesisSignature
        before = signatureArrayInfo.get("oldest")
    return genesisSignature

def getParsedTransaction(signature=None,
                                     txnData=None,
                                     programId=None,
                                     encoding= None,
                                     commitment = None,
                                     maxSupportedTransactionVersion = None):
    if not txnData and not signature:
        return
    if txnData and not signature:
        signature = get_sig_from_txn_data(txnData)
    if signature and not txnData:
        txnData = get_solcatcher_rpc_db_call('getTransaction',signature=signature,encoding=encoding,commitment=commitment,maxSupportedTransactionVersion=maxSupportedTransactionVersion)
    parsedTxnData = get_solcatcher_rpc_db_call('getParsedTransaction',txnData=safe_json_loads(txnData),programId=programId)
    return parsedTxnData
