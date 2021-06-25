from Tools.cache import ConfigCache
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Table, Column, Integer, String
from Tools.sql import sqlconnmanager
from sqlalchemy.future import select
from sqlalchemy import delete
import models

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
    programclass.sqlconnections = sqlconnmanager(user, password, models.Base)

    #assign main table
    mainc = programclass.sqlconnections.CreateConn(programclass.config["sql"]["dbname"]) #main database
    table = await setupmain(mainc)
    mainc.tablesindb[table.tablecls.__tablename__] = table

    #make cache
    cache = ConfigCache(table.getfunc, table.addfunc, 16) # size 16 for now
    programclass.cache = cache

    

async def setupmain(connection):
    session = connection.session
    models.ModBotTable.addconfig = models.ModBotTable.addconfig(session)
    models.ModBotTable.getconf = models.ModBotTable.getconf(session)
    t = table(connection, models.ModBotTable, addfunc=models.ModBotTable.addconfig, getfunc=models.ModBotTable.getconf)
    return t
        

    
