import logging
logging.basicConfig(level=logging.INFO)  # Change to INFO or higher to suppress DEBUG logs
logger = logging.getLogger(__name__)
import psycopg2
from psycopg2.extras import Json
from datetime import datetime, timezone
from .utils import get_signatures
from .db_credentials import DB_CONFIG

def insert_transaction_log(all_js):
    """
    Inserts transaction log data into the solana_logs table.
    
    Parameters:
    - all_js (dict): A dictionary containing the transaction data.
    """
    # Database connection parameters (replace with your actual credentials)


    # Map the all_js dictionary keys to the table columns
    data = {
        'padding': all_js.get('padding'),
        'name': all_js.get('name'),
        'symbol': all_js.get('symbol'),
        'uri': all_js.get('uri'),
        'mint': all_js.get('mint'),
        'solAmount': all_js.get('solAmount'),
        'tokenAmount': all_js.get('tokenAmount'),
        'isBuy': all_js.get('isBuy'),
        'user_address': all_js.get('user'),
        'timestamp': all_js.get('timestamp'),
        'virtualSolReserves': all_js.get('virtualSolReserves'),
        'virtualTokenReserves': all_js.get('virtualTokenReserves'),
        'signature': all_js.get('signature'),
        'lognotification': all_js.get('lognotification'),
        'metadata': all_js.get('metadata')
    }

    # Ensure proper data types
    data_types = {
        'solAmount': int,
        'tokenAmount': int,
        'isBuy': bool,
        'timestamp': int,
        'virtualSolReserves': int,
        'virtualTokenReserves': int,
        'lognotification': psycopg2.extras.Json,
        'metadata': psycopg2.extras.Json
    }

    for key, cast_type in data_types.items():
        if data.get(key) is not None:
            if cast_type == psycopg2.extras.Json:
                data[key] = psycopg2.extras.Json(data[key])
            else:
                data[key] = cast_type(data[key])

    # Prepare the INSERT statement
    insert_query = """
    INSERT INTO solana_logs (
        padding,
        name,
        symbol,
        uri,
        mint,
        solAmount,
        tokenAmount,
        isBuy,
        user_address,
        timestamp,
        virtualSolReserves,
        virtualTokenReserves,
        signature,
        lognotification,
        metadata
    ) VALUES (
        %(padding)s,
        %(name)s,
        %(symbol)s,
        %(uri)s,
        %(mint)s,
        %(solAmount)s,
        %(tokenAmount)s,
        %(isBuy)s,
        %(user_address)s,
        %(timestamp)s,
        %(virtualSolReserves)s,
        %(virtualTokenReserves)s,
        %(signature)s,
        %(lognotification)s,
        %(metadata)s
    )
    """

    try:
        # Establish the database connection
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Execute the INSERT statement
        cur.execute(insert_query, data)
        conn.commit()
        print("Transaction log inserted successfully.")

    except Exception as e:
        # Handle any errors and rollback the transaction
        conn.rollback()
        print(f"Error inserting transaction log: {e}")

    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()

def fetch_transaction_logs(limit=10, offset=0, filters=None):
    """
    Fetches transaction logs from the database with optional filters and offset.
    
    :param limit: The maximum number of rows to fetch.
    :param offset: The starting point for fetching rows.
    :param filters: A dictionary of column-value pairs to filter the logs.
    :return: A list of dictionaries containing the transaction log details.
    """
    query = """
    SELECT signature, mint, sol_amount, token_amount, is_buy, user_address, 
           timestamp, virtual_sol_reserves, virtual_token_reserves, metadata, 
           logNotification, signatures, transaction
    FROM transaction_logs
    """
    
    where_clause = []
    params = []

    # Add filters dynamically
    if filters:
        for column, value in filters.items():
            where_clause.append(f"{column} = %s")
            params.append(value)

    # Add WHERE clause if filters exist
    if where_clause:
        query += " WHERE " + " AND ".join(where_clause)
    
    # Add ORDER BY, LIMIT, and OFFSET
    query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s;"
    params.extend([limit, offset])

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, tuple(params))
                results = cur.fetchall()
                colnames = [desc[0] for desc in cur.description]
                return [dict(zip(colnames, row)) for row in results]
    except Exception as e:
        print(f"Error fetching transaction logs: {e}")
        return []
