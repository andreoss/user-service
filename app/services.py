from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from advanced_alchemy.extensions.litestar import providers

from .repositories import UserRepository
from .mq       import emit_on, emit_to, emit_format
from .rabbitmq import RabbitMQAsyncEventEmitter
from .schemas  import UserEvent

class UserService(SQLAlchemyAsyncRepositoryService[UserRepository]):
    repository_type = UserRepository

@emit_to('user-events')
@emit_on('create', 'update', 'delete')
@emit_format(UserEvent)
class EventfulUserService(UserService, RabbitMQAsyncEventEmitter):
    pass

UserServiceProvider = providers.create_service_dependencies(
    EventfulUserService, "service", load=[], filters={}
)
