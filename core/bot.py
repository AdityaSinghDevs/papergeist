from aiogram import Bot, Dispatcher, types 
import asyncio 

from utils.env_loader import BOT_TOKEN
from utils.file_utils import read_json, write_json
from utils.config_loader import load_cfg

cfg = load_cfg("configs/config.yaml")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.reply(
        "👻 Boo! I'm PaperGeist\n"
        "yeah yeah relax, i'm not that kind of ghost.\n"
        "i just haunt research papers and drop them in your chat.\n\n"
        
        "here’s how this works:\n\n"
        
        "1) tell me what you care about\n"
        "/setfield {your topic of interest}\n\n"
        
        "2) tell me at what hour to bother you (0–23) daily\n"
        "/settime 18\n\n"
        
        "that’s it. i’ll send you papers daily at that time.\n\n"
        
        "Want papers right now?\n"
        "/papers\n\n"
        
        "other stuff:\n"
        "/myprefs – see what you told me\n"
        "/setfield <topic> – change your field\n"
        "/settime <hour> – change timing\n\n"
        
        "this is a prototype, so if something breaks...\n"
        "just assume it’s part of the haunting.\n\n"
        
        "go on, summon something interesting.",
        
        parse_mode=None
    )

@dp.message_handler(commands=["setfield"])
async def set_field(msg: types.Message):
    field = msg.get_args()
    
    users = read_json(cfg["paths"]["users_file"], {})
    
    user = users.get(str(msg.chat.id), {})
    user["field"] = field
    
    users[str(msg.chat.id)] = user
    write_json(cfg["paths"]["users_file"], users)
    
    await msg.reply(f"Field set to: {field}")

@dp.message_handler(commands=["settime"])
async def set_time(msg: types.Message):
    try:
        hour = int(msg.get_args())
        assert 0 <= hour <= 23
    except:
        await msg.reply("X use hour 0-23")
        return
    
    users = read_json(cfg["paths"]["users_file"], {})
    
    user = users.get(str(msg.chat.id), {})
    user["hour"] = hour
    
    users[str(msg.chat.id)] = user
    write_json(cfg["paths"]["users_file"], users)
    
    await msg.reply(f"⏰ Time set to: {hour}:00 daily")

@dp.message_handler(commands=["myprefs"])
async def prefs(msg: types.Message):
    users = read_json(cfg["paths"]["users_file"], {})
    user = users.get(str(msg.chat.id), {})
    
    await msg.reply(str(user))

@dp.message_handler(commands=["papers"])
async def manual(msg: types.Message):
    import asyncio
    from core.fetcher import fetch_papers
    from core.processor import filter_new_papers
    from core.llm import summarize
    from core.sender import send_paper
    
    try:
        users = read_json(cfg["paths"]["users_file"], {})
        user = users.get(str(msg.chat.id), {})
        field = user.get("field", cfg["app"]["default_field"])
        
        await msg.reply("fetching papers... hang on")
        
        papers = fetch_papers(field)
        papers = filter_new_papers(papers)
        
        if not papers:
            await msg.reply("no new papers found (or ghost ate them)")
            return
        
        for p in papers:
            try:
                summary = await asyncio.to_thread(summarize, p["summary"])
            except Exception as e:
                print("Groq error:", e)
                summary = "summary unavailable"
            
            await send_paper(bot, msg.chat.id, p, summary)

    except Exception as e:
        print("PAPERS ERROR:", e)
        await msg.reply("something broke while fetching papers")