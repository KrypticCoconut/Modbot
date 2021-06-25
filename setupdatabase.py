from Tools.cache import ConfigCache
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Table, Column, Integer, String
from Tools.sql import sqlconnmanager
from sqlalchemy.future import select
from sqlalchemy import delete


class table:
    def __init__(self, connection, tablecls, getfunc = None, addfunc = None):
        self.connection = connection
        self.dbname = connection.db
        self.tablecls = tablecls
        self.getfunc = getfunc
        self.addfunc = addfunc

    

async def main(programclass):
    user = programclass.config["sql"]["user"]
    password = programclass.config["sql"]["password"]
    programclass.sqlconnections = sqlconnmanager(user, password)

    #assign main table
    mainc = programclass.sqlconnections.CreateConn(programclass.config["sql"]["dbname"], main=True) #main database
    base = programclass.sqlconnections.base
    table = await setupmain(mainc, base)
    mainc.tablesindb[table.tablecls.__tablename__] = table
    mainc.maintable = table


    #make cache
    cache = ConfigCache(table.getfunc, table.addfunc, 16) # size 16 for now
    programclass.cache = cache

    

async def setupmain(connection, base):
    engine = connection.engine
    session = connection.session

    class ModBotTable(base):
        __tablename__ = 'ModbotTable'

        id = Column(Integer, primary_key=True)
        serverid = Column(Integer)
        prefix = Column(String(1), default="!")



    async def addconfig(id: int, config=None):

        stmt = select(ModBotTable).where(ModBotTable.serverid == id)
        res = await session.execute(stmt)
        row = res.scalars().first()

        if(not config):
            config = ModBotTable(serverid=id)

        if(row):
            #i am lazy so i will just delete the thing and remake
            stmt = delete(ModBotTable).where(ModBotTable.serverid == id)
            await session.execute(stmt)
            session.add(config)
            await session.commit()


    async def getconf(id: int):
        stmt = select(ModBotTable).where(ModBotTable.serverid == id)
        res = await session.execute(stmt)
        row = res.scalars().first()
        return row

    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)

    t = table(connection, ModBotTable, addfunc=addconfig, getfunc=getconf)

    return t
        

    
