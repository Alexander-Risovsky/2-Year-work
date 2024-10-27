host="127.0.0.1"
user="postgres"
password="123"
db_name="cURCAS"
port="4321"


#Названия схем
schema_name=['survey','question','presentation']

#Список запрещенных слов
russ_mat=open("Маты на русском", encoding="utf-8").readlines()
eng_mat=open("Маты на английском",encoding="utf-8").readlines()
extr=open("Экстремизм",encoding="utf-8").readlines()
bad_words=[i.strip() for i in russ_mat+eng_mat+extr]

