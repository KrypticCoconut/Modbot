from Tools.Misc import FuncUtils
from models import ModBotTable


      
class node:
    def __init__(self, key: int, val):
        self.key = key
        self.val = val
        self.next = None
        self.prev = None
   

class ConfigCache:

    def __init__(self, cachelength: int): 
        # get and set have to be functions that fetch confs and return the confs
        # get input params: server id -> config
        # set input patrams: server id, new conf -> none

        FuncUtils.checkargs(["getconf", "modconf", "cachelength"])

        self.cache = dict()
        self.cachelength = cachelength

        self.head = node(0, 0)
        self.tail = node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def SetupFuncs(self, getconf, addconf, commitfunc):
        getconf = self.GetConf(getconf)
        self.addtocache = self.addtocache(addconf)
        self.commitall = self.commitall(commitfunc, addconf)
        addconf = self.AddConf
        return getconf, addconf


    def GetConf(self , function) :
        async def wrapper(serverid: int):
            if(serverid in self.cache):
                mnode = self.findnode(serverid)
                await self.movetofront(mnode)
            else:
                conf = await function(serverid)
                if(not conf):
                    return None
                self.cache[serverid] = conf
                mnode = node(serverid, conf)
                await self.addtocache(mnode)
            return mnode.val
        return wrapper
    
    async def AddConf(self, serverid: int, conf=None) -> None:
        if(not conf):
            conf = ModBotTable(serverid=serverid)

        if(serverid in self.cache):
            mnode = self.findnode(serverid)
            mnode.val = conf
            self.cache[serverid] = conf
            await self.movetofront(mnode)
        else:   
            self.cache[serverid] = conf
            mnode = node(serverid, conf)
            await self.addtocache(mnode)




    def addtocache(self, addfunc) -> None:
        async def wrapper(node: node) -> None:
            # set inserted node as next node for prev node
            p = self.tail.prev
            p.next = node
            
            #insert node
            self.tail.prev = node
            node.next = self.tail

            # set prev node as inserted node's prev node
            node.prev = p 

            if(len(self.cache) > self.cachelength):
                n = self.head.next
                await addfunc(n.key, n.val)
                self.remove(n)
                del self.cache[n.key]
                print(self.cache)
                
        return wrapper

    def remove(self, node:node) -> None:
        #unlink nodes, removing refs should delete the object from memory
        p = node.prev
        n = node.next
        p.next = n
        n.prev = p

    def commitall(self, commit, addfunc):
        async def wrapper():
            curr = self.head.next
            while True:
                await addfunc(curr.key, curr.val)
                curr = curr.next
            await commit()

                
                

    def findnode(self, serverid: int) -> node:
        current = self.head
          
        while True:
              
            if current.key == serverid:
                node = current
                return node
              
            else:
                current = current.next 

        
    async def movetofront(self, node: node) -> None:
        self.remove(node)
        await self.addtocache(node) #add will set the prev an next itself 

