from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
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
    users = read_json(cfg["path"]["users_file"], {})

    current_hour = datetime.now().hour

    for chat_id, prefs in users.items():
        user_hour = prefs.get("hour", 9)
        field = prefs.get("field", cfg["app"]["default_field"])

        if user_hour != current_hour:
            continue

        papers = fetch_papers(field)
        papers = filter_new_papers(papers)

        for p in papers:
            try:
                summary = await asyncio.to_thread(summarize, p["summary"])
            except:
                summary = "Summary Unavailable"

            await send_paper(bot, int(chat_id), p, summary)

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