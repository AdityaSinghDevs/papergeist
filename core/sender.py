async def send_paper(bot, chat_id, paper, summary):
    caption = f"📄 {paper['title']}\n\n{summary}"
    
    await bot.send_document(
        chat_id,
        paper["pdf"].replace("http://", "https://"),
        caption=caption
    )