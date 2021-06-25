from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Table, Column, Integer, String
from Tools.sql import sqlconnmanager
from sqlalchemy.future import select
from sqlalchemy import delete


Base = declarative_base()

class ModBotTable(Base):
    __tablename__ = 'ModbotTable'

    id = Column(Integer, primary_key=True)
    serverid = Column(Integer)
    prefix = Column(String(1), default = "!")

    def addconfig(session):
        async def wrapper(id: int, config=None):
            stmt = select(ModBotTable).where(ModBotTable.serverid == id)
            res = await session.execute(stmt)
            row = res.scalars().first()

            if(not config):
                config = ModBotTable(serverid=id)

            if(row):
                stmt = delete(ModBotTable).where(ModBotTable.serverid == id)
                await session.execute(stmt)
                session.add(config)
                await session.commit()
        return wrapper

    def getconf(session):
        async def wrapper(id: int):
            stmt = select(ModBotTable).where(ModBotTable.serverid == id)
            res = await session.execute(stmt)
            row = res.scalars().first()
            return row
        return wrapper


        