def insert_into_table(query,data=None):

    try:
        # Establish the database connection
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                if data is not None:
                    cur.execute(query, data)
                else:
                    cur.execute(query)
                logger.info("owneraccounts table created or already exists.")
        
        
        print("Transaction log inserted successfully.")

    except Exception as e:
        # Handle any errors and rollback the transaction
   
        print(f"Error inserting transaction log: {e}")

  
        

def handle_wallet_signatures(wallet_address, txnsignature, mint_address,batch_signatures):
    """
    Compare generated signatures with existing rows in owneraccounts and return matched row data or None.

    Args:
        wallet_address (str): The wallet address to generate signatures from.
        txnsignature (str): The transaction signature to associate with the wallet.
        mint_address (str): The mint address to associate with the wallet.

    Returns:
        dict or None: Shared row data if signatures overlap; otherwise, None.
    """

    query = """
    SELECT id, user_addresses, signatures, mints, transactions
    FROM owneraccounts
    WHERE signatures && %s::text[];
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (batch_signatures,))
                rows = cur.fetchall()

                if rows:
                    # Combine all unique signatures from matched rows
                    existing_signatures = set()
                    for row in rows:
                        row_signatures = row.get('signatures', [])
                        existing_signatures.update(row_signatures)
                    
                    combined_signatures = list(existing_signatures.union(set(batch_signatures)))
                    return {
                        "row_id": rows[0]['id'],
                        "user_addresses": rows[0]['user_addresses'],
                        "signatures": combined_signatures,
                        "mints": rows[0]['mints'],
                        "transactions": rows[0]['transactions'],
                    }
    except Exception as e:
        logger.error(f"Error comparing wallet signatures: {e}")
        return None

def update_existing_owneraccounts(existing_data, new_data):
    """
    Update an existing owneraccount row with new data.

    Args:
        existing_data (dict): Data of the matched row from the database.
        new_data (dict): New data to append to the row.
    """
    query = """
    UPDATE owneraccounts
    SET 
        user_addresses = ARRAY(
            SELECT DISTINCT unnest(user_addresses || %s::text[])
        ),
        signatures = ARRAY(
            SELECT DISTINCT unnest(signatures || %s::text[])
        ),
        mints = ARRAY(
            SELECT DISTINCT unnest(mints || %s::text[])
        ),
        transactions = ARRAY(
            SELECT DISTINCT unnest(transactions || %s::text[])
        ),
        timestamp = NOW()
    WHERE id = %s
    RETURNING mints, user_addresses, transactions;
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Prepare data for update
                new_user_address = new_data.get("user_address")
                new_signatures = new_data.get("signatures", [])
                new_mints = [new_data.get("mint")] if new_data.get("mint") else []
                new_transactions = [new_data.get("transaction")] if new_data.get("transaction") else []

                # Ensure all fields are lists
                if not isinstance(new_user_address, list):
                    new_user_address = [new_user_address] if new_user_address else []
                if not isinstance(new_signatures, list):
                    new_signatures = [new_signatures]
                if not isinstance(new_mints, list):
                    new_mints = [new_mints]
                if not isinstance(new_transactions, list):
                    new_transactions = [new_transactions]

                cur.execute(query, (
                    new_user_address,    # Now a list
                    new_signatures,      # Already a list
                    new_mints,           # Already a list
                    new_transactions,    # Already a list
                    existing_data["row_id"],
                ))
                updated_row = cur.fetchone()
                conn.commit()

                if updated_row:
                    mints, user_addresses, transactions = updated_row
                    logger.info(f"Updated owneraccount ID {existing_data['row_id']}.")
                    logger.info(f"Mints: {mints}")
                    logger.info(f"User Addresses: {user_addresses}")
                    logger.info(f"Transactions: {transactions}")

    except Exception as e:
        logger.error(f"Error updating owneraccount: {e}")


