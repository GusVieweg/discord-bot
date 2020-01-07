from JokeyBot import JokeyBot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
from dotenv import load_dotenv
load_dotenv()

jb = JokeyBot()

if os.environ['IS_PRODUCTION'] == 1:
    sched = AsyncIOScheduler()

    @sched.scheduled_job('interval', days=1, start_date='2020-01-07 23:59:00', timezone="US/Eastern")
    async def scheduled_job():
        await jb.nightly_cloud_reset()

    sched.start()

jb.run(os.environ["ACCESS_TOKEN"])
