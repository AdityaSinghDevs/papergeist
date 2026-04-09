from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import asyncio

from utils.env_loader import BOT_TOKEN
from utils.file_utils import read_json, write_json
from utils.config_loader import load_cfg

cfg = load_cfg("configs/config.yaml")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())



class UserState(StatesGroup):
    waiting_for_field = State()
    waiting_for_time = State()


# ------------------ KEYBOARD ------------------

def main_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton("Set Field"),
        KeyboardButton("Set Time")
    )
    kb.add(
        KeyboardButton("Get Papers"),
        KeyboardButton("My Prefs")
    )
    return kb


# ------------------ START ------------------

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
    
    "go on, summon something interesting.\n\n"
    
    "You can also use quick buttons to save time!! hasta la vista",
    
    reply_markup=main_keyboard()
)


# ------------------ SET FIELD FLOW ------------------

@dp.message_handler(lambda msg: msg.text == "Set Field")
async def ask_field(msg: types.Message):
    await msg.reply("what field do you want?")
    await UserState.waiting_for_field.set()


@dp.message_handler(state=UserState.waiting_for_field)
async def save_field(msg: types.Message, state: FSMContext):
    field = msg.text

    users = read_json(cfg["paths"]["users_file"], {})
    user = users.get(str(msg.chat.id), {})
    user["field"] = field

    users[str(msg.chat.id)] = user
    write_json(cfg["paths"]["users_file"], users)

    await msg.reply(f"got it. field = {field}", reply_markup=main_keyboard())
    await state.finish()


# ------------------ SET TIME FLOW ------------------

@dp.message_handler(lambda msg: msg.text == "Set Time")
async def ask_time(msg: types.Message):
    await msg.reply("enter hour (0–23)")
    await UserState.waiting_for_time.set()


@dp.message_handler(state=UserState.waiting_for_time)
async def save_time(msg: types.Message, state: FSMContext):
    try:
        hour = int(msg.text)
        assert 0 <= hour <= 23
    except:
        await msg.reply("enter a valid hour (0–23)")
        return

    users = read_json(cfg["paths"]["users_file"], {})
    user = users.get(str(msg.chat.id), {})
    user["hour"] = hour

    users[str(msg.chat.id)] = user
    write_json(cfg["paths"]["users_file"], users)

    await msg.reply(f"time set to {hour}:00", reply_markup=main_keyboard())
    await state.finish()


# ------------------ PREFS ------------------

@dp.message_handler(lambda msg: msg.text == "My Prefs")
async def prefs(msg: types.Message):
    users = read_json(cfg["paths"]["users_file"], {})
    user = users.get(str(msg.chat.id), {})
    
    await msg.reply(str(user), reply_markup=main_keyboard())


# ------------------ PAPERS ------------------

@dp.message_handler(lambda msg: msg.text == "Get Papers")
async def manual(msg: types.Message):
    from core.fetcher import fetch_papers
    from core.processor import filter_new_papers
    from core.llm import summarize
    from core.sender import send_paper

    try:
        users = read_json(cfg["paths"]["users_file"], {})
        user = users.get(str(msg.chat.id), {})
        field = user.get("field", cfg["app"]["default_field"])
        
        await msg.reply("fetching papers...")

        papers = fetch_papers(field)
        papers = filter_new_papers(papers)

        if not papers:
            await msg.reply("no papers found")
            return

        for p in papers:
            try:
                summary = await asyncio.to_thread(summarize, p["summary"])
            except:
                summary = "summary unavailable"

            await send_paper(bot, msg.chat.id, p, summary)

    except Exception as e:
        print("ERROR:", e)
        await msg.reply("something broke")