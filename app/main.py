import os

from litestar import Litestar
from litestar.plugins.structlog import StructlogPlugin

from .controllers import UserController
from .schemas import User
from .middleware import TraceIdMiddleware, MeasureExecutionTimeMiddleware
from advanced_alchemy.extensions.litestar import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)

import structlog
structlog.configure(
    processors=[
        structlog.threadlocal.merge_threadlocal,
        structlog.contextvars.merge_contextvars,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://svc:svc@localhost:5432/svc")

app = Litestar(
    route_handlers=[UserController],
    middleware=[MeasureExecutionTimeMiddleware, TraceIdMiddleware],
    plugins=[
        StructlogPlugin(),
        SQLAlchemyPlugin(
            SQLAlchemyAsyncConfig(
                metadata=User.metadata,
                connection_string=DATABASE_URL,
                session_config=AsyncSessionConfig(),
                create_all=True,
                before_send_handler="autocommit",
            )
        )
    ]
)
