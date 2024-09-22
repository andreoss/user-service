from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from advanced_alchemy.extensions.litestar import providers

from .repositories import UserRepository

class UserService(SQLAlchemyAsyncRepositoryService[UserRepository]):
    repository_type = UserRepository

UserServiceProvider = providers.create_service_dependencies(
    UserService, "service", load=[], filters={}
)
