from JokeyBot import JokeyBot
from apscheduler.schedulers.blocking import BlockingScheduler
import os
from dotenv import load_dotenv
load_dotenv()

jb = JokeyBot()

sched = BlockingScheduler()

@sched.scheduled_job('interval', days=1, start_date='2020-01-06 23:59:00', timezone="US/Eastern")
async def scheduled_job():
    print("Running scheduled_job()")
    await jb.nightly_cloud_reset()

sched.start()

jb.run(os.environ["ACCESS_TOKEN"])