def insert_owneraccount(data):
    """saction log: relation "solana_logs" already exists

    Insert a new owneraccount into the database.

    Args:
        data (dict): Transaction data to insert.
    """
    query = """
    INSERT INTO owneraccounts (
        signatures, mints, user_addresses, transactions
    )
    VALUES (
        %s::text[], %s::text[], %s::text[], 
        %s::text[]
    )
    RETURNING id;
    """
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Prepare data for insertion
                signatures = data.get("signatures", [])
                mints = [data.get("mint")] if data.get("mint") else []
                user_addresses = [data.get("user_address")] if data.get("user_address") else []
                transactions = [data.get("transaction")] if data.get("transaction") else []

                # Ensure all fields are lists of strings
                if not isinstance(signatures, list):
                    signatures = [signatures]
                if not isinstance(mints, list):
                    mints = [mints]
                if not isinstance(user_addresses, list):
                    user_addresses = [user_addresses]
                if not isinstance(transactions, list):
                    transactions = [transactions]

                cur.execute(query, (
                    signatures,
                    mints,
                    user_addresses,
                    transactions,
                ))
                new_id = cur.fetchone()[0]
                conn.commit()
                logger.info(f"Inserted new owneraccount with ID {new_id} successfully.")

    except Exception as e:
        logger.error(f"Error inserting owneraccount: {e}")




def process_owners(wallet_address, txnsignature, mint_address):
    """
    Process the provided wallet_address, txnsignature, and mint_address.
    Generates signatures, checks against owneraccounts, and updates or inserts accordingly.

    Args:
        wallet_address (str): The wallet address.
        txnsignature (str): The transaction signature.
        mint_address (str): The mint address.
    """
    
    # Step 1: Generate signatures from wallet_address
    signatures = get_signatures(wallet_address)
    if not signatures:
        raise ValueError("No signatures generated from the provided wallet address.")
    # Ensure signatures are a list of strings
    signatures = [sig.get('signature') for sig in signatures]
    if not signatures:
        raise ValueError("No valid signatures found after filtering.")

    # Step 2: Check for existing owneraccounts with overlapping signatures
    shared_data = handle_wallet_signatures(wallet_address, txnsignature, mint_address,signatures)
    if shared_data:
        # Matching signatures found; update the existing owneraccount
        new_data = {
            "user_address": wallet_address,
            "signatures": signatures,
            "mint": mint_address,
            "transaction": txnsignature,
        }
        update_existing_owneraccounts(shared_data, new_data)
    else:
        # No matching signatures; create a new owneraccount
        new_data = {
            "user_address": wallet_address,
            "signatures": signatures,
            "mint": mint_address,
            "transaction": txnsignature,
        }
        insert_owneraccount(new_data)
def create_solana_logs_table():
    query = """CREATE TABLE solana_logs (
        id SERIAL PRIMARY KEY,
        padding TEXT,
        name TEXT,
        symbol TEXT,
        uri TEXT,
        mint TEXT,
        solAmount BIGINT,
        tokenAmount BIGINT,
        isBuy BOOLEAN,
        user_address TEXT,
        timestamp BIGINT,
        virtualSolReserves BIGINT,
        virtualTokenReserves BIGINT,
        signature TEXT,
        lognotification JSON,
        metadata JSON
    );
    """
    create_table(query)
def create_solana_logs_table():
    query = """CREATE TABLE IF NOT EXISTS owneraccounts (
        id SERIAL PRIMARY KEY,
        signatures TEXT[],
        mints TEXT[],
        user_addresses TEXT[],
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        transactions TEXT[]
    );"""
    create_table(query)
def create_table(query):
    """
    Creates the owneraccounts table in the database.
    """
    
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                conn.commit()
                logger.info("table created or already exists.")
    except Exception as e:
        logger.error(f"Error creating owneraccounts table: {e}")
