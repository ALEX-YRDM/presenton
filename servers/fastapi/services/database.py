from collections.abc import AsyncGenerator
import os
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlmodel import SQLModel

from models.sql.async_presentation_generation_status import (
    AsyncPresentationGenerationTaskModel,
)
from models.sql.image_asset import ImageAsset
from models.sql.key_value import KeyValueSqlModel
from models.sql.ollama_pull_status import OllamaPullStatus
from models.sql.presentation import PresentationModel
from models.sql.slide import SlideModel
from models.sql.presentation_layout_code import PresentationLayoutCodeModel
from models.sql.template import TemplateModel
from models.sql.webhook_subscription import WebhookSubscription
from models.sql.ppt_create_sessions import PptCreateSessionModel
from models.sql.ppt_create_reference_files import PptCreateReferenceFilesModel
from models.sql.ppt_template import PptTemplateModel
from utils.db_utils import get_database_url_and_connect_args

# 该文件管理数据库的连接和会话

# 获取数据库URL和连接参数
database_url, connect_args = get_database_url_and_connect_args()

# 创建异步引擎
sql_engine: AsyncEngine = create_async_engine(database_url, connect_args=connect_args)

# 创建异步会话生成器
async_session_maker = async_sessionmaker(sql_engine, expire_on_commit=False)

# 获取异步会话
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# Container DB (Lives inside the container)
container_db_url = "sqlite+aiosqlite:////app/container.db"
container_db_engine: AsyncEngine = create_async_engine(
    container_db_url, connect_args={"check_same_thread": False}
)
container_db_async_session_maker = async_sessionmaker(
    container_db_engine, expire_on_commit=False
)


async def get_container_db_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with container_db_async_session_maker() as session:
        yield session


# Create Database and Tables
async def create_db_and_tables():
    async with sql_engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: SQLModel.metadata.create_all(
                sync_conn,
                tables=[
                    PresentationModel.__table__,
                    SlideModel.__table__,
                    KeyValueSqlModel.__table__,
                    ImageAsset.__table__,
                    PresentationLayoutCodeModel.__table__,
                    TemplateModel.__table__,
                    WebhookSubscription.__table__,
                    AsyncPresentationGenerationTaskModel.__table__,
                    PptCreateSessionModel.__table__,
                    PptCreateReferenceFilesModel.__table__,
                    PptTemplateModel.__table__,
                ],
            )
        )

    # async with container_db_engine.begin() as conn:
    #     await conn.run_sync(
    #         lambda sync_conn: SQLModel.metadata.create_all(
    #             sync_conn,
    #             tables=[OllamaPullStatus.__table__],
    #         )
    #     )
