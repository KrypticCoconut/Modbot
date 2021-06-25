from Tools.Misc import FuncUtils



      
class node:
    def __init__(self, key: int, val):
        self.key = key
        self.val = val
        self.next = None
        self.prev = None
   

class ConfigCache:

    def __init__(self, getconf, addfunc, cachelength: int): 
        # get and set have to be functions that fetch confs and return the confs
        # get input params: server id -> config
        # set input patrams: server id, new conf -> none

        FuncUtils.checkargs(["getconf", "modconf", "cachelength"])

        self.GetConf = self.GetConf(getconf)
        self.addtocache = self.addtocache(addfunc)

        self.cache = dict()
        self.cachelength = cachelength

        self.head = node(0, 0)
        self.tail = node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def GetConf(self , function) :
        async def wrapper(serverid: int):
            if(serverid in self.cache):
                mnode = self.findnode(serverid)
                self.movetofront(mnode)
            else:
                conf = await function(serverid)
                if(not conf):
                    return None
                self.cache[serverid] = conf
                mnode = node(serverid, conf)
                await self.addtocache(mnode)
            return mnode
        return wrapper
    
    async def AddConf(self, serverid: int, conf) -> None:
        if(serverid in self.cache):
            mnode = self.findnode(serverid)
            mnode.val = conf
            self.cache[serverid] = conf
            self.movetofront(mnode)
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
                
        return wrapper

    def remove(self, node:node) -> None:
        #unlink nodes, removing refs should delete the object from memory
        p = node.prev
        n = node.next
        p.next = n
        n.prev = p


    def findnode(self, serverid: int) -> node:
        current = self.head
          
        while True:
              
            if current.key == serverid:
                node = current
                return node
              
            else:
                current = current.next 

        
    def movetofront(self, node: node) -> None:
        self.remove(node)
        self.addtocache(node) #add will set the prev an next itself 

