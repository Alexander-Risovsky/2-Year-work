from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from BadWordFilter import FilterBadWords

# Функция для проверки строки на содержание мата
async def check_string(string: str):
    filter_instance = FilterBadWords()
    offensive_content = await filter_instance.filter_bad_words(string.split())
    if offensive_content:
        return False
    return True

app = FastAPI()

class InputModel(BaseModel):
    input_string: str

class ResultModel(BaseModel):
    result: bool


@app.get("/check")
async def get_message_for_check(message: str):
    result =await check_string(message)
    return {"result": result}



if __name__ == "__main__":
    uvicorn.run("Web:app", host="127.0.0.1", port=8000, reload=True)
