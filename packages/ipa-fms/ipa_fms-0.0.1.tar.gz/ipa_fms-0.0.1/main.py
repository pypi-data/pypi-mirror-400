import uvicorn
from fastapi import FastAPI
from typer import Typer

from biz import demo_biz_add

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


cmd = Typer()


@cmd.command()
def add(a: int, b: int) -> int:
    return demo_biz_add(a, b)


@cmd.command()
def sub(a: int, b: int) -> int:
    c = a - b
    print(f"sub({a}, {b}) = {c}")
    return c


@cmd.command()
def serve(host: str = "0.0.0.0", port: int = 8000):
    from conf import setup_database

    setup_database()

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    cmd()
