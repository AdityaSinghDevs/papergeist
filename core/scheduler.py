from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz
import asyncio 

from utils.file_utils import read_json
from utils.config_loader import load_cfg

from core.fetcher import fetch_papers
from core.processor import filter_new_papers
from core.llm import summarize
from core.sender import send_paper

scheduler = AsyncIOScheduler()
cfg = load_cfg("configs/config.yaml")

async def job(bot):
    users = read_json(cfg["paths"]["users_file"], {})

    now = datetime.now(pytz.timezone("Asia/Kolkata"))
    current_hour = now.hour
    current_minute = now.minute

    for chat_id, prefs in users.items():
        user_hour = prefs.get("hour", 9)
        user_minute = prefs.get("minute", 0)

        field = prefs.get("field", cfg["app"]["default_field"])

        # allow small window (±1 min)
        if not (user_hour == current_hour and abs(user_minute - current_minute) <= 1):
            continue

        offset = prefs.get("offset", 0)

        papers = fetch_papers(field, start=offset)
        papers = filter_new_papers(papers, chat_id)

        # update offset
        prefs["offset"] = offset + cfg["app"]["papers_per_day"]
        users[str(chat_id)] = prefs

        for p in papers:
            try:
                summary = await asyncio.to_thread(summarize, p["summary"])
            except:
                summary = "Summary Unavailable"

            await send_paper(bot, int(chat_id), p, summary)

    from utils.file_utils import write_json
    write_json(cfg["paths"]["users_file"], users)

def start(bot):
    import asyncio
    
    loop = asyncio.get_event_loop()

    scheduler.configure(event_loop=loop)

    scheduler.add_job(
        job,
        "interval",
        minutes=cfg["scheduler"]["check_interval_minutes"],
        args=[bot]
    )

    scheduler.start()