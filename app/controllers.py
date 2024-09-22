from litestar import get, delete, post, put
from litestar.controller import Controller

from .services import UserService, UserServiceProvider
from .schemas import User, UserDTO, UserCreateDTO

class UserController(Controller):
    dependencies = UserServiceProvider

    @get("/", return_dto=UserDTO)
    async def get_users(self, service: UserService) -> list[User]:
        return await service.list()
    
    @post("/", dto=UserCreateDTO, return_dto=UserDTO)
    async def add_user(self, data: User, service: UserService) -> User:
        return await service.create(data)

    @get("/{id:int}", return_dto=UserDTO)
    async def get_user(self, id: int, service: UserService) -> User:
        return await service.get(id)
    
    @put("/{id:int}", dto=UserCreateDTO, return_dto=UserDTO)
    async def update_user(self, id: int, data: User, service: UserService) -> User:
        return await service.update(data, item_id = id)

    @delete("/{id:int}")
    async def delete_user(self, id: int, service: UserService) -> None:
        await service.delete(id)
