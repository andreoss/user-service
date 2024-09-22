from faststream import FastStream
from faststream.rabbit import RabbitBroker
from structlog import get_logger

logger = get_logger()
broker = RabbitBroker("amqp://guest:guest@localhost:5672/")

app = FastStream(broker)

@broker.subscriber("created", exchange='user-events')
@broker.subscriber("updated", exchange='user-events')
@broker.subscriber("deleted", exchange='user-events')
async def handle_msg(msg: dict):
    logger.info(msg)
