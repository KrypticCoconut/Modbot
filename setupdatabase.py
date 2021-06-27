from Tools.cache import ConfigCache
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Table, Column, Integer, String
from Tools.sql import sqlconnmanager
from sqlalchemy.future import select
from sqlalchemy import delete
from models import Base, ModBotTable

class sqlconnection:
    def __init__(self, engine, Base=None):
        self.engine = engine
        self.base = Base    
    def createsession(self):
        return sessionctxmanager(self)
    def begin(self):
        return enginectxmanager(self)

class sessionctxmanager:
    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        self.session = AsyncSession(self.conn.engine) #start session
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close() # releases connection and transaction object


class enginectxmanager:
    def __init__(self, conn):
        self.engine = conn.engine

    async def __aenter__(self):
        self.c = self.engine.connect()
        await self.c.start(is_ctxmanager=False) #start connection without ctx manager
        return self.c

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.c.close() #closes connection
        await self.engine.dispose() # removes all associated connections

        
def addconfig(conn):
    async def wrapper(id: int, config):
        stmt = select(ModBotTable).where(ModBotTable.serverid == id)
        res = await session.execute(stmt)
        row = res.scalars().first()
        async with conn.begin() as engine:
            async with conn.createsession() as session:
                if(row):
                    stmt = delete(ModBotTable).where(ModBotTable.serverid == id)
                    await session.execute(stmt)
                    session.add(config)
                else:
                    session.add(config)


    return wrapper

def getconfig(conn):
    async def wrapper(id: int):
        async with conn.begin() as engine:
            async with conn.createsession() as session:
                stmt = select(ModBotTable).where(ModBotTable.serverid == id)
                res = await session.execute(stmt)
                row = res.scalars().first()
        return row
    return wrapper
    


async def main(programclass):

    #setup db connection
    user = programclass.config["sql"]["user"]
    password = programclass.config["sql"]["password"]
    dbname  = programclass.config["sql"]["dbname"]
    engine = create_async_engine("mariadb+aiomysql://{}:{}@127.0.0.1:3306/{}".format(user, password, dbname))
    programclass.sqlconnection = sqlconnection(engine, Base=Base)

    async with programclass.sqlconnection.begin() as conn: 
        await conn.run_sync(programclass.sqlconnection.base.metadata.create_all)
        #async with AsyncSession(engine) as session: works too
            


    #make cache
    cache = ConfigCache(2) # size 16 for now
    global getconfig
    global addconfig
    getconfig, addconfig = cache.SetupFuncs(getconfig(programclass.sqlconnection),addconfig(programclass.sqlconnection), None)
    programclass.cache = cache


    # server = ModBotTable(serverid = 21208932)
    # y = await addconfig(21208932, server)
    # x = await getconfig(21208932)
    
