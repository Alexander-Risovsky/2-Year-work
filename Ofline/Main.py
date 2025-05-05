import asyncio
import aiopg
from config import dsn,limit
from ImportFromDB import DBLoader
from BadWordFilter import FilterBadWords
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


async def about_presentation(pool, presentation_ids):
    db_loader = DBLoader(pool)
    content_processor = FilterBadWords()

    for presentation_id in presentation_ids:
        content = await db_loader.take_content_from_presentation(presentation_id)
        if content: #Если есть какой-то контент то проверяем
            content = await content_processor.edit_content(content)
            offensive_content = await content_processor.filter_bad_words(content)
            if offensive_content: #Если есть нецензерный контент, то ставим False
                await db_loader.update_presentation_tag(presentation_id, False)
            else:   #Иначе ставим True
                await db_loader.update_presentation_tag(presentation_id, True)
        # else: #Если нет контента, то ставим False
        #     await db_loader.update_presentation_tag(presentation_id, False)

async def main():
    async with aiopg.create_pool(dsn) as pool:
        db_loader = DBLoader(pool)
        presentation_ids = await db_loader.select_presentation(limit)
        await about_presentation(pool, presentation_ids)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
