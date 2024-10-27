import asyncio
import aiopg
from config import host, port, user, db_name, password
from typing import List
from config import bad_words

dsn = f"dbname={db_name} user={user} password={password} host={host} port={port}"

#Берем презентации у которых дата создание октябрь 2024 года, потом поменяю на день
async def select_presentation(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            presentation_id = []
            await cur.execute(
                        f"SELECT id FROM presentation.presentation "
                        f"WHERE EXTRACT(MONTH FROM date_creation) = 10 "
                        f"AND EXTRACT(YEAR FROM date_creation) = 2024;"
                    )
            async for row in cur:
                        presentation_id.append(row[0])
            return presentation_id
#Берем id слайдов, которые в ходят в презентацию у которой id=presentation_id
async def select_slides_from_presentation_slide(pool, presentation_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            id_slide = []
            await cur.execute(f"SELECT * FROM presentation.slide WHERE id_presentation = {presentation_id}")
            async for row in cur:
                id_slide.append(row[0])
            return id_slide
#Берем id вопросов и контент на них
async def select_id_question_and_content_from_question_question(pool, slides_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            content = []
            id_question=[]
            await cur.execute("SELECT id,content FROM question.question WHERE id_slide = ANY(%s)",
                (slides_id,)  )
            async for row in cur:
                id_question.append(row[0])
                content.append(row[1])
            return content,id_question,

##Берем id опросов и контент на них
async def select_id_survey_and_content_from_survey_survey(pool, slides_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            content = []
            id_survey=[]
            await cur.execute("SELECT id,content FROM survey.survey WHERE id_slide = ANY(%s)",
                (slides_id,)  )
            async for row in cur:
                content.append(row[1])
                id_survey.append([row[0]])
            return id_survey,content

#Берем контент из survey.option, где id_question=question_id
async def select_content_from_survey_option(pool, survey_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            content = []
            await cur.execute("SELECT content FROM  survey.survey_option WHERE id_survey = ANY(%s)",
                (survey_id,)  )
            async for row in cur:
                content.append(row[0])
            return content

#Берем контент из question.option, где id_question=question_id
async def select_content_from_question_option(pool, question_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            content = []
            await cur.execute("SELECT content FROM question.option WHERE id_question = ANY(%s)",
                (question_id,)  )
            async for row in cur:
                content.append(row[0])
            return content


async def select_content_from_slide(pool, id_slide):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(f"SELECT content FROM presentation.content_slide WHERE id_slide = {id_slide}")
            content = ""
            async for row in cur:
                content += row[0]
            return content

# Фильтр для анализа контента
import re
from config import bad_words
import html as html1
from lxml import html



async def main():
    async with aiopg.create_pool(dsn) as pool:
        presentation_ids = await select_presentation(pool)

        await about_presentation(pool,presentation_ids)

async def take_content_from_presentation(pool,presentation_id):
    slides_id = await select_slides_from_presentation_slide(pool, presentation_id)
    if len(slides_id)>=4: #если слайдов больше 4
        slides_content = []
        # добавляем контент со всех слайдов презентации
        for j in range(len(slides_id)):
            con = await select_content_from_slide(pool, slides_id[j])
            slides_content.append(con)

        # получаем id вопросов и контент вопроса
        question_content, question_id = await select_id_question_and_content_from_question_question(pool, slides_id)

        # получаем контент с question.option
        question_option_content = await select_content_from_question_option(pool, question_id)

        # получаем id опросов и контент вопроса
        survey_id,survey_content=await select_id_survey_and_content_from_survey_survey(pool,slides_id)

        # получаем контент с survey.option
        survey_option_content=await select_content_from_survey_option(pool,survey_id)
        return slides_content+question_content+question_option_content+survey_content+survey_option_content
    else:
        return 0

#Обработка одной презентации

#Убираем html
async def edit_text(text_escaped):
    if len(text_escaped)!=0:
        unescaped_text = html1.unescape(text_escaped)
        text = html.fromstring(unescaped_text)
        return text.text_content()
    return text_escaped

async def edit_content(content):
    if len(content)!=0:
        return await asyncio.gather(*(edit_text(item) for item in content))
    return content

# Функция для нормализации строки
def normalize_text(text: str) -> str:
    replacements = {
        '@': 'а', '*': '', '1': 'и', 'i': 'и', '!': 'и', '3': 'з', '$': 'с', '0': 'о'
    }
    text = text.lower()
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

# Функция для построения универсальных регулярных выражений
def build_regex(bad_word: str) -> re.Pattern:
    # Преобразуем слово в паттерн с возможными заменами символов
    pattern = bad_word.replace('а', '[аa@]').replace('и', '[иi1!]') \
        .replace('о', '[оo0]').replace('з', '[з3]').replace('с', '[с$]')

    return re.compile(pattern, re.IGNORECASE)

# Функция проверки строки на содержание матов
async def check_bad_words(text: str, bad_words_patterns: List[re.Pattern]) -> bool:
    normalized_text = normalize_text(text)

    for pattern in bad_words_patterns:
        if pattern.search(normalized_text):
            return True
    return False


#Функция для проверки массива строк
async def filter_bad_words(texts: List[str]) -> List[str]:
    # Компилируем регулярные выражения для всех плохих слов
    bad_words_patterns = [build_regex(word) for word in bad_words if word.strip()]
    tasks = [check_bad_words(text, bad_words_patterns) for text in texts]
    results = await asyncio.gather(*tasks)

    # Возвращаем список строк, содержащих маты
    return [text for text, has_bad_word in zip(texts, results) if has_bad_word]
async def about_presentation(pool,presentation_ids):
    async with aiopg.create_pool(dsn) as pool:
        for presentation_id in presentation_ids:
            #Получили контент для презентации
            content=await take_content_from_presentation(pool,presentation_id)
            if content!=0:
                #Удаление html разметки из контента
                content=await edit_content(content)

                offensive_content = await filter_bad_words(content)
                if offensive_content:
                    await update_teg_copy_presentation_false(pool, presentation_id)
                else:
                    await update_teg_copy_presentation_true(pool,presentation_id)


                # print(f"Контент со слайдов:{slides_content}")
                # print(f"Контент с question.question:{question_content}",i)
                # print(f"Контент с question_option_content:{question_option_content}")
                # print(f"Контент с survey.survey:{survey_content}")
                # print(f"Контент с survey.option:{survey_option_content}")
                #print(f"Матерный контент:{offensive_content}")
            else:
                await update_teg_copy_presentation_false(pool,presentation_id)

async def update_teg_copy_presentation_false(pool, presentation_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE presentation.presentation SET copy = %s WHERE id = %s",
                ("false", presentation_id)
            )

async def update_teg_copy_presentation_true(pool, presentation_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE presentation.presentation SET copy = %s WHERE id = %s",
                ("true", presentation_id)
            )


# Запуск программы
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())






