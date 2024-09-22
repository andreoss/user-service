from sqlalchemy.orm import Mapped, MappedAsDataclass

from dataclasses import dataclass, field
from typing import Any, List, Dict
from advanced_alchemy.extensions.litestar import base, SQLAlchemyDTO, SQLAlchemyDTOConfig

class User(base.BigIntAuditBase, MappedAsDataclass):
    __tablename__ = "user"
    name: Mapped[str]
    surname: Mapped[str]
    password: Mapped[str]


class UserDTO(SQLAlchemyDTO[User]):
    config = SQLAlchemyDTOConfig(exclude={"password"})

class UserCreateDTO(SQLAlchemyDTO[User]):
    config = SQLAlchemyDTOConfig(exclude={"id", "created_at"})

@dataclass
class UserEvent:
    event: str
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, event: str, *args: Any, **kwargs: Any):
        self.event = event
        self.args = list(args)
        self.kwargs = kwargs
