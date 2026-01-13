"""Async Database Library"""

from os import environ

from loguru import logger
from sqlalchemy import ColumnElement, TextClause, and_, delete, text, update
from sqlalchemy.engine import CursorResult, Result, ScalarResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import Delete, Insert, Select, Update

# --------------------------------------------------------------------------------------------------

DEBUG = environ.get("DEBUG")

# --------------------------------------------------------------------------------------------------
# Async execute helpers
# --------------------------------------------------------------------------------------------------


async def async_session_execute(
    session: AsyncSession,
    statement: str | TextClause | Delete | Insert | Select | Update,
) -> Result | CursorResult | None:
    """Async session execute"""

    info = "database execute statement"

    if DEBUG:
        logger.debug(f"{info} [SQL]\n------\n\n{statement}\n\n------")

    logger.info(f"{info} [ start ]")

    try:
        stmt = text(statement) if isinstance(statement, str) else statement
        result = await session.execute(stmt)
        await session.commit()
        logger.success(f"{info} [ success ]")
        return result
    except Exception as e:
        logger.error(f"{info} [ error ]")
        await session.rollback()
        if DEBUG:
            logger.exception(e)
        else:
            logger.error(e)
        return None


async def async_session_scalars(
    session: AsyncSession,
    statement: str | TextClause | Delete | Insert | Select | Update,
) -> ScalarResult | None:
    """Async session scalars"""

    info = "database execute statement"

    if DEBUG:
        logger.debug(f"{info} [SQL]\n------\n\n{statement}\n\n------")

    logger.info(f"{info} [ start ]")

    try:
        stmt = text(statement) if isinstance(statement, str) else statement
        result = await session.scalars(stmt)
        await session.commit()
        logger.success(f"{info} [ success ]")
        return result
    except Exception as e:
        logger.error(f"{info} [ error ]")
        await session.rollback()
        if DEBUG:
            logger.exception(e)
        else:
            logger.error(e)
        return None


# --------------------------------------------------------------------------------------------------
# ORM Base
# --------------------------------------------------------------------------------------------------


class ORMBase(DeclarativeBase):
    """ORM Base"""

    pass  # pylint: disable=unnecessary-pass


# --------------------------------------------------------------------------------------------------
# Async ORM Session Wrapper
# --------------------------------------------------------------------------------------------------


