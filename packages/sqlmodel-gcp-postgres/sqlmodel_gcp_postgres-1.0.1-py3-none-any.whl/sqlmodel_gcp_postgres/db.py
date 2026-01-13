import inspect
import os
from functools import wraps
from typing import Any, Awaitable, Callable, Generator, Union
from sqlalchemy import Engine
from sqlmodel import Session, create_engine
from google.cloud.sql.connector import Connector, IPTypes

from loguru import logger


def _create_engine() -> Engine:
    """
    Create database engine based on configuration.

    Creates either a Cloud SQL PostgreSQL engine or a standard PostgreSQL engine
    depending on the USE_CLOUD_SQL environment variable.  In both scenarios, the
    pg8000 driver is utilized (Google Cloud SQL Connector currently supports pg8000
    and asyncpg).

    Cloud SQL Mode (USE_CLOUD_SQL=true):
        Requires environment variables:
        - CLOUD_SQL_INSTANCE_CONNECTION_NAME: Full instance connection name
        - DB_USER: Database username
        - DB_PASS: Database password
        - DB_NAME: Database name
        - CLOUD_SQL_PRIVATE_IP: Optional, use private IP if set

        Uses Google Cloud SQL Connector with lazy refresh strategy for
        Cloud Run compatibility and auto-scaling to zero.

    Standard Mode (USE_CLOUD_SQL=false or unset):
        Requires environment variable:
        - DB_URL: Complete database connection URL
    Returns:
        SQLAlchemy Engine: Configured database engine
    """
    use_cloud_sql = os.getenv("USE_CLOUD_SQL", "false").lower() == "true"

    if use_cloud_sql:
        # Cloud SQL configuration
        instance_connection_name = os.getenv("CLOUD_SQL_INSTANCE_CONNECTION_NAME")
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASS")
        db_name = os.getenv("DB_NAME")

        ip_type = (
            IPTypes.PRIVATE
            if os.environ.get("CLOUD_SQL_PRIVATE_IP")
            else IPTypes.PUBLIC
        )

        if not all([instance_connection_name, db_user, db_pass, db_name]):
            raise ValueError(
                "Missing required Cloud SQL environment variables: "
                "CLOUD_SQL_INSTANCE_CONNECTION_NAME, DB_USER, DB_PASS, DB_NAME"
            )

        # Initialize Cloud SQL connector using a lazy refresh strategy to
        # ensure that this service may be used in Cloud Run environments that may scale to zero
        connector = Connector(refresh_strategy="LAZY")

        def _get_connection():
            connection = connector.connect(
                instance_connection_name,
                "pg8000",
                user=db_user,
                password=db_pass,
                db=db_name,
                ip_type=ip_type,
            )
            return connection

        # Create engine with Cloud SQL connector
        return create_engine(
            "postgresql+pg8000://",
            creator=_get_connection,
        )
    else:
        # Use standard DB_URL for local deployment and automated testing
        db_url = os.getenv("DB_URL")
        if not db_url:
            logger.warning(
                "DB_URL environment variable is required for non Cloud SQL environments - no database engine will be created!"
            )
            return None
        else:
            return create_engine(db_url)


engine = _create_engine()


def get_session() -> Generator[Session, None, None]:
    """Get database session with proper cleanup."""
    with Session(engine) as session:
        yield session


def transactional(func: Callable) -> Union[Callable, Callable[..., Awaitable[Any]]]:
    """
    Decorator for managing database transactions.

    Automatically commits transactions if the function completes successfully
    and rolls back if an exception occurs. Supports both sync and async functions.

    IMPORTANT: When using this decorator on methods with other decorators (i.e. FastAPI
    path operation decorators like @router.post()), this decorator *MUST* be ordered
    closest to the method definition such that it executes BEFORE other decorators.

    Examples:
        ```python
        @router.post("/api/data")
        @transactional
        async def my_post_func(data_to_save: MyData, session: Session = Depends(get_session)):
           ...
        ```
    Args:
        func: The function to wrap with transaction management

    Returns:
        The wrapped function with transaction management
    """

    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            session = _find_session(*args, **kwargs)

            try:
                result = await func(*args, **kwargs)
                session.commit()
                return result
            except Exception as e:
                session.rollback()
                raise e

        return async_wrapper
    else:

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            session = _find_session(*args, **kwargs)

            try:
                result = func(*args, **kwargs)
                session.commit()
                return result
            except Exception as e:
                session.rollback()
                raise e

        return sync_wrapper


def _find_session(*args, **kwargs) -> Session:
    """Helper function to find session in function arguments."""
    if 'session' in kwargs:
        return kwargs['session']

    for arg in args:
        if isinstance(arg, Session):
            return arg

    raise ValueError("Session object not found in function arguments")
