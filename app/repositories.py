from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from .schemas import User

class UserRepository(SQLAlchemyAsyncRepository[User]):
    model_type = User
