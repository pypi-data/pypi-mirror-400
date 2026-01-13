from typing import Optional, Generator, Any
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from .settings import settings, Settings

# 全局 engine 实例
_engine: Optional[Engine] = None


def init_database(
    database_url: Optional[str] = None,
    settings_instance: Optional[Settings] = None,
    **engine_kwargs: Any
) -> Engine:
    """
    初始化数据库引擎

    支持三种配置方式（按优先级从高到低）：
    1. 直接传入 database_url
    2. 传入自定义的 Settings 实例
    3. 使用默认的 settings（从环境变量或 .env 加载）

    Args:
        database_url: 数据库连接 URL，例如 "postgresql://user:pass@localhost:5432/db"
        settings_instance: 自定义的 Settings 实例
        **engine_kwargs: 传递给 create_engine 的额外参数，例如 echo=True, pool_size=10

    Returns:
        Engine: SQLModel 引擎实例

    Example:
        ```python
        # 方式 1: 使用自定义 Settings
        from fastapi_toolbox import Settings, init_database

        class MySettings(Settings):
            DATABASE_URL: str = "postgresql://user:pass@prod:5432/prod_db"

        my_settings = MySettings()
        init_database(settings_instance=my_settings)

        # 方式 2: 直接传入 URL
        init_database(
            database_url="postgresql://user:pass@localhost:5432/mydb",
            echo=True,
            pool_size=10
        )

        # 方式 3: 使用默认配置（从 .env 读取）
        init_database()
        ```
    """
    global _engine

    # 优先级: database_url > settings_instance > 默认 settings
    if database_url:
        url = database_url
    elif settings_instance:
        url = settings_instance.DATABASE_URL
    else:
        url = settings.DATABASE_URL

    _engine = create_engine(url, **engine_kwargs)
    return _engine


def get_engine() -> Engine:
    """
    获取数据库引擎

    如果引擎未初始化，会使用默认配置自动初始化

    Returns:
        Engine: SQLModel 引擎实例
    """
    if _engine is None:
        init_database()
    return _engine


def get_session() -> Generator[Session, None, None]:
    """
    获取数据库会话（用于 FastAPI 依赖注入）

    Yields:
        Session: SQLModel 会话对象

    Example:
        ```python
        from fastapi import FastAPI, Depends
        from fastapi_toolbox import get_session, init_database
        from sqlmodel import Session

        app = FastAPI()

        # 应用启动时初始化数据库
        @app.on_event("startup")
        def on_startup():
            init_database()

        @app.get("/users")
        def get_users(session: Session = Depends(get_session)):
            # 使用 session 查询数据库
            return session.exec(select(User)).all()
        ```
    """
    with Session(get_engine()) as session:
        yield session


def create_db_and_tables():
    """
    创建所有数据库表

    会根据所有继承 SQLModel 的模型创建对应的表

    Example:
        ```python
        from fastapi_toolbox import init_database, create_db_and_tables
        from sqlmodel import SQLModel, Field

        class User(SQLModel, table=True):
            id: int = Field(primary_key=True)
            name: str

        # 初始化数据库并创建表
        init_database()
        create_db_and_tables()
        ```
    """
    SQLModel.metadata.create_all(get_engine())
