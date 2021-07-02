from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
import asyncio

class EventScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.events = dict()
        self.scheduler.start()

    def AddEvent(self, memberid, serverid, category, datetime, func, args):

        #this is a terrible implementation but im lazy
        if(not self.events.get(serverid, None)):
            self.events[serverid] = dict()
        if(not self.events[serverid].get(category, None)):
            self.events[serverid][category] = dict()

        job = self.scheduler.add_job(func, 'date', args, next_run_time=datetime)
        
        try:
            if(self.events[serverid][category][memberid]):
                self.events[serverid][category][memberid][1].remove()
        except:
            pass
        self.events[serverid][category][memberid] = [datetime.strftime("Month:%m Day:%d Time:%H:%M:%S"), job]
    
    def GetEvents(self, serverid):
        events = self.events.get(serverid, None)
        if(not events):
            return None
        return events


# async def runfunc():
#     print("running function")

# async def main():
#     e = EventScheduler()
#     e.AddEvent(213768231768, "warns", datetime.datetime.now() + datetime.timedelta(seconds=3), runfunc)

#     while True:
#         await asyncio.sleep(.5)


# asyncio.run(main())