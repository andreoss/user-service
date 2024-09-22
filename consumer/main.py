from faststream import FastStream
from faststream.rabbit import RabbitBroker
from structlog import get_logger

logger = get_logger()
broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = FastStream(broker)

@broker.subscriber("create", exchange='user-events')
@broker.subscriber("update", exchange='user-events')
@broker.subscriber("delete", exchange='user-events')
async def handle_msg(msg: dict):
    logger.info(msg)
