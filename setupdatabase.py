from Tools.cache import ConfigCache
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Table, Column, Integer, String
from Tools.sql import sqlconnmanager
from sqlalchemy.future import select
from sqlalchemy import delete
from models import *
import json
from sqlalchemy.orm import selectinload


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
            await self.session.commit()
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


def DeSerializeObject(schema=None): #convert dict to config 
    schema = ModBotTableSchema()
    def wrapper(sconfig):
        r = schema.load(sconfig)
        return r
    return wrapper

def SerializeObject(schema=None): #convert config to dict 
    schema = ModBotTableSchema()
    def wrapper(dsconfig):
        r = schema.dump(dsconfig)
        return r
    return wrapper


def addconfigdirectly(conn):
    async def wrapper(id: int, config):
        config = DeSerializeObject(config)
        async with conn.begin() as engine:
            async with conn.createsession() as session:
                stmt = select(ModBotTable).where(ModBotTable.server_id == id).options(selectinload(ModBotTable.members))
                res = await session.execute(stmt)
                row = res.scalars().first()
                if(row):
                    # horrible way to update but what can i do, im lazy 
                    await session.delete(row)
                    stmt = select(ModBotTable)
                    res = await session.execute(stmt)
                    for row in res.scalars():
                        print(SerializeObject(row))
                    session.add(config)
                else:
                    print("yes")
                    session.add(config)

    return wrapper

def getconfigdirectly(conn):
    async def wrapper(id: int):
        async with conn.begin() as engine:
            async with conn.createsession() as session:
                stmt = select(ModBotTable).where(ModBotTable.server_id == id).options(selectinload(ModBotTable.members))
                res = await session.execute(stmt)
                row = res.scalars().first()
                r = SerializeObject(row)
        return r
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
            
    #setup marshmallow
    global SerializeObject, DeSerializeObject
    SerializeObject = SerializeObject()
    DeSerializeObject = DeSerializeObject()

    #make cache
    cache = ConfigCache(2) # size 2 for now
    programclass.getconfigcache, programclass.addconfigcache = cache.SetupFuncs(getconfigdirectly(programclass.sqlconnection),addconfigdirectly(programclass.sqlconnection), SerializeObject)
    programclass.cache = cache


    
