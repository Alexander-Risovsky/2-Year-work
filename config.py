from dotenv import load_dotenv
import os

load_dotenv()
host=os.environ.get("PG_DB_HOST")
user=os.environ.get("PG_DB_USER")
password=os.environ.get("PG_DB_PASSWORD")
db_name=os.environ.get("PG_DB_NAME")
port=os.environ.get("PG_DB_PORT")

dsn = f"dbname={db_name} user={user} password={password} host={host} port={port}"
#Названия схем
schema_name=[os.environ.get("SCHEMA_NAME")]

#Список запрещенных слов
russ_mat=open("RU_BAD_WORDS", encoding="utf-8").readlines()
eng_mat=open("EN_BAD_WORDS", encoding="utf-8").readlines()
extr=open("extremism", encoding="utf-8").readlines()
bad_words=[i.strip() for i in russ_mat+eng_mat+extr]



