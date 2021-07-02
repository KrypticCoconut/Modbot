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

    def AddEvent(self, conf, user, datetime, func, args):
        #assumes datetime in format `Month-Day-Hour-Minute`
        
        member = [member for member in conf["members"] if member["member_id"] == user.id]
        if(not member):
            member = {"member_id": user.id, "warnsleft": conf["default_warns"]}
            job = self.scheduler.add_job(func, 'date', args, next_run_time=datetime)
            member["job"] = dict()
            member["job"]["datetime"] = self.GetDateTime(datetime)
            member["job"]["jobid"] = job.id
            conf["members"].append(member)
        else:
            member = member[0]
            job = self.scheduler.add_job(func, 'date', args, next_run_time=datetime)
            member["job"]["datetime"] = self.GetDateTime(datetime)
            member["job"]["jobid"] = job.id

    def GetDateTime(self, dt):
        return str(dt.strftime("%d/%m/%Y %H:%M:%S"))

