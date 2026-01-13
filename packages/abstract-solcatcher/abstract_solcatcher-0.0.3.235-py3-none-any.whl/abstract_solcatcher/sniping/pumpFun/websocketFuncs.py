import logging
logging.basicConfig(level=logging.INFO)  # Change to INFO or higher to suppress DEBUG logs
logger = logging.getLogger(__name__)
from .utils import get_socket_url,get_websocket_params
from .programData import break_logs,get_log_value_from_key
from .db_credentials import RABBIT_CONFIG
import pika,logging,threading,websockets,asyncio
from ...database_calls import TypescriptRequest
from .dbFuncs import insert_transaction_log,create_solana_logs_table,create_solana_logs_table,process_owners
INSTRUCTION_PREFIX = "Program log: Instruction: "
TARGET_KEYS = {"InitializeAccount3", "InitializeMint2", "Create"}
def process_websocket_message(lognotification):
    """
    Process an individual WebSocket message, updating or creating account rows
    based on shared wallet signatures and parsed data.
    """
    # Step 1: Parse the log notification for signature and other relevant data
    all_js = break_logs(lognotification)
    all_js["signature"]=get_log_value_from_key(lognotification,'signature')
    all_js["lognotification"]=lognotification
    all_js['metadata'] = TypescriptRequest(endpoint='getMetaData', mintAddress=all_js.get('mint'))
    insert_transaction_log(all_js)
    process_owners(all_js.get('user_address'), all_js["signature"], all_js.get('mint'))

def process_log(message):
    logs = get_log_value_from_key(message, 'logs')
    # Check for the presence of all target keys
    if logs and all(key in (log[len(INSTRUCTION_PREFIX):].split(' ')[0]
                            for log in logs if log.startswith(INSTRUCTION_PREFIX)) for key in TARGET_KEYS):
        process_websocket_message(message)
def consume_rabbitmq():
    try:
        connection_params = pika.ConnectionParameters(
            host=RABBIT_CONFIG.get('host'),
            credentials=pika.PlainCredentials(RABBIT_CONFIG.get('user'), RABBIT_CONFIG.get('password'))
        )
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        channel.queue_declare(queue=RABBIT_CONFIG.get('queue'), durable=True)

        logger.info(f"Connected to RabbitMQ. Listening on queue: {RABBIT_CONFIG.get('queue')}")

        def callback(ch, method, properties, body):
            logger.info(f"Received RabbitMQ message: {body.decode()}")
            try:
                message_data = json.loads(body)
                logger.info(f"Parsed RabbitMQ message: {message_data}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse RabbitMQ message: {e}")

            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        channel.basic_consume(queue=RABBIT_CONFIG.get('queue'), on_message_callback=callback)
        channel.start_consuming()

    except Exception as e:
        logger.error(f"Error in RabbitMQ consumer: {e}")
# WebSocket listener function
async def connect_to_websocket():
    """
    Connect to the WebSocket and process incoming messages.
    """
    while True:
        try:
            async with websockets.connect(get_socket_url()) as websocket:
                await websocket.send(get_websocket_params(commitment="processed"))
                response = await websocket.recv()
                logger.info(f"Subscribed to logs: {response}")

                # Process incoming messages
                async for message in websocket:
                    if get_log_value_from_key(message, 'err') is None:
                        process_log(message)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await asyncio.sleep(5)  # Reconnect delay
def run_solcatcher():
    rabbitmq_thread = threading.Thread(target=consume_rabbitmq, daemon=True)
    rabbitmq_thread.start()
    create_solana_logs_table()
    asyncio.run(connect_to_websocket())
run_solcatcher()
