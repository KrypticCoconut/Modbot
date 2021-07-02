from sqlalchemy import Integer, ForeignKey, String, Column, BigInteger, ColumnDefault
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields, post_load, post_dump


Base = declarative_base()

class MuteJob(Base):
    __tablename__ = 'MuteJob'
    datetime = Column(String(100))
    id = Column(BigInteger, primary_key=True)

class MuteJobSchema(Schema):
    datetime  = fields.String(allow_none=False)
    jobid = fields.String() #job id is the in program id var used to identify background jobs, this isnt saved to do the databse - see post_dump

    @post_dump
    def dump(self, data, **kwargs):
        # braindead code - i dont know how to implement this better
        x = dict()
        x["datetime"] = data.datetime
        x["jobid"] = ""
        return x

    @post_load
    def create(self,data, **kwargs):
        del data["jobid"]
        r = MuteJob(**data)
        return r

class MemberTable(Base):
    __tablename__ = "Members"
    member_id = Column(BigInteger, primary_key=True)
    warnsleft = Column(Integer, default=3)
    server_id = Column(BigInteger, ForeignKey('MainTable.server_id'))

    job_id = Column(BigInteger, ForeignKey('MuteJob.id'))
    job = relationship("MuteJob", lazy="noload", uselist=False)



class MemberTableSchema(Schema):
    member_id = fields.Integer(allow_none=False)
    warnsleft = fields.Integer(allow_none=False)
    job = fields.Nested(MuteJobSchema, allow_none=True)
    @post_load
    def create(self, data, **kwargs):
        r = MemberTable(**data)
        #print(r)
        return r


class ModBotTable(Base):
    __tablename__ = 'MainTable'

    server_id = Column(BigInteger, primary_key=True)
    prefix = Column(String(5), ColumnDefault("!"))
    members = relationship("MemberTable", lazy="noload", cascade="all, delete-orphan")

    default_warns = Column(Integer, ColumnDefault("4"))
    default_mute_role = Column(BigInteger, ColumnDefault(None), nullable=True)

class ModBotTableSchema(Schema):
    server_id = fields.Integer(allow_none=False)
    prefix = fields.String(allow_none=False)
    members = fields.List(fields.Nested(MemberTableSchema))

    default_warns = fields.Integer(allow_none=False)
    default_mute_role = fields.Integer(allow_none=True)
    @post_load
    def create(self, data, **kwargs):
        r = ModBotTable(**data)
        #print(r)
        return r

def SerializeObject(schema=None): #convert config to dict 
    schema = ModBotTableSchema()
    def wrapper(dsconfig):
        r = schema.dumps(dsconfig)
        return r
    return wrapper

# SerializeObject = SerializeObject()
# schema = ModBotTableSchema()
# table = ModBotTable(server_id=7438966712, prefix="!", default_warns=3)
# member1 = MemberTable(member_id=231876139762, warnsleft=3)
# job = MuteJob(datetime="12-12-12-12")
# member1.job = job
# table.members.append(member1)
# s = SerializeObject(table)
# print(s)

# l = schema.loads(s)
# # print(l.members[0].job.datetime)