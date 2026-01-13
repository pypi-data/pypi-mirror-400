# -*- coding: utf-8 -*-
# @Author	: brotherbaby
# @Date		: 2025/8/22 9:51
# @Last Modified by:   brotherbaby
# @Last Modified time: 2025/8/22 9:51
# Thanks for your comments!

import asyncio
import logging
import traceback
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Tuple, Optional, AsyncGenerator, Union

from asyncpg.exceptions import UniqueViolationError
from sqlalchemy import text, select, and_, insert, func, update, delete, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncConnection
from sqlalchemy.orm import sessionmaker, InstrumentedAttribute

logger = logging.getLogger(__name__)


def row_to_dict(row, model, join_models):
    """将查询结果行转换为字典"""
    result = {}
    if not row:
        return result
    index = 0
    for col in model.__table__.columns:
        result[col.name] = row[index]
        index += 1
    for j_model in join_models:
        model_name = j_model.__name__
        result[model_name] = {}
        for col in j_model.__table__.columns:
            result[model_name][col.name] = row[index]
            index += 1
    return result


class AsyncPostgreSQLConnection:
    """单个PostgreSQL数据库的异步连接封装（使用单一连接池）"""

    def __init__(
            self,
            host: str,
            port: int,
            database: str,
            user: str,
            password: str,
            connect_args: dict,
            echo_sql: bool = True
    ):
        """初始化单个数据库连接配置"""
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.pool_size = connect_args.get("pool_size", 5)
        self.max_overflow = connect_args.get("max_overflow", 20)
        self.pool_recycle = connect_args.get("pool_recycle", 3600)
        self.pool_timeout = connect_args.get("pool_timeout", 15)
        self.echo_sql = echo_sql

        self.base = None  # 允许不同数据库使用不同的模型基类

        # 连接池和引擎初始化标志
        self._pool_initialized = False
        self._async_engine = None
        self._async_session_factory = None

        # 初始化锁
        self._init_lock = asyncio.Lock()

    async def set_model_base(self, model_base):
        if not self.base:
            self.base = model_base

    async def initialize(self):
        """异步初始化连接池（必须在使用前调用）"""
        # 使用锁避免竞争条件
        async with self._init_lock:
            if self._pool_initialized:
                return

            try:
                # 初始化SQLAlchemy异步引擎和会话工厂
                conn_str = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
                self._async_engine = create_async_engine(
                    conn_str,
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                    pool_recycle=self.pool_recycle,
                    pool_pre_ping=True,  # 连接前ping检查
                    pool_timeout=self.pool_timeout,  # 连接池超时
                    echo=self.echo_sql
                )

                # 创建异步会话工厂
                self._async_session_factory = sessionmaker(
                    self._async_engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                    autoflush=False
                )

                # 测试连接
                async with self._async_engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))

                self._pool_initialized = True
                logger.info(f"Database connection pool initialized for {self.database}")
            except Exception:
                logger.error(f"Failed to initialize database connection: {traceback.format_exc()}")
                raise

    async def close(self):
        """关闭连接池"""
        async with self._init_lock:
            if self._async_engine:
                try:
                    await self._async_engine.dispose()
                except Exception:
                    logger.warning(f"Error disposing SQLAlchemy engine: {traceback.format_exc()}")
                finally:
                    self._async_engine = None

            self._pool_initialized = False
            logger.info(f"Database connection pool closed for {self.database}")

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[AsyncConnection, None]:
        """获取原始数据库连接（异步上下文管理器）"""
        if not self._pool_initialized:
            await self.initialize()

        conn = None
        try:
            conn = await self._async_engine.connect()
            yield conn
        except Exception:
            if conn:
                await conn.rollback()
            logger.error(f"Error getting database connection: {traceback.format_exc()}")
            raise
        finally:
            if conn:
                await conn.close()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取ORM会话（异步上下文管理器）"""
        if not self._pool_initialized:
            await self.initialize()

        session: AsyncSession = self._async_session_factory()
        try:
            yield session
            await session.commit()
        except (UniqueViolationError, IntegrityError) as e:
            await session.rollback()
            logger.error(f"get_session ORM session error: {str(e)}")
            raise
        except Exception:
            await session.rollback()
            logger.error(f"ORM session error: {traceback.format_exc()}")
            raise
        finally:
            await session.close()

    async def execute_sql_with_return(self, sql: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """执行原生SQL查询（异步）"""
        async with self.get_connection() as conn:
            try:
                logger.info(f"execute_sql_with_return, executing native SQL: {sql}")
                result = await conn.execute(text(sql), params or {})
                if result.returns_rows:
                    rows = result.fetchall()
                    return [dict(row._mapping) for row in rows]
                else:
                    return []
            except Exception:
                logger.error(f"Error executing native SQL: {sql}, params: {params}, error: {traceback.format_exc()}")
                raise

    async def execute_sql_with_noreturn(self, sql: str) -> None:
        """执行原生SQL脚本"""
        async with self.get_connection() as conn:
            try:
                logger.info(f"execute_sql_with_noreturn, executing native SQL: {sql}")
                await conn.execute(text(sql))
                await conn.commit()
            except Exception:
                await conn.rollback()
                logger.error(f"Error executing SQL script: {sql}, error: {traceback.format_exc()}")
                raise

    async def bulk_insert_native(self, table: str, columns: List[str], data: List[Tuple]) -> int:
        """批量插入数据（原生方式）"""
        if not data:
            return 0

        # 构建INSERT语句
        stmt = insert(self.base.metadata.tables[table]).values([
            {col: val for col, val in zip(columns, row)} for row in data
        ])

        async with self.get_session() as session:
            try:
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount
            except Exception:
                await session.rollback()
                logger.error(f"Error in bulk insert: {traceback.format_exc()}")
                raise

    async def bulk_insert_native_with_session(self, session: AsyncSession, table: str, columns: List[str],
                                              data: List[Tuple]) -> int:
        """批量插入数据（原生方式），传入session以完成事务操作"""
        if not data:
            return 0

        # 构建INSERT语句
        stmt = insert(self.base.metadata.tables[table]).values([
            {col: val for col, val in zip(columns, row)} for row in data
        ])

        try:
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
        except Exception:
            await session.rollback()
            logger.error(f"Error in bulk insert: {traceback.format_exc()}")
            raise

    async def query_one_orm(
            self,
            model,
            filters: Optional[Union[Dict, List]] = None,
            joins: Optional[List] = None,
            outerjoins: Optional[List] = None,
            options: Optional[List] = None,
            return_obj: Optional[bool] = False
    ):
        """
        使用ORM查询单条数据（异步）

        :param model: 要查询的模型类
        :param filters: 过滤条件，可以是字典或SQLAlchemy表达式列表
        :param joins: 关联查询列表，格式为 [(关联模型, 关联条件)]
        :param outerjoins: 外联接查询列表，格式为 [(关联模型, 关联条件)]
        :param options: SQLAlchemy加载选项，如 joinedload, selectinload 等
        :return: 查询到的单条记录，如果没有则返回None
        """
        async with self.get_session() as session:
            try:
                model_columns = [getattr(model, col.name) for col in model.__table__.columns]
                selected_entities = list()
                join_models = []
                if joins:
                    for join_model, _ in joins:
                        join_columns = [getattr(join_model, col.name) for col in join_model.__table__.columns]
                        selected_entities.extend(join_columns)
                        join_models.append(join_model)

                if outerjoins:
                    for join_model, _ in outerjoins:
                        join_columns = [getattr(join_model, col.name) for col in join_model.__table__.columns]
                        selected_entities.extend(join_columns)
                        join_models.append(join_model)

                if selected_entities:
                    model_columns.extend(selected_entities)
                query = select(*model_columns).select_from(model)

                # 处理关联查询
                if joins:
                    for join_model, join_condition in joins:
                        query = query.join(join_model, join_condition)
                if outerjoins:
                    for ojoin_model, ojoin_condition in outerjoins:
                        query = query.outerjoin(ojoin_model, ojoin_condition)

                # 处理过滤条件
                if filters:
                    if isinstance(filters, dict):
                        conditions = []
                        for key, value in filters.items():
                            if hasattr(model, key):
                                conditions.append(getattr(model, key) == value)
                        if conditions:
                            query = query.where(and_(*conditions))
                    elif isinstance(filters, list):
                        # 支持SQLAlchemy表达式列表
                        query = query.where(and_(*filters))

                # 处理加载选项
                if options:
                    for option in options:
                        query = query.options(option)

                result = await session.execute(query)
                record = result.first()
                if return_obj:
                    return record
                else:
                    structured_record = row_to_dict(record, model, join_models)
                    return structured_record
            except Exception:
                logger.error(f"Error in ORM query_one: {traceback.format_exc()}")
                raise

    async def query_one_orm_with_session(
            self,
            session: AsyncSession,
            model,
            filters: Optional[Union[Dict, List]] = None,
            joins: Optional[List] = None,
            outerjoins: Optional[List] = None,
            options: Optional[List] = None,
            return_obj: Optional[bool] = False
    ):
        """
        使用ORM查询单条数据（异步），传入session以完成事务操作

        :param model: 要查询的模型类
        :param filters: 过滤条件，可以是字典或SQLAlchemy表达式列表
        :param joins: 关联查询列表，格式为 [(关联模型, 关联条件)]
        :param outerjoins: 外联接查询列表，格式为 [(关联模型, 关联条件)]
        :param options: SQLAlchemy加载选项，如 joinedload, selectinload 等
        :return: 查询到的单条记录，如果没有则返回None
        """
        try:
            model_columns = [getattr(model, col.name) for col in model.__table__.columns]
            selected_entities = list()
            join_models = []
            if joins:
                for join_model, _ in joins:
                    join_columns = [getattr(join_model, col.name) for col in join_model.__table__.columns]
                    selected_entities.extend(join_columns)
                    join_models.append(join_model)

            if outerjoins:
                for join_model, _ in outerjoins:
                    join_columns = [getattr(join_model, col.name) for col in join_model.__table__.columns]
                    selected_entities.extend(join_columns)
                    join_models.append(join_model)

            if selected_entities:
                model_columns.extend(selected_entities)
            query = select(*model_columns).select_from(model)

            # 处理关联查询
            if joins:
                for join_model, join_condition in joins:
                    query = query.join(join_model, join_condition)
            if outerjoins:
                for ojoin_model, ojoin_condition in outerjoins:
                    query = query.outerjoin(ojoin_model, ojoin_condition)

            # 处理过滤条件
            if filters:
                if isinstance(filters, dict):
                    conditions = []
                    for key, value in filters.items():
                        if hasattr(model, key):
                            conditions.append(getattr(model, key) == value)
                    if conditions:
                        query = query.where(and_(*conditions))
                elif isinstance(filters, list):
                    # 支持SQLAlchemy表达式列表
                    query = query.where(and_(*filters))

            # 处理加载选项
            if options:
                for option in options:
                    query = query.options(option)

            result = await session.execute(query)
            record = result.first()
            if return_obj:
                return record
            else:
                structured_record = row_to_dict(record, model, join_models)
                return structured_record
        except Exception:
            logger.error(f"Error in ORM query_one: {traceback.format_exc()}")
            raise

    async def query_all_orm(
            self,
            model,
            filters: Optional[Union[Dict, List]] = None,
            order_by: Optional[Union[str, List, InstrumentedAttribute]] = None,
            direction: Optional[str] = 'asc',
            limit: Optional[int] = 100000,
            joins: Optional[List] = None,
            outerjoins: Optional[List] = None,
            options: Optional[List] = None
    ):
        """使用ORM查询数据（异步）"""
        async with self.get_session() as session:
            try:
                model_columns = [getattr(model, col.name) for col in model.__table__.columns]
                selected_entities = list()
                join_models = []
                if joins:
                    for join_model, _ in joins:
                        join_columns = [getattr(join_model, col.name) for col in join_model.__table__.columns]
                        selected_entities.extend(join_columns)
                        join_models.append(join_model)

                if outerjoins:
                    for join_model, _ in outerjoins:
                        join_columns = [getattr(join_model, col.name) for col in join_model.__table__.columns]
                        selected_entities.extend(join_columns)
                        join_models.append(join_model)

                if selected_entities:
                    model_columns.extend(selected_entities)
                query = select(*model_columns).select_from(model)

                # 处理关联查询
                if joins:
                    for join_model, join_condition in joins:
                        query = query.join(join_model, join_condition)
                if outerjoins:
                    for ojoin_model, ojoin_condition in outerjoins:
                        query = query.outerjoin(ojoin_model, ojoin_condition)

                # 支持更复杂的过滤条件
                if filters:
                    if isinstance(filters, dict):
                        conditions = []
                        for key, value in filters.items():
                            if hasattr(model, key):
                                conditions.append(getattr(model, key) == value)
                        if conditions:
                            query = query.where(and_(*conditions))
                    elif isinstance(filters, list):
                        # 支持SQLAlchemy表达式列表
                        query = query.where(and_(*filters))

                # 支持多字段排序
                if order_by:
                    if isinstance(order_by, str):
                        if hasattr(model, order_by):
                            if direction == "desc":
                                query = query.order_by(desc(getattr(model, order_by)))
                            else:
                                query = query.order_by(getattr(model, order_by))
                    elif isinstance(order_by, list):
                        order_clauses = []
                        for field in order_by:
                            if isinstance(field, str) and hasattr(model, field):
                                current_field = getattr(model, field)
                            elif hasattr(field, 'name'):  # 处理 InstrumentedAttribute（如 model.id）
                                current_field = field
                            else:
                                continue

                            if direction == "desc":
                                order_clauses.append(desc(current_field))
                            else:
                                order_clauses.append(current_field)
                        if order_clauses:
                            query = query.order_by(*order_clauses)
                    elif hasattr(order_by, 'name'):  # InstrumentedAttribute
                        if direction == "desc":
                            query = query.order_by(desc(order_by))
                        else:
                            query = query.order_by(order_by)

                # 处理加载选项
                if options:
                    for option in options:
                        query = query.options(option)

                # 限制最大查询数量
                query = query.limit(limit)

                result = await session.execute(query)
                records = result.all()
                structured_records = [row_to_dict(record, model, join_models) for record in records]
                return structured_records
            except Exception:
                logger.error(f"Error in ORM query: {traceback.format_exc()}")
                raise

    async def query_all_orm_with_session(
            self,
            session: AsyncSession,
            model,
            filters: Optional[Union[Dict, List]] = None,
            order_by: Optional[Union[str, List, InstrumentedAttribute]] = None,
            direction: Optional[str] = 'asc',
            limit: Optional[int] = 100000,
            joins: Optional[List] = None,
            outerjoins: Optional[List] = None,
            options: Optional[List] = None
    ):
        """使用ORM查询数据（异步），查询所有满足条件的数据，传入session以完成事务操作"""
        try:
            model_columns = [getattr(model, col.name) for col in model.__table__.columns]
            selected_entities = list()
            join_models = []
            if joins:
                for join_model, _ in joins:
                    join_columns = [getattr(join_model, col.name) for col in join_model.__table__.columns]
                    selected_entities.extend(join_columns)
                    join_models.append(join_model)

            if outerjoins:
                for join_model, _ in outerjoins:
                    join_columns = [getattr(join_model, col.name) for col in join_model.__table__.columns]
                    selected_entities.extend(join_columns)
                    join_models.append(join_model)

            if selected_entities:
                model_columns.extend(selected_entities)
            query = select(*model_columns).select_from(model)

            # 处理关联查询
            if joins:
                for join_model, join_condition in joins:
                    query = query.join(join_model, join_condition)
            if outerjoins:
                for ojoin_model, ojoin_condition in outerjoins:
                    query = query.outerjoin(ojoin_model, ojoin_condition)

            # 支持更复杂的过滤条件
            if filters:
                if isinstance(filters, dict):
                    conditions = []
                    for key, value in filters.items():
                        if hasattr(model, key):
                            conditions.append(getattr(model, key) == value)
                    if conditions:
                        query = query.where(and_(*conditions))
                elif isinstance(filters, list):
                    # 支持SQLAlchemy表达式列表
                    query = query.where(and_(*filters))

            # 支持多字段排序
            if order_by:
                if isinstance(order_by, str):
                    if hasattr(model, order_by):
                        if direction == "desc":
                            query = query.order_by(desc(getattr(model, order_by)))
                        else:
                            query = query.order_by(getattr(model, order_by))
                elif isinstance(order_by, list):
                    order_clauses = []
                    for field in order_by:
                        if isinstance(field, str) and hasattr(model, field):
                            current_field = getattr(model, field)
                        elif hasattr(field, 'name'):  # 处理 InstrumentedAttribute（如 model.id）
                            current_field = field
                        else:
                            continue

                        if direction == "desc":
                            order_clauses.append(desc(current_field))
                        else:
                            order_clauses.append(current_field)
                    if order_clauses:
                        query = query.order_by(*order_clauses)
                elif hasattr(order_by, 'name'):  # InstrumentedAttribute
                    if direction == "desc":
                        query = query.order_by(desc(order_by))
                    else:
                        query = query.order_by(order_by)

            # 处理加载选项
            if options:
                for option in options:
                    query = query.options(option)

            # 限制最大查询数量
            query = query.limit(limit)

            result = await session.execute(query)
            records = result.all()
            structured_records = [row_to_dict(record, model, join_models) for record in records]
            return structured_records
        except Exception:
            logger.error(f"Error in ORM query: {traceback.format_exc()}")
            raise

    async def query_all_orm_list(
            self,
            model,
            filters: Optional[Union[Dict, List]] = None,
            order_by: Optional[Union[str, List, InstrumentedAttribute]] = None,
            direction: Optional[str] = 'asc',
            joins: Optional[List] = None,
            outerjoins: Optional[List] = None,
            options: Optional[List] = None,
            offset: Optional[int] = 0,
            limit: Optional[int] = 10
    ):
        """使用ORM查询数据（异步）,支持分页"""
        async with self.get_session() as session:
            try:
                model_columns = [getattr(model, col.name) for col in model.__table__.columns]
                selected_entities = list()
                join_models = []
                if joins:
                    for join_model, _ in joins:
                        join_columns = [getattr(join_model, col.name) for col in join_model.__table__.columns]
                        selected_entities.extend(join_columns)
                        join_models.append(join_model)

                if outerjoins:
                    for join_model, _ in outerjoins:
                        join_columns = [getattr(join_model, col.name) for col in join_model.__table__.columns]
                        selected_entities.extend(join_columns)
                        join_models.append(join_model)

                if selected_entities:
                    model_columns.extend(selected_entities)
                query = select(*model_columns).select_from(model)

                # 处理关联查询
                if joins:
                    for join_model, join_condition in joins:
                        query = query.join(join_model, join_condition)
                if outerjoins:
                    for ojoin_model, ojoin_condition in outerjoins:
                        query = query.outerjoin(ojoin_model, ojoin_condition)

                # 支持更复杂的过滤条件
                if filters:
                    if isinstance(filters, dict):
                        conditions = []
                        for key, value in filters.items():
                            if hasattr(model, key):
                                conditions.append(getattr(model, key) == value)
                        if conditions:
                            query = query.where(and_(*conditions))
                    elif isinstance(filters, list):
                        # 支持SQLAlchemy表达式列表
                        query = query.where(and_(*filters))

                # 支持多字段排序
                if order_by:
                    if isinstance(order_by, str):
                        if hasattr(model, order_by):
                            if direction == "desc":
                                query = query.order_by(desc(getattr(model, order_by)))
                            else:
                                query = query.order_by(getattr(model, order_by))
                    elif isinstance(order_by, list):
                        order_clauses = []
                        for field in order_by:
                            if isinstance(field, str) and hasattr(model, field):
                                current_field = getattr(model, field)
                            elif hasattr(field, 'name'):  # 处理 InstrumentedAttribute（如 model.id）
                                current_field = field
                            else:
                                continue

                            if direction == "desc":
                                order_clauses.append(desc(current_field))
                            else:
                                order_clauses.append(current_field)
                        if order_clauses:
                            query = query.order_by(*order_clauses)
                    elif hasattr(order_by, 'name'):  # InstrumentedAttribute
                        if direction == "desc":
                            query = query.order_by(desc(order_by))
                        else:
                            query = query.order_by(order_by)

                # 处理加载选项
                if options:
                    for option in options:
                        query = query.options(option)

                count_subquery = select(model).select_from(model)
                # 添加相同的关联条件
                if joins:
                    for join_model, join_condition in joins:
                        count_subquery = count_subquery.join(join_model, join_condition)
                if outerjoins:
                    for ojoin_model, ojoin_condition in outerjoins:
                        count_subquery = count_subquery.outerjoin(ojoin_model, ojoin_condition)
                # 添加相同的过滤条件
                if filters:
                    if isinstance(filters, dict):
                        conditions = []
                        for key, value in filters.items():
                            if hasattr(model, key):
                                conditions.append(getattr(model, key) == value)
                        if conditions:
                            count_subquery = count_subquery.where(and_(*conditions))
                    elif isinstance(filters, list):
                        count_subquery = count_subquery.where(and_(*filters))
                count_query = select(func.count()).select_from(count_subquery.subquery())
                count_result = await session.execute(count_query)
                total = count_result.scalar() or 0  # 确保返回0而非None

                # 添加分页支持
                query = query.offset(offset).limit(limit)

                result = await session.execute(query)
                records = result.all()
                structured_records = [row_to_dict(record, model, join_models) for record in records]
                return structured_records, total
            except Exception:
                logger.error(f"Error in ORM query: {traceback.format_exc()}")
                raise

    async def query_all_orm_list_with_session(
            self,
            session: AsyncSession,
            model,
            filters: Optional[Union[Dict, List]] = None,
            order_by: Optional[Union[str, List, InstrumentedAttribute]] = None,
            direction: Optional[str] = 'asc',
            joins: Optional[List] = None,
            outerjoins: Optional[List] = None,
            options: Optional[List] = None,
            offset: Optional[int] = 0,
            limit: Optional[int] = 10
    ):
        """使用ORM查询数据（异步）,支持分页"""
        try:
            model_columns = [getattr(model, col.name) for col in model.__table__.columns]
            selected_entities = list()
            join_models = []
            if joins:
                for join_model, _ in joins:
                    join_columns = [getattr(join_model, col.name) for col in join_model.__table__.columns]
                    selected_entities.extend(join_columns)
                    join_models.append(join_model)

            if outerjoins:
                for join_model, _ in outerjoins:
                    join_columns = [getattr(join_model, col.name) for col in join_model.__table__.columns]
                    selected_entities.extend(join_columns)
                    join_models.append(join_model)

            if selected_entities:
                model_columns.extend(selected_entities)
            query = select(*model_columns).select_from(model)

            # 处理关联查询
            if joins:
                for join_model, join_condition in joins:
                    query = query.join(join_model, join_condition)
            if outerjoins:
                for ojoin_model, ojoin_condition in outerjoins:
                    query = query.outerjoin(ojoin_model, ojoin_condition)

            # 支持更复杂的过滤条件
            if filters:
                if isinstance(filters, dict):
                    conditions = []
                    for key, value in filters.items():
                        if hasattr(model, key):
                            conditions.append(getattr(model, key) == value)
                    if conditions:
                        query = query.where(and_(*conditions))
                elif isinstance(filters, list):
                    # 支持SQLAlchemy表达式列表
                    query = query.where(and_(*filters))

            # 支持多字段排序
            if order_by:
                if isinstance(order_by, str):
                    if hasattr(model, order_by):
                        if direction == "desc":
                            query = query.order_by(desc(getattr(model, order_by)))
                        else:
                            query = query.order_by(getattr(model, order_by))
                elif isinstance(order_by, list):
                    order_clauses = []
                    for field in order_by:
                        if isinstance(field, str) and hasattr(model, field):
                            current_field = getattr(model, field)
                        elif hasattr(field, 'name'):  # 处理 InstrumentedAttribute（如 model.id）
                            current_field = field
                        else:
                            continue

                        if direction == "desc":
                            order_clauses.append(desc(current_field))
                        else:
                            order_clauses.append(current_field)
                    if order_clauses:
                        query = query.order_by(*order_clauses)
                elif hasattr(order_by, 'name'):  # InstrumentedAttribute
                    if direction == "desc":
                        query = query.order_by(desc(order_by))
                    else:
                        query = query.order_by(order_by)

            # 处理加载选项
            if options:
                for option in options:
                    query = query.options(option)

            count_subquery = select(model).select_from(model)
            # 添加相同的关联条件
            if joins:
                for join_model, join_condition in joins:
                    count_subquery = count_subquery.join(join_model, join_condition)
            if outerjoins:
                for ojoin_model, ojoin_condition in outerjoins:
                    count_subquery = count_subquery.outerjoin(ojoin_model, ojoin_condition)
            # 添加相同的过滤条件
            if filters:
                if isinstance(filters, dict):
                    conditions = []
                    for key, value in filters.items():
                        if hasattr(model, key):
                            conditions.append(getattr(model, key) == value)
                    if conditions:
                        count_subquery = count_subquery.where(and_(*conditions))
                elif isinstance(filters, list):
                    count_subquery = count_subquery.where(and_(*filters))
            count_query = select(func.count()).select_from(count_subquery.subquery())
            count_result = await session.execute(count_query)
            total = count_result.scalar() or 0  # 确保返回0而非None

            # 添加分页支持
            query = query.offset(offset).limit(limit)

            result = await session.execute(query)
            records = result.all()
            structured_records = [row_to_dict(record, model, join_models) for record in records]
            return structured_records, total
        except Exception:
            logger.error(f"Error in ORM query: {traceback.format_exc()}")
            raise

    async def query_count(self, model, filters: Optional[Union[Dict, List]] = None):
        async with self.get_session() as session:
            try:
                query = select(func.count()).select_from(model)
                if isinstance(filters, dict):
                    conditions = []
                    for key, value in filters.items():
                        if hasattr(model, key):
                            conditions.append(getattr(model, key) == value)
                    if conditions:
                        query = query.where(and_(*conditions))
                elif isinstance(filters, list):
                    # 支持SQLAlchemy表达式列表
                    query = query.where(and_(*filters))

                result = await session.execute(query)
                return result.scalar()
            except Exception:
                logger.error(f"Error in ORM query: {traceback.format_exc()}")
                raise

    async def query_count_with_session(self, session: AsyncSession, model, filters: Optional[Union[Dict, List]] = None):
        """ 传入session以完成事务操作 """
        try:
            query = select(func.count()).select_from(model)
            if isinstance(filters, dict):
                conditions = []
                for key, value in filters.items():
                    if hasattr(model, key):
                        conditions.append(getattr(model, key) == value)
                if conditions:
                    query = query.where(and_(*conditions))
            elif isinstance(filters, list):
                # 支持SQLAlchemy表达式列表
                query = query.where(and_(*filters))

            result = await session.execute(query)
            return result.scalar()
        except Exception:
            logger.error(f"Error in ORM query: {traceback.format_exc()}")
            raise

    async def insert_orm(self, item):
        """使用ORM插入数据（异步）"""
        async with self.get_session() as session:
            try:
                session.add(item)
                await session.flush()
                await session.refresh(item)
                return item
            except (UniqueViolationError, IntegrityError) as e:
                await session.rollback()
                logger.error(f"insert_orm Error inserting ORM instance: {str(e)}")
                raise
            except Exception:
                await session.rollback()
                logger.error(f"insert_orm Error inserting ORM instance: {traceback.format_exc()}")
                raise

    async def insert_orm_with_session(self, session: AsyncSession, item):
        """使用ORM插入数据（异步），传入session以完成事务操作"""
        try:
            session.add(item)
            await session.flush()
            await session.refresh(item)
            return item
        except (UniqueViolationError, IntegrityError) as e:
            await session.rollback()
            logger.error(f"insert_orm_with_session Error inserting ORM instance: {str(e)}")
            raise
        except Exception:
            await session.rollback()
            logger.error(f"insert_orm_with_session Error inserting ORM instance: {traceback.format_exc()}")
            raise

    async def bulk_insert_orm(self, items) -> int:
        """批量插入数据（ORM方式）"""
        if not items:
            return 0

        async with self.get_session() as session:
            try:
                session.add_all(items)
                await session.flush()
                return len(items)
            except (UniqueViolationError, IntegrityError) as e:
                await session.rollback()
                logger.error(f"bulk_insert_orm Error in bulk ORM insert: {str(e)}")
                raise
            except Exception:
                await session.rollback()
                logger.error(f"bulk_insert_orm Error in bulk ORM insert: {traceback.format_exc()}")
                raise

    async def bulk_insert_orm_with_session(self, session: AsyncSession, items) -> int:
        """批量插入数据（ORM方式），传入session以完成事务操作"""
        if not items:
            return 0

        try:
            session.add_all(items)
            await session.flush()
            return len(items)
        except (UniqueViolationError, IntegrityError) as e:
            await session.rollback()
            logger.error(f"bulk_insert_orm_with_session Error in bulk ORM insert: {str(e)}")
            raise
        except Exception:
            await session.rollback()
            logger.error(f"bulk_insert_orm_with_session Error in bulk ORM insert: {traceback.format_exc()}")
            raise

    async def update(self, model, filters, values):
        """更新"""
        async with self.get_session() as session:
            try:
                stmt = update(model).where(*filters).values(**values)
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount
            except Exception:
                await session.rollback()
                logger.error(f"Error update ORM instance: {traceback.format_exc()}")
                raise

    async def update_with_session(self, session: AsyncSession, model, filters, values):
        """更新，传入session以完成事务操作"""
        try:
            stmt = update(model).where(*filters).values(**values)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
        except Exception:
            await session.rollback()
            logger.error(f"Error update ORM instance: {traceback.format_exc()}")
            raise

    async def delete(self, model, filters: List[Any]):
        """删除数据"""
        async with self.get_session() as session:
            try:
                stmt = delete(model).where(*filters)
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount
            except Exception:
                await session.rollback()
                logger.error(f"Error deleting ORM instance: {traceback.format_exc()}")
                raise

    async def delete_with_session(self, session: AsyncSession, model, filters: List[Any]):
        """删除数据"""
        try:
            stmt = delete(model).where(*filters)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
        except Exception:
            await session.rollback()
            logger.error(f"Error deleting ORM instance: {traceback.format_exc()}")
            raise

    async def create_tables(self):
        """创建所有模型对应的数据库表"""
        if not self._pool_initialized:
            await self.initialize()

        try:
            async with self.get_connection() as conn:
                async with conn.begin():
                    await conn.run_sync(self.base.metadata.create_all)
            logger.info(f"Tables created for {self.database}")
        except Exception:
            logger.error(f"Error creating tables: {traceback.format_exc()}")
            raise

    async def drop_tables(self):
        """删除所有模型对应的数据库表"""
        if not self._pool_initialized:
            await self.initialize()

        try:
            async with self._async_engine.begin() as conn:
                async with conn.begin():
                    await conn.run_sync(self.base.metadata.drop_all)
            logger.info(f"Tables dropped for {self.database}")
        except Exception:
            logger.error(f"Error dropping tables: {traceback.format_exc()}")
            raise

    async def check_connection_health(self) -> bool:
        """检查连接健康状态"""
        try:
            async with self.get_connection() as conn:
                # 执行简单查询测试连接
                result = await conn.execute(text("SELECT 1"))
                return True
        except Exception:
            logger.warning(f"Connection health check failed: {traceback.format_exc()}")
            return False

    async def reconnect_if_needed(self) -> bool:
        """如果需要则重新连接"""
        if not await self.check_connection_health():
            logger.info("Connection unhealthy, attempting to reconnect...")
            await self.close()
            await self.initialize()
            return True
        return False

    async def get_pool_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        if not self._pool_initialized:
            return {}

        stats = {}
        try:
            if self._async_engine:
                stats = {
                    "checkedin": self._async_engine.pool.checkedin(),
                    "checkedout": self._async_engine.pool.checkedout(),
                    "overflow": self._async_engine.pool.overflow(),
                    "size": self._async_engine.pool.size(),
                }
        except Exception:
            logger.warning(f"Error getting pool stats: {traceback.format_exc()}")

        return stats
