from sqlalchemy import Integer, ForeignKey, String, Column, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields, post_load


Base = declarative_base()

class ModBotTable(Base):
    __tablename__ = 'MainTable'

    server_id = Column(BigInteger, primary_key=True)
    prefix = Column(String(5), default="!")
    members = relationship("MemberTable", lazy="noload", cascade="all, delete-orphan")

    default_warns = Column(Integer, default="4")
    default_mute_role = Column(BigInteger, nullable=True, default=None)

class MemberTable(Base):
    __tablename__ = "Members"
    member_id = Column(BigInteger, primary_key=True)
    warnsleft = Column(Integer, default=3)
    server_id = Column(BigInteger, ForeignKey('MainTable.server_id'))


class MemberTableSchema(Schema):
    member_id = fields.Integer(required=True)
    warnsleft = fields.Integer(required=True)
    
    @post_load
    def create(self, data, **kwargs):
        r = MemberTable(**data)
        #print(r)
        return r

class ModBotTableSchema(Schema):
    server_id = fields.Integer(required=True)
    prefix = fields.String(required=True)
    members = fields.List(fields.Nested(MemberTableSchema))

    default_warns = fields.Integer(required=True)
    default_mute_role = fields.Inferred()
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
# table = ModBotTable(server_id=7438966712, prefix="!")
# member1 = MemberTable(member_id=231876139762, warnsleft=3)
# table.members.append(member1)
# s = SerializeObject(table)
# print(s)
# l = schema.loads(s)
# print(l.members[0].member_id)
