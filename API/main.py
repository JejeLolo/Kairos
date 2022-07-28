from fastapi import FastAPI, Request
from typing import Union

app = FastAPI()

@app.get("/")
def read_root():
    return "Server is Alive"


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/login")
async def login(request: Request):
    print(await request.json())
    return {}
