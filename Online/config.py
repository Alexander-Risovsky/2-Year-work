from dotenv import load_dotenv
import os

load_dotenv()
host=os.environ.get("PG_DB_HOST")
user=os.environ.get("PG_DB_USER")
password=os.environ.get("PG_DB_PASSWORD")
db_name=os.environ.get("PG_DB_NAME")
port=os.environ.get("PG_DB_PORT")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dsn = f"dbname={db_name} user={user} password={password} host={host} port={port}"
#Названия схем
schema_name=[os.environ.get("SCHEMA_NAME")]

#Список запрещенных слов
with open(os.path.join(BASE_DIR, "RU_BAD_WORDS.txt"), encoding="utf-8") as f:
    russ_mat = f.readlines()

with open(os.path.join(BASE_DIR, "EN_BAD_WORDS.txt"), encoding="utf-8") as f:
    eng_mat = f.readlines()

with open(os.path.join(BASE_DIR, "extremism.txt"), encoding="utf-8") as f:
    extr = f.readlines()
with open(os.path.join(BASE_DIR, "white_list.txt"), encoding="utf-8") as f:
    white = f.readlines()

bad_words=set([i.strip() for i in russ_mat+eng_mat+extr])
white_list=set([i.strip() for i in white])
#Лимит для выкачки БД
limit=os.environ.get("BD_LIMIT")

