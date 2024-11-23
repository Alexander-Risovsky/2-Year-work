import asyncio
import aiopg
from config import dsn
from typing import List

class DBLoader:
    def __init__(self, pool):
        self.pool = pool

    # Получаем презентации старше 1 дня
    async def select_presentation(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                presentation_id = []
                await cur.execute("""
                    SELECT id FROM presentation.presentation  WHERE date_creation < (CURRENT_DATE - INTERVAL '1 day') 
                    
                    and visible is true""")
                    #and copy is null
                    #and template is false
                    #and diaclass_pick is false
                    #пока закомментил так как в тестовых данных у всех през dia_pic is null

                async for row in cur:
                    presentation_id.append(row[0])
                return presentation_id

    # Получаем id слайдов для презентации с указанным id
    async def select_slides_from_presentation_slide(self, presentation_id):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                id_slide = []
                await cur.execute("SELECT id FROM presentation.slide WHERE id_presentation = %s", (presentation_id,))
                async for row in cur:
                    id_slide.append(row[0])
                return id_slide

    # Получаем контент из question и survey
    async def select_id_content(self, slides_id, table_name, id_column):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                content, ids = [], []
                await cur.execute(f"SELECT id, content FROM {table_name} WHERE {id_column} = ANY(%s)", (slides_id,))
                async for row in cur:
                    ids.append(row[0])
                    if row[1] is not None:
                        content.append(row[1])
                return ids, content

    # Получаем контент из options для вопроса или опроса
    async def select_options_content(self, ids, table_name, id_column):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                content = []
                await cur.execute(f"SELECT content FROM {table_name} WHERE {id_column} = ANY(%s)", (ids,))
                async for row in cur:
                    if row[0] is not None:
                        content.append(row[0])
                return content

    # Получаем контент для указанного id слайда
    async def select_content_from_slide(self, id_slide, table_name):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(f"SELECT content FROM presentation.{table_name} WHERE id_slide = %s", (id_slide,))
                content = ""
                async for row in cur:
                    if row[0] is not None:
                        content += row[0]
                return content

    # Сбор контента презентации
    async def take_content_from_presentation(self, presentation_id):
        slides_id = await self.select_slides_from_presentation_slide(presentation_id)
        if len(slides_id) < 4:
            return

        content = []
        for slide_id in slides_id:
            content_slide = await self.select_content_from_slide(slide_id, "content_slide")
            result_slide = await self.select_content_from_slide(slide_id, "result_slide")
            content.extend([content_slide, result_slide])

        question_ids, question_content = await self.select_id_content(slides_id, "question.question", "id_slide")
        question_option_content = await self.select_options_content(question_ids, "question.option", "id_question")

        survey_ids, survey_content = await self.select_id_content(slides_id, "survey.survey", "id_slide")
        survey_option_content = await self.select_options_content(survey_ids, "survey.survey_option", "id_survey")

        return content + question_content + question_option_content + survey_content + survey_option_content

    # Обновление тега презентации
    async def update_presentation_tag(self, presentation_id, tag_value):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("UPDATE presentation.presentation SET copy = %s WHERE id = %s",
                                  (str(tag_value).lower(), presentation_id))
