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

    serverid = Column(Integer, primary_key=True)
    prefix = Column(String(5), default="!")


server = ModBotTable(serverid=12112)