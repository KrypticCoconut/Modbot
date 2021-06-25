
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

class sqlconnmanager:
    def __init__(self, user:str, password:str, base):
        self.base = base
        self.metadata = self.base.metadata
        self.all_conns = dict()
        self.user = user
        self.password = password
    

    def CreateConn(self, dbname: str, main:bool = False):

        # if([key for key,val in self.all_sessions.items() if val == dbname ]):
        #     raise Exception("Cannot have sessions with same name")
        # i dont yet know how sqlalchemy sessions interact together so im commenting this out
             
        conn = sqlconn(dbname, self.user, self.password, self.base)
        if(main):
            self.mainconn = conn
        self.all_conns[dbname] = conn
        setattr(self, dbname, conn)
        return conn


class sqlconn:
    def __init__(self, dbname: str, user: str, password: str, base):
        self.engine = create_async_engine("mariadb+aiomysql://{}:{}@127.0.0.1:3306/{}".format(user, password, dbname))
        self.db = dbname
        self.session = AsyncSession(self.engine)
        self.tablesindb =dict()
        self.maintable = None #placeholder