class AsyncORMSession:
    """Async ORM Session"""

    def __init__(self, model: type[ORMBase], session: AsyncSession):

        self.model: type[ORMBase] = model
        self.session: AsyncSession = session
        self.info: str = f"Model: {model.__tablename__}"

    # ----------------------------------------------------------------------------------------------

    async def close(self):
        """关闭连接"""
        # await self.session.get_bind().dispose()
        await self.session.close()

    # ----------------------------------------------------------------------------------------------

    async def test_connection(self) -> bool:
        logger.info(f"{self.info} [ test connection | start ]")
        try:
            await self.session.execute(text("SELECT 1;"))
            logger.success(f"{self.info} [ test connection | success ]")
            return True
        except Exception as e:
            logger.error(f"{self.info} [ test connection | error ]")
            if DEBUG:
                logger.exception(e)
            else:
                logger.error(e)
            return False

    # ----------------------------------------------------------------------------------------------

    # async def init_model(self) -> bool:
    #     logger.info(f"{self.info} [ initialization | start ]")
    #     try:
    #         bind = await self.session.get_bind()
    #         self.model.__table__.drop(bind=bind, checkfirst=True)
    #         self.model.__table__.create(bind=bind, checkfirst=True)
    #         logger.success(f"{self.info} [ initialization | success ]")
    #         return True
    #     except Exception as e:
    #         logger.error(f"{self.info} [ initialization | error ]")
    #         if DEBUG:
    #             logger.exception(e)
    #         else:
    #             logger.error(e)
    #         return False

    # ----------------------------------------------------------------------------------------------

    async def execute(self, *args, **kwargs):
        return await async_session_execute(self.session, *args, **kwargs)

    async def scalars(self, *args, **kwargs):
        return await async_session_scalars(self.session, *args, **kwargs)

    # ----------------------------------------------------------------------------------------------
    # Create
    # ----------------------------------------------------------------------------------------------

    async def create(self, data: dict | list[dict] | tuple[dict, ...]) -> int:

        if isinstance(data, dict) and data:
            logger.info(f"{self.info} [ create single data | start ]")
            try:
                self.session.add(self.model(**data))
                await self.session.commit()
                logger.success(f"{self.info} [ create single data | success ]")
                return 1
            except Exception as e:
                await self.session.rollback()
                logger.error(f"{self.info} [ create single data | error ]")
                if DEBUG:
                    logger.exception(e)
                else:
                    logger.error(e)
                return 0

        if isinstance(data, (list, tuple)) and data:
            logger.info(f"{self.info} [ create batch data | start ]")
            try:
                self.session.add_all(self.model(**item) for item in data)
                await self.session.commit()
                logger.success(f"{self.info} [ create batch data | success ]")
                return len(data)
            except IntegrityError as ie:
                await self.session.rollback()
                logger.warning(ie)

                count = 0
                for item in data:
                    try:
                        self.session.add(self.model(**item))
                        await self.session.commit()
                        count += 1
                        logger.success(f"{self.info} [ {count} pieces created ]")
                    except IntegrityError:
                        await self.session.rollback()
                        logger.warning(f"{self.info} [ data exists | skip ]")
                    except Exception as e:
                        await self.session.rollback()
                        if DEBUG:
                            logger.exception(e)
                        else:
                            logger.error(e)

                logger.success(f"{self.info} [ create batch | finish ]")
                return count

        logger.warning(f"{self.info} [ create data | none ]")
        return 0

    # ----------------------------------------------------------------------------------------------
    # Where builder
    # ----------------------------------------------------------------------------------------------

    def _build_where(
        self,
        where: dict | list | tuple | ColumnElement | None,
    ) -> ColumnElement | None:
        try:
            if where is None:
                return None

            if isinstance(where, dict) and where:
                conditions = [getattr(self.model, k) == v for k, v in where.items()]
                return and_(*conditions)

            if isinstance(where, (list, tuple)) and where:
                return and_(*where)

            if isinstance(where, ColumnElement):
                return where

            return None
        except Exception as e:
            if DEBUG:
                logger.exception(e)
            else:
                logger.error(e)
            return None

    # ----------------------------------------------------------------------------------------------
    # Update
    # ----------------------------------------------------------------------------------------------

    async def update(self, where: dict | list | tuple | ColumnElement | None, data: dict) -> bool:
        logger.info(f"{self.info} [ update data | start ]")
        try:
            cond = self._build_where(where)
            if cond is None:
                logger.error(f"{self.info} [ build where error ]")
                return False

            stmt = update(self.model).where(cond).values(**data).execution_options(synchronize_session="fetch")

            result = await self.execute(stmt)
            if not result:
                return False

            logger.success(f"{self.info} [ update data | success ]")
            return True
        except Exception as e:
            logger.error(f"{self.info} [ update data | error ]")
            if DEBUG:
                logger.exception(e)
            else:
                logger.error(e)
            return False

    # ----------------------------------------------------------------------------------------------
    # Delete
    # ----------------------------------------------------------------------------------------------

    async def delete(self, where: dict | list | tuple | ColumnElement | None) -> bool:
        logger.info(f"{self.info} [ delete data | start ]")
        try:
            cond = self._build_where(where)
            if cond is None:
                logger.error(f"{self.info} [ build where error ]")
                return False

            stmt = delete(self.model).where(cond)
            result = await self.execute(stmt)
            if not result:
                return False

            logger.success(f"{self.info} [ delete data | success ]")
            return True
        except Exception as e:
            logger.error(f"{self.info} [ delete data | error ]")
            if DEBUG:
                logger.exception(e)
            else:
                logger.error(e)
            return False
