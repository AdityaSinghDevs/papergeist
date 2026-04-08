from aiogram.utils import executor
from core.bot import dp, bot
from core.scheduler import start

if __name__ == "__main__":
    start(bot)
    executor.start_polling(dp, skip_updates=True)